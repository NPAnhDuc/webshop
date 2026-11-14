"""Deterministic answers for one approved sales-plan target at a time."""
from __future__ import annotations

import json
import re
from pathlib import Path

from .retrieval import normalize

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ROOT / "data/business_sql/scenario_v1/documents"
MANIFEST = DOCUMENTS / "manifest.json"

COMPARISON = re.compile(
    r"\b(?:so sanh|chenh lech|khac nhau|cao hon|thap hon|vuot ke hoach|"
    r"so voi|hon ke hoach|duoi ke hoach|tang bao nhieu|giam bao nhieu)\b"
)
DRAFT = re.compile(r"\b(?:ban nhap|draft|du thao)\b")
ACTUAL = re.compile(r"\b(?:thuc hien|thuc te|da dat|da ban|doanh thu shop|doanh thu thuc)\b")
PLAN_WORDS = re.compile(r"\b(?:muc tieu|ke hoach|chi tieu|du kien)\b")
NAMED_TARGET = re.compile(
    r"\b(?:doanh thu|doanh so|bien|loi nhuan|lai|gia von|chi phi|don hang|"
    r"hoan tra|marketing|ngan sach|ton kho)\b"
)

REPORT = re.compile(r"\bbao cao\b")
PLAN_DOCUMENT = re.compile(r"\b(?:ke hoach|muc tieu)\b")
# Distinct target families. A question naming two or more of them is a multi-metric
# request (often a monthly report), which this reader leaves to the normal flow.
TARGET_FAMILIES = {
    "revenue": re.compile(r"\b(?:doanh thu|doanh so)\b"),
    "margin": re.compile(r"\bbien\b"),
    "cost": re.compile(r"\b(?:gia von|chi phi)\b"),
    # Not bare "lai": without accents it is also "lại" ("nhắc lại", "lấy lại").
    "profit": re.compile(r"\b(?:loi nhuan|lai gop|lai rong|lai truoc)\b"),
    "orders": re.compile(r"\bdon hang\b"),
    "returns": re.compile(r"\bhoan tra\b"),
    "inventory": re.compile(r"\bton kho\b"),
    "marketing": re.compile(r"\b(?:marketing|ngan sach)\b"),
}


def _target_families(q):
    text = q.replace("sau hoan tra", " ")
    text = re.sub(r"\bbien loi nhuan gop\b", "bien gop", text)
    text = re.sub(r"\b(?:chi phi|ngan sach) marketing\b", "marketing", text)
    return {name for name, pattern in TARGET_FAMILIES.items() if pattern.search(text)}


METRICS = {
    "quarter_net_sales": re.compile(r"\b(?:doanh thu thuan|doanh so thuan|doanh so)\b"),
    "gross_margin": re.compile(r"\b(?:bien gop|bien loi nhuan gop)\b"),
    "month_sales": re.compile(r"\bdoanh thu\b"),
    "marketing": re.compile(r"\bmarketing\b"),
}


