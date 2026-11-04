"""Check numeric calculation answers in a natural2_20261031 runner round.

Usage: score_natural2_20261031.py ROUND [BASE_ROUND]
Only calculation cases are rescored here; other cases keep the runner's checks.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shopbot.retrieval import normalize

BASE = ROOT / "evaluation/natural2_20261031"
GROUPED = re.compile(r"(?<!\w)([+-]?)(\d{1,3}(?:[., \u00a0]\d{3})+)(?:([.,]\d+))?(?!\w)")
NUMBER = re.compile(r"(?<!\w)([+-]?\d+(?:[.,]\d+)?)(?!\w)")
NEGATIVE_WORDS = re.compile(r"\b(?:giảm|giảm xuống|thấp hơn|thấp|hụt|sụt|âm|ít hơn)\b", re.I)
ASKS_A_DROP = re.compile(r"\b(?:giam|thap hon|hut|sut|it hon)\b")


def _decimal(text: str) -> Decimal | None:
    token = text.strip().replace("\u00a0", " ").replace(" ", "")
    if "," in token and "." in token:
        # In a grouped number, the rightmost separator is the decimal mark only
        # when the final group is not three digits.
        if token.rfind(",") > token.rfind("."):
            token = token.replace(".", "").replace(",", ".")
        else:
            token = token.replace(",", "")
    elif "," in token:
        token = token.replace(",", ".")
    try:
        return Decimal(token)
    except InvalidOperation:
        return None


def answer_numbers(answer: str) -> list[tuple[Decimal, int, int]]:
    """Return parsed number tokens and their character offsets."""
    found: list[tuple[Decimal, int, int]] = []
    occupied: list[tuple[int, int]] = []
    for match in GROUPED.finditer(answer):
        sign, whole, fraction = match.groups()
        token = sign + re.sub(r"[., \u00a0]", "", whole)
        if fraction:
            token += "." + fraction[1:]
        value = _decimal(token)
        if value is not None:
            found.append((value, match.start(), match.end()))
            occupied.append((match.start(), match.end()))
    for match in NUMBER.finditer(answer):
        if any(match.start() < end and match.end() > start for start, end in occupied):
            continue
        value = _decimal(match.group(1))
        if value is not None:
            found.append((value, match.start(), match.end()))
    return found


def expected_value_found(value: int | float, answer: str, question: str = "") -> bool:
    expected = Decimal(str(value))
    # "Giảm bao nhiêu %" has a positive gold; "thay đổi: -19,63%" states the same drop.
    drop_asked = bool(ASKS_A_DROP.search(normalize(question)))
    for actual, start, end in answer_numbers(answer):
        if actual == expected:
            return True
        if expected < 0 and actual == abs(expected):
            context = answer[max(0, start - 36):min(len(answer), end + 36)]
            if NEGATIVE_WORDS.search(context):
                return True
        if expected > 0 and actual == -expected and drop_asked:
            return True
    return False


def score_case(case: dict, result: dict) -> str:
    if not case.get("expected_sql"):
        return result.get("checks", {}).get("status", "MISSING_RESULT")
    if result.get("basic_action") != "answer":
        return "FAIL_CALC_ACTION"
    answer = result.get("answer", "")
    values = [item.get("value") for item in case.get("expected_values", [])]
    if not values or any(not isinstance(value, (int, float)) for value in values):
        return "FAIL_CALC_GOLD"
    if not all(expected_value_found(value, answer, case.get("question", "")) for value in values):
        return "FAIL_CALC_VALUE"
    return "PASS_CALC"


def load_round(name: str) -> tuple[dict[str, str], dict[str, dict]]:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", name):
        raise ValueError("Invalid round name")
    bank = {case["id"]: case for case in json.loads((BASE / "bank.json").read_text(encoding="utf-8"))}
    rows = json.loads((BASE / name / "results.json").read_text(encoding="utf-8"))
    scores = {}
    for row in rows:
        case_id = row["id"]
        if case_id not in bank:
            raise ValueError(f"Unknown case in round: {case_id}")
        scores[case_id] = score_case(bank[case_id], row.get("result", {}) | {"checks": row.get("checks", {})})
    return scores, bank


def report(name: str, scores: dict[str, str], bank: dict[str, dict]) -> None:
    counts = Counter(scores.values())
    calc_ids = [case_id for case_id, case in bank.items() if case.get("expected_sql")]
    calc_counts = Counter(scores[case_id] for case_id in calc_ids if case_id in scores)
    by_topic: dict[str, Counter] = defaultdict(Counter)
    for case_id, status in scores.items():
        by_topic[bank[case_id]["topic"]][status] += 1
    print(f"{name}: {len(scores)}/{len(bank)}", dict(counts))
    print(f"calculation cases: {sum(calc_counts.values())}/{len(calc_ids)}", dict(calc_counts))
    for topic in sorted(by_topic):
        print(f"  {topic:24}", dict(by_topic[topic]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("round")
    parser.add_argument("base_round", nargs="?")
    args = parser.parse_args()
    current, bank = load_round(args.round)
    report(args.round, current, bank)
    if args.base_round:
        prior, _ = load_round(args.base_round)
        calc_ids = [case_id for case_id, case in bank.items() if case.get("expected_sql")]
        down = [case_id for case_id in calc_ids if prior.get(case_id) == "PASS_CALC" and current.get(case_id) != "PASS_CALC"]
        up = [case_id for case_id in calc_ids if prior.get(case_id) != "PASS_CALC" and current.get(case_id) == "PASS_CALC"]
        print("calculation PASS->not PASS:", len(down), down)
        print("calculation not PASS->PASS:", len(up), up)


if __name__ == "__main__":
    main()
