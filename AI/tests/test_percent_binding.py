from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag
from shopbot.percent_binding import bind_percent

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


def fragment(text, document_id="doc"):
    return dict(text=text, source=dict(document_id=document_id))


def bind(question, picked, fragments):
    return bind_percent({"P1": question}, {"P1": picked}, fragments)


FRAGMENTS = {
    "a": fragment("Nhận trả hàng trong 7 ngày."),
    "b": fragment("Trả hàng được hoàn 100% giá đã trả."),
    "c": fragment("Trả góp 0% qua thẻ.", "other"),
}


@pytest.mark.parametrize("question", ["Shop hoàn lại bao nhiêu phần trăm?", "shop hoan lai may %", "hoàn bao nhiêu %"])
def test_a_sentence_without_a_percentage_gives_way_to_one_from_the_same_document(question):
    bound, bindings = bind(question, ["a"], FRAGMENTS)
    assert bound["P1"] == ["b"] and bindings[0]["picked"] == ["a"]


def test_another_document_never_supplies_the_percentage():
    fragments = {key: value for key, value in FRAGMENTS.items() if key != "b"}
    bound, bindings = bind("Shop hoàn lại bao nhiêu phần trăm?", ["a"], fragments)
    assert bound["P1"] == ["a"] and not bindings


def test_a_selection_that_states_a_percentage_is_left_alone():
    assert bind("Shop hoàn lại bao nhiêu phần trăm?", ["b"], FRAGMENTS)[1] == []


def test_the_sentence_sharing_most_words_with_the_question_wins():
    fragments = dict(FRAGMENTS, d=fragment("Phí đổi máy là 5%."))
    assert bind("Trả hàng thì hoàn bao nhiêu phần trăm giá đã trả?", ["a"], fragments)[0]["P1"] == ["b"]


@pytest.mark.parametrize("question", ["Trả hàng trong bao nhiêu ngày?", "Shop có hoàn tiền không?"])
def test_other_questions_are_untouched(question):
    assert bind(question, ["a"], FRAGMENTS)[1] == []


def test_a_part_the_selector_left_empty_stays_missing():
    assert bind("Shop hoàn lại bao nhiêu phần trăm?", [], FRAGMENTS)[1] == []


def run(monkeypatch, question, role, types, wrong):
    """The real pipeline with a selector that picks the sentence containing `wrong`."""
    monkeypatch.delenv("VI_EMBEDDING_URL", raising=False)
    monkeypatch.delenv("RAG_EVIDENCE_RERANK", raising=False)
    seen = {}

    def chat(system, payload, schema, **_):
        if "parts" not in payload:
            return dict(action="answer", query=question, doc_types=types, category="all", private_request=False, task="lookup")
        seen.update(payload)
        chosen = [f["id"] for f in payload["fragments"] if wrong in f["text"]][:1]
        return dict(action="answer", answers={key: chosen for key in payload["parts"]}, missing=[], negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    return grounded_rag.answer(question, role, {}, DB, TODAY), seen


def test_a_refund_question_gets_the_refund_rate(monkeypatch):
    result, _ = run(monkeypatch, "Máy còn tem, trả trong hạn thì hoàn lại bao nhiêu phần trăm?", "customer", ["policy"], "nhận trả hàng hoàn tiền")
    assert "hoàn 100%" in result["answer"]
    assert "evidence: percentage sentence bound from the selected document" in result["trace"]


def test_a_customer_route_to_internal_documents_still_reads_the_policy(monkeypatch):
    result, seen = run(monkeypatch, "Đơn chưa tới ngưỡng miễn phí thì tiền giao tính lúc nào?", "customer", ["procedure"], "Đơn dưới 500.000đ")
    assert "tính phí giao hàng khi thanh toán" in result["answer"]
    assert seen["fragments"]


def test_an_admin_route_keeps_its_types(monkeypatch):
    _, seen = run(monkeypatch, "Quy trình nhập hàng gồm những bước nào?", "admin", ["procedure"], "khong-co-cau-nay")
    assert all(not item["text"].startswith("TechStore đổi 1 đổi 1") for item in seen["fragments"])
