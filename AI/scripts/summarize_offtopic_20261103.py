#!/usr/bin/env python3
"""Summarize the off-topic evaluation without exposing validation examples."""
import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

EVAL_DIR = Path(__file__).resolve().parents[1] / "evaluation" / "offtopic_20261103"
PASS = "PASS_CHECKS"


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def summarize(round_dir, bank_path=None):
    round_dir = Path(round_dir)
    bank_path = Path(bank_path) if bank_path else (round_dir.parent / "bank.json")
    if not bank_path.exists():
        bank_path = EVAL_DIR / "bank.json"
    bank = read_json(bank_path)
    results_path = round_dir / "results.json"
    results = read_json(results_path)
    if not isinstance(bank, list) or not isinstance(results, list):
        raise ValueError("bank.json and results.json must contain arrays")

    bank_by_id = {row["id"]: row for row in bank}
    if len(bank_by_id) != len(bank):
        raise ValueError("bank.json contains duplicate ids")
    result_ids = [row.get("id") for row in results]
    duplicate_ids = len(result_ids) - len(set(result_ids))
    if duplicate_ids:
        raise ValueError(f"results.json contains {duplicate_ids} duplicate ids")
    result_by_id = {row.get("id"): row for row in results}
    missing = sorted(set(bank_by_id) - set(result_by_id))
    unknown = sorted(set(result_by_id) - set(bank_by_id))
    if missing or unknown:
        raise ValueError(f"results incomplete: missing={len(missing)}, unknown={len(unknown)}")

    entries = []
    for case in bank:
        result_row = result_by_id[case["id"]]
        result = result_row.get("result") or {}
        checks = result_row.get("checks") or {}
        entries.append({
            "case": case,
            "row": result_row,
            "passed": checks.get("status") == PASS,
            "actual_action": result.get("basic_action") or "missing",
            "answer": result.get("answer") or "",
        })

    topic_split = defaultdict(lambda: [0, 0])
    group_totals = defaultdict(lambda: [0, 0])
    outside_failures = Counter()
    conversations = defaultdict(list)
    for entry in entries:
        case = entry["case"]
        split = case["split"]
        topic_split[(case["topic"], split)][0] += int(entry["passed"])
        topic_split[(case["topic"], split)][1] += 1
        group = "outside" if case["expected_behavior"] == "outside" else "control"
        group_totals[(group, split)][0] += int(entry["passed"])
        group_totals[(group, split)][1] += 1
        if group == "outside" and not entry["passed"]:
            outside_failures[(split, entry["actual_action"])] += 1
        conversations[case["conversation"]].append(entry)

    second_turn = defaultdict(lambda: [0, 0])
    for turns in conversations.values():
        if len(turns) == 2 and turns[1]["case"]["expected_behavior"] == "outside":
            split = turns[1]["case"]["split"]
            second_turn[split][0] += int(turns[1]["passed"])
            second_turn[split][1] += 1

    development_failures = []
    for entry in entries:
        case = entry["case"]
        if case["split"] == "development" and not entry["passed"]:
            development_failures.append({
                "id": case["id"],
                "topic": case["topic"],
                "question": case["question"],
                "expected_action": case["expected_behavior"],
                "actual_action": entry["actual_action"],
                "answer_excerpt": entry["answer"][:120],
            })

    # Validation deliberately has aggregate counts only: no IDs, prompts, or answers.
    validation_counts = {
        "total": sum(case["split"] == "validation" for case in bank),
        "passed": sum(e["passed"] for e in entries if e["case"]["split"] == "validation"),
        "failed": sum(not e["passed"] for e in entries if e["case"]["split"] == "validation"),
        "outside_total": sum(e["case"]["split"] == "validation" and e["case"]["expected_behavior"] == "outside" for e in entries),
        "control_total": sum(e["case"]["split"] == "validation" and e["case"]["expected_behavior"] != "outside" for e in entries),
    }
    return {
        "completeness": {"missing_count": len(missing), "unknown_count": len(unknown)},
        "topic_split": [
            {"topic": topic, "split": split, "passed": counts[0], "total": counts[1]}
            for (topic, split), counts in sorted(topic_split.items())
        ],
        "group_totals": [
            {"group": group, "split": split, "passed": counts[0], "total": counts[1]}
            for (group, split), counts in sorted(group_totals.items())
        ],
        "outside_failures_by_action": [
            {"split": split, "basic_action": action, "count": count}
            for (split, action), count in sorted(outside_failures.items())
        ],
        "second_turn_outside": [
            {"split": split, "passed": counts[0], "total": counts[1]}
            for split, counts in sorted(second_turn.items())
        ],
        "development_failures": development_failures,
        "validation_counts": validation_counts,
    }


def render(report):
    lines = ["Off-topic summary", "", "Topic x split (PASS_CHECKS / total)", "topic | split | passed/total"]
    for row in report["topic_split"]:
        lines.append(f"{row['topic']} | {row['split']} | {row['passed']}/{row['total']}")
    lines.extend(["", "Group totals", "group | split | passed/total"])
    for row in report["group_totals"]:
        lines.append(f"{row['group']} | {row['split']} | {row['passed']}/{row['total']}")
    lines.extend(["", "Outside failures by actual basic_action", "split | basic_action | count"])
    for row in report["outside_failures_by_action"]:
        lines.append(f"{row['split']} | {row['basic_action']} | {row['count']}")
    lines.extend(["", "Two-turn conversations, second turn expected outside", "split | passed/total"])
    for row in report["second_turn_outside"]:
        lines.append(f"{row['split']} | {row['passed']}/{row['total']}")
    lines.extend(["", "Validation counts only", json.dumps(report["validation_counts"], ensure_ascii=False, sort_keys=True)])
    lines.extend(["", "Development failures"])
    if not report["development_failures"]:
        lines.append("None")
    for row in report["development_failures"]:
        lines.append(f"{row['id']} | {row['topic']} | {row['question']} | expected={row['expected_action']} | actual={row['actual_action']} | answer={row['answer_excerpt']}")
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("round_dir", type=Path)
    parser.add_argument("--json", dest="json_out", type=Path)
    args = parser.parse_args(argv)
    try:
        report = summarize(args.round_dir)
    except (OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(render(report), end="")
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
