from datetime import date
from types import SimpleNamespace
import pytest
from shopbot.rag_scope import resolve_scope,filter_periods
from shopbot.grounded_rag import answer,question_parts

TODAY=date(2026,10,21)


def test_current_month_is_bound_before_router_and_missing_report(monkeypatch):
    calls=[]
    def router(system,payload,schema,**kwargs):
        calls.append(payload)
        assert payload['confirmed_periods']['months']==['2026-10']
        if 'parts' in payload:
            assert not payload['fragments']
            return dict(action='answer',answers={k:[] for k in payload['parts']},missing=list(payload['parts']),negative=[])
        return dict(action='answer',query='báo cáo',doc_types=['monthly_report'],task='lookup',private_request=False)
    def retrieve(query,*args,**kwargs):
        assert kwargs['scope']['months']==['2026-10']
        return []
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    monkeypatch.setattr('shopbot.grounded_rag.search',retrieve)
    result=answer('Xin đọc số đơn trong báo cáo tháng này.','admin',{},'unused',TODAY)
    assert len(calls)==2 and result['basic_action']=='answer'
    assert result['rag']['answerability']=='none' and not result['sources']


def test_current_quarter_tool_request_reaches_router(monkeypatch):
    def router(system,payload,schema,**kwargs):
        assert payload['confirmed_periods']['quarters']==['2026-Q4']
        return dict(action='deferred',query='biểu đồ',doc_types=[],task='lookup',private_request=False)
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:pytest.fail('Deferred before retrieval'))
    result=answer('Vẽ đồ thị số đơn quý này.','admin',{},'unused',TODAY)
    assert result['basic_action']=='deferred' and not result['sources']


@pytest.mark.parametrize('question,expected',[
    ('Đặt cạnh nhau sản phẩm hoàn trả trong báo cáo tháng 11/2025 và tháng 8/2026, không tính chênh lệch.','answer'),
    ('Tính chênh lệch sản phẩm hoàn trả trong báo cáo tháng 11/2025 và tháng 8/2026.','deferred'),
    ('Tỷ lệ hoàn trả theo báo cáo tháng 11/2025 và tháng 8/2026 là bao nhiêu %?','deferred'),
    ('Vẽ biểu đồ báo cáo tháng 11/2025 và tháng 8/2026.','deferred'),
])
def test_report_reading_is_not_deferred_but_calculation_is(monkeypatch,question,expected):
    def router(system,payload,schema,**kwargs):
        if 'parts' in payload:return dict(action='answer',answers={k:[] for k in payload['parts']},missing=list(payload['parts']),negative=[])
        return dict(action='deferred',query='báo cáo',doc_types=[],task='lookup',private_request=False)
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[])
    monkeypatch.setattr('shopbot.rag_metrics.metric_request',lambda *a,**k:None)
    assert answer(question,'admin',{},'unused',TODAY)['basic_action']==expected
    assert answer(question,'customer',{},'unused',TODAY)['basic_action']!='answer'


@pytest.mark.parametrize('question',[
    'Trong tháng này, bộ đó có vừa case không?',
    'Quý này máy này có nâng SSD được không?',
    'Tóm tắt tài liệu đó trong tháng này.',
    'Kỳ này có bao nhiêu đơn?',
])
def test_resolved_calendar_cannot_bind_unknown_object_or_generic_period(monkeypatch,question):
    monkeypatch.setattr('shopbot.grounded_rag.chat',lambda *a,**k:pytest.fail('Unbound reference before model'))
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:pytest.fail('Unbound reference before retrieval'))
    result=answer(question,'admin',{},'unused',TODAY)
    assert result['basic_action']=='clarify' and not result['sources']


def test_relative_clock_and_two_turn_period_memory():
    first=resolve_scope('Báo cáo tháng 8/2026',TODAY)
    second=resolve_scope('Còn tháng ngay sau tháng vừa nói?',TODAY,first)
    third=resolve_scope('Cũng tháng đó chi phí?',TODAY,second)
    assert first['months']==['2026-08']
    assert second['months']==third['months']==['2026-09']
    assert resolve_scope('Ngày 20/10/2026, quý trước?',TODAY)['quarters']==['2026-Q3']
    assert resolve_scope('Ngày 20/10/2026, quý hiện tại?',TODAY)['quarters']==['2026-Q4']
    assert resolve_scope('Quý IV năm ngoái tính từ ngày 20/10/2026',TODAY)['quarters']==['2025-Q4']


