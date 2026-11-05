from pathlib import Path

import pytest

from shopbot.product_lookup import product_names
from shopbot.route_guard import corpus_words, guard

DB = Path(__file__).resolve().parents[1] / "data/business_sql/scenario_v1/shop.sqlite"


def decide(question, role="customer", has_history=False):
    return guard(question, role, has_history, product_names(DB), corpus_words())


@pytest.mark.parametrize("question", [
    "Giải giúp mình bất phương trình 2x - 3 > 7.",
    "Tính đạo hàm của x mũ 3 cộng 2x.",
    "Viết đoạn văn nghị luận về lòng biết ơn khoảng 200 chữ.",
    "Dịch ra tiếng Nhật câu: cảm ơn bạn rất nhiều.",
    "Định luật 2 Newton phát biểu thế nào?",
    "Viết giúp mình đoạn code JavaScript đảo ngược chuỗi.",
    "sua giup minh script python bi loi indent",
    "Bot ngu quá, trả lời toàn sai.",
    "dm hoi may cau ma cung khong biet",
    "Gửi tiết kiệm 6 tháng ngân hàng nào lãi cao?",
    "Có nên đầu tư bitcoin lúc này không?",
    "Lazada đang có flash sale gì hôm nay?",
    "Spotify Premium gói gia đình giá bao nhiêu?",
])
def test_a_request_with_nothing_of_the_shop_is_outside(question):
    assert decide(question) == "outside"


def test_an_admin_off_topic_request_is_outside_too():
    assert decide("Giải thích thuyết tiến hóa của Darwin giúp tôi.", role="admin") == "outside"


@pytest.mark.parametrize("question", [
    "Laptop nào viết code Python mượt trong tầm 20 triệu?",
    "Dịch giúp mình thông số card RTX 4060 sang tiếng Việt.",
    "Bot ngu quá, con chuột G502 bảo hành bao lâu?",
    "Shop có giao nhanh hơn Tiki không?",
    "Mua laptop trả góp lãi suất bao nhiêu?",
    "Mua trên Shopee rồi mang qua shop bảo hành được không?",
    "Đang học môn kiến trúc máy tính, cho hỏi ổ M.2 với NVMe có phải là một không?",
    "Xem Netflix 4K trên laptop này có mượt không?",
])
def test_a_question_about_the_shop_or_its_goods_is_left_to_the_router(question):
    assert decide(question) != "outside"
