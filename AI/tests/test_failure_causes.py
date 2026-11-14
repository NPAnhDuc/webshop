import json
import zipfile
from pathlib import Path

import scripts.failure_causes as failure_causes
from scripts.failure_causes import classify_failure, main, render, summarize


def make_case(case_id, behavior="facts", doc="gold-doc", split="development"):
    return {"id": case_id, "expected_behavior": behavior, "split": split,
            "required": [{"document_id": doc}], "question": f"question-{case_id}"}


def make_row(case, *, cause="", action="answer", trace=None, sources=None, status="FAIL_CHECKS", split=None):
    issues = [{"cause": cause}] if cause else []
    return {"id": case["id"], "split": split or case.get("split", "development"),
            "checks": {"status": status, "issues": issues},
            "result": {"basic_action": action, "trace": trace or [],
                       "sources": sources if sources is not None else [{"document_id": "gold-doc"}],
                       "answer": f"answer-{case['id']}"}}


def write_zip(path, rows, *, member="folder/results.json"):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(member, json.dumps(rows))


def setup_eval(tmp_path, monkeypatch, bank_name, cases):
    eval_root = tmp_path / "evaluation"
    bank_dir = eval_root / bank_name
    bank_dir.mkdir(parents=True)
    (bank_dir / "bank.json").write_text(json.dumps(cases), encoding="utf-8")
    monkeypatch.setattr(failure_causes, "EVAL_ROOT", eval_root)
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    return results_dir


def test_each_failure_group_is_classified_by_priority():
    cases = [
        make_case("infra"), make_case("law"), make_case("router", "outside"),
        make_case("search"), make_case("selection"), make_case("scope", "unknown"),
        make_case("other", "denied"),
    ]
    rows = [
        make_row(cases[0], cause="INFRASTRUCTURE"),
        make_row(cases[1], cause="ROUTING", action="clarify", trace=["route guard: blocked"]),
        make_row(cases[2], cause="ROUTING", action="answer", trace=["model router selected answer"]),
        make_row(cases[3], cause="RETRIEVAL_OR_ROUTING", sources=[]),
        make_row(cases[4], cause="SELECTION_OR_CHUNKING", sources=[]),
        make_row(cases[5], cause="WRONG_SCOPE"),
        make_row(cases[6], cause="PERMISSION"),
    ]
    assert [classify_failure(c, r) for c, r in zip(cases, rows)] == [
        "ha_tang", "luat", "router", "tim_kiem", "chon_cau", "pham_vi", "khac"
    ]


def test_selection_cause_wins_even_when_result_sources_lack_gold():
    case = make_case("selection")
    row = make_row(case, cause="SELECTION_OR_CHUNKING", sources=[])
    assert classify_failure(case, row) == "chon_cau"


def test_retrieval_cause_classifies_facts_answer_as_search():
    case = make_case("search")
    row = make_row(case, cause="RETRIEVAL_OR_ROUTING", action="answer", sources=[])
    assert classify_failure(case, row) == "tim_kiem"


def test_zip_run_computes_bank_split_causes_and_selected_steps(tmp_path, monkeypatch):
    bank = "sample_bank"
    cases = [make_case("A"), make_case("B", "outside")]
    results_dir = setup_eval(tmp_path, monkeypatch, bank, cases)
    write_zip(results_dir / f"{bank}__kaggle_r1_development.zip", [
        make_row(cases[0], cause="SELECTION_OR_CHUNKING", sources=[], trace=[
            "generic start", "route guard: checked", "evidence: chunk matched", "irrelevant tail"
        ]),
        make_row(cases[1], cause="ROUTING", action="answer", trace=["model"]),
    ])
    report = summarize(results_dir)
    assert {(r["cause"], r["stable"], r["fluctuating"]) for r in report["failure_counts"]} == {
        ("chon_cau", 1, 0), ("router", 1, 0)
    }
    failure = next(row for row in report["development_failures"] if row["id"] == "A")
    assert failure["steps"] == "route guard: checked > evidence: chunk matched"
    assert "first_trace" not in failure


def test_fail_then_pass_is_fluctuating_not_stable(tmp_path, monkeypatch):
    bank = "sample_bank"
    case = make_case("osc")
    results_dir = setup_eval(tmp_path, monkeypatch, bank, [case])
    write_zip(results_dir / f"{bank}__kaggle_a_development.zip", [make_row(case, cause="SELECTION_OR_CHUNKING")])
    write_zip(results_dir / f"{bank}__kaggle_b_development.zip", [make_row(case, status="PASS_CHECKS", cause="")])
    report = summarize(results_dir)
    assert report["failure_counts"] == [{"bank": bank, "split": "development", "cause": "chon_cau", "stable": 0, "fluctuating": 1}]


def test_validation_ids_questions_answers_and_trace_are_redacted(tmp_path, monkeypatch):
    bank = "sample_bank"
    case = make_case("SECRET_VALIDATION_ID", split="validation")
    case["question"] = "SECRET_VALIDATION_QUESTION"
    results_dir = setup_eval(tmp_path, monkeypatch, bank, [case])
    row = make_row(case, cause="SELECTION_OR_CHUNKING", trace=["SECRET_VALIDATION_TRACE"])
    row["result"]["answer"] = "SECRET_VALIDATION_ANSWER"
    write_zip(results_dir / f"{bank}__kaggle_r1_validation.zip", [row])
    report = summarize(results_dir)
    text = render(report)
    serialized = json.dumps(report)
    for secret in ("SECRET_VALIDATION_ID", "SECRET_VALIDATION_QUESTION", "SECRET_VALIDATION_TRACE", "SECRET_VALIDATION_ANSWER"):
        assert secret not in text and secret not in serialized
    assert report["validation_counts_by_cause"] == {"chon_cau": {"stable": 1, "fluctuating": 0}}


