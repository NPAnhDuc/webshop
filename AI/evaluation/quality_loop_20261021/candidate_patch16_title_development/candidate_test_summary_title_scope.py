from datetime import date
import pytest
from shopbot.grounded_rag import answer,summary_title
from shopbot.knowledge import KnowledgeStore
from shopbot.retrieval import search
from shopbot.store import initialize

TODAY=date(2026,10,21)


@pytest.mark.parametrize('question,task,expected',[
    ('Tóm tắt “Nguồn A, B và C”.','summary','Nguồn A, B và C'),
    ('Đọc "Giới hạn nâng cấp". Điều nào trong đó có điều kiện?','summary','Giới hạn nâng cấp'),
    ('Tóm tắt «Chọn máy».','summary','Chọn máy'),
    ('Tóm tắt “Chọn máy” và so sánh hai laptop.','summary',None),
    ('Đọc “Chọn máy”. Cho biết RAM laptop.','summary',None),
    ('Tóm tắt “Chọn máy”; tìm đơn hàng.','summary',None),
    ('So sánh “A” với “B”.','summary',None),
    ('Tóm tắt “Chọn máy” cho Chip7-9000.','summary',None),
    ('Giá của “Laptop A” hiện tại?','lookup',None),
    ('Tóm tắt bài không có tên cụ thể.','summary',None),
    ('Đọc “dấu ngoặc không đóng.','summary',None),
])
def test_summary_reference_does_not_drop_other_requests(question,task,expected):
    assert summary_title(question,task)==expected


@pytest.fixture
def kb(tmp_path,monkeypatch):
    db=tmp_path/'shop.db';initialize(db)
    monkeypatch.setattr('shopbot.knowledge.ROOT',tmp_path)
    monkeypatch.setattr('shopbot.retrieval.ROOT',tmp_path)
    monkeypatch.setattr('shopbot.knowledge.local_today',lambda:TODAY)
    monkeypatch.delenv('VI_EMBEDDING_URL',raising=False)
    return KnowledgeStore(db,root=tmp_path)


def save(kb,identifier,title,text='Nội dung thông số chỉ cho bản vùng SG.',**options):
    metadata=dict(role='admin',title=title,doc_type='glossary',audience='customer',
                  approved=True,effective_from='2026-01-01')
    metadata.update(options)
    return kb.save(identifier,text,**metadata)


def test_exact_document_identity_survives_incidental_catalog_code_and_type_guess(kb):
    title='Chip7-081SG: chỉ vùng SG'
    save(kb,'catalog','Laptop Chip7',doc_type='product')
    save(kb,'article',title)
    save(kb,'near','Chip7-081SG: bản gần giống')
    result=search('Tóm tắt “'+title+'”.','customer',db_path=kb.db,as_of=TODAY,
                  document_title=title,doc_types=['policy'],scope={'months':[],'quarters':[]})
    assert result and {r['document_id'] for r in result}=={'article'}
    assert not search('Chip7','customer',db_path=kb.db,as_of=TODAY,document_title='Tên chưa có')


def test_exact_title_cannot_override_access_or_active_version(kb):
    title='Tài liệu giới hạn'
    save(kb,'article',title,audience='admin')
    args=dict(db_path=kb.db,as_of=TODAY,document_title=title)
    assert not search(title,'customer',**args)
    assert search(title,'admin',**args)
    save(kb,'article',title,text='Nội dung phiên bản mới.',audience='admin',expected_version=1)
    assert {r['version'] for r in search(title,'admin',**args)}=={2}
    save(kb,'article',title,text='Bản tương lai.',audience='admin',effective_from='2027-01-01',expected_version=2)
    assert {r['version'] for r in search(title,'admin',**args)}=={2}
    kb.delete('article',role='admin',expected_version=3)
    assert not search(title,'admin',**args)


def test_exact_title_cannot_revive_expired_or_draft_document(kb):
    save(kb,'expired','Tài liệu cũ',effective_to='2026-09-30')
    save(kb,'draft','Tài liệu nháp',approved=False)
    for title in ['Tài liệu cũ','Tài liệu nháp']:
        assert not search(title,'admin',db_path=kb.db,as_of=TODAY,document_title=title)


def test_summary_routes_exact_title_through_both_retrieval_passes(kb,monkeypatch):
    title='Nâng cấp của Chip7-081SG'
    save(kb,'article',title)
    observed=[]
    def retrieve(*args,**kwargs):
        observed.append(kwargs.get('document_title'))
        return search(*args,**kwargs)
    def local_model(system,payload,schema,**kwargs):
        if 'parts' not in payload:
            return dict(action='answer',query='tóm tắt',doc_types=['glossary'],task='summary',private_request=False)
        assert payload['sources'] and all(s['title']==title for s in payload['sources'])
        return dict(action='answer',answers={p:[payload['fragments'][0]['id']] for p in payload['parts']},missing=[],negative=[])
    monkeypatch.setattr('shopbot.grounded_rag.search',retrieve)
    monkeypatch.setattr('shopbot.grounded_rag.chat',local_model)
    result=answer('Tóm tắt “'+title+'”.','customer',{},kb.db,TODAY)
    assert observed==[title,title]
    assert result['basic_action']=='answer' and {s['document_id'] for s in result['sources']}=={'article'}
