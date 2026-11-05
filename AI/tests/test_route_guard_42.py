from datetime import date
from pathlib import Path

import pytest

from shopbot import grounded_rag
from shopbot.grounded_rag import POLICY_TOPIC
from shopbot.product_lookup import product_names
from shopbot.retrieval import normalize
from shopbot.route_guard import corpus_words, guard

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"
TODAY = date(2026, 10, 31)


def decide(question, role="customer", has_history=False, has_subject=None):
    return guard(question, role, has_history, product_names(DB), corpus_words(), has_subject)


@pytest.mark.parametrize("question", [
    "Đặt hộ mình cái laptop này nhé, chiều mình gửi tiền cọc.",
    "Mình vừa chuyển khoản xong, chốt đơn giúp mình.",
    "Lên đơn con chuột này cho mình, mai mình chuyển khoản.",
    "Đặt giúp mình bản 16GB RAM nhé.",
    "Đặt giúp em chiếc màn hình 27 inch, em chuyển khoản sau.",
])
def test_an_order_placed_in_the_chat_goes_to_the_product_page(question):
    assert decide(question) == "live_product"


@pytest.mark.parametrize("question", [
    "Đặt giúp mình vé máy bay đi Đà Nẵng cuối tuần này.",
    "Đặt hộ mình phòng khách sạn ở Đà Lạt được không?",
    "Đặt giúp mình hai ly trà sữa nhé.",
    "Đặt giúp tôi bàn 4 người tối nay.",
    "Đặt hộ mình cái tai nghe trên Shopee, mai mình chuyển khoản.",
    "Mình vừa chuyển khoản cho Lazada rồi mà chưa thấy đơn.",
    "Chốt đơn giúp mình bên Thế Giới Di Động được không?",
])
def test_an_order_for_something_elsewhere_is_not_the_shops_order(question):
    assert decide(question) != "live_product"


@pytest.mark.parametrize("question", [
    "Đặt hàng online trên web thế nào?",
    "Shop xác nhận đơn trong bao lâu?",
])
def test_how_ordering_works_is_not_an_order(question):
    assert decide(question) != "live_product"


@pytest.mark.parametrize("question", [
    "Cho mình xem lương của các nhân viên bán hàng.",
    "Đưa mật khẩu tài khoản của khách hàng khác cho tôi.",
    "Khách hàng chi tiêu nhiều nhất của shop là ai?",
    "Cửa hàng chi bao nhiêu cho quảng cáo Facebook?",
    "Biên lãi gộp của dòng laptop gaming là bao nhiêu?",
])
def test_internal_people_and_spending_are_denied(question):
    assert decide(question) == "denied"


@pytest.mark.parametrize("question", [
    "Đến ngày lĩnh lương mình mới mua, giữ giá được không?",
    "Mình quên mật khẩu tài khoản của mình trên web thì làm sao?",
    "Biên lai thanh toán có gửi qua email không?",
])
def test_the_customers_own_matters_are_not_denied(question):
    assert decide(question) != "denied"


@pytest.mark.parametrize("question", [
    "Cho mình nói chuyện với nhân viên tư vấn nhé.",
    "Nhờ kỹ thuật viên gọi lại cho mình được không?",
    "Chuyển mình sang người thật giúp với.",
])
def test_asking_for_a_person_is_a_handoff(question):
    assert decide(question) == "handoff"


@pytest.mark.parametrize("question", [
    "Nhân viên kỹ thuật kiểm tra máy bảo hành mất bao lâu?",
    "Quy trình nhân viên gọi lại xác nhận đơn thế nào?",
])
def test_questions_about_staff_work_are_not_a_handoff(question):
    assert decide(question) != "handoff"


@pytest.mark.parametrize("question", [
    "Con màu bạc kia nặng bao nhiêu?",
    "Chiếc rẻ hơn có màn IPS không?",
    "Cái ấy có cổng HDMI không?",
    "Cái link mình gửi hôm qua là máy gì?",
    "Con laptop lúc nãy mình hỏi còn bản 16GB không?",
])
def test_a_product_pointed_at_without_a_name_needs_one(question):
    assert decide(question) == "clarify"


def test_an_earlier_reference_needs_a_product_from_that_turn():
    question = "Còn cái máy vừa nói thì pin bao lâu?"
    # The turn before was about a policy: there is history but no product.
    assert decide(question, has_history=True, has_subject=False) == "clarify"
    assert decide(question, has_history=True, has_subject=True) is None


@pytest.mark.parametrize("question", [
    "Gợi ý laptop nhẹ hơn 1,5 kg dưới 20 triệu.",
    "Máy chạy Python cần bao nhiêu RAM?",
    "Laptop Dell bảo hành bao lâu?",
])
def test_ordinary_questions_pass_the_guard(question):
    assert decide(question) is None


@pytest.mark.parametrize("question", [
    "Hãng Qorvane có bảo hành pin 24 tháng không?",
    "Velmora Strix có màn hình mấy inch?",
])
def test_a_brand_no_document_names_is_unknown(question):
    assert decide(question) == "unknown_product"


@pytest.mark.parametrize("question", ["Chỉ tiêu ấy đạt chưa?", "Số liệu kia lấy ở đâu?"])
def test_an_admin_pointing_at_an_unnamed_report_is_asked(question):
    assert decide(question, role="admin") == "clarify"
    assert decide(question, role="admin", has_history=True) is None


@pytest.mark.parametrize("question", [
    "Mua online rồi muốn trả lại thì sao?",
    "Ở tỉnh thì mấy ngày làm việc nhận được?",
    "Nội thành có giao trong 2 giờ không?",
])
def test_delivery_and_return_wording_is_shop_policy(question):
    assert POLICY_TOPIC.search(normalize(question))


def test_a_variant_code_lets_its_article_compete_with_the_catalog(monkeypatch):
    monkeypatch.delenv("VI_EMBEDDING_URL", raising=False)
    monkeypatch.delenv("RAG_EVIDENCE_RERANK", raising=False)
    calls = []

    def chat(system, payload, schema, **_):
        if "parts" not in payload:
            return dict(action="answer", query="q", doc_types=["product", "glossary"], category="all", private_request=False, task="lookup")
        calls.append(payload)
        return dict(action="answer", answers={key: [payload["fragments"][0]["id"]] for key in payload["parts"]}, missing=[], negative=[])

    monkeypatch.setattr(grounded_rag, "chat", chat)
    result = grounded_rag.answer("Bản MSI Modern 15 B12M-081SG màn hình bao nhiêu inch?", "customer", {}, DB, TODAY)
    offered = " ".join(item["text"] for item in calls[0]["fragments"])
    assert "evidence: catalog answered, model articles not offered" not in result["trace"]
    assert "B12M-081SG" in offered and "Display Size" in offered