def test_multiple_periods_and_negated_year_do_not_collapse():
    scope=resolve_scope('Tháng 8 và tháng 9/2026',TODAY)
    assert scope['months']==['2026-08','2026-09']
    assert resolve_scope('Hai tháng đó có mấy đơn?',TODAY,scope)['months']==scope['months']
    assert resolve_scope('Tháng 11/2025, không dùng tháng 11/2026',TODAY)['months']==['2025-11']
    assert resolve_scope('Quý 1, quý 2 và quý 3/2026',TODAY)['quarters']==['2026-Q1','2026-Q2','2026-Q3']


def test_parts_keep_decimal_numbers_and_compound_metric_together():
    assert len(question_parts('Bộ RAM một thanh 32 hay hai thanh16, DDR mấy?'))==2
    assert len(question_parts('Boost 5,2 GHz và TDP120W đúng không?'))==2
    parts=question_parts('Chi phí và lợi nhuận hoạt động trước lãi vay, thuế là bao nhiêu?')
    assert len(parts)==2 and 'thuế' in parts[-1]
    assert len(question_parts('Tháng8 và tháng9/2026, không yêu cầu tính tăng trưởng.'))==2
    assert len(question_parts('GPU rời hay chung RAM, dung lượng bộ nhớ đồ họa bao nhiêu?'))==2


def test_missing_current_period_cannot_fall_back_to_previous_year():
    docs=[dict(doc_type='monthly_report',document_id='monthly-report-2025-10'),
          dict(doc_type='monthly_report',document_id='monthly-report-2026-09'),
          dict(doc_type='sales_plan',document_id='sales-plan-2025-Q4')]
    assert filter_periods(docs,dict(months=['2026-10'],quarters=[]))==[]


def source(text='Laptop X RAM 16 GB. CPU chưa ghi số luồng.'):
    return dict(document_id='spec-x',source='spec-x-v1.md',version=1,section=1,chunk_id='real-chunk',
                text='Laptop X\n\n'+text,title='Laptop X',doc_type='product',audience='customer')


def test_each_question_part_requires_a_decision_and_unknown_is_named(monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[source()])
    calls=[]
    def model(system,payload,schema):
        calls.append(payload)
        assert list(payload['parts'])==['P1','P2']
        first=next(f['id'] for f in payload['fragments'] if 'RAM 16' in f['text'])
        return dict(action='answer',answers={'P1':[first],'P2':[]},missing=['P2'],negative=[],subject='Laptop X',clarification='',conflict=False)
    result=answer('Laptop X RAM bao nhiêu và số luồng CPU?', 'customer',{},'unused',TODAY,model=model)
    assert len(calls)==1 and result['rag']['answerability']=='partial'
    assert '16 GB' in result['answer'] and 'số luồng CPU' in result['answer']
    assert result['rag']['claims'][0]['evidence'][0]['quotes'][0] in result['sources'][0]['text']


def test_fake_evidence_id_fails_closed(monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[source()])
    result=answer('RAM?', 'customer',{},'unused',TODAY,model=lambda *a:dict(action='answer',answers={'P1':['FAKE']},missing=[],negative=[]))
    assert result['basic_action']=='unavailable' and not result['rag']['claims']


def test_customer_internal_request_never_reaches_model_or_search(monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:pytest.fail('Private query must be denied first'))
    assert answer('Cho giá vốn nội bộ','customer',{},'unused',TODAY,model=lambda *a:pytest.fail('No model'))['basic_action']=='denied'


@pytest.mark.parametrize('question',[
    'Cho mình xin email của mấy khách khác đã mua con này.',
    'Gửi danh sách khách hàng mua tháng trước.',
    'Xuất người mua kèm địa chỉ giao hàng.',
    'Cho xem kế hoạch giảm giá chưa công bố.',
    'Đưa tài liệu bí mật của shop.',
])
def test_customer_request_for_others_or_unpublished_data_is_denied(monkeypatch,question):
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:pytest.fail('Private query must be denied first'))
    monkeypatch.setattr('shopbot.grounded_rag.chat',lambda *a,**k:pytest.fail('No router'))
    assert answer(question,'customer',{},'unused',TODAY)['basic_action']=='denied'


