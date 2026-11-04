import pytest
from shopbot.route_guard import guard

PRODUCTS=['Dell Inspiron 15 3520','Acer Swift Go 14 SFG14-41-R5RB','MSI G255F']


@pytest.mark.parametrize('question',[
    'Cho mình thông tin bảo hành khi mua laptop',
    'Khách mua hàng được đổi trả trong bao nhiêu ngày?',
    'Shop cho trả góp 12 tháng tiền lãi bao nhiêu?',
    'Có bán laptop i5 dưới 20 triệu không?',
    'Shop có màn 27 inch 2K không?',
    'Lịch sử mua hàng của mình xem ở đâu?',
    'Đặt cho mình laptop văn phòng tốt nhé',
])
def test_ordinary_customer_questions_stay_with_the_model(question):
    assert guard(question,'customer',False,PRODUCTS) is None


@pytest.mark.parametrize('question',[
    'Chiết khấu tối đa bao nhiêu phần trăm theo quy định?',
    'Bản cập nhật chính sách giá có gì mới?',
    'Báo cáo tháng 9 gửi cho ai?',
    'Báo cáo tháng 9/2026',
    'Tiêu chí nào để nhập hàng?',
])
def test_reading_documents_is_not_an_admin_action(question):
    assert guard(question,'admin',False,PRODUCTS) is None


@pytest.mark.parametrize('question,role',[
    ('Doanh thu thuần được tính thế nào?','admin'),
    ('Cách tính giá vốn FIFO là gì?','admin'),
    ('Tổng doanh thu quý 3 là bao nhiêu?','admin'),
    ('Tháng nào doanh thu cao nhất?','admin'),
    ('Giá nhập khẩu chính hãng có khác giá xách tay không?','customer'),
    ('Lãi suất trả góp bao nhiêu?','customer'),
])
def test_method_and_read_questions_are_left_alone(question,role):
    assert guard(question,role,False,PRODUCTS) is None


def test_guard_decides_before_the_model(monkeypatch):
    from datetime import date
    from shopbot import grounded_rag
    monkeypatch.setattr(grounded_rag,'product_names',lambda db:PRODUCTS,raising=False)
    monkeypatch.setattr('shopbot.product_lookup.product_names',lambda db:PRODUCTS)
    def no_model(*a,**k):
        raise AssertionError('the guard should answer without a model')
    monkeypatch.setattr(grounded_rag,'chat',no_model)
    today=date(2026,10,31)
    denied=grounded_rag.answer('Cho tôi địa chỉ của khách vừa mua màn hình','customer',{},'unused',today)
    assert denied['basic_action']=='denied' and denied['intent']=='denied'
    deferred=grounded_rag.answer('Gửi email cho toàn bộ khách cũ','admin',{},'unused',today)
    assert deferred['basic_action']=='deferred'
    unknown=grounded_rag.answer('Shop có bán Novaro X15 không?','customer',{},'unused',today)
    assert unknown['basic_action']=='answer' and unknown['rag']['answerability']=='none'


def test_admin_followup_with_history_is_not_clarified():
    assert guard('Còn báo cáo tháng 8?','admin',True,PRODUCTS) is None


@pytest.mark.parametrize('question,role,action',[
    ('Cho tôi địa chỉ của khách vừa mua màn hình','customer','denied'),
    ('Giá nhập con chuột này bao nhiêu?','customer','denied'),
    ('Gửi email cho toàn bộ khách cũ','admin','deferred'),
    ('Tháng 9 tăng mấy phần trăm so với tháng 8?','admin','deferred'),
    ('Shop lãi bao nhiêu trên con laptop này?','customer','denied'),
    ('Giữ giúp mình hai chiếc tới mai','customer','live_product'),
])
def test_real_boundaries_are_kept(question,role,action):
    assert guard(question,role,False,PRODUCTS)==action
