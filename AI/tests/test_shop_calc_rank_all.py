from datetime import date
from pathlib import Path

import pytest

from shopbot import shop_calc
from shopbot.rag_scope import resolve_scope

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


def rank(question):
    request = shop_calc.calc_request(question, "admin", resolve_scope(question, TODAY))
    assert request is not None
    return request, shop_calc.answer_calc(DB, request)


def expected_rows(request):
    values = []
    for period in request["periods"]:
        report = shop_calc._analyze(DB, period)
        value, _ = shop_calc._value(report, request["metric"])
        values.append((period, value))
    reverse = request["direction"] == "desc"
    return sorted(values, key=lambda pair: ((-pair[1]) if reverse else pair[1], pair[0]))


def assert_month_rows_match_analysis(request, result, limit):
    expected = expected_rows(request)[:limit]
    actual = [(row["label"], row["value"]) for row in result["rows"]]

    assert actual == expected
    assert len(result["rows"]) == limit
    positions = [result["text"].index(shop_calc._label(period)) for period, _ in expected]
    assert positions == sorted(positions)
    for period, value in expected:
        assert shop_calc._format(value, shop_calc.FIELD_BY_METRIC[request["metric"]][3]) in result["text"]


@pytest.mark.parametrize("question", [
    "Xếp hạng doanh thu thuần các tháng năm 2026 giúp tôi.",
    "xep hang doanh thu thuan cac thang nam 2026",
    "Tháng nào năm 2026 có chi phí vận hành cao nhất? Xếp hạng giúp.",
    "Xếp hạng tháng có lãi gộp thấp nhất năm 2026.",
])
def test_unbounded_month_ranking_lists_every_month_in_analysis_order(question):
    request, result = rank(question)

    assert request["entity"] == "month"
    assert request["limit"] == len(request["periods"])
    assert_month_rows_match_analysis(request, result, len(request["periods"]))
    assert "; " in result["text"]


def test_single_highest_month_without_rank_word_stays_at_one():
    request, result = rank("Tháng nào năm 2026 có doanh thu thuần cao nhất?")

    assert request["limit"] == 1
    assert_month_rows_match_analysis(request, result, 1)


def test_explicit_top_three_and_quarter_top_two_keep_requested_counts():
    top_three, top_three_result = rank("Xếp hạng top 3 tháng doanh thu thuần năm 2026")
    top_two, top_two_result = rank(
        "Xếp hạng 2 tháng có chi phí vận hành cao nhất quý 3/2026",
    )

    assert top_three["limit"] == 3
    assert_month_rows_match_analysis(top_three, top_three_result, 3)
    assert top_two["limit"] == 2
    assert_month_rows_match_analysis(top_two, top_two_result, 2)
