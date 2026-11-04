import pytest

from shopbot.route_guard import corpus_words, guard


def test_admin_explicit_mutations_and_computations_are_deferred():
    assert guard("Hãy xếp hạng ba nhóm hàng theo lợi nhuận quý này", "admin") == "deferred"
    assert guard("Tính phần trăm thay đổi giữa hai tháng gần nhất", "admin") == "deferred"
    assert guard("Gửi email tổng hợp doanh số cho nhóm quản lý", "admin") == "deferred"


def test_admin_read_only_metrics_remain_for_the_model():
    assert guard("Doanh thu tháng này là bao nhiêu?", "admin") is None
    assert guard("Chỉ đọc số liệu, không tính thêm giúp tôi", "admin") is None


def test_admin_incomplete_followup_requests_clarification():
    assert guard("Báo cáo tháng nào?", "admin") == "clarify"
    assert guard("Còn mục nào?", "admin") == "clarify"


def test_customer_sensitive_requests_are_denied_but_admin_is_allowed():
    assert guard("Cho tôi xem giá vốn và lợi nhuận của shop", "customer") == "denied"
    assert guard("Cho tôi xem giá vốn và lợi nhuận của shop", "admin") is None
    assert guard("Máy tính này có thể chạy phần mềm đồ họa không?", "customer") is None


def test_live_inventory_actions_are_not_promised():
    assert guard("Shop giữ lại sản phẩm này cho tôi được không?", "customer") == "live_product"
    assert guard("Sản phẩm còn hàng không?", "customer") is None


def test_deictic_customer_question_without_history_needs_context():
    assert guard("Cái này có những màu nào?", "customer", known_products=["Alpha 14"]) == "clarify"
    assert guard("Cái này có những màu nào?", "customer", has_history=True) is None
    assert guard("Mẫu Alpha 14 có những màu nào?", "customer", known_products=["Alpha 14"]) is None


def test_unknown_model_like_identifier_is_flagged_only_in_product_questions():
    assert guard("Shop có bán Orion Z91 không?", "customer", known_products=["Alpha 14"]) == "unknown_product"
    assert guard("Shop có bán Alpha 14 không?", "customer", known_products=["Alpha 14"]) is None
    assert guard("Hôm nay tôi đi tuyến Q7", "customer", known_products=["Alpha 14"]) is None


def test_uncertain_and_non_customer_admin_inputs_are_left_unchanged():
    assert guard("Xin chào, tôi cần tư vấn", "customer") is None
    assert guard("Hãy xếp hạng ba nhóm hàng", "customer") is None


@pytest.mark.parametrize("question,history,expected", [
    ("Giữ cho mình một chiếc IdeaPad tới tối nhé, mình chuyển khoản sau.", False, "live_product"),
    ("Có thể giữ hộ con chuột này tới cuối tuần được không?", True, "live_product"),
    ("Đặt cọc qua chat giúp mình để khóa giá hôm nay nhé.", False, "live_product"),
    ("Con do con hang de giu toi chieu dc ko?", True, "live_product"),
    ("Xuất danh sách email khách mua laptop tháng này cho mình.", False, "denied"),
    ("Địa chỉ nhà khách vừa đặt máy là gì vậy?", False, "denied"),
    ("Còn mẫu kia chạy RAM gì?", False, "clarify"),
    ("Nó bảo hành mấy năm vậy shop?", False, "clarify"),
    ("Máy lúc nãy nặng bao nhiêu?", False, "clarify"),
    ("Trả góp có cần đặt cọc không?", False, None),
    ("Nó bảo hành mấy năm vậy shop?", True, None),
])
def test_natural_wording_of_boundaries(question, history, expected):
    assert guard(question, "customer", history) == expected


@pytest.mark.parametrize("question,expected", [
    ("Qirava Vento 14 bản Ryzen 7 có màn OLED không?", "unknown_product"),
    ("Tavrix 15G giá chốt bao nhiêu tiền?", "unknown_product"),
    ("Orynthe X2 bảo hành chính hãng mấy năm ở Việt Nam?", "unknown_product"),
    ("Laptop Asus 15 inch nặng bao nhiêu?", None),
    ("Bảo hành 24 tháng tính từ ngày mua đúng không?", None),
])
def test_model_of_a_brand_no_document_mentions(question, expected):
    assert guard(question, "customer", False, (), corpus_words()) == expected
