from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)
TOP = "Alpha policy is the top-ranked statement."
SECOND = "Beta policy is the second-ranked statement."
SELECTED = "Gamma policy is the selector's original answer."
FOURTH = "Delta policy is another original selector choice."
TRACE = "evidence: reranker top fragment added to selector picks"


class RerankResponse:
    def __init__(self, scores):
        self.scores = scores

    def raise_for_status(self):
        return None

    def json(self):
        return {"scores": self.scores}


def policy_doc(sentences):
    title = "Synthetic policy"
    return dict(
        document_id="policy-rerank-test",
        source="policy-rerank-test.md",
        version=1,
        section=1,
        chunk_id="policy-rerank-chunk",
        title=title,
        heading_path=title,
        doc_type="policy",
        audience="customer",
        authority="shop_document",
        text=title + "\n\n" + "\n\n".join(sentences),
    )


def run_case(monkeypatch, question, *, scores, selected, missing=(), rerank=True, docs=None):
    documents = docs or [policy_doc([TOP, SECOND, SELECTED, FOURTH])]
    selector_payloads = []
    selector_outputs = []
    rerank_requests = []

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}) and "parts" not in payload:
            return dict(action="answer", query=question, doc_types=[documents[0]["doc_type"]],
                        strict_filters=False, task="lookup", private_request=False)
        selector_payloads.append(payload)
        by_text = {fragment["text"]: fragment["id"] for fragment in payload["fragments"]}
        answers = {
            part: [by_text[text] for text in (value if isinstance(value, list) else [value]) if text]
            for part, value in selected.items()
        }
        output = dict(action="answer", answers=answers, missing=list(missing), negative=[])
        selector_outputs.append(output)
        return output

    def search(*args, **kwargs):
        return [dict(document) for document in documents]

    def post(url, *, json, timeout):
        texts = list(json["texts"])
        rerank_requests.append(texts)
        return RerankResponse([scores[text] for text in texts])

    monkeypatch.setenv("RAG_EVIDENCE_RERANK", "1" if rerank else "0")
    monkeypatch.setenv("VI_EMBEDDING_URL", "http://reranker.test")
    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr(grounded_rag, "search", search)
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    monkeypatch.setattr("requests.post", post)
    result = grounded_rag.answer(question, "customer", {}, DB, TODAY)
    return result, selector_payloads, selector_outputs, rerank_requests


def fragment_id(payload, text):
    return next(fragment["id"] for fragment in payload["fragments"] if fragment["text"] == text)


def scores_for(top=2.0, second=-2.0, selected=-5.0):
    return {TOP: top, SECOND: second, SELECTED: selected, FOURTH: -6.0}


def test_top_fragment_is_appended_after_selector_pick_and_raw_stays_original(monkeypatch):
    result, payloads, selector_outputs, _ = run_case(
        monkeypatch, "Tóm tắt quy định liên quan.", scores=scores_for(), selected={"P1": SELECTED},
    )
    original_id = fragment_id(payloads[0], SELECTED)
    top_id = fragment_id(payloads[0], TOP)

    assert result["rag"]["part_evidence"] == {"P1": [original_id, top_id]}
    assert result["answer"].index(SELECTED) < result["answer"].index(TOP)
    assert TRACE in result["trace"]
    assert result["rag"]["selector_raw"] == dict(
        answers=selector_outputs[0]["answers"], missing=selector_outputs[0]["missing"],
        negative=selector_outputs[0]["negative"],
    )
    assert result["rag"]["selector_raw"]["answers"] == {"P1": [original_id]}


def test_top_fragment_fills_first_empty_part_and_clears_missing(monkeypatch):
    question = "Mục alpha thế nào, mục beta thế nào?"
    result, payloads, selector_outputs, _ = run_case(
        monkeypatch, question, scores=scores_for(),
        selected={"P1": SELECTED, "P2": ""}, missing=["P2"],
    )
    original_id = fragment_id(payloads[0], SELECTED)
    top_id = fragment_id(payloads[0], TOP)

    assert result["rag"]["part_evidence"] == {"P1": [original_id], "P2": [top_id]}
    assert result["rag"]["unanswered"] == []
    assert result["rag"]["selector_raw"]["answers"] == {"P1": [original_id], "P2": []}
    assert result["rag"]["selector_raw"]["missing"] == selector_outputs[0]["missing"] == ["P2"]
    assert TRACE in result["trace"]


def test_top_fragment_is_appended_even_after_three_existing_choices(monkeypatch):
    result, payloads, _, _ = run_case(
        monkeypatch, "Tóm tắt quy định liên quan.", scores=scores_for(),
        selected={"P1": [SECOND, SELECTED, FOURTH]},
    )
    chosen_ids = [fragment_id(payloads[0], text) for text in (SECOND, SELECTED, FOURTH, TOP)]

    assert result["rag"]["part_evidence"] == {"P1": chosen_ids}
    assert TRACE in result["trace"]


@pytest.mark.parametrize("score_map,selected", [
    (scores_for(), {"P1": TOP}),
    (scores_for(top=-0.5, second=-2.0), {"P1": SELECTED}),
    (scores_for(top=2.0, second=-0.9), {"P1": SELECTED}),
    (scores_for(), {"P1": ""}),
])
def test_selector_or_score_threshold_controls_leave_selection_unchanged(monkeypatch, score_map, selected):
    result, payloads, selector_outputs, _ = run_case(
        monkeypatch, "Tóm tắt quy định liên quan.", scores=score_map,
        selected=selected, missing=["P1"] if not selected["P1"] else [],
    )

    assert TRACE not in result["trace"]
    assert result["rag"]["part_evidence"] == selector_outputs[0]["answers"]
    assert result["rag"]["selector_raw"]["answers"] == selector_outputs[0]["answers"]
    assert payloads


def test_disabled_reranker_leaves_selection_unchanged(monkeypatch):
    result, payloads, selector_outputs, rerank_requests = run_case(
        monkeypatch, "Tóm tắt quy định liên quan.", scores=scores_for(),
        selected={"P1": SELECTED}, rerank=False,
    )

    assert rerank_requests == []
    assert payloads
    assert TRACE not in result["trace"]
    assert result["rag"]["part_evidence"] == selector_outputs[0]["answers"]


def test_catalog_label_pick_is_not_modified_by_reranker_top(monkeypatch):
    title = "Laptop A1"
    ram = f"{title}: RAM: 16 GB."
    gpu = f"{title}: GPU: RTX 4050."
    document = dict(
        document_id="product-a1",
        source="catalog-a1-v1.md",
        version=1,
        section=1,
        chunk_id="product-a1-chunk",
        title=title,
        heading_path=title,
        doc_type="product",
        audience="customer",
        authority="shop_document",
        retrieval="explicit named product",
        text=title + "\n\n" + ram + "\n\n" + gpu,
    )
    result, payloads, _, requests = run_case(
        monkeypatch, f"{title} RAM bao nhiêu?", scores={"RAM: 16 GB.": -2.0, "GPU: RTX 4050.": 2.0},
        selected={}, docs=[document],
    )

    assert requests
    assert payloads == []  # Labelled catalog lookup bypasses the selector.
    assert "evidence: catalog fields picked by label (no model selection)" in result["trace"]
    assert TRACE not in result["trace"]
    assert ram in result["answer"]
    assert gpu not in result["answer"]
