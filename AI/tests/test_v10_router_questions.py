import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/v10_router/questions.json"
BUSINESS = ROOT / "data/business_sql/scenario_v1/documents"
POLICY = ROOT / "data/unstructured/managed/e397df083984c120"


def norm(text):
    text = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())


def questions():
    return json.loads(DATA.read_text(encoding="utf-8"))


def tokens(text):
    return set(norm(text).split())


def jaccard(left, right):
    a, b = tokens(left), tokens(right)
    return len(a & b) / len(a | b) if a | b else 1


def source_path(row):
    return (POLICY if row["document_id"].startswith("policy-") else BUSINESS) / row["document_id"]


def bot_units(row):
    from shopbot.chunking import chunk_document
    from shopbot.rag_answer import evidence_fragments

    filename = row["document_id"]
    doc = {"text": source_path(row).read_text(encoding="utf-8"), "source": filename,
           "title": filename, "document_id": filename}
    fragments = evidence_fragments(chunk_document(doc))
    units = set()
    for fragment in fragments.values():
        quotes = fragment["quotes"]
        units.add(quotes[-1] if quotes[0].startswith("|") else quotes[0])
    return units


def test_schema_group_counts_ids_and_labels():
    data = questions()
    assert len(data) == 160
    assert [r["id"] for r in data] == [f"R10-{i:03d}" for i in range(1, 161)]
    assert Counter(r["group"] for r in data) == {
        "doc_san": 60, "ky_chua_co": 30, "tinh_that": 30, "khach_noi_chon": 40,
    }
    for row in data:
        assert row["label"] == ("deferred" if row["group"] == "tinh_that" else "answer")
        assert row["role"] == ("customer" if row["group"] == "khach_noi_chon" else "admin")
        required = {"id", "role", "group", "label", "question", "document_id", "quote"}
        if row["group"] == "ky_chua_co":
            required.add("doc_type")
        if row["group"] == "khach_noi_chon":
            required.update(("place", "topic"))
        assert set(row) == required
        assert len(row["question"].strip()) >= 20
    normalized = [norm(r["question"]) for r in data]
    assert len(set(normalized)) == 160


def test_sources_and_verbatim_bot_quote_units():
    data = questions()
    for row in data:
        if row["group"] in {"ky_chua_co", "tinh_that"}:
            assert row["document_id"] is row["quote"] is None
            continue
        if row["quote"] is not None:
            assert row["quote"] in bot_units(row), row["id"]
    docs = [r for r in data if r["group"] == "doc_san"]
    counts = Counter()
    for row in docs:
        name = row["document_id"]
        assert "-draft" not in name
        if name.startswith("sales-plan-"):
            counts["plan"] += 1
        elif name.startswith("monthly-report-"):
            counts["report"] += 1
        else:
            counts["policy"] += 1
        assert source_path(row).is_file()
    assert counts["plan"] >= 20 and counts["report"] >= 20 and counts["policy"] >= 10


def test_doc_san_has_bounded_contrast_triggers():
    triggers = ["tinh", "lay", "tra", "keo", "rut", "check", "xem giup", "cho so",
                "sau hoan tra", "chua vat", "sau giam", "toi thieu", "phai duyet", "chot"]
    counts = Counter()
    for row in questions():
        if row["group"] != "doc_san":
            continue
        q = norm(row["question"])
        hits = [term for term in triggers if re.search(rf"\b{re.escape(term)}\b", q)]
        assert hits, row["id"]
        counts.update(hits)
    assert all(count <= 8 for count in counts.values())


def test_missing_periods_are_absent_and_balanced():
    missing = [r for r in questions() if r["group"] == "ky_chua_co"]
    assert Counter(r["doc_type"] for r in missing) == {"sales_plan": 15, "monthly_report": 15}
    periods = set()
    for row in missing:
        q = norm(row["question"])
        assert not any(term in q for term in ("du bao", "uoc tinh", "du doan"))
        if row["doc_type"] == "sales_plan":
            match = re.search(r"\b(?:(20\d{2})\s*[-/]?\s*q([1-4])|(?:q|quy|ky)\s*([1-4])\s*[/ -]\s*(20\d{2}))\b", q)
            assert match, row["id"]
            year, quarter = ((int(match.group(1)), int(match.group(2))) if match.group(1)
                             else (int(match.group(4)), int(match.group(3))))
            period = f"{year}-Q{quarter}"
            assert not (year == 2025 and quarter >= 4 or year == 2026 and quarter <= 3)
            filename = f"sales-plan-{period}-v1.md"
        else:
            match = re.search(r"\b(?:(20\d{2})\s+(0?[1-9]|1[0-2])|(0?[1-9]|1[0-2])\s+(20\d{2})|(?:thang|ky)\s+(0?[1-9]|1[0-2])\s+(20\d{2}))\b", q)
            assert match, row["id"]
            if match.group(1):
                year, month = int(match.group(1)), int(match.group(2))
            elif match.group(4):
                month, year = int(match.group(3)), int(match.group(4))
            else:
                year, month = int(match.group(6)), int(match.group(5))
            period = f"{year}-{month:02d}"
            assert not (year == 2025 and month >= 10 or year == 2026 and month <= 9)
            filename = f"monthly-report-{period}-v1.md"
        periods.add((row["doc_type"], period))
        assert not (BUSINESS / filename).exists()
    assert len(periods) >= 10


def test_customer_places_topics_and_quotes():
    rows = [r for r in questions() if r["group"] == "khach_noi_chon"]
    places = Counter(r["place"] for r in rows)
    topics = Counter(r["topic"] for r in rows)
    assert len(places) >= 12 and max(places.values()) <= 5
    assert topics["giao_hang"] >= 15 and topics["doi_tra"] >= 8
    assert topics["bao_hanh"] >= 8 and topics["tra_gop"] + topics["thanh_toan"] >= 5
    assert sum(r["quote"] is not None for r in rows) >= 25
    assert all(r["document_id"].startswith("policy-") for r in rows)


def test_question_similarity_templates_and_old_sets():
    data = questions()
    for i, row in enumerate(data):
        first_five = " ".join(norm(row["question"]).split()[:5])
        assert sum(first_five == " ".join(norm(other["question"]).split()[:5])
                   for other in data) <= 4
        for other in data[i + 1:]:
            assert jaccard(row["question"], other["question"]) < 0.7, (row["id"], other["id"])
    for dirname in ("v6_questions", "v7_selector", "v8_router_questions", "v9_selector"):
        old_path = ROOT / "data" / dirname / "questions.json"
        old = json.loads(old_path.read_text(encoding="utf-8"))
        for row in data:
            for other in old:
                assert jaccard(row["question"], other["question"]) < 0.7, (
                    dirname, row["id"], other.get("id"))


def test_vi_text_checker_is_clean():
    from scripts.check_vi_text import find_issues

    text = DATA.read_text(encoding="utf-8")
    assert not find_issues(text)