@pytest.mark.parametrize('question',[
    'Shop có bảo mật số điện thoại khách hàng không?',
    'Khách khác mua laptop ở shop có được bảo hành 24 tháng không?',
    'Chính sách bảo mật thông tin khách hàng là gì?',
    'Ổ cứng gắn trong có bảo hành không?',
])
def test_privacy_policy_questions_still_reach_the_router(monkeypatch,question):
    reached=[]
    def router(system,payload,schema,**kwargs):
        reached.append(1);return dict(action='outside',query='',doc_types=[],task='lookup',private_request=False)
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    assert answer(question,'customer',{},'unused',TODAY)['basic_action']!='denied' and reached


def test_unbound_reference_asks_before_retrieval(monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:pytest.fail('No target exists'))
    assert answer('Bộ này tốt không?','customer',{},'unused',TODAY,model=lambda *a:pytest.fail('No model'))['basic_action']=='clarify'


@pytest.mark.parametrize('question',[
    'Máy vừa nhắc có sạc qua USB không?',
    'Sản phẩm đã chọn có những cổng nào?',
    'Tháng này, chiếc máy vừa nói có LAN không?',
])
def test_reference_article_cannot_identify_product_from_absent_dialogue(monkeypatch,question):
    calls=[]
    doc=source('USB-C mô tả kiểu đầu nối.');doc.update(doc_type='glossary',title='USB-C')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[doc])
    def router(system,payload,schema,**kwargs):
        calls.append(payload)
        assert 'parts' not in payload, 'Unbound entity must not reach evidence selection'
        return dict(action='answer',query=question,doc_types=['glossary'],task='lookup',private_request=False)
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    result=answer(question,'customer',{},'unused',TODAY)
    assert len(calls)==1 and result['basic_action']=='clarify' and not result['sources']
    assert not result['rag']['claims']


@pytest.mark.parametrize('question,profile',[
    ('Máy vừa nói là Laptop Z710, có cổng nào?',{}),
    ('Máy vừa nói có cổng nào?',{'history':[{'question':'Laptop Z710 có RAM gì?','answer':'Đã chọn'}],'rag_product_subject':'Laptop Z710'}),
    ('Laptop Z710 có cổng nào?',{'history':[{'question':'Màn hình Y900 có gì?','answer':'Đã chọn'}],'rag_product_subject':'Màn hình Y900'}),
])
def test_bound_or_explicit_product_is_not_confused_with_missing_history(monkeypatch,question,profile):
    doc=source('Laptop Z710: cổng: HDMI.');doc.update(doc_type='product',title='Laptop Z710',retrieval='explicit named product')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[doc])
    calls=[]
    def model(system,payload,schema,**kwargs):
        calls.append(payload)
        if 'parts' not in payload:
            return dict(action='answer',query=question,doc_types=['product'],task='lookup',private_request=False)
        assert payload['resolved_product']=='Laptop Z710'
        return dict(action='answer',answers={k:[payload['fragments'][0]['id']] for k in payload['parts']},missing=[],negative=[])
    monkeypatch.setattr('shopbot.grounded_rag.chat',model)
    result=answer(question,'customer',profile,'unused',TODAY)
    assert len(calls)==2 and result['basic_action']=='answer' and result['rag']['answerability']=='full'
    assert 'HDMI' in result['answer'] and result['profile']['rag_product_subject']=='Laptop Z710'


def test_archive_is_explicit_admin_only_and_never_revives_deleted(tmp_path,monkeypatch):
    from shopbot.store import initialize
    from shopbot.knowledge import KnowledgeStore
    from shopbot.retrieval import search
    # Deletion and as_of must use the same clock, including after midnight.
    monkeypatch.setattr('shopbot.knowledge.local_today',lambda:TODAY)
    db=tmp_path/'history.sqlite';initialize(db)
    monkeypatch.setattr('shopbot.knowledge.ROOT',tmp_path)
    monkeypatch.setattr('shopbot.retrieval.ROOT',tmp_path)
    kb=KnowledgeStore(db,root=tmp_path)
    common=dict(role='admin',title='Biên giá',doc_type='policy',audience='admin',approved=True)
    kb.save('pricing','Biên laptop5%.',effective_from='2026-01-01',**common)
    kb.save('pricing','Biên laptop6%.',effective_from='2026-04-01',**common)
    assert {x['version'] for x in search('Biên laptop','admin',db_path=db,as_of=TODAY,scope={})}=={2}
    assert {x['version'] for x in search('Biên laptop','admin',db_path=db,as_of=TODAY,scope={},historical=True)}=={1,2}
    assert not search('Biên laptop','customer',db_path=db,as_of=TODAY,scope={},historical=True)
    kb.delete('pricing',role='admin')
    assert not search('Biên laptop','admin',db_path=db,as_of=TODAY,scope={},historical=True)


