from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag, retrieval
from shopbot.grounded_rag import customer_story, question_parts, spell_out
from shopbot.retrieval import about_model

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


def plan(types):
    return dict(action="answer", query="q", doc_types=types, category="all", private_request=False, task="lookup")


def ask(monkeypatch, question, types=("product",), role="customer"):
    """Run the real retrieval and stop at the selector, returning what it was given."""
    monkeypatch.delenv("VI_EMBEDDING_URL", raising=False)
    monkeypatch.delenv("RAG_EVIDENCE_RERANK", raising=False)
    selector = {}

    def chat(system, payload, schema, **_):
        if "parts" not in payload:
            return plan(list(types))
        selector.update(payload)
        parts = list(payload["parts"])
        return dict(action="answer", answers={key: [] for key in parts}, missing=parts, negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    result = grounded_rag.answer(question, role, {}, DB, TODAY)
    return result, selector


def fragments(selector):
    return " ".join(item["text"] for item in selector["fragments"])


@pytest.mark.parametrize("question,expected", [
    ("LOQ 15IRH8 có mấy khe SO-DIMM, dùng RAM DDR5 phải không?", "hai khe SO-DIMM DDR5"),
    ("IdeaPad Slim 3i 15ITL6 có RAM hàn hay khe SO-DIMM vậy?", "RAM hàn cùng một khe"),
    ("Legion Slim 5 16IRH8 trong tài liệu có mấy khe RAM?", "hai khe SO-DIMM DDR5"),
])
def test_an_article_titled_with_the_model_code_survives_product_isolation(monkeypatch, question, expected):
    result, selector = ask(monkeypatch, question, types=("product", "glossary"))
    assert "evidence: isolated to bound product records" in result["trace"]
    assert expected in fragments(selector)


def test_isolation_still_drops_articles_about_other_things(monkeypatch):
    _, selector = ask(monkeypatch, "LOQ 15IRH8 có mấy khe SO-DIMM, dùng RAM DDR5 phải không?", types=("product", "glossary"))
    assert "DIMM thường dùng ở máy bàn" not in fragments(selector)


@pytest.mark.parametrize("question", [
    "LOQ 15IRH8 có mấy khe SO-DIMM, dùng RAM DDR5 phải không?",
    "Lenovo LOQ Gaming 15IRH8 dùng DDR5 hay DDR4 vậy?",
])
def test_a_technology_named_in_the_question_is_not_a_model(monkeypatch, question):
    result, selector = ask(monkeypatch, question, types=("product", "glossary"))
    assert "evidence: isolated to bound product records" in result["trace"]
    assert "on-die ECC" not in fragments(selector)
    assert "cắm chung" not in fragments(selector)


def selector_calls(monkeypatch, question, decide):
    """The real pipeline; `decide` answers the selector from what it was offered."""
    monkeypatch.delenv("VI_EMBEDDING_URL", raising=False)
    monkeypatch.delenv("RAG_EVIDENCE_RERANK", raising=False)
    calls = []

    def chat(system, payload, schema, **_):
        if "parts" not in payload:
            return plan(["product", "glossary"])
        calls.append(payload)
        return decide(payload)

    monkeypatch.setattr(grounded_rag, "chat", chat)
    return grounded_rag.answer(question, "customer", {}, DB, TODAY), calls


def answered(payload):
    return dict(action="answer", answers={key: [payload["fragments"][0]["id"]] for key in payload["parts"]}, missing=[], negative=[])


def lacking(payload, keys):
    answers = {key: [] if key in keys else [payload["fragments"][0]["id"]] for key in payload["parts"]}
    return dict(action="answer", answers=answers, missing=list(keys), negative=[])


SLOTS = "Legion Slim 5 16IRH8 trong tài liệu có mấy khe RAM?"
ARTICLE = "hai khe SO-DIMM DDR5"
OFFERED = "evidence: catalog answered, model articles not offered"


def test_the_catalog_alone_is_asked_first_and_keeps_its_answer(monkeypatch):
    result, calls = selector_calls(monkeypatch, SLOTS, answered)
    assert len(calls) == 1 and ARTICLE not in fragments(calls[0])
    assert OFFERED in result["trace"]
    assert {claim["evidence"][0]["source"] for claim in result["rag"]["claims"]} and "Lenovo" in result["answer"]


def test_the_article_opens_when_the_catalog_lacks_the_answer(monkeypatch):
    result, calls = selector_calls(monkeypatch, SLOTS, lambda payload: answered(payload) if ARTICLE in fragments(payload) else lacking(payload, list(payload["parts"])))
    assert len(calls) == 2
    assert ARTICLE not in fragments(calls[0]) and ARTICLE in fragments(calls[1])
    assert OFFERED not in result["trace"]


def test_one_part_lacking_is_enough_to_open_the_article(monkeypatch):
    _, calls = selector_calls(monkeypatch, "LOQ 15IRH8 có mấy khe SO-DIMM, dùng RAM DDR5 phải không?", lambda payload: lacking(payload, ["P1"]))
    assert len(calls) == 2 and len(calls[0]["parts"]) == 2 and ARTICLE in fragments(calls[1])


def test_an_empty_part_is_not_an_answer_even_when_nothing_is_marked_missing(monkeypatch):
    _, calls = selector_calls(monkeypatch, SLOTS, lambda payload: dict(lacking(payload, list(payload["parts"])), missing=[]))
    assert len(calls) == 2


def test_the_catalog_pass_does_not_lose_lines_to_the_article_budget(monkeypatch):
    decide = lambda payload: lacking(payload, list(payload["parts"]))
    _, calls = selector_calls(monkeypatch, SLOTS, decide)
    assert ARTICLE in fragments(calls[1])
    monkeypatch.setattr(retrieval, "about_model", lambda *_: False)
    _, without_articles = selector_calls(monkeypatch, SLOTS, decide)
    assert len(without_articles) == 1
    assert calls[0]["fragments"] == without_articles[0]["fragments"]


def test_a_question_without_a_model_article_still_asks_once(monkeypatch):
    _, calls = selector_calls(monkeypatch, "Kingston NV2 giao tiếp chuẩn nào?", answered)
    assert len(calls) <= 1


@pytest.mark.parametrize("title,question,products,kept", [
    ("DDR5 là gì?", "loq 15irh8 dung ddr5 khong", ["Lenovo LOQ Gaming 15IRH8"], False),
    ("Lenovo LOQ 15IRH8: tài liệu nền tảng của dòng máy", "loq 15irh8 dung ddr5 khong", ["Lenovo LOQ Gaming 15IRH8"], True),
    ("Modern 15 B12M-081SG: thông số chỉ cho bản SG", "msi b12m-081sg man hinh", ["MSI Modern 15 B12M"], True),
    ("Kingston NV2: thông số tốc độ thay đổi theo dung lượng", "lenovo loq 15irh8 ssd", ["Kingston NV2"], False),
])
def test_about_model_keeps_only_articles_on_the_bound_model(title, question, products, kept):
    assert about_model(dict(title=title), question, [dict(title=name) for name in products]) is kept


@pytest.mark.parametrize("question", [
    "MSI B12M-081SG được ghi màn hình cỡ nào?",
    "MSI Modern 15 B12M-408AU ghi RAM onboard bao nhiêu?",
])
def test_a_regional_variant_does_not_take_the_catalog_line(monkeypatch, question):
    result, selector = ask(monkeypatch, question, types=("product", "glossary"))
    assert "evidence: catalog fields picked by label (no model selection)" not in result["trace"]
    assert selector


def test_the_catalog_line_still_answers_the_catalog_model(monkeypatch):
    result, _ = ask(monkeypatch, "MSI Modern 15 B12M RAM bao nhiêu?", types=("product", "glossary"))
    assert "evidence: catalog fields picked by label (no model selection)" in result["trace"]


def test_the_selector_reads_shorthand_spelled_out(monkeypatch):
    _, selector = ask(monkeypatch, "Laptop bh bn thang vay shop?", types=("policy",))
    assert selector["question"] == spell_out("Laptop bh bn thang vay shop?")
    assert "bảo hành" in selector["question"] and "bao nhiêu" in selector["question"]


@pytest.mark.parametrize("question,clauses", [
    ("Shop oi, minh mua sp o ben minh gan day, may gap loi phan cung thi bh doi 1-1 trong bn ngay?", 2),
    ("Hom qua may bi do nuoc vao ban phim, minh chua mang sua o dau ca, neu dem qua shop thi co duoc bh nua khong?", 2),
    ("Sp minh mua van con tem va chua kich hoat, neu tra trong thoi han thi shop hoan lai bn phan tram?", 1),
])
def test_clauses_before_the_question_are_the_customers_story(question, clauses):
    assert len(customer_story(question)) == clauses


@pytest.mark.parametrize("question", [
    "LOQ 15IRH8 có mấy khe SO-DIMM, dùng RAM DDR5 phải không?",
    "NV2 giao tiếp chuẩn nào, tốc độ đọc ghi tuần tự ra sao?",
    "CPU gì, RAM bao nhiêu?",
    "CPU, RAM, pin của máy này?",
    "Chốt giá rẻ nhất hôm nay và xác nhận AOC 24G4XE còn hàng ngay bây giờ.",
    "Tôi muốn xem CPU và RAM của TechStore LunarPad J919. Kho tài liệu có đúng model này không?",
    "Theo danh mục, CPU gì, RAM bao nhiêu?",
    "Shop oi, minh muon tu van",
])
def test_real_questions_are_not_a_story(question):
    assert customer_story(question) == []


def select(monkeypatch, question, chosen_for):
    """The real pipeline with a selector that answers each part through `chosen_for`."""
    monkeypatch.delenv("VI_EMBEDDING_URL", raising=False)
    monkeypatch.delenv("RAG_EVIDENCE_RERANK", raising=False)
    seen = {}

    def chat(system, payload, schema, **_):
        if "parts" not in payload:
            return plan(["policy"])
        seen.update(payload)
        answers = {key: chosen_for(part, payload["fragments"]) for key, part in payload["parts"].items()}
        return dict(action="answer", answers=answers, missing=[key for key, ids in answers.items() if not ids], negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    return grounded_rag.answer(question, "customer", {}, DB, TODAY), seen


def warranty(part, fragments):
    return [f["id"] for f in fragments if "Vỏ case và chuột" in f["text"]][:1] if "bảo hành" in part else []


def test_the_story_keeps_its_own_part_for_the_selector(monkeypatch):
    _, seen = select(monkeypatch, "Neu ky thuat xac nhan hang gia that, shop den bu theo cach nao?", lambda part, fragments: [])
    assert list(seen["parts"].values()) == question_parts("Neu ky thuat xac nhan hang gia that, shop den bu theo cach nao?")
    assert len(seen["parts"]) == 2


def test_an_unanswered_story_is_not_reported_as_missing(monkeypatch):
    result, _ = select(monkeypatch, "Minh mua con chuot tuan truoc, chuot duoc bh bao lau?", warranty)
    assert "Chưa có nguồn" not in result["answer"]
    assert result["rag"]["answerability"] == "full" and result["rag"]["unanswered"] == []


def test_an_unanswered_question_still_is(monkeypatch):
    result, _ = select(monkeypatch, "Minh mua con chuot tuan truoc, chuot duoc bh bao lau?", lambda part, fragments: [])
    assert "Chưa có nguồn đủ để xác nhận: chuot duoc bảo hành bao lau" in result["answer"]
    assert "Minh mua con chuot" not in result["answer"]


def test_a_question_that_does_not_end_the_story_keeps_every_part(monkeypatch):
    result, _ = select(monkeypatch, "Minh mua con chuot tuan truoc, chuot cua minh bi hong roi nen rat buon.", lambda part, fragments: [])
    assert "Minh mua con chuot tuan truoc" in result["answer"]


def test_admin_questions_reach_the_calculator_before_the_guard_defers_them(monkeypatch):
    result, selector = ask(monkeypatch, "Chênh lệch giá vốn giữa tháng 4/2026 và tháng 5/2026 là bao nhiêu?", role="admin")
    assert not selector and result["basic_action"] == "answer"
    assert result["rag"]["method"] == "deterministic SQL calculation"
    assert result["rag"]["claims"] and result["sources"][0]["document_id"] == "sql-financial-ledger"
    assert "-151.983.000 đ" in result["answer"]


def test_customers_never_reach_the_calculator(monkeypatch):
    result, _ = ask(monkeypatch, "Chênh lệch giá vốn giữa tháng 4/2026 và tháng 5/2026 là bao nhiêu?")
    assert result["basic_action"] == "denied"
