from datetime import date
from pathlib import Path

import pytest

from shopbot.product_lookup import product_names
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)
TRACE = "admin business terms: technical route widened to policy documents"


def run_with_route(monkeypatch, question, *, role="admin", types=("glossary",), profile=None):
    from shopbot import grounded_rag

    route = {
        "action": "answer",
        "query": question,
        "doc_types": list(types),
        "category": "all",
        "private_request": False,
        "task": "lookup",
        "strict_filters": False,
    }
    calls = []

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}):
            return route
        pytest.fail("Unexpected selector/model call in source-type test")

    def search(*args, **kwargs):
        calls.append(kwargs.get("doc_types"))
        return []

    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr(grounded_rag, "search", search)
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    result = grounded_rag.answer(
        question, role, profile or {"rag_metric_source": "document"}, DB, TODAY,
    )
    return result, calls


@pytest.mark.parametrize("question", [
    "Biên gộp tối thiểu laptop hiện giờ là mấy phần trăm?",
    "Biên lợi nhuận theo quy định là bao nhiêu?",
    "Biên tối thiểu shop yêu cầu là bao nhiêu?",
    "Giá vốn nhập hàng tối đa được duyệt thế nào?",
    "Giá bán tối thiểu áp dụng ra sao?",
    "Mức giảm cho khách tối đa là bao nhiêu?",
    "Chính sách giảm giá tối đa hiện tại thế nào?",
    "Đơn hàng được cộng dồn khuyến mại không?",
    "Hàng tồn quá lâu thì quy định xử lý thế nào?",
    "Tồn kho tối thiểu được quy định bao nhiêu?",
    "Hàng tồn trên 90 ngày có cần xin duyệt không?",
    "Quy trình xả hàng cần ai phê duyệt?",
    "Quy định xả kho theo chính sách nào?",
    "Nhập hàng cần duyệt giá ra sao?",
    "Nhà cung cấp cần đáp ứng điều kiện gì?",
    "Đặt hàng NCC có cần xin duyệt không?",
    "Duyệt giá nhà cung cấp thực hiện thế nào?",
    "Xin duyệt mức giá mới gửi cho ai?",
    "Phê duyệt giá nhập cần những bước nào?",
    "Chính sách giá của cửa hàng hiện thế nào?",
    "QUY DINH GIA ban toi thieu ra sao?",
])
def test_admin_business_terms_widen_technical_route(monkeypatch, question):
    result, calls = run_with_route(monkeypatch, question)

    assert calls[0] == ["glossary", "policy", "procedure"]
    assert TRACE in result["trace"]


def test_customer_business_question_does_not_widen(monkeypatch):
    result, calls = run_with_route(
        monkeypatch,
        "Biên gộp tối thiểu laptop hiện giờ là mấy phần trăm?",
        role="customer",
    )

    assert calls[0] == ["glossary"]
    assert TRACE not in result["trace"]


def test_admin_technical_question_does_not_widen(monkeypatch):
    result, calls = run_with_route(monkeypatch, "SSD NVMe khác SATA thế nào?")

    assert calls[0] == ["glossary"]
    assert TRACE not in result["trace"]


def test_named_catalog_product_does_not_widen(monkeypatch):
    name = product_names(DB)[0]
    result, calls = run_with_route(monkeypatch, f"{name} có giá vốn là bao nhiêu?")

    assert calls[0] == ["glossary"]
    assert TRACE not in result["trace"]


def test_existing_business_route_does_not_widen(monkeypatch):
    result, calls = run_with_route(
        monkeypatch, "Biên gộp tối thiểu là bao nhiêu?", types=("policy",),
    )

    assert calls[0] == ["policy"]
    assert TRACE not in result["trace"]


def test_empty_router_types_keep_existing_all_types_search(monkeypatch):
    result, calls = run_with_route(
        monkeypatch, "Biên gộp tối thiểu là bao nhiêu?", types=(),
    )

    # Existing code represents an empty preferred list as doc_types=None (all types).
    assert calls[0] is None
    assert TRACE not in result["trace"]


def test_monthly_report_request_type_does_not_widen(monkeypatch):
    result, calls = run_with_route(
        monkeypatch,
        "Báo cáo tháng 5/2026 ghi quy định giá hiện tại thế nào?",
        profile={"rag_metric_source": "document"},
    )

    assert calls[0] == ["monthly_report"]
    assert TRACE not in result["trace"]


def test_unaccented_business_term_is_recognized(monkeypatch):
    result, calls = run_with_route(
        monkeypatch, "QUY DINH GIA ban toi thieu ra sao?",
    )

    assert calls[0] == ["glossary", "policy", "procedure"]
    assert TRACE in result["trace"]
