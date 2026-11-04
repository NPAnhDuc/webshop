import json
import re
import sqlite3
import sys
from datetime import date
from pathlib import Path

import pytest

AI_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_ROOT / "scripts"))
from shopbot import shop_calc
from shopbot.rag_metrics import answer_metrics, metric_request
from shopbot.rag_scope import resolve_scope
from shopbot.retrieval import normalize
from score_natural2_20261031 import score_case

DB = AI_ROOT / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


def request(question, role="admin", today=TODAY):
    return shop_calc.calc_request(question, role, resolve_scope(question, today))


def sql_value(query, *args):
    uri = DB.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as con:
        return con.execute(query, args).fetchone()[0]


def test_difference_and_percentage_change_keep_period_order_and_inputs():
    diff = request("Chênh lệch giá vốn giữa tháng 4/2026 và tháng 5/2026")
    assert diff["operation"] == "difference"
    assert diff["periods"] == ["2026-04", "2026-05"]
    result = shop_calc.answer_calc(DB, diff)
    values = [row["value"] for row in result["rows"]]
    assert values == [
        sql_value("SELECT SUM(cost) FROM financial_ledger WHERE day>='2026-04-01' AND day<'2026-05-01'"),
        sql_value("SELECT SUM(cost) FROM financial_ledger WHERE day>='2026-05-01' AND day<'2026-06-01'"),
        -151983000,
    ]
    assert "tháng 4/2026" in result["text"] and "tháng 5/2026" in result["text"]
    assert "850.948.000 đ" in result["text"] and "1.002.931.000 đ" in result["text"]

    pct = request("Lợi nhuận gộp tháng 8/2026 tăng mấy phần trăm so với tháng 7/2026?")
    assert pct["periods"] == ["2026-08", "2026-07"]
    pct_result = shop_calc.answer_calc(DB, pct)
    numerator, denominator = pct_result["rows"][:2]
    assert numerator["value"] == 187149000 and denominator["value"] == 135904000
    assert pct_result["rows"][-1]["value"] == 37.71
    assert "37,71%" in pct_result["text"] and "tăng" in pct_result["text"]


def test_values_match_existing_answer_metrics_for_each_explicit_period():
    question = "Chênh lệch giá vốn giữa tháng 4/2026 và tháng 5/2026"
    calc = shop_calc.answer_calc(DB, request(question))
    for period_row in calc["rows"][:2]:
        month = period_row["period"]
        metric_question = f"Giá vốn tháng {int(month[-2:])}/{month[:4]} là bao nhiêu?"
        asked, found = metric_request(metric_question, "admin", resolve_scope(metric_question, TODAY))
        assert asked and found
        text, _, coverage = answer_metrics(DB, asked, found, TODAY)
        expected = f"{period_row['value']:,}".replace(",", ".")
        assert expected in text
        assert coverage[0]["missing"] == []

    question = "Lợi nhuận gộp tháng 8/2026 tăng mấy phần trăm so với tháng 7/2026?"
    calc = shop_calc.answer_calc(DB, request(question))
    for period_row in calc["rows"][:2]:
        month = period_row["period"]
        metric_question = f"Lãi gộp tháng {int(month[-2:])}/{month[:4]} là bao nhiêu?"
        asked, found = metric_request(metric_question, "admin", resolve_scope(metric_question, TODAY))
        text, _, coverage = answer_metrics(DB, asked, found, TODAY)
        assert f"{period_row['value']:,}".replace(",", ".") in text
        assert coverage[0]["missing"] == []


