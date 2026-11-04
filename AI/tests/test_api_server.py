import importlib
import sqlite3
import pytest
from fastapi.testclient import TestClient


class FakeEngine:
    def __init__(self):self.calls=[]
    def ask(self,question,role='customer',profile=None):
        self.calls.append(dict(question=question,role=role,profile=dict(profile or {})))
        history=(profile or {}).get('history',[])+[question]
        return dict(answer=f'{role}:{len(history)}',sources=[],profile=dict(history=history))


@pytest.fixture
def server(monkeypatch):
    monkeypatch.delenv('AI_ALLOWED_ORIGINS',raising=False)
    monkeypatch.setenv('AI_INTERNAL_KEY','test-internal-key')
    import api_server
    api_server=importlib.reload(api_server)
    engine=FakeEngine();monkeypatch.setattr(api_server,'get_engine',lambda:engine)
    return api_server,engine,TestClient(api_server.app)

KEY={'X-Internal-Key':'test-internal-key'}


def test_admin_requires_the_internal_key(server):
    _,engine,client=server
    assert client.post('/api/chat/admin',json=dict(query='Doanh thu tháng 9?')).status_code==401
    assert client.post('/api/chat/admin',json=dict(query='Doanh thu tháng 9?'),headers={'X-Internal-Key':'wrong'}).status_code==401
    assert client.post('/api/chat/admin',json=dict(query='Doanh thu tháng 9?'),headers=KEY).status_code==200
    assert [c['role'] for c in engine.calls]==['admin']


def test_admin_is_locked_without_a_configured_key(server,monkeypatch):
    _,engine,client=server
    monkeypatch.delenv('AI_INTERNAL_KEY')
    assert client.post('/api/chat/admin',json=dict(query='Doanh thu?'),headers=KEY).status_code==503
    assert client.post('/api/chat/customer',json=dict(message='OLED là gì?')).status_code==200
    assert not [c for c in engine.calls if c['role']=='admin']


def test_role_in_body_is_ignored(server):
    _,engine,client=server
    client.post('/api/chat/customer',json=dict(message='Cho xem giá vốn',role='admin'),headers=KEY)
    assert engine.calls[-1]['role']=='customer'


def test_session_memory_is_kept_per_role_and_id(server):
    _,engine,client=server
    first=client.post('/api/chat/customer',json=dict(message='Laptop A',sessionId='cust-session-1'),headers=KEY).json()
    second=client.post('/api/chat/customer',json=dict(message='Pin máy đó?',sessionId='cust-session-1'),headers=KEY).json()
    assert (first['replyText'],second['replyText'])==('customer:1','customer:2')
    # Same id on the admin channel or another id starts empty; no id is stateless.
    assert client.post('/api/chat/admin',json=dict(query='Q',sessionId='cust-session-1'),headers=KEY).json()['insight']=='admin:1'
    assert client.post('/api/chat/customer',json=dict(message='Q',sessionId='cust-session-2'),headers=KEY).json()['replyText']=='customer:1'
    assert client.post('/api/chat/customer',json=dict(message='Q'),headers=KEY).json()['replyText']=='customer:1'
    assert client.post('/api/chat/customer',json=dict(message='Q'),headers=KEY).json()['replyText']=='customer:1'


def test_session_expiry_limit_and_invalid_id(server):
    api_server,_,client=server
    store=api_server.SessionStore(ttl=60,limit=2)
    for i in range(3):store.put(('customer',str(i)),dict(n=i))
    assert store.get(('customer','0'))=={} and store.get(('customer','2'))==dict(n=2)
    store.ttl=-1;assert store.get(('customer','2'))=={}
    assert client.post('/api/chat/customer',json=dict(message='Q',sessionId='x'),headers=KEY).status_code==400


def test_answers_reach_the_web_without_citations_or_internal_paths(server,monkeypatch):
    api_server,engine,client=server
    answer=('OLED dùng điểm ảnh tự phát sáng.\n\n[Nguồn: tech-oled-basics-v1.md, mục OLED là gì?, đoạn 1, phiên bản 1]\n\n'
            'OLED dùng các điểm ảnh tự phát sáng.\n\n[Nguồn: glossary-oled-v1.md, mục OLED, đoạn 1, phiên bản 1]\n\nIPS là tấm nền LCD.')
    monkeypatch.setattr(engine,'ask',lambda *a,**k:dict(answer=answer,sources=[dict(source='tech-oled-basics-v1.md')],profile={}))
    body=client.post('/api/chat/customer',json=dict(message='OLED?'),headers=KEY).json()
    assert body['replyText']=='OLED dùng điểm ảnh tự phát sáng.\n\nIPS là tấm nền LCD.'
    assert 'sources' not in body
    two=api_server.for_reader('Doanh thu thuần tháng 8/2026: 1.000 VND.\n\nDoanh thu thuần tháng 9/2026: 2.000 VND.')
    assert '1.000' in two and '2.000' in two
    sql='Doanh thu thuần kỳ 2026-09: 1.189.908.000 VND.\n\nTính trực tiếp bằng SQL trên database shop (data/business_sql/scenario_v1/shop.sqlite, dữ liệu mô phỏng); chưa có thuế.'
    monkeypatch.setattr(engine,'ask',lambda *a,**k:dict(answer=sql,profile={}))
    insight=client.post('/api/chat/admin',json=dict(query='Doanh thu?'),headers=KEY).json()['insight']
    assert '1.189.908.000 VND' in insight and 'data/' not in insight and 'shop.sqlite' not in insight


