import json
import unicodedata
from collections import Counter
from pathlib import Path

DATA = Path(__file__).parents[1] / "data" / "v6_questions" / "questions.json"
EXPECTED = {
    "education": 40, "coding": 40, "abuse": 25, "money_health_law": 30,
    "other_services": 30, "life_creative": 25, "control": 60, "pointing": 20,
}
OUTSIDE = {"education", "coding", "abuse", "money_health_law", "other_services", "life_creative"}


def load_questions():
    return json.loads(DATA.read_text(encoding="utf-8"))


def strip_accents(value):
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    return value.replace("đ", "d").replace("Đ", "D")


def normalize_question(value):
    return " ".join(strip_accents(value).casefold().split())


def has_diacritic(value):
    return any(unicodedata.category(ch) == "Mn" or ch in "đĐ"
               for ch in unicodedata.normalize("NFD", value))


def is_unaccented(value):
    return value == strip_accents(value)


def test_schema_and_exact_group_counts():
    questions = load_questions()
    assert len(questions) == 270
    assert all(set(item) == {"role", "label", "group", "question"} for item in questions)
    assert all(item["role"] in {"customer", "admin"} for item in questions)
    assert all(isinstance(item["question"], str) and item["question"].strip() for item in questions)
    assert Counter(item["group"] for item in questions) == Counter(EXPECTED)
    for item in questions:
        if item["group"] in OUTSIDE:
            assert item["label"] == "outside"
        elif item["group"] == "control":
            assert item["label"] == "answer"
        else:
            assert item["group"] == "pointing"
            assert item["label"] == "clarify"


def test_admin_share_is_about_ten_percent_in_each_group():
    questions = load_questions()
    for group, total in EXPECTED.items():
        group_items = [item for item in questions if item["group"] == group]
        admins = sum(item["role"] == "admin" for item in group_items)
        assert 0.08 <= admins / total <= 0.15


def test_each_group_has_varied_accented_and_unaccented_questions():
    questions = load_questions()
    for group, total in EXPECTED.items():
        group_items = [item for item in questions if item["group"] == group]
        plain = sum(is_unaccented(item["question"]) for item in group_items)
        assert 0.20 <= plain / total <= 0.50
    assert sum(has_diacritic(item["question"]) for item in questions) >= 50


def test_questions_are_unique_after_accent_and_spacing_normalization():
    questions = load_questions()
    normalized = [normalize_question(item["question"]) for item in questions]
    assert len(normalized) == len(set(normalized))


def test_pointing_group_asks_for_missing_device_context():
    pointing = [item for item in load_questions() if item["group"] == "pointing"]
    assert len(pointing) == 20
    assert all(item["label"] == "clarify" for item in pointing)