def test_ratios_rankings_and_channel_category_filter():
    margin = shop_calc.answer_calc(DB, request("Biên lợi nhuận gộp tháng 6/2026 là bao nhiêu?"))
    assert margin["rows"][0]["value"] == 14.38
    assert "120.582.000 đ / 838.580.000 đ" in margin["text"]

    per_order = shop_calc.answer_calc(DB, request("Lãi gộp bình quân mỗi đơn quý 2/2026 là bao nhiêu?"))
    assert per_order["rows"][0]["unit"] == "đ/đơn"
    assert per_order["rows"][0]["value"] == round(440123000 / 325, 2)
    assert "đ/đơn" in per_order["text"] and "%" not in per_order["text"]

    return_rate = shop_calc.answer_calc(DB, request("Tỷ lệ lượt hoàn trên số đơn tháng 8/2026 là bao nhiêu?"))
    assert return_rate["rows"][0]["value"] == round(4 / 163 * 100, 2)

    highest = shop_calc.answer_calc(DB, request("Tháng nào năm 2026 có chi phí vận hành cao nhất?"))
    assert highest["rows"][0]["label"] == "2026-08"
    assert highest["rows"][0]["value"] == 141500520
    assert "Chi phí vận hành" in highest["text"]

    top_orders = shop_calc.answer_calc(DB, request("Top 3 tháng nhiều đơn nhất năm 2026?"))
    assert [row["label"] for row in top_orders["rows"]] == ["2026-08", "2026-03", "2026-09"]

    channel = shop_calc.answer_calc(DB, request("Kênh nào doanh thu cao nhất quý 2/2026?"))
    assert channel["rows"][0]["label"] == "store"
    category = shop_calc.answer_calc(DB, request("Danh mục nào doanh thu cao nhất quý 2/2026?"))
    assert category["rows"][0]["label"] == "laptop"

    filtered = shop_calc.answer_calc(DB, request("Doanh thu laptop qua website quý 3/2026 là bao nhiêu?"))
    expected = sql_value("""SELECT SUM(l.revenue) FROM financial_ledger l
        LEFT JOIN returns r ON l.kind='return' AND r.id=l.id
        JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END
        JOIN orders o ON o.id=i.order_id JOIN products p ON p.sku=l.sku
        WHERE l.day>='2026-07-01' AND l.day<'2026-10-01' AND p.category=? AND o.channel=?""", "laptop", "website")
    assert filtered["rows"][0]["value"] == expected
    assert filtered["sources"] and "sổ cái" in filtered["text"]


@pytest.mark.parametrize("question", [
    "Mục tiêu doanh thu quý 3/2026 là bao nhiêu?",
    "Vì sao doanh thu tháng 9/2026 giảm?",
    "Vẽ biểu đồ chi phí vận hành các tháng năm 2026.",
    "Ghi doanh thu laptop quý 3/2026 vào database.",
    "Đọc báo cáo tháng 9/2026 rồi cho biết lãi gộp.",
    "Tỷ lệ hoàn tháng 8/2026 là bao nhiêu?",
    "Doanh thu laptop qua kênh Facebook quý 3/2026?",
    "Doanh thu laptop' OR '1'='1 qua website quý 3/2026?",
    "Lãi gộp tháng 8/2026 và doanh thu tháng đó chênh lệch bao nhiêu?",
])
def test_uncertain_or_non_calculation_requests_stay_on_existing_path(question):
    assert request(question) is None


@pytest.mark.parametrize("question", [
    "Chênh lệch doanh thu tai nghe giữa tháng 7/2026 và tháng 8/2026 là bao nhiêu?",
    "Doanh thu laptop Dell quý 3/2026 là bao nhiêu?",
    "Doanh thu không tính laptop quý 3/2026 là bao nhiêu?",
    "Doanh thu trước hoàn tháng 8/2026 chênh lệch bao nhiêu so với tháng 7/2026?",
    "Doanh thu mỗi ngày tháng 8/2026 chênh lệch bao nhiêu so với tháng 7/2026?",
    "Laptop chiếm bao nhiêu phần trăm doanh thu quý 3/2026?",
    "Sản phẩm nào doanh thu cao nhất năm 2026?",
    "Quý nào doanh thu cao nhất năm 2026?",
    "Kênh nào doanh thu laptop cao nhất quý 2/2026?",
    "Top 7 tháng nhiều đơn nhất năm 2026?",
    "Tháng nào doanh thu cao nhất và thấp nhất năm 2026?",
    "Từ tháng 4 đến tháng 6 năm 2026, tháng nào doanh thu cao nhất?",
    "Chênh lệch doanh thu tháng 3 năm ngoái và tháng 4 năm ngoái?",
    "Chênh lệch doanh thu quý 1/2026 và tháng 8/2026?",
    "Doanh thu của cửa hàng tháng 8/2026 là bao nhiêu?",
    "Doanh thu laptop ở website và cửa hàng quý 3/2026 là bao nhiêu?",
    "Doanh thu giữa tháng 8/2026 so với giữa tháng 7/2026 chênh lệch bao nhiêu?",
    "Tỷ lệ đơn hoàn trên số đơn tháng 8/2026 là bao nhiêu?",
    "Tỷ lệ tiền hoàn trên số đơn tháng 8/2026?",
])
def test_a_word_the_parser_does_not_understand_is_never_ignored(question):
    assert request(question) is None


