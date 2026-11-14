import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "data" / "v8_router_questions" / "questions.json"
EXPECTED = {"policy": 90, "tech": 50, "report": 40, "internal": 40}


def normalize(text):
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def load_rows(path):
    return json.loads(path.read_text(encoding="utf-8"))


def question_strings(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"question", "text"} and isinstance(child, str):
                yield child
            yield from question_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from question_strings(child)


def has_vietnamese_diacritic(text):
    decomposed = unicodedata.normalize("NFD", text)
    return any(unicodedata.category(ch) == "Mn" for ch in decomposed)


def vietnamese_diacritic_words(text):
    words = re.findall(r"\w+", text, flags=re.UNICODE)
    return sum(has_vietnamese_diacritic(word) for word in words), len(words)


def has_enough_diacritic_words(text):
    accented, total = vietnamese_diacritic_words(text)
    return total > 0 and accented / total >= 0.25


def rows():
    return load_rows(QUESTIONS)


def test_group_counts_schema_and_roles():
    data = rows()
    assert len(data) == sum(EXPECTED.values())
    assert {group: sum(row["group"] == group for row in data) for group in EXPECTED} == EXPECTED
    assert all(set(row) == {"role", "label", "group", "question"} for row in data)
    assert all(row["role"] in {"customer", "admin"} for row in data)
    assert all(row["group"] in EXPECTED for row in data)
    assert all(row["label"] == ("private" if row["group"] == "internal" else "answer") for row in data)
    for row in data:
        if row["group"] == "report":
            assert row["role"] == "admin"
        elif row["group"] == "internal":
            assert row["role"] == "customer"
    for group in ("policy", "tech"):
        subset = [r for r in data if r["group"] == group]
        admin_share = sum(r["role"] == "admin" for r in subset) / len(subset)
        assert 0.08 <= admin_share <= 0.12
    assert all(isinstance(r["question"], str) and r["question"].strip() for r in data)


def test_questions_are_unique_and_not_in_v6_v7():
    data = rows()
    normalized = [normalize(row["question"]) for row in data]
    assert len(normalized) == len(set(normalized))
    for relative in ("data/v6_questions/questions.json", "data/v7_selector/questions.json"):
        old = load_rows(ROOT / relative)
        old_questions = {normalize(q) for q in question_strings(old)}
        assert not (set(normalized) & old_questions), relative


def test_accent_and_no_accent_balance():
    data = rows()
    assert sum(has_enough_diacritic_words(row["question"]) for row in data) >= 80
    for group in EXPECTED:
        subset = [r["question"] for r in data if r["group"] == group]
        plain = sum(not has_enough_diacritic_words(q) for q in subset) / len(subset)
        assert 0.20 <= plain <= 0.50, (group, plain)


def test_policy_contains_ambiguous_shop_terms():
    terms = ("giao", "ship", "tai khoan", "ngan hang", "vi", "no", "tra tien", "vay", "the")
    policy = [normalize(row["question"]) for row in rows() if row["group"] == "policy"]
    assert sum(any(term in question for term in terms) for question in policy) >= 40


def test_question_marks_only_terminate_questions_and_no_parentheses():
    for row in rows():
        question = row["question"]
        assert question.endswith("?"), question
        assert "?" not in question[:-1], question
        assert not re.search(r"\?\s*\S", question), question
        assert "(" not in question and ")" not in question, question


def test_questions_have_real_accented_words_and_letter_variety():
    data = rows()
    accented = 0
    letters = set()
    for row in data:
        question = row["question"]
        accented_words, total_words = vietnamese_diacritic_words(question)
        has_enough_accents = has_enough_diacritic_words(question)
        accented += has_enough_accents
        if has_enough_accents:
            letters.update(ch.lower() for ch in question if ch.lower() in "áàảãạăắằẳẵặâấầẩẫậđéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵ")
    assert accented >= 80
    assert len(letters) >= 30, sorted(letters)


def test_normalized_three_word_ending_is_not_overused():
    endings = []
    for row in rows():
        words = normalize(row["question"]).split()
        assert len(words) >= 3, row["question"]
        endings.append(" ".join(words[-3:]))
    assert max(endings.count(ending) for ending in set(endings)) <= 5
