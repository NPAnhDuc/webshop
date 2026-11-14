from datetime import date
from pathlib import Path

import pytest

from shopbot.grounded_rag import asks_calculation

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


@pytest.mark.parametrize("question", [
    "Giao về tỉnh mất mấy ngày làm việc?",
    "Giao tới tỉnh thành khác có mất bao lâu?",
    "Shop giao hàng ngoài tỉnh trong mấy ngày?",
    "Tình trạng bảo hành máy mình thế nào?",
    "Tình trạng đơn hàng của mình ra sao?",
    "Báo cáo tình hình tháng 5 ghi doanh thu thế nào?",
    "Tính năng máy này có gì?",
    "Đơn ở tỉnh được giao mấy ngày?",
    "tinh trang don hang cua minh the nao?",
    "tinh thanh khac giao hang may ngay?",
    "Giao ve tinh mat may ngay lam viec?",
    "Don hang gui ngoai tinh mat may ngay?",
    "Giao noi tinh can bao lau?",
    "Giao lien tinh phai doi may ngay?",
    "Giao den tinh xa mat bao lau?",
    "Giao tinh/thanh khac mat may ngay?",
    "Ship tính sao?",
    "Tính thế nào để được miễn phí giao hàng?",
])
def test_accented_homophones_and_status_or_place_phrases_are_not_calculations(question):
    assert asks_calculation(question) is False


@pytest.mark.parametrize("question", [
    "Tính phí ship cho 2 đơn.",
    "Tổng tiền đơn này là bao nhiêu?",
    "Mỗi tháng trả góp bao nhiêu?",
    "tinh giup minh phi ship 3 don",
    "tong phi ship cho 2 don",
    "Tính tổng doanh thu tháng 5 và tháng 6.",
    "Mỗi kỳ phải trả bao nhiêu tiền?",
    "Tính doanh thu thuần sau hoàn trả.",
])
def test_calculation_phrases_remain_calculations(question):
    assert asks_calculation(question) is True


def _run_with_router(monkeypatch, question, action, role="customer", profile=None):
    from shopbot import grounded_rag

    route = {
        "action": action,
        "query": question,
        "doc_types": [],
        "category": "all",
        "private_request": False,
        "task": "lookup",
        "strict_filters": False,
    }

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}):
            return route
        pytest.fail("Unexpected selector/model call in route override test")

    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr(grounded_rag, "search", lambda *args, **kwargs: [])
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    return grounded_rag.answer(question, role, profile or {}, DB, TODAY)


def test_outside_router_is_overridden_for_shipping_to_a_province(monkeypatch):
    result = _run_with_router(
        monkeypatch, "Giao về tỉnh mất mấy ngày làm việc?", "outside",
    )
    assert "router overridden: shop policy is read from documents" in result["trace"]
    assert result["basic_action"] != "outside"


def test_shipping_fee_calculation_is_not_overridden(monkeypatch):
    result = _run_with_router(
        monkeypatch, "Tính phí ship cho 3 đơn ở tỉnh giúp mình.", "outside",
    )
    assert "router overridden: shop policy is read from documents" not in result["trace"]
    assert result["basic_action"] == "outside"


def test_monthly_report_situation_does_not_block_admin_read_override(monkeypatch):
    result = _run_with_router(
        monkeypatch,
        "Báo cáo tình hình tháng 5/2026 ghi doanh thu thuần bao nhiêu?",
        "deferred",
        role="admin",
        profile={"rag_metric_source": "document"},
    )
    assert "router deferred overridden: reading confirmed monthly reports, no calculation asked" in result["trace"]
    assert result["basic_action"] != "deferred"


@pytest.mark.parametrize("question", [
    "Báo cáo tháng 5 và tháng 6/2026 chênh lệch bao nhiêu theo số đã ghi?",
    "Bao cao thang 5 cong thang 6/2026 ghi duoc bao nhieu",
    "Báo cáo tháng 5/2026 tính tổng doanh thu đã ghi là bao nhiêu?",
])
def test_report_ghi_does_not_hide_calculation_words_before_it(monkeypatch, question):
    # Only the reading verb "ghi" is dropped; calculation words before it still defer.
    result = _run_with_router(monkeypatch, question, "deferred", role="admin",
                              profile={"rag_metric_source": "document"})
    assert "router deferred overridden: reading confirmed monthly reports, no calculation asked" not in result["trace"]