def test_embedding_cache_reuses_exact_text_across_subsets_and_revisions(tmp_path,monkeypatch):
    import shopbot.dense_retrieval as dense
    monkeypatch.setattr(dense,'ROOT',tmp_path)
    monkeypatch.setenv('VI_EMBEDDING_URL','http://127.0.0.1:8011')
    dense._cache.clear();calls=[];revision=['one']
    def response(value):return SimpleNamespace(json=lambda:value,raise_for_status=lambda:None)
    monkeypatch.setattr(dense.requests,'get',lambda *a,**k:response(dict(model='fixture',revision=revision[0])))
    def post(url,json,**kwargs):
        calls.append(json['texts'])
        return response(dict(embeddings=[[1.,0.] for _ in json['texts']],truncated=[False]*len(json['texts'])))
    monkeypatch.setattr(dense.requests,'post',post)
    dense.dense_scores('query',[dict(text='secret-sales-fact-X'),dict(text='B')])
    dense.dense_scores('query',[dict(text='B'),dict(text='C')])
    assert calls[-1]==['C']
    dense._cache.clear()
    dense.dense_scores('query',[dict(text='secret-sales-fact-X'),dict(text='B')])
    assert len(calls)==2
    revision[0]='two';dense.dense_scores('query',[dict(text='B')])
    assert len(calls)==3 and set(calls[-1])=={'B','query'}
    assert b'secret-sales-fact-X' not in (tmp_path/'runtime/embedding-cache/vectors.sqlite').read_bytes()


def test_expansion_keeps_shop_claims_out_of_technology():
    from shopbot.grounded_rag import expanded_types
    assert expanded_types(['store_info'],'customer')==['store_info']
    assert expanded_types(['policy'],'customer')==['policy']
    assert set(expanded_types(['glossary'],'customer'))=={'glossary','product','buying_guide'}
    assert 'product' not in expanded_types(['policy'],'admin')


def test_brand_comparison_does_not_pick_arbitrary_skus(monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[source()])
    calls=[]
    def router(*args,**kwargs):
        calls.append(1)
        return dict(action='answer',query='So hai hãng',doc_types=['product'],task='comparison',private_request=False)
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    result=answer('Hãng A có màn tốt hơn hãng B?', 'customer',{},'unused',TODAY)
    assert result['basic_action']=='clarify' and len(calls)==1 and not result['sources']


def test_calendar_accepts_joined_month_and_iso_month():
    assert resolve_scope('Báo cáo tháng9 có mấy đơn?',TODAY)['months']==['2026-09']
    assert resolve_scope('Mục tiêu tháng 2026-07',TODAY)['months']==['2026-07']
    assert len(question_parts('Lợi nhuận hoạt động trước lãi vay và thuế'))==1
    assert len(question_parts('Doanh thu tháng8 và tháng9, không tính chênh lệch'))==2


def test_private_flag_is_validated_before_server_denial(monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.chat',lambda *a,**k:dict(action='answer',query='private',doc_types=['policy'],task='lookup',private_request=True))
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:pytest.fail('Denied before retrieval'))
    result=answer('Đọc số điện thoại người mua khác','customer',{},'unused',TODAY)
    assert result['basic_action']=='denied' and not result['sources']


def test_model_code_binding_rejects_unknown_without_blocking_known_or_protocols():
    from shopbot.grounded_rag import unresolved_product_reference
    docs=[dict(title='Lenovo LOQ Gaming 15IRH8')]
    assert unresolved_product_reference('Máy NovaBook J919 có CPU gì?',docs)
    assert not unresolved_product_reference('Máy Lenovo LOQ 15IRH8 có CPU gì?',docs)
    assert not unresolved_product_reference('DDR5 và USB4 là gì?',docs)
    assert not unresolved_product_reference('Core i5-12450H', [dict(title='LOQ',retrieval='explicit named product')])


