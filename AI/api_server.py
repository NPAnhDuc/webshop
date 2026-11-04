"""
TechStore AI Chatbot & RAG Model Microservice
---------------------------------------------
FastAPI service exposing REST API endpoints for Docker deployment.
Bridges directly to TechStore Web Backend (Node.js/Express).

Only the web backend calls this service; browsers never do. The backend decides who
is asking (its own login) and picks the endpoint; the role is never read from the body.
Environment:
  AI_INTERNAL_KEY     shared secret sent by the backend as X-Internal-Key. Required for
                      /api/chat/admin (refused while unset); also required for customer
                      chat once set.
  AI_ALLOWED_ORIGINS  comma-separated browser origins for CORS; empty = no CORS.
  AI_SESSION_TTL      seconds a conversation is remembered (default 1800).
  AI_SESSION_LIMIT    conversations kept in memory (default 5000).
"""
import hmac
import os
import re
import sqlite3
import sys
import threading
import time
from collections import OrderedDict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure root paths are in sys.path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

app = FastAPI(
    title="TechStore AI Chatbot & RAG Model Microservice",
    description="Containerized AI inference microservice for TechStore",
    version="1.0.0"
)

# Server-to-server calls need no CORS; list browser origins only if one must call directly.
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("AI_ALLOWED_ORIGINS", "").split(",") if o.strip()]
if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=False,
        allow_methods=["POST", "GET"],
        allow_headers=["Content-Type", "X-Internal-Key"],
    )


def require_internal_key(supplied: Optional[str], admin: bool):
    expected = os.getenv("AI_INTERNAL_KEY", "")
    if not expected:
        if admin:
            raise HTTPException(status_code=503, detail="AI_INTERNAL_KEY chưa được cấu hình; kênh admin bị khoá.")
        return
    if not supplied or not hmac.compare_digest(supplied.encode(), expected.encode()):
        raise HTTPException(status_code=401, detail="Không có quyền gọi dịch vụ AI.")


class SessionStore:
    """Conversation memory per (role, sessionId); a customer id never reads an admin profile."""

    def __init__(self, ttl: float, limit: int):
        self.ttl, self.limit = ttl, limit
        self.items: "OrderedDict[tuple, tuple]" = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            item = self.items.get(key)
            if not item or time.monotonic() - item[0] > self.ttl:
                self.items.pop(key, None)
                return {}
            return dict(item[1])

    def put(self, key, profile):
        with self.lock:
            self.items[key] = (time.monotonic(), dict(profile))
            self.items.move_to_end(key)
            while len(self.items) > self.limit:
                self.items.popitem(last=False)


sessions = SessionStore(float(os.getenv("AI_SESSION_TTL", "1800")), int(os.getenv("AI_SESSION_LIMIT", "5000")))
SESSION_ID = re.compile(r"^[A-Za-z0-9_.:-]{8,128}$")


def session_key(role: str, session_id: Optional[str]):
    if session_id is None:
        return None  # stateless: every question stands alone
    if not SESSION_ID.match(session_id):
        raise HTTPException(status_code=400, detail="sessionId không hợp lệ (8-128 ký tự chữ, số, _ . : -).")
    return (role, session_id)


# "[Nguồn: …]" and labelled variants such as "[Nguồn phép tính: …]".
CITATION = re.compile(r"\s*\[Nguồn[^:\]]*:[^\]]*\]")
INTERNAL_PATH = re.compile(r"\s*\((?:data|runtime)/[^)]*\)")


def for_reader(answer: str) -> str:
    """Web readers get the answer without evidence markers or internal file paths. The engine keeps
    them (evaluation checks every claim against its quote); only this presentation drops them."""
    text = INTERNAL_PATH.sub("", CITATION.sub("", answer or ""))
    # Two documents often state the same fact; without the citations the repeat is just noise.
    # Only wording may differ: paragraphs with different numbers (months, amounts) are distinct facts.
    paragraphs, seen = [], []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        key = re.sub(r"\W+", " ", paragraph.lower()).strip()
        numbers = re.findall(r"\d+", key)
        if paragraph and not any(numbers == other_numbers and SequenceMatcher(None, key, other).ratio() >= 0.8
                                 for other, other_numbers in seen):
            seen.append((key, numbers))
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


def answer_products(result: Dict[str, Any], limit: int = 5) -> list:
    """Products the answer rests on, in the order it used them, for the web's product cards.
    Names and prices always come from the shop database, never from model text."""
    wanted = [("name", row["name"]) for row in result.get("rows") or [] if isinstance(row, dict) and row.get("name")]
    wanted += [("sku", str(source.get("document_id", "")).removeprefix("catalog-"))
               for source in result.get("sources") or []
               if isinstance(source, dict) and source.get("doc_type") == "product"]
    if not wanted or db_path is None:
        return []
    from shopbot.store import connect

    products: Dict[str, Dict[str, Any]] = {}
    try:
        with connect(db_path, readonly=True) as con:
            for column, value in wanted:
                row = con.execute(f"SELECT sku, name, price FROM products WHERE {column} = ?", (value,)).fetchone()
                if row and len(products) < limit:
                    products.setdefault(row["sku"], dict(sku=row["sku"], name=row["name"], price=row["price"]))
    except sqlite3.Error as e:
        # Cards are extra; the written answer must still reach the shopper.
        print(f"[AI Model Server] product lookup error: {e!r}")
        return []
    return list(products.values())


