from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


def run_offline(monkeypatch, question, *, strict=False, complete_catalog=False):
    searches, selections = [], []
    real_search = grounded_rag.search

    def search(*args, **kwargs):
        docs = real_search(*args, **kwargs)
        searches.append(docs)
        return docs

    def chat(system, payload, schema, **kwargs):
        if "parts" not in payload:
            return dict(action="answer", query=question, doc_types=["product"],
                        strict_filters=strict, task="lookup", private_request=False)
        selections.append(payload)
        parts = list(payload["parts"])
        chosen = [payload["fragments"][0]["id"]] if complete_catalog and payload["fragments"] else []
        return dict(action="answer", answers={key: chosen for key in parts},
                    missing=[] if chosen else parts, negative=[])

    monkeypatch.setenv("VI_EMBEDDING_URL", "")
    monkeypatch.setenv("RAG_RERANK", "0")
    monkeypatch.setenv("RAG_EVIDENCE_RERANK", "0")
    monkeypatch.setattr(grounded_rag, "search", search)
    monkeypatch.setattr(grounded_rag, "chat", chat)
    result = grounded_rag.answer(question, "customer", {}, DB, TODAY)
    return result, searches, selections


def ids(docs):
    return {doc["document_id"] for doc in docs}


def test_bound_product_keeps_catalog_and_technical_usage_article(monkeypatch):
    _, searches, selections = run_offline(
        monkeypatch, "Legion Slim 5 16IRH8 ho tro nang cap bo nho theo tai lieu nao?")
    assert len(searches) == 2
    assert any(doc.get("retrieval") == "explicit named product" for doc in searches[0])
    assert "tech-legion-family" in ids(searches[1])
    assert len(selections) == 2
    assert any("16IRH8" in source["title"] and "Legion" in source["title"]
               for source in selections[-1]["sources"])
    assert len(selections[-1]["sources"]) > len(selections[0]["sources"])


def test_price_and_stock_still_return_direct_sql_without_search(monkeypatch):
    result, searches, selections = run_offline(
        monkeypatch, "Kingston NV2 gia bao nhieu va ton kho bao nhieu?")
    assert result["basic_action"] == "live_product"
    assert result["rag"]["method"] == "deterministic catalog lookup"
    assert searches == selections == []


def test_unbound_question_keeps_existing_search_without_catalog_isolation(monkeypatch):
    result, searches, selections = run_offline(monkeypatch, "SO-DIMM dung de lam gi?")
    assert searches and selections
    assert not any(doc.get("retrieval") == "explicit named product"
                   for docs in searches for doc in docs)
    assert "evidence: isolated to bound product records" not in result["trace"]
    assert len(selections) == 1


def test_strict_model_type_choice_disables_technical_expansion(monkeypatch):
    _, searches, _ = run_offline(
        monkeypatch, "Legion Slim 5 16IRH8 ho tro nang cap bo nho theo tai lieu nao?", strict=True)
    assert len(searches) == 1
    assert {doc["doc_type"] for doc in searches[0]} == {"product"}


def test_model_accepting_catalog_prevents_article_selector_pass(monkeypatch):
    result, searches, selections = run_offline(
        monkeypatch, "Legion Slim 5 16IRH8 ho tro nang cap bo nho theo tai lieu nao?", complete_catalog=True)
    assert "tech-legion-family" in ids(searches[1])
    assert len(selections) == 1
    assert "evidence: catalog answered, model articles not offered" in result["trace"]