@pytest.mark.parametrize("question", [
    "Từ tháng 7/2026 đến tháng 8/2026 doanh thu tăng mấy phần trăm?",
    "So với tháng 7/2026, doanh thu tháng 8/2026 tăng bao nhiêu phần trăm?",
])
def test_percentage_change_starts_from_the_base_period(question):
    answer = shop_calc.answer_calc(DB, request(question))
    assert answer["rows"][-1]["value"] == 39.35
    assert "so với tháng 7/2026" in answer["text"] and "tăng" in answer["text"]


def test_change_between_periods_can_be_filtered_by_category_or_channel():
    answer = shop_calc.answer_calc(DB, request("Doanh thu laptop tháng 8/2026 tăng bao nhiêu so với tháng 7/2026?"))
    laptop = """SELECT SUM(l.revenue) FROM financial_ledger l JOIN products p ON p.sku=l.sku
        WHERE l.day>=? AND l.day<? AND p.category='laptop'"""
    august = sql_value(laptop, "2026-08-01", "2026-09-01")
    july = sql_value(laptop, "2026-07-01", "2026-08-01")
    assert [row["value"] for row in answer["rows"]] == [august, july, august - july]
    assert "laptop" in answer["text"]
    assert request("Giá vốn laptop tháng 8/2026 tăng bao nhiêu so với tháng 7/2026?") is None


def test_answers_name_filters_in_vietnamese_and_say_a_year_is_partial():
    assert "card màn hình" in shop_calc.answer_calc(DB, request("Doanh thu card màn hình quý 3/2026 là bao nhiêu?"))["text"]
    assert "cửa hàng:" in shop_calc.answer_calc(DB, request("Top 3 kênh doanh thu quý 2/2026?"))["text"]
    top = shop_calc.answer_calc(DB, request("Top 3 tháng doanh thu laptop cao nhất năm 2026?"))["text"]
    assert "laptop" in top and "từ tháng 1/2026 đến tháng 9/2026" in top


def test_role_bounds_periods_identical_periods_and_missing_comparison_period():
    assert request("Doanh thu tháng 9/2026 là bao nhiêu?", role="customer") is None
    assert request("Chênh lệch giá vốn tháng 9/2025 và tháng 10/2025?", today=date(2026, 10, 31)) is None
    assert request("Chi phí vận hành tháng 10/2026 là bao nhiêu?", today=date(2026, 10, 31)) is None
    assert request("Chênh lệch giá vốn tháng 4/2026 là bao nhiêu?") is None

    same = request("Chênh lệch giá vốn tháng 4/2026 và tháng 4/2026 là bao nhiêu?")
    assert same and same["periods"] == ["2026-04", "2026-04"]
    same_answer = shop_calc.answer_calc(DB, same)
    assert "Hai kỳ được hỏi giống nhau" in same_answer["text"]
    assert not same_answer["rows"]


def test_zero_denominator_and_rank_tie_are_reported_without_silent_selection(monkeypatch):
    monkeypatch.setattr(shop_calc, "_analyze", lambda *_: {"totals": {"gross_profit": 0, "revenue": 0}, "monthly": [{"month": "2026-01"}], "quality": {"source_rows": 1}})
    zero = shop_calc.answer_calc(DB, {"operation": "ratio", "ratio": "gross_margin", "periods": ["2026-01"]})
    assert "Mẫu số" in zero["text"] and not zero["rows"]

    tied_report = {
        "totals": {}, "monthly": [{"month": "2026-01"}], "quality": {"source_rows": 1},
        "products": [
            {"category": "laptop", "revenue": 200, "gross_profit": 20},
            {"category": "cpu", "revenue": 200, "gross_profit": 15},
            {"category": "mouse", "revenue": 100, "gross_profit": 10},
        ],
    }
    monkeypatch.setattr(shop_calc, "_analyze", lambda *_: tied_report)
    tied = shop_calc.answer_calc(DB, {"operation": "rank", "metric": "revenue", "entity": "category", "periods": ["2026-01"], "direction": "desc", "limit": 1})
    assert [row["label"] for row in tied["rows"]] == ["cpu", "laptop"]
    assert "đồng hạng" in tied["text"]


def test_dev_agent_steps_are_none_or_match_their_sql_gold():
    rows = json.loads((AI_ROOT / "evaluation/agent_steps_20261031/bank.json").read_text(encoding="utf-8"))
    with sqlite3.connect(DB.resolve().as_uri() + "?mode=ro", uri=True) as con:
        for item in rows:
            if item["split"] != "dev":
                continue
            calc = request(item["question"])
            if calc is None:
                continue
            actual = shop_calc.answer_calc(DB, calc)
            gold = con.execute(item["expected_sql"]).fetchall()
            if item["kind"] == "months":
                assert [row["label"] for row in actual["rows"]] == [row[0] for row in gold], item["id"]
            else:
                value = actual["rows"][-1]["value"]
                expected = gold[0][0]
                if item["kind"] == "pct":
                    assert round(value, 2) == round(expected, 2), item["id"]
                else:
                    assert value == expected, item["id"]


