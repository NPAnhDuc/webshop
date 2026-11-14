from datetime import date

import pytest

from shopbot import grounded_rag
from shopbot.rag_scope import resolve_scope


TODAY = date(2026, 10, 31)
PREVIOUS = {"months": ["2025-12"], "quarters": []}


@pytest.mark.parametrize("question", [
    "Còn giá vốn cùng tháng?",
    "Còn chi phí vận hành cùng tháng thì sao?",
    "con so don cung thang",
    "Cùng tháng đó lãi gộp bao nhiêu?",
])
def test_same_month_followup_carries_previous_month(question):
    assert resolve_scope(question, TODAY, PREVIOUS)["months"] == ["2025-12"]


@pytest.mark.parametrize("question", [
    "Doanh thu cùng tháng năm trước là bao nhiêu?",
    "So với cùng tháng năm ngoái thì sao?",
])
def test_same_month_year_comparison_does_not_carry_previous_month(question):
    assert resolve_scope(question, TODAY, PREVIOUS)["months"] == []


def test_explicit_month_wins_over_same_month_carry_forward():
    assert resolve_scope("Cùng tháng 8 năm 2025 thì sao?", TODAY, PREVIOUS)["months"] == ["2025-08"]


def test_same_month_without_previous_scope_stays_unbound():
    assert resolve_scope("Còn giá vốn cùng tháng?", TODAY, None)["months"] == []


def test_admin_followup_keeps_previous_month_in_grounded_rag_plan(monkeypatch):
    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}) and "parts" not in payload:
            return dict(action="answer", query="giá vốn", doc_types=["monthly_report"],
                        category="all", private_request=False, task="lookup", strict_filters=False)
        parts = list(payload["parts"])
        return dict(action="answer", answers={key: [] for key in parts},
                    missing=parts, negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr(grounded_rag, "search", lambda *args, **kwargs: [])
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    profile = {
        "rag_scope": PREVIOUS,
        "rag_metric_source": "document",
        "history": [{"role": "user", "content": "Tháng 12/2025"}],
    }

    result = grounded_rag.answer("Còn giá vốn cùng tháng?", "admin", profile, "unused", TODAY)

    assert result["plan"]["scope"]["months"] == ["2025-12"]
