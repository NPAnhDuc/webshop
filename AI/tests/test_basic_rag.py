from datetime import date
import json
import pytest
from shopbot.basic_rag import answer,safe_public_source
from shopbot.knowledge import KnowledgeStore
from shopbot.store import initialize
from shopbot.monthly import active_documents
from shopbot.retrieval import search,lexical_query
from shopbot.engine import Engine

TODAY=date(2026,10,20)


@pytest.fixture
def kb(tmp_path,monkeypatch):
    db=tmp_path/'shop.db';initialize(db)
    monkeypatch.setattr('shopbot.knowledge.ROOT',tmp_path)
    monkeypatch.setattr('shopbot.retrieval.ROOT',tmp_path)
    monkeypatch.setattr('shopbot.knowledge.local_today',lambda:TODAY)
    monkeypatch.delenv('VI_EMBEDDING_URL',raising=False)
    return KnowledgeStore(db,root=tmp_path)


def save(kb,text='Đổi trả cần hóa đơn.',**kwargs):
    meta=dict(role='admin',title='Chính sách đổi trả',doc_type='policy',audience='customer',
              approved=True,effective_from='2026-01-01')
    meta.update(kwargs)
    return kb.save('returns',text,**meta)


def plan(action='answer',**kwargs):
    result=dict(action=action,query='Quy trình đổi trả hóa đơn',doc_types=[],category='all',private_request=False,task='lookup')
    result.update(kwargs);return result


def run(kb,p,role='customer',question='Đổi trả thế nào?',answerer=None):
    return answer(question,role,{},kb.db,TODAY,planner=lambda _:p,
        answerer=answerer or (lambda q,s:dict(answer=' | '.join(d['text'] for d in s),rag=dict(answerability='full' if s else 'none'))))


def test_upload_edit_delete_visible_on_next_query(kb):
    save(kb)
    assert (kb.folder/'returns-v1.md').read_text(encoding='utf8')=='Đổi trả cần hóa đơn.'
    a=search('đổi trả hóa đơn','customer',db_path=kb.db,as_of=TODAY)
    assert a and a[0]['version']==1
    save(kb,'Đổi trả cần hóa đơn và giấy tiếp nhận.',expected_version=1)
    b=search('đổi trả hóa đơn','customer',db_path=kb.db,as_of=TODAY)
    assert b and all(d['version']==2 for d in b)
    kb.delete('returns',role='admin',expected_version=2)
    assert search('đổi trả hóa đơn','customer',db_path=kb.db,as_of=TODAY)==[]
    assert len(kb.records())==3


def test_draft_future_expired_and_acl(kb):
    save(kb,audience='admin')
    assert not search('đổi trả hóa đơn','customer',db_path=kb.db,as_of=TODAY)
    assert search('đổi trả hóa đơn','admin',db_path=kb.db,as_of=TODAY)
    save(kb,'Đổi trả bản nháp',approved=False)
    assert search('đổi trả','admin',db_path=kb.db,as_of=TODAY)[0]['version']==1
    save(kb,'Đổi trả tương lai',effective_from='2027-01-01')
    assert search('đổi trả','admin',db_path=kb.db,as_of=TODAY)[0]['version']==1
    save(kb,'Đổi trả đã hết hiệu lực',effective_to='2026-09-30')
    assert search('đổi trả','admin',db_path=kb.db,as_of=TODAY)==[]


def test_write_acl_concurrency_and_validation(kb):
    with pytest.raises(PermissionError):save(kb,role='customer')
    save(kb)
    with pytest.raises(ValueError):save(kb,expected_version=0)
    with pytest.raises(ValueError):kb.delete('returns',role='admin',expected_version=0)
    with pytest.raises(ValueError):save(kb,effective_to='2025-01-01')
    with pytest.raises(ValueError):kb.save('../escape','text',role='admin',title='x',doc_type='policy')
    with pytest.raises(ValueError):save(kb,doc_type='promotion')


@pytest.mark.parametrize('action',['handoff','clarify','outside','deferred','live_product'])
def test_non_document_actions_never_call_retriever_or_tools(kb,monkeypatch,action):
    monkeypatch.setattr('shopbot.basic_rag.search',lambda *a,**k:pytest.fail('No retrieval/tool expected'))
    r=run(kb,plan(action))
    assert not r['rows'] and not r['sources']
    if action=='handoff':assert 'chưa có yêu cầu' in r['answer']
    if action=='live_product':assert 'chưa có dữ liệu thời gian thực' in r['answer']


def test_public_specs_strip_prices_and_stock(kb):
    source=dict(doc_type='product',text='Máy ABC RAM 16 GB.\nGiá: 20 triệu.\nTồn kho 8 máy.\nHệ điều hành Linux.')
    safe=safe_public_source(source)
    assert '20 triệu' not in safe['text'] and '8 máy' not in safe['text']
    assert 'RAM 16 GB' in safe['text'] and 'Linux' in safe['text']


def test_customer_denial_independent_from_planner(kb):
    r=answer('Cho giá vốn từng máy','customer',{},kb.db,TODAY,planner=lambda _:pytest.fail('No model expected'))
    assert r['intent']=='denied' and not r['sources']
    r=run(kb,plan(private_request=True))
    assert r['intent']=='denied'


