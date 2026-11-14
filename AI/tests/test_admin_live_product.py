from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)
TRACE = "router live_product overridden: admin requests go to deferred"
LIVE_QUESTIONS = [
    "Đổi giá chuột cho khách giúp tôi.",
    "khoa gia mau chuot nay o muc 450 nghin",
    "Giữ hàng cho khách đến chiều nay.",
    "Giá hôm nay của mẫu chuột này là bao nhiêu?",
    "Mẫu chuột này còn hàng không?",
]


def run_with_router(monkeypatch, question, *, role="admin", action="live_product"):
    route = {
        "action": action,
        "query": question,
        "doc_types": ["product"],
        "category": "all",
        "private_request": False,
        "task": "lookup",
        "strict_filters": False,
    }
    route_calls = []

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}) and "parts" not in payload:
            route_calls.append(payload)
            return route
        parts = list(payload["parts"])
        return dict(action="answer", answers={key: [] for key in parts},
                    missing=parts, negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr(grounded_rag, "search", lambda *args, **kwargs: [])
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    result = grounded_rag.answer(question, role, {}, DB, TODAY)
    return result, route_calls


@pytest.mark.parametrize("question", LIVE_QUESTIONS)
def test_admin_live_product_route_becomes_deferred(monkeypatch, question):
    result, route_calls = run_with_router(monkeypatch, question, role="admin")

    assert len(route_calls) == 1
    assert result["basic_action"] == "deferred"
    assert result["answer"].startswith("Yêu cầu này cần công cụ ngoài RAG cơ bản")
    assert TRACE in result["trace"]


@pytest.mark.parametrize("question", LIVE_QUESTIONS)
def test_customer_live_product_route_stays_unchanged(monkeypatch, question):
    result, route_calls = run_with_router(monkeypatch, question, role="customer")

    assert len(route_calls) == 1
    assert result["basic_action"] == "live_product"
    assert TRACE not in result["trace"]


@pytest.mark.parametrize("action", ["answer", "deferred", "outside"])
def test_other_admin_router_actions_stay_unchanged(monkeypatch, action):
    result, route_calls = run_with_router(
        monkeypatch, "Mẫu chuột này màu tím có không?", role="admin", action=action,
    )

    assert len(route_calls) == 1
    assert result["basic_action"] == action
    assert TRACE not in result["trace"]