def plan_request(question, role, scope) -> dict | None:
    """Recognize a single plan-target reading with exactly one resolved period."""
    if role != "admin" or not isinstance(question, str) or not isinstance(scope, dict):
        return None
    q = normalize(question)
    if not q or DRAFT.search(q) or ACTUAL.search(q) or COMPARISON.search(q):
        return None
    if REPORT.search(q) and not PLAN_DOCUMENT.search(q):
        return None
    if len(_target_families(q)) > 1:
        return None

    months = list(dict.fromkeys(scope.get("months") or []))
    quarters = list(dict.fromkeys(scope.get("quarters") or []))
    quarter_only = len(quarters) == 1 and not months
    month_only = len(months) == 1 and not quarters
    combined_quarter_month = False
    if len(quarters) == 1 and len(months) == 1:
        try:
            year, number = map(int, months[0].split("-"))
            month_quarter = f"{year:04}-Q{(number - 1) // 3 + 1}"
        except (ValueError, TypeError):
            return None
        combined_quarter_month = month_quarter == quarters[0]
    if not (quarter_only or month_only or combined_quarter_month):
        return None

    has_plan_context = bool(PLAN_WORDS.search(q))
    candidates = []
    if has_plan_context and METRICS["gross_margin"].search(q):
        candidates.append("gross_margin")
    if has_plan_context and re.search(r"\b(?:ngan sach|chi phi|thuong xuyen)\b", q) and METRICS["marketing"].search(q):
        candidates.append("marketing")
    revenue_request = bool(METRICS["month_sales"].search(q) or METRICS["quarter_net_sales"].search(q))
    if has_plan_context and revenue_request:
        candidates.append("month_sales" if (month_only or combined_quarter_month) else "quarter_net_sales")
    if has_plan_context and quarter_only and re.search(r"\b(?:muc tieu|chi tieu)\b", q):
        # In this plan format an unnamed quarterly target means net sales, unless
        # the question names a different target. "Sau hoàn trả" is the net-sales
        # definition, not a separate returns target.
        target_terms = q.replace("sau hoan tra", " ")
        if not NAMED_TARGET.search(target_terms):
            candidates.append("quarter_net_sales")
    candidates = list(dict.fromkeys(candidates))
    if len(candidates) != 1:
        return None

    metric = candidates[0]
    if metric == "month_sales":
        month = months[0]
        year, number = map(int, month.split("-"))
        quarter = f"{year:04}-Q{(number - 1) // 3 + 1}"
        return {"metric": metric, "period": quarter, "month": month}
    if months:
        return None
    return {"metric": metric, "period": quarters[0], "month": None}


def _source_record(period):
    filename = f"sales-plan-{period}-v1.md"
    if not re.fullmatch(r"sales-plan-20\d{2}-Q[1-4]-v1\.md", filename):
        return None
    try:
        records = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    record = next((item for item in records
                   if item.get("source") == filename
                   and item.get("document_id") == filename.removesuffix("-v1.md")
                   and item.get("doc_type") == "sales_plan"
                   and item.get("status") == "approved"
                   and item.get("audience") == "admin"), None)
    if record is None:
        return None
    path = DOCUMENTS / filename
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    source = dict(record, text=text)
    return source


def _fragment_matches(fragment, request):
    text = normalize(fragment["text"])
    metric = request["metric"]
    if metric == "quarter_net_sales":
        return "muc tieu doanh thu thuan sau hoan tra" in text and "chua vat" in text
    if metric == "gross_margin":
        return "bien loi nhuan gop muc tieu" in text
    if metric == "marketing":
        return "marketing thuong xuyen" in text
    if metric == "month_sales":
        month = request["month"]
        return any(line.strip().startswith(f"| {month} |") for line in fragment["text"].splitlines())
    return False


def answer_plan(request) -> dict:
    """Return one source-owned unit, or a clear missing-approved-plan answer."""
    period = request["period"]
    document = _source_record(period)
    if document is None:
        return {
            "answer": f"Chưa có kế hoạch đã duyệt cho kỳ {period}.",
            "period": period,
            "source": None,
            "claim": None,
            "answerability": "none",
        }

    from .chunking import chunk_document
    from .rag_answer import evidence_fragments

    chunks = chunk_document(document)
    fragments = evidence_fragments(chunks)
    fragment = next((item for item in fragments.values() if _fragment_matches(item, request)), None)
    if fragment is None:
        return {
            "answer": f"Chưa tìm thấy chỉ tiêu này trong kế hoạch đã duyệt cho kỳ {period}.",
            "period": period,
            "source": None,
            "claim": None,
            "answerability": "none",
        }

    source = fragment["source"]
    text = fragment["text"]
    citation = (f"[Nguồn: {source['source']}, mục {source.get('heading_path', '')}, "
                f"đoạn {source['section']}, phiên bản {source.get('version', 'chưa rõ')}]")
    answer = f"{text}\n\n{citation}"
    if source.get("data_kind") == "demo":
        answer += "\n\nNguồn thuộc shop mô phỏng, chưa phải chính sách hoặc số liệu shop thật."
    claim = dict(text=text, evidence=[dict(chunk_id=source["chunk_id"],
                                           quotes=fragment["quotes"], source=source["source"])])
    return {"answer": answer, "period": period, "source": source,
            "claim": claim, "answerability": "full"}
