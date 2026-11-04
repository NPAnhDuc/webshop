import sqlite3
import json
from datetime import date
import pytest
from shopbot.budget_advice import advise,request
from shopbot.grounded_rag import answer

TODAY=date(2026,10,21)


@pytest.fixture
def db(tmp_path):
    path=tmp_path/'shop.sqlite'
    con=sqlite3.connect(path)
    con.executescript('CREATE TABLE products (sku TEXT, name TEXT, price INTEGER, stock INTEGER, category TEXT);'
                      'CREATE TABLE product_facts (sku TEXT, record_json TEXT);')
    def add(sku,name,price,stock,resolution,display,gpu_access='Integrated',weight='1.5 kg',category='laptop'):
        con.execute('INSERT INTO products VALUES (?,?,?,?,?)',(sku,name,price,stock,category))
        con.execute('INSERT INTO product_facts VALUES (?,?)',(sku,json.dumps(dict(cpu='Core i5',gpu='GPU',attributes={
            'Display Resolution':resolution,'Display Type':display,'Graphics Memory Accessibility':gpu_access,'Weight (Kg)':weight,'RAM':'8GB'}))))
    add('a','Retina Air',18_900_000,0,'2560x1600','Retina')
    add('b','Gamer G5',21_900_000,4,'1920x1080','FHD LED Display','Dedicated','2.08 kg')
    add('c','Office 15',19_500_000,2,'1920x1080','FHD LED Display')
    add('d','Slim 14',13_900_000,3,'1920x1080','FHD','Integrated','1.22 kg')
    add('e','Legion QHD',26_000_000,2,'2560x1600','2.5K QHD WQXGA Display','Dedicated')
    con.commit();con.close()
    return path


def test_budget_pick_uses_stock_and_never_lists_sold_out_as_available(db):
    reply=advise('gợi ý cho tau con máy khoảng 20 triệu có màn hình đẹp',db)
    assert [r['name'] for r in reply['rows']]==['Gamer G5','Office 15']
    assert '21.900.000đ' in reply['answer'] and 'Retina Air (18.900.000đ) hợp tiêu chí hơn nhưng đang hết hàng' in reply['answer']
    assert 'Màn hình nét hơn gần ngân sách nhất: Legion QHD – 26.000.000đ' in reply['answer']


def test_bounds_and_preferences(db):
    assert request('Laptop nào dưới 15 triệu nhẹ để đi học?')[2:4]==(0,14_999_999)
    reply=advise('Laptop nào dưới 15 triệu nhẹ để đi học?',db)
    assert reply['answer'].startswith('Trong tầm dưới 15.000.000đ') and [r['name'] for r in reply['rows']]==['Slim 14']
    assert advise('Tư vấn laptop chơi game tầm 20 củ',db)['rows'][0]['name']=='Gamer G5'
    none=advise('tư vấn máy khoảng 40 triệu',db)
    assert none['rows']==[] and 'không có laptop nào còn hàng' in none['answer'] and 'Legion QHD' in none['answer']


@pytest.mark.parametrize('question',['OLED là gì?','Màn hình 144 Hz có cần cho học tập không?',
    'Chốt giá rẻ nhất hôm nay và xác nhận Acer Aspire 5 còn hàng','Laptop 20 triệu thì RAM nên bao nhiêu GB?',
    'Doanh thu thuần tháng 9/2026?','Giữa 15 triệu và 20 triệu nên chọn máy nào?',
    'Có chính sách nào cho đơn 20 triệu không?'])
def test_other_questions_are_not_budget_picks(question):
    assert request(question) is None


@pytest.mark.parametrize('question,expected',[
    ('Shop có vỏ case nào dưới 2,6 tr không?',('case',0,2_599_999)),
    ('Shop có ổ cứng nào tối đa 3,9 triệu không?',('internal-hard-drive',0,3_900_000)),
    ('Shop có chuột nào từ 1,3 triệu không?',('mouse',1_300_000,2_600_000)),
    ('Shop có nguồn máy tính nào dưới 3,4 triệu không?',('power-supply',0,3_399_999))])
def test_asking_whether_the_shop_has_something_in_budget_is_a_pick(question,expected):
    parsed=request(question)
    assert (parsed[0],parsed[2],parsed[3])==expected


def test_customer_budget_pick_skips_the_router_and_admin_does_not(db,monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.chat',lambda *a,**k:pytest.fail('No router for a catalog filter'))
    result=answer('gợi ý máy khoảng 20 triệu màn hình đẹp','customer',{},db,TODAY)
    assert result['basic_action']=='answer' and result['intent']=='products' and 'Gamer G5' in result['answer']
    called=[]
    def router(*a,**k):
        called.append(1);return dict(action='outside',query='',doc_types=[],task='lookup',private_request=False)
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    answer('gợi ý máy khoảng 20 triệu màn hình đẹp','admin',{},db,TODAY)
    assert called
