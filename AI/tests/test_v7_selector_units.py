import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/unstructured/managed/e397df083984c120/manifest.json"
QUESTIONS = ROOT / "data/v7_selector/questions.json"


def load_data():
    docs = {}
    for doc in json.loads(MANIFEST.read_text(encoding="utf-8")):
        previous = docs.get(doc["document_id"])
        if previous is None or doc["version"] > previous["version"]:
            docs[doc["document_id"]] = doc
    return json.loads(QUESTIONS.read_text(encoding="utf-8")), docs


def compact(text):
    return " ".join(text.split())


def overlaps_quote(quote, unit):
    quote = compact(quote)
    unit = compact(unit)
    if unit in quote:
        return True
    return any(quote[start:start + 30] in unit for start in range(max(0, len(quote) - 29)))


def bot_units(doc):
    from shopbot.chunking import chunk_document
    from shopbot.rag_answer import evidence_fragments

    chunks = chunk_document(dict(
        text=doc["text"],
        source=doc.get("source", doc["document_id"]),
        title=doc.get("title", doc["document_id"]),
        document_id=doc["document_id"],
    ))
    units = set()
    for fragment in evidence_fragments(chunks).values():
        quotes = fragment["quotes"]
        units.add(quotes[-1] if quotes[0].startswith("|") else quotes[0])
    return units


def test_units_schema_and_controls_unchanged():
    rows, _ = load_data()
    for row in rows:
        if row["kind"] == "thieu":
            assert isinstance(row.get("units"), list), row["id"]
            assert len(row["units"]) <= 2, row["id"]
        else:
            assert "units" not in row, row["id"]


def test_units_are_real_bot_fragments_overlapping_the_quote():
    rows, docs = load_data()
    cache = {}
    for row in rows:
        if row["kind"] != "thieu":
            continue
        document = docs[row["tech_document_id"]]
        units = cache.setdefault(row["tech_document_id"], bot_units(document))
        for unit in row["units"]:
            assert unit in units, row["id"]
            assert overlaps_quote(row["quote"], unit), row["id"]


def test_at_most_five_missing_unit_labels():
    rows, _ = load_data()
    empty = [row["id"] for row in rows if row["kind"] == "thieu" and not row["units"]]
    assert len(empty) <= 5, empty


def test_v7_question_file_passes_vietnamese_text_guard():
    from scripts.check_vi_text import check_file

    assert not check_file(QUESTIONS)
