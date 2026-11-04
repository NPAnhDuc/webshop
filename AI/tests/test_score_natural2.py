import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from score_natural2_20261031 import expected_value_found, score_case


def make_case(value):
    return {"expected_sql": "SELECT 1", "expected_values": [{"value": value}]}


def test_correct_numeric_answers_pass():
    assert score_case(make_case(1234000), {"basic_action": "answer", "answer": "Doanh thu đạt 1.234.000 đồng."}) == "PASS_CALC"
    assert score_case(make_case(15.06), {"basic_action": "answer", "answer": "Biên lãi gộp là 15,06%."}) == "PASS_CALC"


def test_wrong_value_and_non_answer_action_fail():
    assert score_case(make_case(1234000), {"basic_action": "answer", "answer": "Doanh thu đạt 1.234.100 đồng."}) == "FAIL_CALC_VALUE"
    assert score_case(make_case(1234000), {"basic_action": "clarify", "answer": "Doanh thu đạt 1.234.000 đồng."}) == "FAIL_CALC_ACTION"


def test_supported_thousands_and_decimal_formats():
    for text in ("1.234.000", "1,234,000", "1 234 000"):
        assert expected_value_found(1234000, text), text
    for text in ("15,06", "15.06"):
        assert expected_value_found(15.06, text), text


def test_negative_value_accepts_minus_or_clear_lower_wording():
    assert expected_value_found(-237412000, "-237.412.000")
    assert expected_value_found(-237412000, "Doanh thu thấp hơn 237,412,000 đồng.")
    assert expected_value_found(-237412000, "Doanh thu giảm 237.412.000 đồng.")
    assert not expected_value_found(-237412000, "Doanh thu là 237.412.000 đồng.")


def test_a_drop_stated_with_a_minus_sign_answers_a_question_asking_for_the_drop():
    assert expected_value_found(19.63, "thay đổi so với tháng 8/2026: -19,63% (giảm)", "Số đơn tháng 9 giảm bao nhiêu %?")
    assert expected_value_found(19.63, "thay đổi: -19,63%", "so don thang 9 giam bao nhieu %")


def test_a_minus_sign_is_wrong_when_a_rise_was_asked():
    assert not expected_value_found(19.63, "thay đổi: -19,63%", "Số đơn tháng 9 tăng bao nhiêu %?")
    assert not expected_value_found(19.63, "thay đổi: -19,63%")


def test_the_question_reaches_the_value_check():
    case = dict(make_case(19.63), question="Số đơn giảm bao nhiêu %?")
    assert score_case(case, {"basic_action": "answer", "answer": "thay đổi: -19,63% (giảm)"}) == "PASS_CALC"
