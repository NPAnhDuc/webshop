import sqlite3
import sys
from datetime import date
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_ROOT / "scripts"))

from shopbot import grounded_rag, shop_calc
from shopbot.rag_scope import resolve_scope

DB = AI_ROOT / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


def sql_revenue(period):
    if "-Q" in period:
        year, quarter = map(int, period.replace("-Q", "-").split("-"))
        start_month = 3 * (quarter - 1) + 1
        end_month = start_month + 3
        start = date(year, start_month, 1)
        end = date(year + (end_month > 12), (end_month - 1) % 12 + 1, 1)
    else:
        year, month = map(int, period.split("-"))
        start = date(year, month, 1)
        end = date(year + (month == 12), month % 12 + 1, 1)
    uri = DB.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as con:
        return con.execute(
            "SELECT SUM(revenue) FROM financial_ledger WHERE day>=? AND day<?",
            (start.isoformat(), end.isoformat()),
        ).fetchone()[0]


def answer(question, role="admin"):
    return grounded_rag.answer(question, role, {}, DB, TODAY)


def test_relative_month_and_quarter_comparisons_use_sql_and_report_both_periods():
    cases = [
        ("Doanh thu tháng 8/2026 tăng hay giảm so với tháng liền trước?", ["2026-08", "2026-07"]),
        ("Tháng 9 năm 2026 doanh thu biến động ra sao so với tháng trước đó?", ["2026-09", "2026-08"]),
        ("Doanh thu tháng 9/2026 thay đổi thế nào so với kỳ liền trước?", ["2026-09", "2026-08"]),
        ("Doanh thu thang 9/2026 tang hay giam so voi thang lien truoc?", ["2026-09", "2026-08"]),
        ("Quý 3/2026 doanh thu thay đổi ra sao so với quý trước?", ["2026-Q3", "2026-Q2"]),
        ("Quý vừa rồi doanh thu tăng hay giảm so với quý trước?", ["2026-Q3", "2026-Q2"]),
    ]
    for question, periods in cases:
        result = answer(question)
        assert any(item.startswith("calculation: deterministic SQL via shop_calc") for item in result["trace"]), question
        rows = result["rag"]["calculation"]
        expected = [sql_revenue(period) for period in periods]
        assert [row["period"] for row in rows[:2]] == periods, question
        assert [row["value"] for row in rows] == [*expected, expected[0] - expected[1]], question
        assert all(shop_calc._label(period) in result["answer"] for period in periods), question
        direction = "tăng" if expected[0] > expected[1] else "giảm" if expected[0] < expected[1] else "không đổi"
        assert direction in result["answer"], question


def test_relative_percentage_phrase_keeps_percentage_operation():
    question = "Doanh thu tháng 8/2026 thay đổi bao nhiêu phần trăm so với tháng trước?"
    result = answer(question)
    rows = result["rag"]["calculation"]
    values = [sql_revenue("2026-08"), sql_revenue("2026-07")]
    assert rows[-1]["unit"] == "%"
    assert rows[-1]["value"] == round((values[0] - values[1]) / values[1] * 100, 2)
    assert "tăng" in result["answer"]


def test_missing_or_incomplete_relative_period_is_named_without_a_delta():
    cases = [
        ("Doanh thu tháng này thay đổi thế nào so với tháng trước?", "tháng 10/2026"),
        ("Doanh thu tháng 11/2026 tăng hay giảm so với tháng liền trước?", "tháng 11/2026"),
    ]
    for question, missing_label in cases:
        result = answer(question)
        assert any(item.startswith("calculation: deterministic SQL via shop_calc") for item in result["trace"])
        assert missing_label in result["answer"]
        assert "chưa tính chênh lệch" in result["answer"]
        assert result["rag"]["calculation"] == []


def test_explicit_periods_read_only_reports_and_customer_role_keep_existing_bounds():
    explicit = answer("Doanh thu tháng 6/2026 tăng bao nhiêu so với tháng 5/2026?")
    assert any(item.startswith("calculation: deterministic SQL via shop_calc") for item in explicit["trace"])
    assert [row["period"] for row in explicit["rag"]["calculation"][:2]] == ["2026-06", "2026-05"]

    read_only = "Chỉ đọc báo cáo doanh thu tháng 8/2026 và tháng 9/2026, không tính chênh lệch."
    assert shop_calc.calc_request(read_only, "admin", resolve_scope(read_only, TODAY)) is None

    customer = "Doanh thu tháng 8/2026 thay đổi thế nào so với tháng trước?"
    assert shop_calc.calc_request(customer, "customer", resolve_scope(customer, TODAY)) is None
