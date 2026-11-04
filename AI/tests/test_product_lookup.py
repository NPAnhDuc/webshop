import sqlite3
from datetime import date
import pytest
from shopbot.grounded_rag import answer
from shopbot.product_lookup import lookup
from shopbot.quality_eval import grade

TODAY=date(2026,10,21)


@pytest.fixture
def db(tmp_path):
    path=tmp_path/'shop.sqlite'
    con=sqlite3.connect(path)
    con.execute('CREATE TABLE products (sku TEXT, name TEXT, price INTEGER, stock INTEGER, category TEXT)')
    con.executemany('INSERT INTO products VALUES (?,?,?,?,?)',[
        ('a','MSI Modern 15 B12M',14_500_000,4,'laptop'),
        ('b','Razer DeathAdder Essential',510_000,0,'mouse'),
        ('c','NZXT H5 Flow (2024)',2_130_000,7,'case'),
        ('d','Acer Nitro 5',19_000_000,2,'laptop'),
        ('e','Acer Nitro 5 Pro',25_000_000,2,'laptop')])
    con.commit();con.close()
    return path


def no_model(*a,**k):
    pytest.fail('No model call expected')


@pytest.mark.parametrize('question',[
    'MSI Modern 15 B12M hôm nay giá bao nhiêu, còn hàng không?',
    'msi modern 15 b12m bao nhiêu tiền',
    'Xác nhận giá chốt MSI Modern 15 B12M hôm nay giúp mình.',
])
def test_price_and_stock_come_from_the_database(db,question):
    r=lookup(question,'customer',db)
    assert r['answer'].startswith('MSI Modern 15 B12M: giá 14.500.000đ, còn hàng.')
    assert r['rows']==[dict(name='MSI Modern 15 B12M',price=14_500_000,stock=4)]


def test_sold_out_is_stated(db):
    assert 'hết hàng' in lookup('Razer DeathAdder Essential còn hàng không?','customer',db)['answer']


def test_customer_sees_availability_and_admin_sees_the_count(db):
    question='MSI Modern 15 B12M còn hàng không?'
    assert '4 sản phẩm' not in lookup(question,'customer',db)['answer']
    assert 'còn 4 sản phẩm' in lookup(question,'admin',db)['answer']


def test_name_matches_without_its_bracketed_year(db):
    assert lookup('NZXT H5 Flow giá bao nhiêu?','customer',db)['rows'][0]['price']==2_130_000


def test_longer_name_hides_the_shorter_one(db):
    assert lookup('Acer Nitro 5 Pro giá bao nhiêu?','customer',db)['name']=='Acer Nitro 5 Pro'


@pytest.mark.parametrize('question',[
    'Laptop giá bao nhiêu?',
    'Acer Aspire 3 giá bao nhiêu?',
    'MSI Modern 15 B12M và Razer DeathAdder Essential giá bao nhiêu?',
    'MSI Modern 15 B12M đánh giá thế nào?',
    'MSI Modern 15 B12M có giá trị sử dụng lâu dài không?',
    'MSI Modern 15 B12M RAM bao nhiêu?',
    'Đặt giữ giúp mình một chiếc MSI Modern 15 B12M với giá đang bán.',
    'MSI Modern 15 B12M có giảm giá không?',
    'MSI Modern 15 B12M trả góp giá bao nhiêu?',
    'Shop nhập MSI Modern 15 B12M giá bao nhiêu?',
    'MSI Modern 15 B12M so với Acer Nitro 5 giá thế nào?',
])
def test_everything_else_stays_on_the_normal_path(db,question):
    assert lookup(question,'customer',db) is None


def test_unreadable_database_falls_back_to_the_normal_path(tmp_path):
    assert lookup('MSI Modern 15 B12M giá bao nhiêu?','customer',tmp_path/'missing.sqlite') is None


def test_reference_uses_the_product_from_the_previous_turn(db):
    assert lookup('Con đó bao nhiêu tiền?','customer',db,'Razer DeathAdder Essential')['name']=='Razer DeathAdder Essential'
    assert lookup('Laptop Dell bao nhiêu tiền?','customer',db,'Razer DeathAdder Essential') is None
    assert lookup('Con đó bao nhiêu tiền?','customer',db) is None


def test_answer_skips_the_model_and_keeps_the_gold_action(db):
    r=answer('MSI Modern 15 B12M giá bao nhiêu?','customer',{},str(db),TODAY,model=no_model)
    assert r['basic_action']=='live_product' and r['rows'][0]['name']=='MSI Modern 15 B12M'
    assert r['profile']['rag_product_subject']=='MSI Modern 15 B12M'
    assert r['sources'][0]['authority']=='derived_from_sql'


def test_grade_accepts_one_product_row_and_rejects_a_list(db):
    case=dict(role='customer',expected_behavior='live_product')
    one=answer('MSI Modern 15 B12M giá bao nhiêu?','customer',{},str(db),TODAY,model=no_model)
    assert grade(case,one)['status']=='PASS_CHECKS'
    many=dict(one,rows=one['rows']*2)
    assert [i['cause'] for i in grade(case,many)['issues']]==['UNEXPECTED_TOOL']