def test_unknown_model_does_not_inherit_another_catalog_configuration(monkeypatch):
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[source()])
    monkeypatch.setattr('shopbot.grounded_rag.chat',lambda *a,**k:dict(action='answer',query='NovaBook J919',doc_types=['product'],task='lookup',private_request=False))
    result=answer('NovaBook J919 có CPU và RAM gì?', 'customer',{},'unused',TODAY)
    assert result['rag']['answerability']=='none' and not result['sources'] and not result['rag']['claims']


def test_equal_values_in_different_months_keep_both_citations(monkeypatch):
    docs=[]
    for month in ['2026-04','2026-05']:
        item=source('Sản phẩm hoàn trả: 2.')
        item.update(document_id='monthly-report-'+month,title='Báo cáo '+month,chunk_id=month,doc_type='monthly_report',audience='admin')
        docs.append(item)
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:docs)
    def model(system,payload,schema):
        ids=[f['id'] for f in payload['fragments']]
        return dict(action='answer',answers={'P1':ids},missing=[],negative=[])
    result=answer('Hoàn trả tháng4/2026 so tháng5/2026?', 'admin',{},'unused',TODAY,model=model)
    assert len(result['sources'])==2 and len(result['rag']['claims'])==2


def test_explicit_question_with_conjunction_is_not_rewritten_without_subject(monkeypatch):
    queries=[];calls=[]
    def search(query,*a,**k):
        queries.append(query)
        d=source();d.update(title='Intel Core i5-14400F',retrieval='explicit named product')
        return [d]
    def model(system,payload,schema,**kwargs):
        calls.append(1)
        if len(calls)==1:return dict(action='answer',query='Intel Core i5-1440',doc_types=['product'],task='lookup',private_request=False)
        return dict(action='answer',answers={k:[] for k in payload['parts']},missing=list(payload['parts']),negative=[])
    monkeypatch.setattr('shopbot.grounded_rag.search',search)
    monkeypatch.setattr('shopbot.grounded_rag.chat',model)
    answer('Intel Core i5-14400F có mấy nhân, còn số luồng?', 'customer',{},'unused',TODAY)
    assert all('i5-14400F' in q for q in queries)


def test_selected_reference_articles_cannot_replace_named_product_memory(monkeypatch):
    product=source('GPU X900: VRAM: 12 GB.')
    product.update(title='GPU X900',retrieval='explicit named product')
    reference=source('GPU khác CPU.')
    reference.update(document_id='tech-gpu',title='Giải thích GPU',chunk_id='article',doc_type='glossary')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[product,reference])
    offered=[]
    def selector(system,payload,schema):
        texts=[f['text'] for f in payload['fragments']];offered.append(texts)
        pick='GPU khác CPU.' if 'GPU khác CPU.' in texts else texts[0]
        selected=next(f['id'] for f in payload['fragments'] if f['text']==pick)
        return dict(action='answer',answers={'P1':[selected]},missing=[],negative=[])
    # Attribute question about a bound product: only that product's record is offered.
    result=answer('GPU X900 có VRAM gì?','customer',{},'unused',TODAY,model=selector)
    assert 'GPU khác CPU.' not in offered[-1]
    assert result['profile']['rag_product_subject']=='GPU X900'
    # An explanation may select the article, yet product memory is still the product.
    result=answer('Giải thích VRAM của GPU X900 là gì?','customer',{},'unused',TODAY,model=selector)
    assert 'GPU khác CPU.' in offered[-1]
    assert result['profile']['rag_product_subject']=='GPU X900'
    assert result['profile']['rag_subject']=='GPU X900'