def test_dev_export_does_not_route_customers_reports_or_targets_to_calculator():
    cases = json.loads((AI_ROOT / "evaluation/dev_export_20261031/cases.json").read_text(encoding="utf-8"))
    accepted = []
    for case in cases:
        calc = request(case["question"], case["role"])
        if calc is None:
            continue
        accepted.append(case)
        q = normalize(case["question"])
        assert case["role"] == "admin"
        assert not re.search(r"\b(?:bao cao|report|muc tieu|ke hoach|du bao|nguyen nhan|vi sao|bieu do)\b", q)
    assert len(accepted) == 5
    assert all(case["topic"] == "admin_tool_request" for case in accepted)


def test_unaccented_aliases_and_short_periods_are_understood():
    assert normalize("DT, LG, Q1, T8") == "dt, lg, q1, t8"
    assert request("DT laptop qua website q3/2026?") is not None
    assert request("LG t8/2026 tăng mấy phần trăm so với t7/2026?") is not None

def test_natural2_comparison_cases_match_sql_and_calculation_scorer():
    bank = json.loads((AI_ROOT / "evaluation/natural2_20261031/bank.json").read_text(encoding="utf-8"))
    ids = {"N2-098", "N2-100", "N2-101", "N2-102", "N2-106", "N2-107", "N2-108", "N2-109"}
    cases = [case for case in bank if case.get("id") in ids]
    assert {case["id"] for case in cases} == ids
    uri = DB.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as con:
        for case in cases:
            expected = con.execute(case["expected_sql"]).fetchone()[0]
            assert expected == case["expected_values"][0]["value"], case["id"]
            calc = request(case["question"])
            assert calc is not None, case["id"]
            answer = shop_calc.answer_calc(DB, calc)
            assert answer["rows"][-1]["value"] == expected, case["id"]
            assert score_case(case, {"basic_action": "answer", "answer": answer["text"]}) == "PASS_CALC", case["id"]


@pytest.mark.parametrize("question", [
    "Lai gop thang 8 hon bao nhieu tien?",
    "Bien loi nhuan gop quy doi ra phan tram la may?",
    "Binh quan moi don trong thang 9 mang lai bao nhieu?",
    "Thuc hien cao hon ke hoach bao nhieu doanh thu?",
    "Trong thang 9 ty le san pham hoan la bao nhieu phan tram?",
    "Gop chi phi van hanh cho toi con so tong nhe.",
    "Quy 3 tien hoan chiem bao nhieu phan tram?",
])
def test_calculations_stay_unhandled_when_period_metric_or_denominator_is_missing(question):
    assert request(question) is None


def test_calculation_capability_is_admin_only_for_new_comparisons():
    question = "Doanh thu thuan tu thang 8 sang thang 9/2026 tang hay giam bao nhieu dong?"
    assert request(question, role="customer") is None



@pytest.mark.parametrize("source_clause", [
    "tính theo sổ cái",
    "tính theo ledger, đã trừ hoàn hàng",
])
def test_net_revenue_comparison_accepts_general_source_and_return_qualifiers(source_clause):
    question = (
        "Doanh thu thuần từ tháng 8 sang tháng 9/2026 tăng hay giảm bao nhiêu đồng, "
        + source_clause
        + "?"
    )
    calc = request(question)
    assert calc is not None
    answer = shop_calc.answer_calc(DB, calc)
    assert answer["rows"][-1]["value"] == -237412000
    assert answer["text"].startswith("Doanh thu thuần ")


def test_return_adjustment_qualifier_does_not_hide_for_other_metrics():
    assert request(
        "Chênh lệch lãi gộp từ tháng 8 sang tháng 9/2026 bao nhiêu, "
        "tính theo ledger, đã trừ hoàn hàng?"
    ) is None


@pytest.mark.parametrize("rounding", ["làm tròn 2", "làm tròn 2 chữ số", "làm tròn hai", "làm tròn hai chữ số"])
def test_rounding_accepts_digit_and_word_forms(rounding):
    question = f"Tiền hoàn chiếm bao nhiêu phần trăm doanh thu thuần quý 3/2026, {rounding}?"
    calc = request(question)
    assert calc is not None
    answer = shop_calc.answer_calc(DB, calc)
    assert answer["rows"][-1]["value"] == 2.71
    assert answer["text"].startswith("Tỷ lệ tiền hoàn / doanh thu thuần")


