import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/unstructured/managed/e397df083984c120/manifest.json"
QUESTIONS = ROOT / "data/v7_selector/questions.json"


def normalized(text):
    text = unicodedata.normalize("NFD", text.casefold().replace("\u0111", "d"))
    return " ".join("".join(c for c in text if unicodedata.category(c) != "Mn").split())


def load_data():
    documents = {}
    for doc in json.loads(MANIFEST.read_text(encoding="utf-8")):
        key = doc["document_id"]
        if key not in documents or doc["version"] > documents[key]["version"]:
            documents[key] = doc
    return json.loads(QUESTIONS.read_text(encoding="utf-8")), documents


def quantities(text):
    return set(re.findall(r"\d+(?:[.,]\d+)*", text))


def test_counts_schema_and_normalized_uniqueness():
    rows, _ = load_data()
    assert Counter(row["kind"] for row in rows) == {"thieu": 150, "doi_chung": 80}
    assert [row["id"] for row in rows] == [f"S7-{i:03d}" for i in range(1, 231)]
    assert len({normalized(row["question"]) for row in rows}) == 230
    fields = {"id", "kind", "role", "question", "catalog_document_id", "tech_document_id", "quote"}
    for row in rows:
        expected_fields = fields | ({"units"} if row["kind"] == "thieu" else set())
        assert set(row) == expected_fields
        assert row["role"] in {"customer", "admin"}
        assert row["question"].strip() == row["question"] and len(row["question"]) >= 20
        assert row["quote"].strip()


def test_references_are_approved_catalog_and_technical_sources():
    rows, docs = load_data()
    for row in rows:
        catalog = docs[row["catalog_document_id"]]
        assert catalog["document_id"].startswith("catalog-")
        assert catalog["doc_type"] == "product"
        assert catalog["status"] == "approved"
        assert normalized(catalog["title"]) in normalized(row["question"])
        if row["kind"] == "thieu":
            tech = docs[row["tech_document_id"]]
            assert tech["document_id"].startswith("tech-")
            assert tech["doc_type"] in {"glossary", "buying_guide"}
            assert tech["status"] == "approved"
        else:
            assert row["tech_document_id"] is None


def test_quotes_are_verbatim_and_missing_labels_have_distinct_evidence():
    rows, docs = load_data()
    for row in rows:
        catalog = docs[row["catalog_document_id"]]
        source = docs[row["tech_document_id"]] if row["kind"] == "thieu" else catalog
        assert row["quote"] in source["text"], row["id"]
        if row["kind"] == "thieu":
            assert row["quote"] not in catalog["text"], row["id"]
            numbers = quantities(row["quote"])
            if numbers:
                assert not numbers <= quantities(catalog["text"]), row["id"]


def test_every_technical_article_has_two_to_six_examples():
    rows, docs = load_data()
    counts = Counter(row["tech_document_id"] for row in rows if row["kind"] == "thieu")
    expected = {key for key, doc in docs.items()
                if key.startswith("tech-") and doc["doc_type"] in {"glossary", "buying_guide"}}
    assert set(counts) == expected
    assert len(expected) == 39
    assert all(2 <= count <= 6 for count in counts.values())


def test_control_categories_and_role_balance():
    rows, docs = load_data()
    categories = Counter(docs[row["catalog_document_id"]]["category"]
                         for row in rows if row["kind"] == "doi_chung")
    assert len(categories) == 10
    assert set(categories.values()) == {8}
    assert Counter(row["role"] for row in rows if row["kind"] == "thieu") == {
        "customer": 127, "admin": 23,
    }


def test_language_distribution_and_light_typo_examples():
    rows, _ = load_data()
    # Product names may retain \u00d7 or other symbols; use accent folding as well.
    unaccented = sum(
        unicodedata.normalize("NFC", row["question"].casefold()).replace("\u0111", "d")
        == unicodedata.normalize("NFC", normalized(row["question"]))
        for row in rows
    )
    assert unaccented == 46
    typo = re.compile(r"\b(?:kh\u00f4gn|th\u00f4gn|tr\u01b0\u1edbv|\u0111\u01b0\u1ecdc|c\u1ea7nn|thoe|m\u00echn|cu\u1ea3|t\u00f4ii|cso|v\u00f3i|nh\u01b0w|\u0111\u1ec5|gfi|\u01a1ii)\b", re.I)
    assert sum(bool(typo.search(row["question"])) for row in rows) == 11


# Snapshot from task 54 before any 54b question edits.
TASK_54_FIXED_FIELDS_SHA256 = "8c58f22125bb5b1ff15bf73f285a9bdaeca8138e12d9822a7377620f28c216ea"


def word_tokens(text):
    return re.findall(r"\w+", normalized(text))


def test_questions_do_not_name_sources_or_data_fields():
    rows, _ = load_data()
    forbidden = re.compile(
        r"\b(catalog|danh muc|ban ghi|bai ky thuat|bai viet|tai lieu|nguon|trich|truong|psref)\b"
    )
    field_label = re.compile(r"\bmuc (?:so nhan|dung luong|toc do|ram|cpu|tdp|cong suat)\b")
    violations = [row["id"] for row in rows
                  if forbidden.search(normalized(row["question"]))
                  or field_label.search(normalized(row["question"]))]
    assert not violations, violations


def test_questions_do_not_copy_five_word_spans_from_their_quote():
    rows, docs = load_data()
    overlaps = []
    for row in rows:
        title = normalized(docs[row["catalog_document_id"]]["title"])
        question = normalized(row["question"]).replace(title, " ")
        quote = normalized(row["quote"]).replace(title, " ")
        question_tokens = word_tokens(question)
        quote_tokens = word_tokens(quote)
        spans = {tuple(question_tokens[i:i + 5]) for i in range(len(question_tokens) - 4)}
        shared = spans & {tuple(quote_tokens[i:i + 5]) for i in range(len(quote_tokens) - 4)}
        if shared:
            overlaps.append((row["id"], sorted(shared)))
    assert not overlaps, overlaps


def test_every_question_has_one_part():
    from shopbot.grounded_rag import question_parts

    rows, _ = load_data()
    split = [(row["id"], question_parts(row["question"])) for row in rows
             if len(question_parts(row["question"])) != 1]
    assert not split, split


def test_fields_other_than_question_match_task_54_snapshot():
    import hashlib

    rows, _ = load_data()
    fixed = [{key: value for key, value in row.items() if key not in {"question", "units"}} for row in rows]
    encoded = json.dumps(fixed, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    assert hashlib.sha256(encoded).hexdigest() == TASK_54_FIXED_FIELDS_SHA256


def test_literal_question_frames_do_not_repeat_more_than_three_times():
    rows, docs = load_data()
    frames = Counter(
        normalized(row["question"]).replace(normalized(docs[row["catalog_document_id"]]["title"]), "{product}")
        for row in rows
    )
    assert all(count <= 3 for count in frames.values()), frames.most_common(5)
