import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[1]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from scripts import build_natural_bank_20261031 as builder


def read_outputs():
    folder = AI_ROOT / "evaluation" / "natural_20261031"
    bank = json.loads((folder / "bank.json").read_text(encoding="utf-8"))
    gold = json.loads((folder / "gold_sources.json").read_text(encoding="utf-8"))
    metadata = json.loads((folder / "metadata.json").read_text(encoding="utf-8"))
    return folder, bank, gold, metadata


def test_bank_has_expected_natural_language_groups_and_conversations():
    _, bank, _, meta = read_outputs()
    assert len(bank) == 120
    assert len({case["id"] for case in bank}) == 120
    assert len({case["question"].casefold() for case in bank}) == 120
    assert Counter(case["topic"] for case in bank) == {
        "customer_policy": 25,
        "product_advice": 30,
        "unsupported_product": 15,
        "privacy_or_handoff": 15,
        "admin_business_question": 25,
        "multi_turn": 10,
    }
    assert all(case["today"] == "2026-10-31" and case["split"] == "development" for case in bank)
    groups = defaultdict(list)
    for case in bank:
        groups[case["conversation"]].append(case)
    dialogues = [cases for name, cases in groups.items() if name.startswith("dialogue-")]
    assert len(dialogues) == 4
    assert all(2 <= len(cases) <= 3 for cases in dialogues)
    assert sum(len(cases) == 3 for cases in dialogues) >= 2
    assert sum(len({case["intent"] for case in cases}) > 1 for cases in dialogues) >= 2
    assert meta["groups"]["multi_turn"] == 10
    labels = Counter(case["expected_behavior"] for case in bank)
    assert labels["denied"] >= 8
    assert labels["live_product"] >= 3
    assert labels["clarify"] >= 6
    assert sum(not builder.has_diacritic(case["question"]) for case in bank) >= 20
    assert sum(builder.re.search(r"\b(?:ko|dc|bn|sp|ship|bh|tr)\b", case["question"], builder.re.I) is not None for case in bank) >= 15
    assert sum(len(case["question"].split()) >= 20 for case in bank) >= 15
    assert all(case["rubric"].strip() and "\n" not in case["rubric"] for case in bank)
    by_id = {case["id"]: case for case in bank}
    for group, pairs in meta["boundary_pairs"].items():
        assert len(pairs) >= 3, group
        for left_id, right_id in pairs:
            left, right = by_id[left_id], by_id[right_id]
            assert left["question"] != right["question"]
            if group in {"product_advice", "unsupported_product", "privacy_or_handoff", "admin_business_question"}:
                assert left["expected_behavior"] != right["expected_behavior"]
            else:
                assert left["required"] and right["required"]


def test_every_fact_quote_is_verbatim_in_gold_sources_with_correct_audience():
    _, bank, gold, _ = read_outputs()
    sources = {(doc["document_id"], doc["version"]): doc for doc in gold}
    for case in bank:
        assert case["gold_document_ids"] == sorted({ref["document_id"] for ref in case["required"]})
        for ref in case["required"]:
            doc = sources[(ref["document_id"], ref["version"])]
            assert ref["quote"] in doc["text"]
            assert case["role"] == "admin" or doc["audience"] == "customer"
        if case["expected_behavior"] == "unknown":
            assert case["required"] == []


def test_all_monthly_numeric_claims_match_shop_database():
    _, bank, _, _ = read_outputs()
    builder.check_database_numbers(bank)


def test_new_fake_names_are_absent_from_existing_cases_and_metadata_is_portable():
    _, _, _, metadata = read_outputs()
    existing = [path.read_text(encoding="utf-8").casefold()
                for path in builder.CASES_FILES if path.is_file()]
    assert existing
    for name in builder.UNSEEN_PRODUCT_NAMES:
        assert all(name.casefold() not in content for content in existing)
    assert "D:\\" not in json.dumps(metadata, ensure_ascii=False)


def test_builder_reproduces_identical_files():
    folder, _, _, _ = read_outputs()
    before = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
              for name in ("bank.json", "gold_sources.json", "metadata.json")}
    rebuilt = builder.build()
    after = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
             for name in ("bank.json", "gold_sources.json", "metadata.json")}
    assert len(rebuilt) == 120
    assert before == after
