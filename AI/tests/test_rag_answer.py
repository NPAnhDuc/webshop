import pytest
from shopbot.rag_answer import validate_claim,numbers,synthesize,rerank,evidence_fragments,extractive_synthesize,rewrite_document_query
from shopbot.chunking import chunk_document


def source(text='Biên gộp laptop tối thiểu 6%. Không cộng dồn.',**extra):
    return dict(text=text,source='policy.md',section=1,version=2,heading_path='Giá > Ràng buộc',**extra)


def test_claim_requires_real_span_and_supported_numbers():
    lookup={'S1':source()}
    assert validate_claim(dict(text='Laptop phải giữ biên gộp 6%.',evidence=[dict(id='S1',quote='Biên gộp laptop tối thiểu 6%.')]),lookup)
    assert not validate_claim(dict(text='Laptop có biên 9%.',evidence=[dict(id='S1',quote='Biên gộp laptop tối thiểu 6%.')]),lookup)
    assert not validate_claim(dict(text='Bảo hành 12 tháng.',evidence=[dict(id='S1',quote='Bảo hành 12 tháng.')]),lookup)
    assert not validate_claim(dict(text='Laptop 6%.',evidence=[dict(id='S9',quote='Biên gộp laptop tối thiểu 6%.')]),lookup)
    assert numbers('28 triệu đồng, 6%, 1.539.000.000 VND, 14,5%')==numbers('28000000, 6%, 1539000000, 14.5%')


def test_verifier_rejects_wrong_entity_despite_matching_number(monkeypatch):
    calls=iter([dict(answerability='full',claims=[dict(text='Card đồ họa phải giữ biên 6%.',evidence=[dict(id='S1',quote='Biên gộp laptop tối thiểu 6%.')])],missing=[]),
                dict(complete=False,checks=[dict(index=0,supported=False,relevant=True)])])
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:next(calls))
    result=synthesize('Card đồ họa cần biên bao nhiêu?',[source()])
    assert result['rag']['answerability']=='none' and not result['rag']['claims']
    assert 'Card đồ họa phải giữ' not in result['answer']


def test_multiple_sources_and_partial_answer(monkeypatch):
    calls=iter([dict(answerability='partial',claims=[dict(text='Laptop giữ biên gộp tối thiểu 6%.',evidence=[dict(id='S1',quote='Biên gộp laptop tối thiểu 6%.')]),
                   dict(text='SUP-LAP có lead time 4 ngày.',evidence=[dict(id='S2',quote='SUP-LAP có lead time 4 ngày.')])],missing=['Mức phạt giao chậm chưa rõ']),
                dict(complete=False,checks=[dict(index=0,supported=True,relevant=True),dict(index=1,supported=True,relevant=True)])])
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:next(calls))
    result=synthesize('Biên laptop, lead time và phạt giao chậm?',[source(),source('SUP-LAP có lead time 4 ngày.',data_kind='demo')])
    assert len(result['rag']['claims'])==2 and result['rag']['answerability']=='partial'
    assert result['answer'].count('[Nguồn:')==2 and 'Chưa có đủ thông tin' in result['answer']


def test_missing_or_incomplete_verification_fails_closed(monkeypatch):
    assert synthesize('Bảo hành mấy tháng?',[])['rag']['answerability']=='none'
    calls=iter([dict(answerability='full',claims=[dict(text='Laptop 6%.',evidence=[dict(id='S1',quote='Biên gộp laptop tối thiểu 6%.')])],missing=[]),dict(checks=[])])
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:next(calls))
    result=synthesize('Biên laptop?',[source()])
    assert result['rag']['verified'] is False and 'Laptop 6%' not in result['answer']


def test_reranker_cannot_add_sources_or_duplicate_ids(monkeypatch):
    docs=[source(),source('Nội dung thứ hai.')]
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(ids=['C2','C2']))
    assert all(d['rerank_fallback'] for d in rerank('Hỏi',docs,2))
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(ids=['C2']))
    assert rerank('Hỏi',docs,2)[0]['text']=='Nội dung thứ hai.'


def test_heading_without_blank_lines_and_boilerplate():
    text='# Giá\nDỮ LIỆU MÔ PHỎNG — shop thử.\n## Laptop\nGiữ biên 6%.\n## GPU\nGiữ biên 4%.'
    chunks=chunk_document(dict(source='p.md',text=text))
    lap=next(c for c in chunks if 'Giữ biên 6%' in c['text'])
    gpu=next(c for c in chunks if 'Giữ biên 4%' in c['text'])
    assert lap['heading_path']=='Giá > Laptop' and gpu['heading_path']=='Giá > GPU'
    assert any('DỮ LIỆU MÔ PHỎNG' in c['text'] for c in chunks)
    assert all('DỮ LIỆU MÔ PHỎNG' not in c['retrieval_text'] for c in chunks)


def test_extractive_tables_preserve_headers_and_only_source_rows(monkeypatch):
    docs=[source('Kế hoạch\n\n| Tháng | VND |\n|---|---:|\n| 2026-08 | 10 |\n| 2026-09 | 20 |')]
    fragments=evidence_fragments(docs)
    assert len(fragments)==2 and '| Tháng | VND |' in fragments['S1P2']['text']
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(unanswered=[],ids=['S1P2']))
    result=extractive_synthesize('Tháng 9? ',docs)
    assert '| 2026-09 | 20 |' in result['answer'] and '| 2026-08 | 10 |' not in result['answer']
    assert '| 2026-09 | 20 |\n\n[Nguồn:' in result['answer']
    assert result['rag']['verified'] is True


def test_extractive_unknown_and_invalid_ids_never_fabricate(monkeypatch):
    docs=[source()]
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(unanswered=['Bảo hành mấy tháng?'],ids=[]))
    assert extractive_synthesize('Bảo hành mấy tháng?',docs)['rag']['answerability']=='none'
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(unanswered=[],ids=['FAKE']))
    result=extractive_synthesize('Biên?',docs)
    assert result['rag']['verified'] is False and '6%' not in result['answer']


def test_document_rewrite_keeps_explicit_date_and_asks_on_ambiguity(monkeypatch):
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(question='Biên gộp laptop tháng 8/2026?',ambiguous=False,clarification=''))
    assert rewrite_document_query('Còn tháng 8/2026?','Biên gộp laptop tháng 2/2026?')[0]=='Biên gộp laptop tháng 8/2026?'
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(question='Biên gộp tháng 2/2026?',ambiguous=False,clarification=''))
    assert rewrite_document_query('Còn tháng 8/2026?','Câu cũ')[0]=='Còn tháng 8/2026?'
    monkeypatch.setattr('shopbot.rag_answer.chat',lambda *a:dict(question='',ambiguous=True,clarification='Bạn muốn nói đến chính sách nào?'))
    assert rewrite_document_query('Cái kia?','Hai chính sách')[1]
