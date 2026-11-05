import json
from pathlib import Path

from scripts.summarize_offtopic_20261103 import main, render, summarize


def make_case(case_id, *, split="development", topic="weather", behavior="outside", conversation=None, question=None):
    return {
        "id": case_id,
        "split": split,
        "topic": topic,
        "expected_behavior": behavior,
        "conversation": conversation or case_id,
        "question": question or f"question-{case_id}",
    }


def make_result(case, *, passed=True, action="outside", answer=None):
    return {
        "id": case["id"],
        "result": {"basic_action": action, "answer": answer or f"answer-{case['id']}"},
        "checks": {"status": "PASS_CHECKS" if passed else "FAIL_CHECKS", "issues": []},
    }


def write_fixture(tmp_path, cases, rows):
    bank_path = tmp_path / "bank.json"
    round_dir = tmp_path / "round"
    round_dir.mkdir()
    bank_path.write_text(json.dumps(cases), encoding="utf-8")
    (round_dir / "results.json").write_text(json.dumps(rows), encoding="utf-8")
    return round_dir, bank_path


def test_counts_by_topic_and_split_use_expected_behavior_from_bank(tmp_path):
    cases = [
        make_case("d1", topic="weather", behavior="outside"),
        make_case("d2", topic="weather", behavior="facts"),
        make_case("v1", split="validation", topic="poem", behavior="outside"),
    ]
    rows = [make_result(c, passed=c["id"] != "v1") for c in cases]
    round_dir, bank_path = write_fixture(tmp_path, cases, rows)
    report = summarize(round_dir, bank_path)
    assert { (x["topic"], x["split"]): (x["passed"], x["total"]) for x in report["topic_split"] } == {
        ("weather", "development"): (2, 2), ("poem", "validation"): (0, 1)
    }
    assert { (x["group"], x["split"]): (x["passed"], x["total"]) for x in report["group_totals"] } == {
        ("outside", "development"): (1, 1), ("control", "development"): (1, 1), ("outside", "validation"): (0, 1)
    }


def test_outside_failures_are_counted_by_actual_action_and_split(tmp_path):
    cases = [make_case("d1"), make_case("d2"), make_case("v1", split="validation", question="PRIVATE_VALIDATION_QUESTION")]
    rows = [make_result(c, passed=False, action=action, answer="PRIVATE_VALIDATION_ANSWER" if c["split"] == "validation" else "dev") for c, action in zip(cases, ("answer", "clarify", "handoff"))]
    round_dir, bank_path = write_fixture(tmp_path, cases, rows)
    report = summarize(round_dir, bank_path)
    assert report["outside_failures_by_action"] == [
        {"split": "development", "basic_action": "answer", "count": 1},
        {"split": "development", "basic_action": "clarify", "count": 1},
        {"split": "validation", "basic_action": "handoff", "count": 1},
    ]


def test_validation_details_never_appear_in_text_or_json(tmp_path):
    cases = [
        make_case("DEV_ID", question="development prompt"),
        make_case("SECRET_VALIDATION_ID", split="validation", topic="secret-topic", question="SECRET_VALIDATION_QUESTION"),
    ]
    rows = [make_result(cases[0], passed=False), make_result(cases[1])]
    round_dir, bank_path = write_fixture(tmp_path, cases, rows)
    report = summarize(round_dir, bank_path)
    output = render(report)
    json_output = json.dumps(report, ensure_ascii=False)
    for secret in ("SECRET_VALIDATION_ID", "SECRET_VALIDATION_QUESTION", "answer-SECRET_VALIDATION_ID"):
        assert secret not in output
        assert secret not in json_output
    assert "DEV_ID" in output and "development prompt" in output
    assert report["validation_counts"] == {"total": 1, "passed": 1, "failed": 0, "outside_total": 1, "control_total": 0}


def test_missing_case_exits_nonzero_and_reports_count(tmp_path, capsys):
    cases = [make_case("one"), make_case("SECRET_MISSING_ID")]
    round_dir, bank_path = write_fixture(tmp_path, cases, [make_result(cases[0])])
    status = main([str(round_dir), "--json", str(tmp_path / "report.json")])
    captured = capsys.readouterr()
    assert status != 0
    assert "missing=1" in captured.err
    assert "SECRET_MISSING_ID" not in captured.err
    assert not (tmp_path / "report.json").exists()


def test_two_turn_outside_second_turn_counted_by_split(tmp_path):
    first = make_case("first", behavior="facts", conversation="pair")
    second = make_case("second", behavior="outside", conversation="pair")
    round_dir, bank_path = write_fixture(tmp_path, [first, second], [make_result(first), make_result(second, passed=False)])
    report = summarize(round_dir, bank_path)
    assert report["second_turn_outside"] == [{"split": "development", "passed": 0, "total": 1}]