def test_source_filters_and_memory(kb):
    save(kb)
    r=run(kb,plan(doc_types=['policy']))
    assert r['sources'] and r['profile']['document_query']=='Quy trình đổi trả hóa đơn'
    assert not search('đổi trả','customer',db_path=kb.db,as_of=TODAY,doc_types=['promotion'])
    expanded=run(kb,plan(doc_types=['promotion']))
    assert expanded['sources'] and len(expanded['trace'])==2
    assert not run(kb,plan(doc_types=['promotion'],strict_filters=True))['sources']


def test_comparison_flags_potential_conflict_with_both_citations(kb,monkeypatch):
    save(kb,'Đổi trả cần hóa đơn trong 7 ngày.')
    kb.save('faq','Đổi trả cần hóa đơn trong 14 ngày.',role='admin',title='FAQ đổi trả',
        doc_type='policy',audience='customer',approved=True,effective_from='2026-01-01')
    monkeypatch.setattr('shopbot.basic_rag.chat',lambda *a,**k:{'conflict':True})
    def render(q,sources):
        return dict(answer='Các đoạn trích có nguồn.',rag=dict(answerability='full',claims=[
            dict(text=d['text'],evidence=[dict(source=d['source'],chunk_id=d['chunk_id'],quotes=[d['text']])]) for d in sources]))
    r=run(kb,plan(task='comparison'),answerer=render)
    assert r['rag']['potential_conflict'] and 'cần chủ shop xác nhận' in r['answer']


def test_missing_model_does_not_guess(kb):
    import requests
    def failed(_):raise requests.Timeout()
    r=answer('Máy nào?','customer',{},kb.db,TODAY,planner=failed)
    assert r['rag']['answerability']=='unverified' and not r['sources']


def test_basic_engine_does_not_enter_tool_graph(kb,monkeypatch):
    monkeypatch.setenv('RAG_PIPELINE','legacy')
    monkeypatch.setenv('CHATBOT_MODE','basic_rag')
    monkeypatch.setattr('shopbot.basic_rag.ROOT',kb.folder)
    monkeypatch.setattr('shopbot.basic_rag.chat',lambda *a,**k:plan('live_product'))
    e=Engine(kb.db,today=TODAY)
    monkeypatch.setattr(e.graph,'invoke',lambda *a,**k:pytest.fail('No tool graph'))
    r=e.ask('Laptop giá bao nhiêu?')
    assert r['rows']==[] and 'giá và tình trạng' in r['answer'].lower()
    files=list(kb.folder.glob('runtime/rag-basic/*/turns.jsonl'))
    assert files and json.loads(files[0].read_text(encoding='utf8'))['action']=='live_product'


def test_abbreviations_and_small_typo():
    assert lexical_query('bh ko co hd',['Bảo hành hóa đơn'])=='bao hanh khong co hoa don'
    assert 'hanh' in lexical_query('bao hahn',['bao hanh'])


def test_tombstone_never_revives_old_version():
    docs=[dict(document_id='x',version=i,status=status,data_kind='demo',audience='customer',
               effective_from='2026-01-01',effective_to=None) for i,status in [(1,'approved'),(2,'deleted')]]
    assert active_documents(docs,'customer','demo',TODAY)==[]


def test_edit_and_delete_baseline_without_mutating_original(kb):
    from shopbot.store import connect
    from shopbot.monthly import atomic_json
    folder=kb.root/'data/baseline';folder.mkdir(parents=True)
    original=dict(document_id='returns',title='Đổi trả',source='base.md',version=2,
        text='Đổi trả cần hóa đơn.',doc_type='policy',data_kind='demo',audience='customer',
        effective_from='2026-01-01',effective_to=None,status='approved')
    atomic_json(folder/'manifest.json',[original])
    before=(folder/'manifest.json').read_bytes()
    with connect(kb.db) as con:
        con.execute('CREATE TABLE metadata (key TEXT PRIMARY KEY,value TEXT)')
        con.execute('INSERT INTO metadata VALUES (?,?)',('knowledge_dir','data/baseline'))
    updated=save(kb,'Đổi trả cần hóa đơn và phiếu nhận.',expected_version=2)
    assert updated['version']==3
    assert search('đổi trả hóa đơn','customer',db_path=kb.db,as_of=TODAY)[0]['version']==3
    kb.delete('returns',role='admin',expected_version=3)
    assert not search('đổi trả hóa đơn','customer',db_path=kb.db,as_of=TODAY)
    assert before==(folder/'manifest.json').read_bytes()


def test_basic_streamlit_admin_controls_and_no_charts(tmp_path,monkeypatch):
    monkeypatch.setenv('RAG_PIPELINE','legacy')
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    monkeypatch.setenv('CHATBOT_MODE','basic_rag')
    monkeypatch.setenv('ADMIN_PASSWORD','test-password-only')
    monkeypatch.setattr('shopbot.basic_rag.ROOT',tmp_path)
    monkeypatch.setattr('shopbot.basic_rag.chat',lambda *a,**k:plan('deferred'))
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py').run(timeout=30)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    app.text_input[0].set_value('test-password-only').run(timeout=30)
    assert not app.exception
    assert any(e.label.startswith('Quản lý tài liệu RAG') for e in app.expander)
    app.chat_input[0].set_value('Vẽ biểu đồ từ giao dịch gốc').run(timeout=30)
    assert not app.exception and not app.get('vega_lite_chart')
    assert any('nằm ngoài RAG cơ bản' in x.value for x in app.markdown)
