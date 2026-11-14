import re
from datetime import date
from functools import lru_cache
from pathlib import Path

import pytest

from shopbot import grounded_rag
from shopbot.product_specs import LABELLED, asked_subject_fields, subject_field_labels
from shopbot.retrieval import normalize

AI_ROOT = Path(__file__).resolve().parents[1]
DB = AI_ROOT / "data/business_sql/scenario_v1/shop.sqlite"
CATALOG_ROOT = AI_ROOT / "data/unstructured/managed"
TODAY = date(2026, 10, 31)
FOLLOWUP_TRACE = "router overridden: follow-up names a field of the bound product"


@lru_cache(maxsize=1)
def latest_catalogs():
    latest = {}
    for path in CATALOG_ROOT.rglob("catalog-*-v*.md"):
        match = re.fullmatch(r"catalog-(.+)-v(\d+)\.md", path.name)
        if not match:
            continue
        catalog_id, version = match[1], int(match[2])
        if catalog_id not in latest or version > latest[catalog_id][0]:
            latest[catalog_id] = (version, path)
    return [path for _, path in latest.values()]


def catalog_title_labels(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    title = lines[0][2:] if lines and lines[0].startswith("# ") else ""
    labels = set()
    for line in lines:
        prefix = title + ": "
        if not title or not line.startswith(prefix):
            continue
        match = LABELLED.match(line[len(prefix):])
        if match:
            labels.add(normalize(match[1]))
    return title, frozenset(labels)


@lru_cache(maxsize=1)
def example_catalogs():
    ssd = graphics = None
    for path in latest_catalogs():
        title, labels = catalog_title_labels(path)
        if not title:
            continue
        if {"dung luong", "giao tiep"} <= labels:
            ssd = (title, labels)
        if {"gpu", "vram", "xung co ban"} <= labels:
            graphics = (title, labels)
        if ssd and graphics:
            break
    assert ssd is not None, "No latest SSD catalog with capacity and interface labels"
    assert graphics is not None, "No latest graphics catalog with GPU clock labels"
    return ssd, graphics


def run_with_router(monkeypatch, question, *, title, action, role="customer"):
    route_calls = []
    search_types = []

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}) and "parts" not in payload:
            route_calls.append(payload)
            return dict(action=action, query=question, doc_types=[], category="all",
                        private_request=False, task="lookup", strict_filters=False)
        parts = list(payload["parts"])
        return dict(action="answer", answers={key: [] for key in parts},
                    missing=parts, negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    def search(*args, **kwargs):
        search_types.append(kwargs.get("doc_types"))
        return []

    monkeypatch.setattr(grounded_rag, "search", search)
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    profile = {
        "rag_product_subject": title,
        "history": [{"role": "user", "content": f"Thông tin về {title}"}],
    }
    result = grounded_rag.answer(question, role, profile, DB, TODAY)
    return result, route_calls, search_types


def test_subject_field_labels_use_latest_ssd_and_graphics_catalogs():
    (ssd_title, ssd_expected), (graphics_title, graphics_expected) = example_catalogs()

    assert subject_field_labels(ssd_title) == ssd_expected
    assert subject_field_labels(graphics_title) == graphics_expected
    assert subject_field_labels("A title absent from the catalogs") == frozenset()


@pytest.mark.parametrize("field_index,action", [
    (0, "outside"), (1, "clarify"), (2, "outside"),
    (3, "clarify"), (4, "outside"), (5, "clarify"),
])
@pytest.mark.parametrize("role", ["customer", "admin"])
def test_followup_field_overrides_outside_and_clarify(monkeypatch, field_index, action, role):
    (ssd_title, _), (graphics_title, _) = example_catalogs()
    cases = [
        (ssd_title, "Dung lượng thì sao?"),
        (ssd_title, "Giao tiếp thì sao bạn?"),
        (ssd_title, "Kích thước/chuẩn thiết kế thì sao?"),
        (graphics_title, "Xung cơ bản thì sao bạn?"),
        (graphics_title, "VRAM thì sao?"),
        (graphics_title, "con xung co ban thi sao"),
    ]
    title, question = cases[field_index]
    assert asked_subject_fields(question, title)

    result, route_calls, search_types = run_with_router(
        monkeypatch, question, title=title, action=action, role=role,
    )

    assert len(route_calls) == 1
    assert FOLLOWUP_TRACE in result["trace"]
    assert result["basic_action"] == "answer"
    assert search_types and search_types[0] == ["product"]


def test_no_bound_subject_keeps_router_action(monkeypatch):
    question = "Giao tiếp thì sao bạn?"
    route = {"action": "outside", "query": question, "doc_types": [], "category": "all",
             "private_request": False, "task": "lookup", "strict_filters": False}

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}) and "parts" not in payload:
            return route
        pytest.fail("Selector should not run after an unchanged outside action")

    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    result = grounded_rag.answer(question, "customer", {}, DB, TODAY)

    assert result["basic_action"] == "outside"
    assert FOLLOWUP_TRACE not in result["trace"]


def test_field_not_present_on_bound_ssd_keeps_clarify(monkeypatch):
    (ssd_title, _), _ = example_catalogs()
    result, route_calls, _ = run_with_router(
        monkeypatch, "Xung cơ bản thì sao?", title=ssd_title, action="clarify",
    )

    assert len(route_calls) == 1
    assert result["basic_action"] == "clarify"
    assert FOLLOWUP_TRACE not in result["trace"]


def test_real_outside_question_keeps_outside_with_bound_product(monkeypatch):
    (ssd_title, _), _ = example_catalogs()
    result, route_calls, _ = run_with_router(
        monkeypatch, "Thời tiết mai thì sao?", title=ssd_title, action="outside",
    )

    assert len(route_calls) == 1
    assert result["basic_action"] == "outside"
    assert FOLLOWUP_TRACE not in result["trace"]


@pytest.mark.parametrize("action", ["answer", "deferred", "live_product"])
def test_other_router_actions_stay_unchanged_for_a_bound_field(monkeypatch, action):
    (ssd_title, _), _ = example_catalogs()
    result, route_calls, _ = run_with_router(
        monkeypatch, "Giao tiếp thì sao bạn?", title=ssd_title, action=action,
    )

    assert len(route_calls) == 1
    assert result["basic_action"] == action
    assert FOLLOWUP_TRACE not in result["trace"]
