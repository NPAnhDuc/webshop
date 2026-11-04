import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from scripts.compare_runs import ArchiveError, compare, load_run, render


def write_run(path, entries):
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("results.json", json.dumps(entries))
    return path


def row(case_id, split, passed):
    return {"id": case_id, "split": split, "checks": {"status": "PASS_CHECKS" if passed else "FAIL_CHECKS"}}


def write_gate_run(root, bank, tag, split, rows):
    results = root / "results"
    results.mkdir(parents=True, exist_ok=True)
    return write_run(results / f"{bank}__kaggle_{tag}_{split}.zip", rows)


def gate_row(case_id, split, passed, **extra):
    entry = row(case_id, split, passed)
    entry.update(extra)
    return entry


def label_row(case_id, split, method="deterministic SQL calculation", extra_issues=()):
    """A failing row shaped like a real result where the frozen label wanted a deferral."""
    entry = row(case_id, split, False)
    entry["checks"]["issues"] = [
        {"cause": "ROUTING", "detail": {"expected": "deferred", "actual": "answer"}},
        *extra_issues,
    ]
    entry["result"] = {"rag": {"method": method}}
    return entry


def run_gate(base, candidate, *extra):
    script = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"
    return subprocess.run(
        [sys.executable, str(script), "--base-dir", str(base), "--candidate-dir", str(candidate), *extra],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )


def test_classifies_all_five_groups_and_lists_only_unlocked_ids():
    base_a = {
        ("dev", "lost"): True,
        ("dev", "won"): False,
        ("dev", "flaky"): True,
        ("dev", "pass"): True,
        ("dev", "fail"): False,
        ("validation", "LOCKED-SECRET-ID"): True,
    }
    base_b = dict(base_a, **{})
    base_b[("dev", "flaky")] = False
    candidate_a = {
        ("dev", "lost"): False,
        ("dev", "won"): True,
        ("dev", "flaky"): False,
        ("dev", "pass"): True,
        ("dev", "fail"): False,
        ("validation", "LOCKED-SECRET-ID"): True,
    }
    candidate_b = dict(candidate_a)
    candidate_b[("dev", "flaky")] = True

    report = compare(
        [{(s, i): v for (s, i), v in run.items()} for run in (base_a, base_b)],
        [{(s, i): v for (s, i), v in run.items()} for run in (candidate_a, candidate_b)],
        locked_splits=("validation",),
    )
    dev = report["dev"]
    assert dev["counts"] == {
        "stable_lost": 1,
        "stable_won": 1,
        "flaky": 1,
        "stable_pass": 1,
        "stable_fail": 1,
    }
    assert dev["ids"]["stable_lost"] == ["lost"]
    assert report["validation"]["ids"] is None
    rendered = render(report)
    assert "LOCKED-SECRET-ID" not in rendered
    assert "stable_lost: 1" in rendered


def test_single_run_on_each_side_is_classified_without_flaky():
    report = compare([{("dev", "x"): True}], [{("dev", "x"): False}])
    assert report["dev"]["counts"]["stable_lost"] == 1
    assert report["dev"]["counts"]["flaky"] == 0


def test_missing_entries_are_counted_and_excluded_from_classification():
    report = compare(
        [{("dev", "present"): True, ("dev", "missing-later"): False}, {("dev", "present"): True}],
        [{("dev", "present"): False}],
    )
    assert report["dev"]["base_missing"] == 1
    assert report["dev"]["candidate_missing"] == 1
    assert report["dev"]["counts"]["stable_lost"] == 1


def test_bad_zip_and_missing_fields_raise_clear_errors(tmp_path):
    broken = tmp_path / "broken.zip"
    broken.write_bytes(b"not a zip")
    with pytest.raises(ArchiveError, match="invalid or unreadable zip"):
        load_run(broken)

    missing = write_run(tmp_path / "missing.zip", [{"id": "x", "split": "dev"}])
    with pytest.raises(ArchiveError, match="checks.status"):
        load_run(missing)