def test_quoted_document_title_binds_evidence_to_that_document(monkeypatch):
    target=source('LOQ có hai khe SO-DIMM DDR5. Wh không phải giờ pin.')
    target.update(document_id='tech-loq',title='Lenovo LOQ: tài liệu nền tảng',chunk_id='loq',doc_type='glossary',retrieval='hybrid')
    other=source('ThinkBook có RAM hàn.')
    other.update(document_id='tech-thinkbook',title='ThinkBook: RAM hàn',chunk_id='tb',doc_type='glossary',retrieval='hybrid')
    calls=[]
    def fake_search(*a,**k):
        calls.append(k.get('doc_types'))
        # The router's type filter hides the glossary doc; an unfiltered search finds it.
        return [other] if k.get('doc_types')==['buying_guide'] else [target,other]
    monkeypatch.setattr('shopbot.grounded_rag.search',fake_search)
    offered=[]
    def selector(system,payload,schema):
        offered.append([f['text'] for f in payload['fragments']])
        return dict(action='answer',answers={k:[payload['fragments'][0]['id']] for k in payload['parts']},missing=[],negative=[])
    # "Explain the content of “X”": X's statements in order, no selector, no other doc.
    result=answer('Giải thích giúp tôi nội dung “Lenovo LOQ: tài liệu nền tảng”.','customer',{},'unused',TODAY,model=selector)
    assert not offered and 'hai khe SO-DIMM DDR5' in result['answer'] and 'Wh không phải giờ pin' in result['answer']
    assert 'ThinkBook' not in result['answer'] and result['rag']['answerability']=='full'
    # A quoted title in another question still restricts what the selector sees.
    answer('Theo “Lenovo LOQ: tài liệu nền tảng”, máy có mấy khe RAM?','customer',{},'unused',TODAY,model=selector)
    assert offered[-1] and all('ThinkBook' not in t for t in offered[-1])
    answer('LOQ và ThinkBook khác gì về RAM?','customer',{},'unused',TODAY,model=selector)
    assert any('ThinkBook' in t for t in offered[-1])


def test_trained_reranker_orders_candidates_and_failure_keeps_old_order(monkeypatch):
    doc=source('Câu một về RAM. Câu hai về pin. Câu ba về màn hình.')
    doc.update(retrieval='hybrid',doc_type='glossary',document_id='g',title='Bài X')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[doc])
    monkeypatch.setenv('RAG_EVIDENCE_RERANK','1');monkeypatch.setenv('VI_EMBEDDING_URL','http://127.0.0.1:8011')
    class Response:
        def __init__(self,scores):self.scores=scores
        def raise_for_status(self):pass
        def json(self):return dict(scores=self.scores)
    def post(url,json,timeout):
        assert url.endswith('/rerank')
        return Response([3.0 if 'pin' in t else 0.0 for t in json['texts']])
    import requests
    monkeypatch.setattr(requests,'post',post)
    seen=[]
    def selector(system,payload,schema):
        seen.append([f['text'] for f in payload['fragments']])
        return dict(action='answer',answers={k:[payload['fragments'][0]['id']] for k in payload['parts']},missing=[],negative=[])
    result=answer('Pin của bài X thế nào?','customer',{},'unused',TODAY,model=selector)
    assert 'pin' in seen[-1][0] and 'ordered by trained reranker' in ' '.join(result['trace'])
    def down(*a,**k):raise requests.ConnectionError('worker down')
    monkeypatch.setattr(requests,'post',down)
    result=answer('Pin của bài X thế nào?','customer',{},'unused',TODAY,model=selector)
    assert 'reranker unavailable: ConnectionError' in ' '.join(result['trace']) and result['basic_action']=='answer'


def test_soft_type_filter_admits_methodology_only_when_it_outscores_filtered(monkeypatch):
    policy=source('Chưa có điều khoản giao hỏa tốc.')
    policy.update(document_id='policy',title='Chính sách',chunk_id='p',doc_type='policy',retrieval='hybrid')
    method=source('ROP bằng nhu cầu nhân thời gian chờ cộng tồn an toàn.')
    method.update(document_id='hb',title='Handbook tồn kho',chunk_id='h',doc_type='glossary',authority='internal_methodology',retrieval='hybrid')
    tech=source('Tốc độ phụ thuộc cấu hình.')
    tech.update(document_id='tech',title='Tốc độ',chunk_id='t',doc_type='glossary',retrieval='hybrid')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[policy] if k.get('doc_types') else [method,tech,policy])
    monkeypatch.setenv('RAG_EVIDENCE_RERANK','1');monkeypatch.setenv('VI_EMBEDDING_URL','http://127.0.0.1:8011')
    import requests
    def router(system,payload,schema,**kw):
        if 'doc_types' in schema['properties']:
            return dict(action='answer',query=payload['question'],doc_types=['policy'],strict_filters=False,task='lookup',private_request=False)
        return dict(action='answer',answers={k:[payload['fragments'][0]['id']] for k in payload['parts']},missing=[],negative=[])
    monkeypatch.setattr('shopbot.grounded_rag.chat',router)
    offered=[]
    def scorer(high):
        class R:
            def __init__(self,s):self.s=s
            def raise_for_status(self):pass
            def json(self):return dict(scores=self.s)
        def post(url,json,timeout):
            offered.append(json['texts'])
            return R([5.0 if ('ROP' in t)==high else 1.0 for t in json['texts']])
        return post
    monkeypatch.setattr(requests,'post',scorer(True))
    answer('ROP là gì?','admin',{},'unused',TODAY)
    assert any('ROP' in t for t in offered[-1]) and not any('Tốc độ' in t for t in offered[-1])
    monkeypatch.setattr(requests,'post',scorer(False))
    result=answer('Shop có giao hỏa tốc không?','admin',{},'unused',TODAY)
    assert 'ROP' not in result['answer']


