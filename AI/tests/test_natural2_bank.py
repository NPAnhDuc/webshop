import json
import hashlib
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_natural2_bank_20261031 as builder
from shopbot.grounded_rag import question_parts


def test_builder_creates_complete_independent_bank():
    cases = builder.build()
    assert len(cases) == 120
    assert len({case["question"].casefold() for case in cases}) == 120
    assert {case["topic"] for case in cases} == {
        "customer_policy", "product_advice", "unsupported_product",
        "privacy_or_handoff", "admin_business_question", "multi_turn",
    }
    assert sum("expected_sql" in case for case in cases) >= 10
    catalog_advice = [case for case in cases if case["topic"] == "product_advice" and any(did.startswith("catalog-") for did in case["gold_document_ids"])]
    assert len(catalog_advice) <= 15
    unsupported = [case for case in cases if case["topic"] == "unsupported_product"]
    colloquial = re.compile(r"\b(?:ko|k|dc|đc|bn|sp|bh|mk|mn|SDT)\b", re.I)
    assert sum(bool(colloquial.search(case["question"])) for case in unsupported) >= 2


def test_quotes_are_one_exact_sentence_and_customer_access_is_safe():
    bank = json.loads((ROOT / "evaluation/natural2_20261031/bank.json").read_text(encoding="utf-8"))
    gold = json.loads((ROOT / "evaluation/natural2_20261031/gold_sources.json").read_text(encoding="utf-8"))
    docs = {doc["document_id"]: doc for doc in gold}
    for case in bank:
        assert case["rubric"].strip()
        for quote in case["required"]:
            assert quote["quote"] in docs[quote["document_id"]]["text"]
            assert len(builder.sentences(quote["quote"])) == 1
            if case["role"] == "customer":
                assert docs[quote["document_id"]]["audience"] == "customer"
    by_id = {case["id"]: case for case in bank}
    assert "hỏi lại giúp" not in by_id["N2-057"]["question"].casefold()


def test_each_numeric_sql_gold_matches_read_only_database():
    bank = json.loads((ROOT / "evaluation/natural2_20261031/bank.json").read_text(encoding="utf-8"))
    db = ROOT / "data/business_sql/scenario_v1/shop.sqlite"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        sql_cases = [case for case in bank if case.get("expected_sql")]
        assert len(sql_cases) >= 10
        for case in sql_cases:
            result = con.execute(case["expected_sql"]).fetchone()[0]
            expected = case["expected_values"][0]["value"]
            assert isinstance(expected, (int, float))
            assert result is not None
            assert round(float(result), 8) == round(float(expected), 8), case["id"]
    finally:
        con.close()


def test_natural_variants_and_metadata_are_recorded():
    bank = json.loads((ROOT / "evaluation/natural2_20261031/bank.json").read_text(encoding="utf-8"))
    no_marks = sum(not any(unicodedata.category(ch) == "Mn" for ch in unicodedata.normalize("NFD", c["question"])) for c in bank)
    long = sum(len(c["question"].split()) >= 20 for c in bank)
    assert no_marks >= 12
    assert long >= 12
    for group in {case["topic"] for case in bank}:
        group_cases = [case for case in bank if case["topic"] == group]
        assert any(not any(unicodedata.category(ch) == "Mn" for ch in unicodedata.normalize("NFD", c["question"])) for c in group_cases)
        assert any(re.search(r"\b(?:ko|k|dc|đc|bn|sp|bh|mk|mn|SDT)\b", c["question"], re.I) for c in group_cases)
        assert any(len(c["question"].split()) >= 20 for c in group_cases)
        assert sum(len(question_parts(c["question"])) >= 2 for c in group_cases) >= 2, group
    meta = json.loads((ROOT / "evaluation/natural2_20261031/metadata.json").read_text(encoding="utf-8"))
    assert meta["splits"] == {"development": 120}
    assert meta["calculation_cases"] >= 10
    manifest_path = ROOT / meta["knowledge_manifest"]
    assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == meta["knowledge_sha256"]
    assert hashlib.sha256((ROOT / meta["database"]).read_bytes()).hexdigest() == meta["database_sha256"]
    assert hashlib.sha256((ROOT / "evaluation/natural2_20261031/bank.json").read_bytes()).hexdigest() == meta["bank_sha256"]
    assert hashlib.sha256((ROOT / "evaluation/natural2_20261031/gold_sources.json").read_bytes()).hexdigest() == meta["gold_sha256"]