@pytest.mark.parametrize(("question", "prefix"), [
    ("Biên lợi nhuận gộp tháng 6/2026 là bao nhiêu?", "Tỷ lệ lãi gộp / doanh thu thuần"),
    ("Doanh thu thuần bình quân mỗi đơn tháng 8/2026 là bao nhiêu?", "Doanh thu thuần bình quân mỗi đơn"),
    ("Lãi gộp bình quân mỗi đơn tháng 8/2026 là bao nhiêu?", "Lãi gộp bình quân mỗi đơn"),
    ("Tỷ lệ lượt hoàn trên số đơn tháng 8/2026 là bao nhiêu?", "Tỷ lệ sản phẩm hoàn trả / số đơn"),
    ("Tỷ lệ sản phẩm hoàn trên tổng lượng đã bán tháng 8/2026 là bao nhiêu?", "Tỷ lệ sản phẩm hoàn trả / tổng sản phẩm đã bán"),
    ("Tổng chi phí vận hành tháng 7/2026 và tháng 8/2026?", "Tổng chi phí vận hành"),
])
def test_calculation_answer_opening_is_capitalized_and_accented(question, prefix):
    calc = request(question)
    assert calc is not None
    answer = shop_calc.answer_calc(DB, calc)
    assert answer["text"].startswith(prefix)
    assert answer["text"][0].isupper()


def test_zero_order_denominator_uses_accented_revenue_formula(monkeypatch):
    monkeypatch.setattr(shop_calc, "_analyze", lambda *_: {
        "totals": {"gross_profit": 0, "revenue": 100},
        "financial": {"orders": 0},
        "monthly": [{"month": "2026-01"}],
        "quality": {"source_rows": 1},
    })
    result = shop_calc.answer_calc(DB, {"operation": "ratio", "ratio": "revenue_per_order", "periods": ["2026-01"]})
    assert result["text"].startswith("Mẫu số của doanh thu thuần / số đơn")
    assert "doanh thu thuan / so don" not in result["text"]
    assert not result["rows"]


@pytest.mark.parametrize(("question", "periods", "metric", "source", "prefix"), [
    ("Doanh thu thuần tháng 9 so với tháng 8 chênh bao nhiêu?", ["2026-09", "2026-08"], "revenue", ("financial_ledger", "revenue"), "Doanh thu thuần "),
    ("Lãi gộp tháng 8 và tháng 9 chênh nhau bao nhiêu?", ["2026-08", "2026-09"], "gross_profit", ("financial_ledger", "revenue - cost"), "Lãi gộp "),
    ("Chi phí vận hành tháng 7 với tháng 8 lệch bao nhiêu?", ["2026-07", "2026-08"], "expenses", ("operating_expenses", "amount"), "Chi phí vận hành "),
])
def test_short_comparison_words_calculate_sql_backed_difference(question, periods, metric, source, prefix):
    calc = request(question)
    assert calc is not None
    assert calc["operation"] == "difference"
    assert calc["metric"] == metric
    assert calc["periods"] == periods
    answer = shop_calc.answer_calc(DB, calc)
    table, expression = source

    def month_total(period):
        year, month = map(int, period.split("-"))
        start = f"{year:04d}-{month:02d}-01"
        next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
        end = f"{next_year:04d}-{next_month:02d}-01"
        sql = f"SELECT COALESCE(SUM({expression}), 0) FROM {table} WHERE day >= ? AND day < ?"
        return sql_value(sql, start, end) or 0

    assert answer["rows"][-1]["value"] == month_total(periods[0]) - month_total(periods[1])
    assert answer["text"].startswith(prefix)
    assert answer["text"][0].isupper()


def test_short_comparison_words_keep_period_filter_and_role_guards():
    assert request("Doanh thu tháng 9 chênh bao nhiêu?") is None
    # A category filter works the same with the short word as with "chênh lệch".
    short = request("Doanh thu laptop tháng 8 và tháng 9 chênh bao nhiêu?")
    assert short is not None and short == request("Doanh thu laptop tháng 8 và tháng 9 chênh lệch bao nhiêu?")
    assert request("Tổng chi phí vận hành laptop tháng 8 và tháng 9 chênh bao nhiêu?") is None
    assert request("Doanh thu thuần tháng 9 so với tháng 8 chênh bao nhiêu?", role="customer") is None