def test_include_locked_is_opt_in_and_validation_stays_count_only(tmp_path, monkeypatch, capsys):
    eval_root = tmp_path / "evaluation"
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    monkeypatch.setattr(failure_causes, "EVAL_ROOT", eval_root)
    banks = ("expansion_20261029", "offtopic_20261103")
    secret_values = []
    for bank in banks:
        case = make_case(f"SECRET_{bank}", split="validation")
        case["question"] = f"SECRET_QUESTION_{bank}"
        bank_dir = eval_root / bank
        bank_dir.mkdir(parents=True)
        (bank_dir / "bank.json").write_text(json.dumps([case]), encoding="utf-8")
        archive_path = results_dir / f"{bank}__kaggle_r1_validation.zip"
        archive_path.write_bytes(b"not opened while include_locked is off")
        secret_values.extend([case["id"], case["question"], f"SECRET_TRACE_{bank}", f"SECRET_ANSWER_{bank}"])
    sources, skipped, locked = failure_causes.discover_sources(results_dir)
    assert sources == [] and skipped == [] and locked == 2

    for bank in banks:
        case = json.loads((eval_root / bank / "bank.json").read_text(encoding="utf-8"))[0]
        row = make_row(case, cause="SELECTION_OR_CHUNKING", trace=[f"SECRET_TRACE_{bank}"])
        row["result"]["answer"] = f"SECRET_ANSWER_{bank}"
        write_zip(results_dir / f"{bank}__kaggle_r1_validation.zip", [row])
    json_path = tmp_path / "summary.json"
    assert main([str(results_dir), "--include-locked", "--json", str(json_path)]) == 0
    text = capsys.readouterr().out
    data = json_path.read_text(encoding="utf-8")
    for secret in secret_values:
        assert secret not in text and secret not in data
    report = json.loads(data)
    assert {row["bank"] for row in report["failure_counts"]} == set(banks)
    assert len(report["validation_counts_by_cause"]["chon_cau"]) == 2


def test_heldout_zip_is_never_opened_even_with_include_locked(tmp_path):
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    heldout = results_dir / "heldout_20261028__kaggle_private_development.zip"
    heldout.write_bytes(b"not a readable zip and must be ignored")
    sources, skipped, locked = failure_causes.discover_sources(results_dir, include_locked=True)
    assert sources == [] and skipped == [] and locked == 1


def test_zip_without_results_json_is_reported_by_name(tmp_path, monkeypatch):
    bank = "sample_bank"
    results_dir = setup_eval(tmp_path, monkeypatch, bank, [])
    path = results_dir / f"{bank}__kaggle_missing_development.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("metadata.json", "{}")
    sources, skipped, locked = failure_causes.discover_sources(results_dir)
    assert sources == [] and skipped == [path.name] and locked == 0
    report = summarize(results_dir)
    assert report["skipped_missing_results"] == [path.name]


def test_old_labels_and_totals_use_only_synthetic_archives(tmp_path, monkeypatch):
    cases = [make_case(name, behavior) for name, behavior in (
        ("old", "deferred"), ("router", "deferred"), ("law", "deferred"),
        ("mixed", "deferred"), ("facts", "facts"), ("infra", "deferred"),
        ("empty", "deferred"), ("malformed", "deferred"),
        ("validation-private", "deferred"),
    )]
    cases[-1]["split"] = "validation"
    rows = [make_row(case, cause="ROUTING") for case in cases]
    for row in rows:
        row["result"]["rag"] = {"method": "deterministic SQL custom calculation"}
    rows[0]["result"]["trace"] = ["route guard: checked"]
    rows[1]["result"]["rag"]["method"] = "model"
    rows[2]["result"]["rag"]["method"] = None
    rows[2]["result"]["trace"] = ["route guard: blocked"]
    rows[3]["checks"]["issues"].append({"cause": "SELECTION_OR_CHUNKING"})
    rows[5]["checks"]["issues"].append({"cause": "INFRASTRUCTURE"})
    rows[6]["checks"]["issues"] = []
    rows[7]["checks"]["issues"].append("invalid issue")
    assert [classify_failure(case, row) for case, row in zip(cases, rows)] == [
        "nhan_de_cu", "router", "luat", "router", "router", "ha_tang",
        "khac", "router", "nhan_de_cu",
    ]
    results_dir = setup_eval(tmp_path, monkeypatch, "sample_bank", cases)
    write_zip(results_dir / "sample_bank__kaggle_r1_all.zip", rows)
    report = summarize(results_dir)
    assert report["development_totals"] == {
        "do_model": 4, "do_code": 1, "other": 2, "nhan_de_cu": 1,
    }
    assert report["validation_counts_by_cause"] == {
        "nhan_de_cu": {"stable": 1, "fluctuating": 0},
    }
    assert "validation-private" not in render(report)
    assert "validation-private" not in json.dumps(report)
