#!/usr/bin/env python3
"""Classify evaluation failures as likely model, code, infrastructure, or other."""
import argparse
import json
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

EVAL_ROOT = Path(__file__).resolve().parents[1] / "evaluation"
CAUSE_ORDER = ("ha_tang", "luat", "router", "tim_kiem", "chon_cau", "pham_vi", "khac")
ZIP_RE = re.compile(r"^(?P<bank>.+)__kaggle_(?P<run>.+)_(?P<split>development|validation|all)\.zip$", re.I)
LOCKED_BANKS = {"expansion_20261029", "offtopic_20261103"}
HELDOUT_MARKER = "heldout_20261028"


def read_json_bytes(data, label):
    try:
        return json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON in {label}: {exc}") from exc


def nearest_bank_name(path):
    for parent in (path.parent, *path.parents):
        if (parent / "bank.json").is_file():
            return parent.name
    raise ValueError(f"cannot infer bank for {path}")


def discover_sources(results_dir, include_locked=False):
    results_dir = Path(results_dir)
    sources = []
    skipped = []
    skipped_locked = 0
    zip_paths = sorted(results_dir.rglob("*.zip"))
    for path in zip_paths:
        lower_name = path.name.casefold()
        if HELDOUT_MARKER in lower_name:
            skipped_locked += 1
            continue
        match = ZIP_RE.match(path.name)
        if not match:
            skipped.append(path.name)
            continue
        bank = match.group("bank")
        if bank.casefold() in LOCKED_BANKS and not include_locked:
            skipped_locked += 1
            continue
        if bank.casefold().startswith("heldout_"):
            skipped_locked += 1
            continue
        try:
            with zipfile.ZipFile(path) as archive:
                member = next((n for n in archive.namelist() if PurePosixPath(n).name == "results.json"), None)
                if member is None:
                    skipped.append(path.name)
                    continue
                rows = read_json_bytes(archive.read(member), f"{path.name}:{member}")
        except zipfile.BadZipFile as exc:
            raise ValueError(f"invalid zip {path.name}: {exc}") from exc
        if not isinstance(rows, list):
            raise ValueError(f"results.json in {path.name} must contain an array")
        sources.append({"bank": bank, "run": match.group("run"), "fallback_split": match.group("split").casefold(), "path": str(path), "rows": rows})

    for path in sorted(results_dir.rglob("results.json")):
        parts = {part.casefold() for part in path.parts}
        if any(HELDOUT_MARKER in part for part in parts):
            skipped_locked += 1
            continue
        if not include_locked and any(bank in parts for bank in LOCKED_BANKS):
            skipped_locked += 1
            continue
        bank = nearest_bank_name(path)
        if (bank.casefold() in LOCKED_BANKS and not include_locked) or bank.casefold().startswith("heldout_"):
            skipped_locked += 1
            continue
        try:
            rows = read_json_bytes(path.read_bytes(), str(path))
        except OSError:
            raise
        if not isinstance(rows, list):
            raise ValueError(f"{path} must contain an array")
        parent_split = next((part.casefold() for part in path.parts if part.casefold() in ("development", "validation", "all")), "all")
        sources.append({"bank": bank, "run": path.parent.name, "fallback_split": parent_split, "path": str(path), "rows": rows})
    return sources, skipped, skipped_locked


def has_law_trace(trace):
    for step in trace if isinstance(trace, list) else []:
        if isinstance(step, str) and step.casefold().startswith(("route guard", "capability preflight")):
            return True
    return False


def classify_failure(case, row):
    checks = row.get("checks") or {}
    causes = {issue.get("cause") for issue in checks.get("issues", []) if isinstance(issue, dict)}
    result = row.get("result") or {}
    action = result.get("basic_action")
    trace = result.get("trace") or []
    behavior = case.get("expected_behavior")
    if "INFRASTRUCTURE" in causes:
        return "ha_tang"
    wrong_handling = "ROUTING" in causes or (behavior == "facts" and action != "answer")
    if wrong_handling:
        return "luat" if has_law_trace(trace) else "router"
    if behavior == "facts" and action == "answer" and "RETRIEVAL_OR_ROUTING" in causes:
        return "tim_kiem"
    if "SELECTION_OR_CHUNKING" in causes:
        return "chon_cau"
    if causes & {"WRONG_SCOPE", "MISSING_NOT_ACKNOWLEDGED"}:
        return "pham_vi"
    return "khac"


def relevant_steps(row):
    trace = (row.get("result") or {}).get("trace") or []
    if not isinstance(trace, list):
        return ""
    prefixes = ("route guard", "capability preflight", "evidence:")
    selected = [step for step in trace if isinstance(step, str) and step.casefold().startswith(prefixes)]
    return " > ".join(selected)[:120]