@pytest.fixture
def shop_db(tmp_path):
    path=tmp_path/'shop.sqlite'
    con=sqlite3.connect(path)
    con.execute('CREATE TABLE products(sku TEXT,name TEXT,price INTEGER)')
    con.executemany('INSERT INTO products VALUES(?,?,?)',[(f'hash{i}',f'Laptop {i}',1000*i) for i in range(1,8)])
    con.commit();con.close()
    return path


def product_source(sku):return dict(document_id=f'catalog-{sku}',doc_type='product',title='Tên trong tài liệu')


def test_products_come_from_the_database_in_answer_order(server,monkeypatch,shop_db):
    api_server,engine,client=server
    monkeypatch.setattr(api_server,'db_path',shop_db)
    monkeypatch.setattr(engine,'ask',lambda *a,**k:dict(answer='Có.',sources=[product_source('hash2'),product_source('hash1'),product_source('hash2'),
        product_source('khong-co'),dict(document_id='tech-oled',doc_type='buying_guide')],rows=[dict(name='Laptop 3',price=999999)],profile={}))
    body=client.post('/api/chat/customer',json=dict(message='So sánh'),headers=KEY).json()
    assert body['products']==[dict(sku='hash3',name='Laptop 3',price=3000),dict(sku='hash2',name='Laptop 2',price=2000),dict(sku='hash1',name='Laptop 1',price=1000)]


def test_products_stop_at_five_and_are_empty_without_product_sources(server,monkeypatch,shop_db):
    api_server,engine,client=server
    monkeypatch.setattr(api_server,'db_path',shop_db)
    monkeypatch.setattr(engine,'ask',lambda *a,**k:dict(answer='Có.',sources=[product_source(f'hash{i}') for i in range(1,8)],profile={}))
    assert [p['sku'] for p in client.post('/api/chat/customer',json=dict(message='Laptop'),headers=KEY).json()['products']]==[f'hash{i}' for i in range(1,6)]
    monkeypatch.setattr(engine,'ask',lambda *a,**k:dict(answer='Chào bạn',sources=[],profile={}))
    assert client.post('/api/chat/customer',json=dict(message='Chào'),headers=KEY).json()['products']==[]


def test_a_broken_product_lookup_never_loses_the_answer(server,monkeypatch,tmp_path):
    api_server,engine,client=server
    broken=tmp_path/'broken.sqlite';sqlite3.connect(broken).close()
    monkeypatch.setattr(api_server,'db_path',broken)
    monkeypatch.setattr(engine,'ask',lambda *a,**k:dict(answer='Vẫn trả lời.',sources=[product_source('hash1')],profile={}))
    body=client.post('/api/chat/customer',json=dict(message='Laptop'),headers=KEY).json()
    assert body['replyText']=='Vẫn trả lời.' and body['products']==[]


def test_health_reports_an_empty_knowledge_store(server,monkeypatch):
    api_server,_,client=server
    monkeypatch.setattr(api_server,'knowledge_documents',254)
    assert client.get('/health').json()['status']=='healthy'
    monkeypatch.setattr(api_server,'knowledge_documents',0)
    body=client.get('/health').json()
    assert body['status']=='degraded' and body['knowledgeDocuments']==0


def test_no_cors_by_default_and_errors_do_not_leak(server,monkeypatch):
    api_server,engine,client=server
    response=client.options('/api/chat/customer',headers={'Origin':'https://evil.example','Access-Control-Request-Method':'POST'})
    assert 'access-control-allow-origin' not in response.headers
    def boom(*a,**k):raise RuntimeError('C:/secret/path.db')
    monkeypatch.setattr(engine,'ask',boom)
    response=client.post('/api/chat/admin',json=dict(query='Q'),headers=KEY)
    assert response.status_code==500 and 'secret' not in response.text
    assert 'database' not in client.get('/health').json()
