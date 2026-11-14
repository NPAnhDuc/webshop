from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)
TRACE = "router live_product overridden: no price, stock or order asked"


def run_with_router(monkeypatch, question, *, role="customer", profile=None):
    route = {
        "action": "live_product",
        "query": question,
        "doc_types": ["product"],
        "category": "all",
        "private_request": False,
        "task": "lookup",
        "strict_filters": False,
    }

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}) and "parts" not in payload:
            return route
        parts = list(payload["parts"])
        return dict(action="answer", answers={key: [] for key in parts},
                    missing=parts, negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr(grounded_rag, "search", lambda *args, **kwargs: [])
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    return grounded_rag.answer(question, role, profile or {}, DB, TODAY)


@pytest.mark.parametrize("question", [
    "Có mẫu chuột này màu trắng không?",
    "Chuột này có kích thước nào?",
    "Bàn phím này nặng bao nhiêu?",
    "Mẫu này có những cổng kết nối nào?",
    "Bàn phím dùng loại switch nào?",
    "Mẫu này có bản đèn RGB không?",
    "Mau chuot nay mau tim co khong?",
])
def test_non_live_product_attributes_are_sent_to_documents(monkeypatch, question):
    result = run_with_router(monkeypatch, question)

    assert TRACE in result["trace"]
    assert result["basic_action"] != "live_product"
    assert result["plan"]["doc_types"] == ["product"]


@pytest.mark.parametrize("question", [
    "Mẫu chuột này giá bao nhiêu?",                     # price
    "Tôi cần bao nhiêu tiền để mua mẫu này?",           # money
    "Mẫu nào rẻ nhất hiện nay?",                         # price ranking
    "Chốt giá mẫu này giúp tôi.",                       # price negotiation
    "Mẫu này còn hàng không?",                          # stock
    "Mẫu này tồn kho bao nhiêu?",                       # stock
    "con hang de giu toi chieu dc ko",                  # unaccented hold/order
    "Đặt cọc mẫu này được không?",                      # deposit/order
    "Tôi chuyển khoản thế nào?",                        # payment
    "Thanh toán tại cửa hàng được không?",              # payment
    "Xác nhận đơn hàng giúp tôi.",                      # order
    "Ngân sách 15 triệu chọn được mẫu nào?",            # budget
    "Mẫu này giá 500k không?",                          # numeric budget
    "Mẫu này còn hàng hôm nay không?",                  # time-sensitive stock
])
def test_live_product_signal_keeps_router_decision(monkeypatch, question):
    result = run_with_router(monkeypatch, question)

    assert TRACE not in result["trace"]
    assert result["basic_action"] == "live_product"


def test_admin_live_product_decision_is_deferred(monkeypatch):
    result = run_with_router(monkeypatch, "Mẫu chuột này màu tím có không?", role="admin")

    assert "router live_product overridden: admin requests go to deferred" in result["trace"]
    assert result["basic_action"] == "deferred"


@pytest.mark.parametrize("profile", [
    {"history": [{"role": "user", "content": "Mẫu chuột này giá bao nhiêu?"}]},
    {"rag_product_subject": "Ternix Glide Pro"},
    {"rag_subject": "Ternix Glide Pro"},
])
def test_prior_conversation_context_preserves_live_product_decision(monkeypatch, profile):
    result = run_with_router(monkeypatch, "Nó màu tím có không?", profile=profile)

    assert TRACE not in result["trace"]
    assert result["basic_action"] == "live_product"