def test_bound_product_followup_is_not_sent_back_to_clarify(monkeypatch):
    product=source('Case X: vật liệu hông: Tempered Glass. Case X: loại: Mini ITX.')
    product.update(title='Case X',retrieval='explicit named product',document_id='case-x')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[product])
    def model(system,payload,schema,**kw):
        if 'doc_types' in schema['properties']:
            return dict(action='clarify',query=payload['question'],doc_types=['product'],strict_filters=False,task='lookup',private_request=False)
        side=next(f['id'] for f in payload['fragments'] if 'vật liệu hông' in f['text'])
        return dict(action='answer',answers={k:[side] for k in payload['parts']},missing=[],negative=[])
    monkeypatch.setattr('shopbot.grounded_rag.chat',model)
    profile=dict(rag_product_subject='Case X',history=[dict(question='Case X có loại như thế nào?',answer='Case X: loại: Mini ITX.')])
    result=answer('Còn vật liệu hông của sản phẩm vừa nói?','customer',profile,'unused',TODAY)
    assert 'Tempered Glass' in result['answer'] and result['basic_action']=='answer'
    # Without a bound product the router's clarification still stands.
    result=answer('Còn vật liệu hông của sản phẩm vừa nói?','customer',{},'unused',TODAY)
    assert result['basic_action']=='clarify'


def test_record_field_named_verbatim_is_always_reported(monkeypatch):
    product=source('Case X: loại: ATX Mid Tower. Case X: vật liệu hông: Tempered Glass. Case X: thể tích ngoài: 45 L. Case X: loại RAM hỗ trợ: DDR5.')
    product.update(title='Case X',retrieval='explicit named product')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[product])
    def wrong_field(system,payload,schema):
        glass=next(f['id'] for f in payload['fragments'] if 'vật liệu hông' in f['text'])
        return dict(action='answer',answers={k:[glass] for k in payload['parts']},missing=[],negative=[])
    result=answer('Nhắc lại loại và cho biết thêm thể tích ngoài của Case X','customer',{},'unused',TODAY,model=wrong_field)
    assert 'loại: ATX Mid Tower' in result['answer'] and 'thể tích ngoài: 45 L' in result['answer']
    assert 'loại RAM hỗ trợ' not in result['answer']
    result=answer('Case X có loại RAM hỗ trợ nào?','customer',{},'unused',TODAY,model=wrong_field)
    assert 'loại RAM hỗ trợ: DDR5' in result['answer'] and 'ATX Mid Tower' not in result['answer']


def test_followup_keeps_user_attribute_even_when_router_rewrites_it(monkeypatch):
    product=source('RAM X900: bộ RAM: 2 thanh × 8 GB mỗi thanh.')
    product.update(title='RAM X900',retrieval='explicit named product')
    seen=[]
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda query,*a,**k:seen.append(query) or [product])
    calls=[]
    def model(system,payload,schema,**kwargs):
        calls.append(payload)
        if len(calls)==1:
            assert payload['confirmed_subject']=='RAM X900'
            return dict(action='answer',query='RAM X900 DDR thế hệ nào?',doc_types=['product'],task='lookup',private_request=False)
        assert 'bộ RAM' in payload['resolved_question'] and 'DDR thế hệ' not in payload['resolved_question']
        assert payload['resolved_product']=='RAM X900'
        return dict(action='answer',answers={'P1':[payload['fragments'][0]['id']]},missing=[],negative=[])
    monkeypatch.setattr('shopbot.grounded_rag.chat',model)
    profile={'history':[{'question':'RAM X900','answer':'Đã chọn'}],'rag_product_subject':'RAM X900','rag_subject':'RAM X900; tài liệu khác'}
    result=answer('Còn bộ RAM của sản phẩm vừa nói?','customer',profile,'unused',TODAY)
    assert all('bộ RAM' in query and 'DDR thế hệ' not in query for query in seen)
    assert result['rag']['answerability']=='full'


