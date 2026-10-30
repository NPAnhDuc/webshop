from datetime import date
import pytest
from shopbot.agent_tools import AgentTools,CatalogTools,GroundedDocuments
from shopbot.agent_conversation import CatalogConversation
from shopbot.engine import Engine
from shopbot.store import initialize


def fake_rag(action='answer',answerability='full',text='DDR5 là thế hệ RAM kế tiếp DDR4. [Nguồn: glossary-ddr5-v1.md]'):
    seen=[]
    def answer(question,role,profile,db,today):
        seen.append(dict(question=question,role=role,profile=profile,db=db,today=today))
        return dict(answer=text,basic_action=action,rag=dict(answerability=answerability),
                    sources=[dict(title='DDR5 là gì?',version=1)] if answerability=='full' else [])
    answer.seen=seen
    return answer


@pytest.mark.parametrize('action,answerability,status,executed',[
    ('answer','full','answered',True),('answer','partial','answered',True),('answer','none','no_source',True),
    ('denied',None,'denied',True),('clarify',None,'clarify',True),('unavailable',None,'unavailable',False),
])
def test_rag_outcomes_map_to_honest_statuses(action,answerability,status,executed):
    rag=fake_rag(action,answerability)
    out=GroundedDocuments('db.sqlite',date(2026,10,23),rag)('DDR5 là gì?','customer')
    assert (out['status'],out['executed'])==(status,executed)
    # Stateless: no catalog/admin memory reaches retrieval; server date and role pass through.
    assert rag.seen[0]['profile']=={} and rag.seen[0]['role']=='customer' and rag.seen[0]['today']==date(2026,10,23)


def test_worker_outage_is_reported_not_answered():
    import requests
    def down(*args):raise requests.ConnectionError('8011 refused')
    out=GroundedDocuments('db',date(2026,10,23),down)('DDR5 là gì?','customer')
    assert out['status']=='unavailable' and out['executed'] is False and out['sources']==[]
    assert 'Chưa truy xuất được nguồn tài liệu' in out['reason']


def test_configured_documents_are_enabled_and_traced():
    tools=AgentTools(None,None,documents=GroundedDocuments('db',date(2026,10,23),fake_rag()))
    cap=next(c for c in tools.capabilities('customer') if c['name']=='documents.answer')
    assert cap['status']=='enabled' and cap['configured']
    with tools.capture_calls() as calls:
        out=tools.execute('customer','documents.answer',{'question':'DDR5 là gì?'})
    assert out['status']=='answered' and calls[0]['status']=='success'
    # Argument validation still runs before the configured answerer.
    with pytest.raises(ValueError):tools.execute('customer','documents.answer',{'question':'x','sql':'drop'})
    with pytest.raises(PermissionError):tools.execute('owner','documents.answer',{'question':'x'})


def base_plan(**changes):
    result=dict(action='documents',budget_max_vnd=0,budget_inclusive=False,limit=0,category='',brand='',continuation=False,
                clear_brand=False,unsupported_filters=False,product_refs=[])
    result.update(changes);return result


@pytest.fixture
def make_agent(tmp_path,monkeypatch):
    db=tmp_path/'shop.db';initialize(db)
    products=[dict(id=f'id{i}',name=f'RAM {i}',slug=f'ram-{i}',category='ram',brand='B',status='active',
                   variants=[dict(id=f'v{i}',sku=f'S{i}',name='default',price=price,status='active',available_qty=3)],
                   specs={},api_path=f'/api/products/ram-{i}',product_page_url=None)
              for i,price in enumerate([1_000_000,2_000_000])]
    catalog=CatalogTools(dict(schema='agent-catalog-v1',data_kind='simulation',captured_at='2026-10-23',source={'path':'fixture'},products=products))
    monkeypatch.setenv('CHATBOT_MODE','agent_tools')
    def make(planner,rag):
        tools=AgentTools(catalog,db,documents=GroundedDocuments(db,date(2026,10,23),rag))
        return Engine(db,today=date(2026,10,23),tool_agent=CatalogConversation(tools,planner))
    return make


def test_documents_route_returns_sourced_answer(make_agent):
    r=make_agent(lambda p:base_plan(),fake_rag()).ask('DDR5 là gì?')
    assert r['basic_action']=='answer' and r['intent']=='documents' and 'glossary-ddr5' in r['answer']
    assert r['sources']==[dict(title='DDR5 là gì?',version=1)]
    assert r['capability_status']['executed'] is True


def test_bare_reference_binds_to_users_prior_knowledge_clause(make_agent):
    from shopbot.catalog_planner import bare_reference,prior_knowledge_clause
    assert bare_reference('Chỉ giải thích thuật ngữ thôi') and not bare_reference('DDR5 nghĩa là gì?')
    history=[dict(question='Tìm3thanhRAMdưới3triệu và giải thích DDR5',answer='OLED là ... (bot prose ignored)')]
    assert prior_knowledge_clause(history)=='giải thích DDR5'
    rag=fake_rag()
    engine=make_agent(lambda p:base_plan(),rag)
    r=engine.ask('Chỉ giải thích thuật ngữ thôi',profile=dict(history=history))
    assert rag.seen[0]['question']=='giải thích DDR5' and r['basic_action']=='answer'


def test_bare_reference_without_prior_topic_asks(make_agent):
    rag=fake_rag()
    r=make_agent(lambda p:base_plan(),rag).ask('Chỉ giải thích thuật ngữ thôi')
    assert r['basic_action']=='clarify' and rag.seen==[] and 'thuật ngữ hoặc chính sách nào' in r['answer']


def test_no_source_is_reported_without_invented_policy(make_agent):
    text='Chưa có nguồn đủ để xác nhận: Hóa đơn VAT của shop được xuất khi nào.'
    r=make_agent(lambda p:base_plan(),fake_rag('answer','none',text)).ask('Hóa đơn VAT xuất khi nào?')
    assert r['answer']==text and r['sources']==[] and r['tool_evidence']['calls'][0]['output']['status']=='no_source'


def test_mixed_request_answers_both_parts_with_both_sources(make_agent):
    plan=base_plan(action='search',budget_max_vnd=3_000_000,limit=2,category='ram',knowledge_question='giải thích DDR5')
    r=make_agent(lambda p:plan,fake_rag()).ask('Tìm 2 thanh RAM dưới 3 triệu và giải thích DDR5')
    assert [c['tool'] for c in r['tool_evidence']['calls']]==['catalog.search','documents.answer']
    assert not r['partial'] and r['components']['documents']['status']=='answered'
    assert 'Tìm thấy 2/2' in r['answer'] and 'Phần “giải thích DDR5”: DDR5 là thế hệ' in r['answer']
    assert len(r['sources'])==2


def test_mixed_request_with_no_document_source_stays_partial(make_agent):
    plan=base_plan(action='search',budget_max_vnd=3_000_000,limit=2,category='ram',knowledge_question='giải thích XYZ')
    r=make_agent(lambda p:plan,fake_rag('answer','none','Chưa có nguồn đủ để xác nhận: XYZ.')).ask('Tìm 2 thanh RAM dưới 3 triệu và giải thích XYZ')
    assert r['partial'] and 'Chưa có nguồn' in r['answer']