def test_locked_split_cli_never_prints_ids_even_on_input_error(tmp_path):
    locked = write_run(tmp_path / "locked.zip", [row("DO-NOT-LEAK", "validation", True)])
    candidate = write_run(tmp_path / "candidate.zip", [row("DO-NOT-LEAK", "validation", False)])
    script = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"
    result = subprocess.run(
        [sys.executable, str(script), "--base", str(locked), "--candidate", str(candidate), "--locked-split", "validation"],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "DO-NOT-LEAK" not in result.stdout + result.stderr
    assert "stable_lost: 1" in result.stdout

    bad = tmp_path / "bad.zip"
    bad.write_bytes(b"broken")
    result = subprocess.run(
        [sys.executable, str(script), "--base", str(bad), "--candidate", str(candidate), "--locked-split", "validation"],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )
    assert result.returncode != 0
    assert "DO-NOT-LEAK" not in result.stdout + result.stderr


def test_directory_mode_aggregates_tags_expands_all_and_prints_gate_verdict(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "bank_a", "base1", "all", [row("a", "development", True), row("b", "validation", True)])
    write_gate_run(base, "bank_a", "base2", "all", [row("a", "development", True), row("b", "validation", True)])
    write_gate_run(candidate, "bank_a", "cand1", "development", [row("a", "development", False)])
    write_gate_run(candidate, "bank_a", "cand2", "development", [row("a", "development", False)])
    write_gate_run(candidate, "bank_a", "cand1", "validation", [row("b", "validation", True)])
    script = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"
    result = subprocess.run(
        [sys.executable, str(script), "--base-dir", str(base), "--candidate-dir", str(candidate)],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert "bank=bank_a split=development" in result.stdout
    assert "run base1: pass=1" in result.stdout
    assert "stable_lost: 1" in result.stdout
    assert "CỔNG: CHƯA ĐẠT" in result.stdout


def test_directory_mode_reports_missing_bank_and_can_pass_gate(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "present_only_in_base", "b", "dev", [row("x", "dev", True)])
    write_gate_run(base, "shared", "b", "dev", [row("same", "dev", True)])
    write_gate_run(candidate, "shared", "c", "dev", [row("same", "dev", True)])
    script = Path(__file__).resolve().parents[1] / "scripts" / "compare_runs.py"
    result = subprocess.run(
        [sys.executable, str(script), "--base-dir", str(base), "--candidate-dir", str(candidate)],
        text=True, encoding="utf-8", capture_output=True, check=False,
    )
    assert result.returncode == 0
    assert "present_only_in_base" in result.stdout and "THIẾU Ở ỨNG VIÊN" in result.stdout
    assert result.stdout.rstrip().endswith("CỔNG: CHƯA ĐẠT: present_only_in_base/dev thiếu ở ứng viên")


def test_a_bank_only_the_candidate_has_does_not_block_the_gate(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "shared", "b", "dev", [row("same", "dev", True)])
    write_gate_run(candidate, "shared", "c", "dev", [row("same", "dev", True)])
    write_gate_run(candidate, "new_bank", "c", "dev", [row("x", "dev", False)])
    result = run_gate(base, candidate)
    assert "THIẾU Ở BẢN GỐC" in result.stdout
    assert result.stdout.rstrip().endswith("CỔNG: ĐẠT")


def test_rows_missing_from_the_candidate_block_the_gate(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "shared", "b", "dev", [row("a", "dev", True), row("b", "dev", True)])
    write_gate_run(candidate, "shared", "c", "dev", [row("a", "dev", True)])
    assert run_gate(base, candidate).stdout.rstrip().endswith("CỔNG: CHƯA ĐẠT: shared/dev thiếu 1 câu ở ứng viên")


def test_empty_directories_do_not_pass_the_gate(tmp_path):
    (tmp_path / "base" / "results").mkdir(parents=True)
    (tmp_path / "candidate" / "results").mkdir(parents=True)
    assert run_gate(tmp_path / "base", tmp_path / "candidate").stdout.rstrip().startswith("CỔNG: CHƯA ĐẠT")


def test_verdict_names_each_bank_and_lost_count(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "one", "b", "dev", [row("a", "dev", True), row("b", "dev", True)])
    write_gate_run(candidate, "one", "c", "dev", [row("a", "dev", False), row("b", "dev", False)])
    write_gate_run(base, "two", "b", "dev", [row("a", "dev", True)])
    write_gate_run(candidate, "two", "c", "dev", [row("a", "dev", False)])
    assert run_gate(base, candidate).stdout.rstrip().endswith("CỔNG: CHƯA ĐẠT: one/dev mất 2 câu, two/dev mất 1 câu")


def test_calc_label_is_read_from_the_candidate_because_the_base_row_passed(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "bank", "b", "dev", [row("calc", "dev", True), row("real", "dev", True)])
    write_gate_run(candidate, "bank", "c", "dev", [label_row("calc", "dev"), row("real", "dev", False)])
    stdout = run_gate(base, candidate).stdout
    assert "calc_label: 1" in stdout
    assert "stable_lost_con_tinh: 1" in stdout
    assert "calc_label_ids: calc" in stdout
    assert "stable_lost_ids: calc, real" in stdout
    assert stdout.rstrip().endswith("CỔNG: CHƯA ĐẠT: bank/dev mất 1 câu")


def test_calc_label_requires_a_calculated_answer_and_no_other_issue(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "bank", "b", "dev", [row("model", "dev", True), row("wrong", "dev", True)])
    write_gate_run(candidate, "bank", "c", "dev", [
        label_row("model", "dev", method="grounded evidence"),
        label_row("wrong", "dev", extra_issues=[{"cause": "NUMERIC", "detail": {}}]),
    ])
    stdout = run_gate(base, candidate).stdout
    assert "calc_label: 0" in stdout
    assert "CỔNG: CHƯA ĐẠT" in stdout


def test_calc_label_is_counted_separately_and_locked_payload_never_leaks(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    secret_id = "UNIQUE_LOCKED_CASE_8f32"
    secret_question = "QUESTION_SECRET silver price 987654"
    write_gate_run(base, "lockedbank", "b", "all", [gate_row(secret_id, "validation", True, question=secret_question)])
    write_gate_run(candidate, "lockedbank", "c", "all", [dict(label_row(secret_id, "validation"), question=secret_question)])
    result = run_gate(base, candidate, "--locked-split", "validation")
    assert result.returncode == 0
    assert secret_id not in result.stdout + result.stderr
    assert secret_question not in result.stdout + result.stderr
    assert "calc_label: 1" in result.stdout
    assert result.stdout.rstrip().endswith("CỔNG: ĐẠT")


def test_validation_and_heldout_stay_counts_only_without_the_flag(tmp_path):
    base = tmp_path / "base"
    candidate = tmp_path / "candidate"
    write_gate_run(base, "expansion", "b", "all", [row("VAL_SECRET", "validation", True)])
    write_gate_run(candidate, "expansion", "c", "all", [row("VAL_SECRET", "validation", False)])
    write_gate_run(base, "heldout_20261028", "b", "test", [row("HELD_SECRET", "test", True)])
    write_gate_run(candidate, "heldout_20261028", "c", "test", [row("HELD_SECRET", "test", False)])
    result = run_gate(base, candidate)
    assert "VAL_SECRET" not in result.stdout + result.stderr
    assert "HELD_SECRET" not in result.stdout + result.stderr
    assert "stable_lost: 1" in result.stdout