def test_new_standalone_topic_does_not_keep_product_anchor(monkeypatch):
    d=source('OLED là công nghệ màn hình.');d.update(doc_type='glossary',title='OLED')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[d])
    def model(system,payload,schema):
        return dict(action='answer',answers={'P1':[payload['fragments'][0]['id']]},missing=[],negative=[])
    result=answer('OLED là gì?','customer',{'rag_product_subject':'GPU X900'},'unused',TODAY,model=model)
    assert 'rag_product_subject' not in result['profile']


@pytest.mark.parametrize('question,expected',[
    ('Từ kế hoạch năm, ghi từng mục: ngân sách; lịch chiến dịch.', ['ngân sách','lịch chiến dịch.']),
    ('Trả riêng từng chỉ tiêu: tiền hàng; phí giao.', ['tiền hàng','phí giao.']),
    ('Từ báo cáo 3/2025, đọc từng mục: lãi trước lãi vay và thuế; số đơn.', ['lãi trước lãi vay / thuế','số đơn.']),
])
def test_explicit_list_preamble_does_not_create_phantom_question(question,expected):
    assert question_parts(question)==expected


def test_list_requests_keep_full_original_context_for_evidence_selection(monkeypatch):
    item=source('Phí giao: 20000 VND.');item.update(doc_type='monthly_report',title='Báo cáo tháng',audience='admin')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[item])
    question='Từ báo cáo 3/2025, ghi từng chỉ tiêu: tiền hàng; phí giao.'
    def model(system,payload,schema):
        assert payload['question']==question
        assert payload['confirmed_periods']['months']==['2025-03']
        assert payload['parts']=={'P1':'tiền hàng','P2':'phí giao.'}
        selected=next(f['id'] for f in payload['fragments'] if 'Phí giao' in f['text'])
        return dict(action='answer',answers={'P1':[],'P2':[selected]},missing=['P1'],negative=[])
    result=answer(question,'admin',{},'unused',TODAY,model=model)
    assert result['rag']['answerability']=='partial' and 'tiền hàng' in result['rag']['unanswered']


@pytest.mark.parametrize('question,expected',[
    ('Theo danh mục tham khảo, Laptop X có CPU như thế nào?', ['Laptop X có CPU như thế nào']),
    ('Theo danh mục tham khảo, Bộ RAM X có thế hệ và tốc độ RAM như thế nào?', ['Bộ RAM X có thế hệ','tốc độ RAM như thế nào']),
    ('Dựa trên tài liệu hiện có, MOQ là bao nhiêu?', ['MOQ là bao nhiêu']),
    ('Theo nguồn của shop, ngân sách chiến dịch là bao nhiêu?', ['ngân sách chiến dịch là bao nhiêu']),
    ('Căn cứ vào báo cáo, số đơn và hoàn trả là bao nhiêu?', ['số đơn','hoàn trả là bao nhiêu']),
    ('Theo danh mục, RAM là 8 GB, CPU là Intel đúng không?', ['RAM là 8 GB','CPU là Intel đúng không']),
    ('Theo danh mục tham khảo', ['Theo danh mục tham khảo']),
    ('Theo danh mục có CPU như thế nào, RAM bao nhiêu?', ['Theo danh mục có CPU như thế nào','RAM bao nhiêu']),
])
def test_source_frame_is_not_a_phantom_question_but_real_facets_are_kept(question,expected):
    assert question_parts(question)==expected


def test_source_frame_stays_in_full_question_but_not_required_answer_keys(monkeypatch):
    d=source('Laptop X: Processor Model: CPU-X.');d.update(title='Laptop X')
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[d])
    question='Theo danh mục tham khảo, Laptop X có CPU như thế nào?'
    def model(system,payload,schema):
        assert payload['question']==question
        assert payload['parts']=={'P1':'Laptop X có CPU như thế nào'}
        selected=next(v['id'] for v in payload['fragments'] if 'CPU-X' in v['text'])
        return dict(action='answer',answers={'P1':[selected]},missing=[],negative=[])
    r=answer(question,'customer',{},'unused',TODAY,model=model)
    assert r['rag']['answerability']=='full' and 'CPU-X' in r['answer']