def ask(eng, question: str, role: str, session_id: Optional[str]):
    key = session_key(role, session_id)
    result = eng.ask(question, role=role, profile=sessions.get(key) if key else {})
    if key:
        sessions.put(key, result.get("profile", {}))
    return result


# Lazy/Graceful initialization of the shopbot Engine
engine = None
db_path = None
knowledge_documents = None

def get_engine():
    global engine, db_path, knowledge_documents
    if engine is None:
        try:
            from shopbot.store import initialize, connect
            from shopbot.engine import Engine
            from shopbot.knowledge import KnowledgeStore

            db_path = (ROOT / os.getenv("SHOP_DATABASE", "data/structured/shop.db")).resolve()
            if not db_path.exists():
                fallback = (ROOT / "data" / "structured" / "shop.db").resolve()
                if fallback.exists():
                    db_path = fallback

            initialize(db_path)
            engine = Engine(db_path)
            print(f"[AI Model Server] Initialized Engine with database: {db_path}")
            knowledge_documents = len(KnowledgeStore(db_path).all_records())
            if not knowledge_documents:
                print(f"[AI Model Server] WARNING: no knowledge documents for {db_path}; answers will have no sources.")
        except Exception as e:
            print(f"[AI Model Server] Engine init error: {e}")
    return engine

class CustomerChatRequest(BaseModel):
    message: str
    sessionId: Optional[str] = None
    pageContext: Optional[Dict[str, Any]] = None

class AdminChatRequest(BaseModel):
    query: str
    sessionId: Optional[str] = None

@app.get("/")
@app.get("/health")
def health_check():
    eng = get_engine()
    return {
        "status": "degraded" if eng is None or knowledge_documents == 0 else "healthy",
        "service": "techstore-ai-model-docker",
        "engineLoaded": eng is not None,
        "knowledgeDocuments": knowledge_documents,
        "adminChannel": bool(os.getenv("AI_INTERNAL_KEY")),
    }

@app.post("/api/chat/customer")
def chat_customer(req: CustomerChatRequest, x_internal_key: Optional[str] = Header(default=None)):
    require_internal_key(x_internal_key, admin=False)
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Tin nhắn không được để trống")

    eng = get_engine()
    if eng is None:
        # Fallback response if engine cannot load SQLite
        return {
            "success": True,
            "replyText": "Chào bạn! Tôi là Trợ lý AI TechStore được đóng gói Docker. Rất sẵn lòng hỗ trợ bạn tìm kiếm cấu hình máy tính và giải đáp thắc mắc!",
            "suggestedPills": ["Tư vấn Laptop Gaming", "Build PC 25 triệu", "Chính sách trả góp"],
            "action": "ai_docker_response"
        }

    try:
        # Run inference through shopbot.engine
        result = ask(eng, req.message, "customer", req.sessionId)
        reply_text = for_reader(result.get("answer") or result.get("replyText")) or "Chào bạn! Em có thể giúp gì cho bạn về máy tính và linh kiện ạ?"

        return {
            "success": True,
            "replyText": reply_text,
            "suggestedPills": [
                "Tư vấn thêm chi tiết",
                "Laptop trong tầm giá này",
                "Chính sách bảo hành"
            ],
            # Document names and chunk ids stay server-side; shoppers only see the answer.
            "products": answer_products(result),
            "action": "ai_inference"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI Model Server] customer chat error: {e!r}")
        raise HTTPException(status_code=500, detail="Lỗi suy luận Model AI.")

@app.post("/api/chat/admin")
def chat_admin(req: AdminChatRequest, x_internal_key: Optional[str] = Header(default=None)):
    require_internal_key(x_internal_key, admin=True)
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Câu hỏi không được để trống")

    eng = get_engine()
    if eng is None:
        return {
            "success": True,
            "thoughtSummary": "Docker AI Model Service (Fallback Mode)",
            "insight": "Dịch vụ Docker AI đang hoạt động và sẵn sàng kết nối mô hình phân tích số liệu."
        }

    try:
        result = ask(eng, req.query, "admin", req.sessionId)
        return {
            "success": True,
            "thoughtSummary": f"Chế độ phân tích RAG: {result.get('mode', 'SQL Analytics')}",
            "insight": for_reader(result.get("answer", "")),
            "analysis": result.get("analysis", {}),
            "sources": result.get("sources", [])
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AI Model Server] admin chat error: {e!r}")
        raise HTTPException(status_code=500, detail="Lỗi phân tích AI Admin.")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
