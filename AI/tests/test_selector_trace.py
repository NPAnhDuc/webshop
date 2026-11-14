from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag
from shopbot.rag_scope import resolve_scope

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)
QUESTION = "Chuột được bảo hành bao lâu?"
TARGET = "Vỏ case và chuột được bảo hành 12 tháng tại TechStore."
EXPECTED_ANSWER = (
    "Vỏ case và chuột được bảo hành 12 tháng tại TechStore.\n\n"
    "[Nguồn: policy-warranty-v1.md, mục Chính sách bảo hành TechStore, "
    "đoạn 1, phiên bản 1]"
)
EXPECTED_SOURCES = [("policy-warranty", "policy-warranty-v1.md")]
EXPECTED_PART_EVIDENCE = {"P1": ["policy_1"]}


class RerankResponse:
    def __init__(self, scores):
        self.scores = scores

    def raise_for_status(self):
        return None

    def json(self):
        return {"scores": self.scores}


def run_case(monkeypatch, docs, *, rerank):
    sent_payloads = []
    selector_outputs = []
    rerank_requests = []

    def chat(system, payload, schema, **kwargs):
        if "action" in schema.get("properties", {}) and "parts" not in payload:
            return dict(action="answer", query=QUESTION, doc_types=["policy"],
                        strict_filters=False, task="lookup", private_request=False)
        sent_payloads.append(payload)
        matches = [item for item in payload["fragments"] if TARGET in item["text"]]
        assert len(matches) == 1
        answer = dict(action="answer", answers={key: [matches[0]["id"]]
                                                  for key in payload["parts"]},
                       missing=[], negative=[])
        selector_outputs.append(answer)
        return answer

    def post(url, *, json, timeout):
        texts = json["texts"]
        rerank_requests.append(list(texts))
        # Preserve the original candidate order. Scores stay unique so the test
        # also verifies that each stored score belongs to its own fragment.
        scores = [0.9876 - index * 0.01357 for index in range(len(texts))]
        return RerankResponse(scores)

    monkeypatch.setenv("VI_EMBEDDING_URL", "http://reranker.test")
    monkeypatch.setenv("RAG_EVIDENCE_RERANK", "1" if rerank else "0")
    monkeypatch.setattr(grounded_rag, "chat", chat)
    monkeypatch.setattr(grounded_rag, "search", lambda *args, **kwargs: list(docs))
    monkeypatch.setattr("requests.post", post)
    result = grounded_rag.answer(QUESTION, "customer", {}, DB, TODAY)
    return result, sent_payloads, selector_outputs, rerank_requests


def test_selector_trace_records_scores_and_preserves_answer(monkeypatch):
    real_docs = grounded_rag.search(
        QUESTION, "customer", db_path=DB, as_of=TODAY, top_k=12,
        scope=resolve_scope(QUESTION, TODAY), historical=False,
        doc_types=["policy"],
    )
    assert [doc["document_id"] for doc in real_docs] == ["policy-warranty"]

    without, payloads_off, outputs_off, requests_off = run_case(monkeypatch, real_docs, rerank=False)
    with_rerank, payloads_on, outputs_on, requests_on = run_case(monkeypatch, real_docs, rerank=True)

    assert requests_off == []
    assert len(requests_on) == 1
    assert without["answer"] == with_rerank["answer"] == EXPECTED_ANSWER
    assert [(source["document_id"], source["source"]) for source in without["sources"]] == EXPECTED_SOURCES
    assert [(source["document_id"], source["source"]) for source in with_rerank["sources"]] == EXPECTED_SOURCES
    assert without["rag"]["part_evidence"] == EXPECTED_PART_EVIDENCE
    assert with_rerank["rag"]["part_evidence"] == EXPECTED_PART_EVIDENCE

    for result, payloads, outputs in (
        (without, payloads_off, outputs_off),
        (with_rerank, payloads_on, outputs_on),
    ):
        expected_raw = dict(answers=outputs[0]["answers"], missing=outputs[0]["missing"],
                            negative=outputs[0]["negative"])
        assert result["rag"]["selector_raw"] == expected_raw
        fragments = {item["id"]: item for item in payloads[0]["fragments"]}
        fields = result["rag"]["available_fields"]
        assert fields
        for field in fields:
            assert field["chunk_id"]
            assert len(field["text"]) <= 300
            assert field["text"] == fragments[field["id"]]["text"][:300]
            if result is without:
                assert field["rerank_score"] is None
            else:
                assert isinstance(field["rerank_score"], (int, float))
                texts = requests_on[0]
                fragment_text = fragments[field["id"]]["text"]
                index = texts.index(fragment_text)
                expected_score = round(0.9876 - index * 0.01357, 4)
                assert field["rerank_score"] == expected_score
