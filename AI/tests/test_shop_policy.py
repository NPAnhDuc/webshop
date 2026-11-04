import importlib.util
import json
import sqlite3
from datetime import date
from pathlib import Path
import pytest
from shopbot import grounded_rag,knowledge
from shopbot.grounded_rag import CALCULATION,POLICY_TOPIC,spell_out
from shopbot.monthly import active_documents
from shopbot.retrieval import normalize

spec=importlib.util.spec_from_file_location('load_shop_policy',Path(__file__).resolve().parents[1]/'scripts/load_shop_policy_20261031.py')
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)


@pytest.fixture
def store(monkeypatch,tmp_path):
    monkeypatch.setattr(knowledge,'dataset_source',lambda db:'demo')
    db=tmp_path/'data/shop.sqlite';db.parent.mkdir()
    sqlite3.connect(db).close()
    policy.load(db,tmp_path)
    return db,tmp_path


def records(store):
    return knowledge.KnowledgeStore(*store).records()


def test_loading_twice_adds_nothing(store):
    assert policy.load(*store)==[] and len(records(store))==len(policy.POLICIES)


def test_changed_text_becomes_a_new_version(store,monkeypatch):
    title,text=policy.POLICIES['policy-warranty']
    monkeypatch.setitem(policy.POLICIES,'policy-warranty',(title,text+'\n\nDòng mới.'))
    assert [d['version'] for d in policy.load(*store)]==[2]


def test_frozen_banks_cannot_see_the_policy(store):
    docs=records(store)
    assert active_documents(docs,'customer','demo',date(2026,10,29))==[]
    assert len(active_documents(docs,'customer','demo',date(2026,10,30)))==len(policy.POLICIES)


def test_demo_policy_ends_when_the_real_one_starts():
    manifest=Path(__file__).resolve().parents[1]/'data/business_sql/scenario_v1/documents/manifest.json'
    docs=[d for d in json.loads(manifest.read_text(encoding='utf-8')) if d['document_id']=='customer-policy']
    assert len(active_documents(docs,'customer','demo',date(2026,10,29)))==1
    assert active_documents(docs,'customer','demo',date(2026,10,30))==[]


def test_customers_can_read_every_policy(store):
    assert all(d['audience']=='customer' and d['status']=='approved' and d['doc_type']=='policy' for d in records(store))


@pytest.mark.parametrize('question',['Laptop bảo hành bao lâu?','Tiền hoàn về đâu?','Đơn 300 nghìn có mất phí ship không?',
                                     'Giao về Đà Nẵng mất mấy ngày?','Hiện shop có khuyến mãi gì không?','Giá trên web đã là giá bán chưa?'])
def test_policy_topics_are_recognised(question):
    assert POLICY_TOPIC.search(normalize(question))


@pytest.mark.parametrize('question',['Laptop nào pin trâu?','Ổ NVMe là gì?','Doanh thu tháng 9 bao nhiêu?'])
def test_other_questions_are_not_policy(question):
    assert not POLICY_TOPIC.search(normalize(question))


def test_instalment_amount_stays_a_calculation():
    assert CALCULATION.search(normalize('Máy 20 triệu trả góp 12 tháng mỗi tháng trả bao nhiêu?'))


def plan(action,types):
    return dict(action=action,query='q',doc_types=types,category='all',private_request=False,task='lookup')


def run(monkeypatch,question,route,role='customer'):
    seen=[]
    def search(*args,doc_types=None,**kw):
        seen.append(doc_types);return []
    monkeypatch.setattr(grounded_rag,'search',search)
    monkeypatch.setattr(grounded_rag,'chat',lambda *a,**k:route)
    result=grounded_rag.answer(question,role,{},Path(__file__).resolve().parents[1]/'data/business_sql/scenario_v1/shop.sqlite',date(2026,10,31))
    return result,seen


def test_policy_is_added_to_a_narrowed_route(monkeypatch):
    _,seen=run(monkeypatch,'Laptop bảo hành bao lâu?',plan('answer',['glossary']))
    assert seen[0]==['glossary','policy']


def test_an_open_route_stays_open(monkeypatch):
    _,seen=run(monkeypatch,'Laptop bảo hành bao lâu?',plan('answer',[]))
    assert seen[0] is None


def test_deferred_policy_question_reads_documents(monkeypatch):
    result,seen=run(monkeypatch,'Đơn 300 nghìn có mất phí ship không?',plan('deferred',[]))
    assert seen[0]==['policy'] and result['basic_action']!='deferred'


def test_instalment_amount_stays_deferred(monkeypatch):
    result,seen=run(monkeypatch,'Máy 20 triệu trả góp 12 tháng mỗi tháng trả bao nhiêu?',plan('deferred',[]))
    assert result['basic_action']=='deferred' and seen==[]


def test_admin_route_is_left_alone(monkeypatch):
    result,seen=run(monkeypatch,'Quy định bảo hành nhập kho thế nào?',plan('deferred',[]),role='admin')
    assert result['basic_action']=='deferred' and seen==[]


def test_policy_text_has_no_internal_wording():
    text=' '.join(t for _,t in policy.POLICIES.values())
    assert 'campaigns' not in text and 'Chatbot' not in text and 'Claude' not in text


@pytest.mark.parametrize('question',[
    'Laptop con han bh ma quat bui nhieu, minh nho ve sinh co mat tien khong?',
    'Minh dang lam ho so tr gop CCCD, co phai den cua hang khong?',
    'Đơn của mình hơn 500k thì ship có được miễn không?',
    'Đủ ngưỡng đó thì free ship phải không?',
    'Shipper giao tới mình được mở hộp kiểm tra trước chứ?',
    'Gửi về tỉnh thường mất cỡ mấy hôm làm việc?',
    'Neu ky thuat xac nhan hang gia that, shop den bu theo cach nao?',
])
def test_shorthand_for_shop_policy_is_recognised(question):
    assert POLICY_TOPIC.search(normalize(question))


def test_asking_how_a_fee_applies_is_not_a_calculation():
    assert not CALCULATION.search(normalize('Đơn chưa tới 500 nghìn thì ship tính sao?'))
    assert CALCULATION.search(normalize('Tính giúp mình tổng tiền đơn này'))


def test_shorthand_is_spelled_out_for_search():
    assert spell_out('laptop bh bn thang, free ship ko?')=='laptop bảo hành bao nhiêu thang, miễn phí giao hàng không?'
    assert spell_out('Shipping box')=='Shipping box'