def summarize(results_dir, include_locked=False):
    sources, skipped_files, skipped_locked = discover_sources(results_dir, include_locked=include_locked)
    if not sources and not skipped_files and not skipped_locked:
        raise ValueError("no readable result files found")
    bank_cache = {}
    runs_by_bank_split = defaultdict(set)
    observations = defaultdict(dict)
    cases_by_key = {}
    for source_index, source in enumerate(sources):
        bank_name = source["bank"]
        if bank_name not in bank_cache:
            bank_path = EVAL_ROOT / bank_name / "bank.json"
            if not bank_path.is_file():
                raise ValueError(f"bank.json not found for {bank_name}")
            bank_cache[bank_name] = {case["id"]: case for case in read_json_bytes(bank_path.read_bytes(), str(bank_path))}
        bank = bank_cache[bank_name]
        run_key = (source["path"], source_index)
        for row in source["rows"]:
            case_id = row.get("id")
            case = bank.get(case_id)
            if case is None:
                continue
            split = str(row.get("split") or source["fallback_split"])
            runs_by_bank_split[(bank_name, split)].add(run_key)
            key = (bank_name, split, case_id)
            cases_by_key[key] = case
            status = (row.get("checks") or {}).get("status")
            record = {"failed": status == "FAIL_CHECKS", "cause": None, "row": row, "run": source["run"]}
            if record["failed"]:
                record["cause"] = classify_failure(case, row)
            observations[key][run_key] = record

    grouped = defaultdict(lambda: {"stable": 0, "fluctuating": 0})
    case_records = []
    validation_counts = defaultdict(lambda: {"stable": 0, "fluctuating": 0})
    for key, case in cases_by_key.items():
        bank_name, split, case_id = key
        run_keys = runs_by_bank_split[(bank_name, split)]
        records = [observations[key].get(run_key) for run_key in run_keys]
        failed = [record for record in records if record and record["failed"]]
        if not failed:
            continue
        cause_counts = Counter(record["cause"] for record in failed)
        cause = next(c for c in CAUSE_ORDER if cause_counts[c] == max(cause_counts.values()))
        stability = "stable" if len(failed) == len(run_keys) else "fluctuating"
        grouped[(bank_name, split, cause)][stability] += 1
        if split == "validation":
            validation_counts[cause][stability] += 1
        if split == "development":
            sample = failed[0]["row"]
            result = sample.get("result") or {}
            case_records.append({
                "bank": bank_name,
                "id": case_id,
                "cause": cause,
                "expected_behavior": case.get("expected_behavior", ""),
                "basic_action": result.get("basic_action", ""),
                "steps": relevant_steps(sample),
            })

    development_totals = {"do_model": 0, "do_code": 0, "other": 0}
    for record in case_records:
        cause = record["cause"]
        target = "do_model" if cause in ("router", "chon_cau", "pham_vi") else "do_code" if cause in ("luat", "tim_kiem") else "other"
        development_totals[target] += 1
    group_rows = [
        {"bank": bank, "split": split, "cause": cause, **counts}
        for (bank, split, cause), counts in sorted(grouped.items())
    ]
    return {
        "failure_counts": group_rows,
        "development_totals": development_totals,
        "development_failures": sorted(case_records, key=lambda row: (row["bank"], row["id"])),
        "validation_counts_by_cause": {cause: counts for cause, counts in sorted(validation_counts.items())},
        "skipped_missing_results": skipped_files,
        "skipped_locked_count": skipped_locked,
    }


def render(report):
    lines = ["Failure causes (stable = failed in every run; fluctuating = failed only in some runs)", "bank | split | cause | stable | fluctuating"]
    for row in report["failure_counts"]:
        lines.append(f"{row['bank']} | {row['split']} | {row['cause']} | {row['stable']} | {row['fluctuating']}")
    lines.extend(["", "Development failure totals", json.dumps(report["development_totals"], ensure_ascii=False, sort_keys=True)])
    lines.extend(["", "Validation counts by cause only", json.dumps(report["validation_counts_by_cause"], ensure_ascii=False, sort_keys=True)])
    lines.extend(["", "Development failures", "bank | id | cause | expected_behavior | basic_action | steps"])
    for row in report["development_failures"]:
        lines.append(f"{row['bank']} | {row['id']} | {row['cause']} | {row['expected_behavior']} | {row['basic_action']} | {row['steps']}")
    if report["skipped_missing_results"]:
        lines.extend(["", "Archives without results.json"])
        lines.extend(report["skipped_missing_results"])
    if report["skipped_locked_count"]:
        lines.extend(["", f"Skipped locked inputs: {report['skipped_locked_count']}"])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--json", dest="json_out", type=Path)
    parser.add_argument("--include-locked", action="store_true", help="include expansion_20261029 and offtopic_20261103; heldout is always skipped")
    args = parser.parse_args(argv)
    try:
        report = summarize(args.results_dir, include_locked=args.include_locked)
    except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(render(report), end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
