from datetime import date
import pytest
from shopbot.agent_tools import CatalogTools,AgentTools
from shopbot.agent_conversation import CatalogConversation
from shopbot.catalog_planner import StagedCatalogPlanner,split_mixed,search_literals
from shopbot.engine import Engine
from shopbot.store import initialize


@pytest.mark.parametrize('question,expected',[
    ('Tìm 3 thanh RAM dưới 3 triệu và giải thích DDR5',('Tìm 3 thanh RAM dưới 3 triệu','giải thích DDR5')),
    ('Tìm laptop dưới 20 triệu, chính sách bảo hành thế nào?',('Tìm laptop dưới 20 triệu','chính sách bảo hành thế nào?')),
    ('Giải thích DDR5 rồi tìm 2 thanh RAM dưới 3 triệu',('tìm 2 thanh RAM dưới 3 triệu','Giải thích DDR5')),
    ('So sánh Acer A315 và Lenovo 15ITL6 rồi giải thích IPS là gì',('So sánh Acer A315 và Lenovo 15ITL6','giải thích IPS là gì')),
    ('Tìm RAM dưới 19,5 triệu và giải thích DDR5',('Tìm RAM dưới 19,5 triệu','giải thích DDR5')),
])
def test_split_keeps_exact_spans_and_every_operand(question,expected):
    catalog,knowledge=split_mixed(question)
    assert (catalog,knowledge)==expected and catalog in question and knowledge in question


@pytest.mark.parametrize('question',[
    'DDR5 nghĩa là gì?','Giải thích DDR5','Tìm cho tôi 3 thanh RAM dưới 3 triệu.',
    'So sánh Acer A315 và Lenovo 15ITL6',
    'Nguồn đó có bao nhiêu SKU và dòng sổ?',
    # Two catalog requests around one explanation: ambiguous, not silently split.
    'Tìm RAM dưới 3 triệu, giải thích DDR5 rồi tìm 2 ổ SSD dưới 2 triệu',
    # No connector: the decimal comma must not become a clause boundary.
    'Tìm RAM dưới 19,5 triệu giải thích DDR5',
    # Policy request that itself names a purchase operand stays one request.
    'Tìm laptop dưới 20 triệu và chính sách khi mua 2 máy',
])
def test_split_declines_single_or_ambiguous_requests(question):
    assert split_mixed(question) is None


def test_monitor_count_is_a_literal_operand():
    assert search_literals('Tìm 2 monitor dưới 5 triệu')[:3]==(5_000_000,False,2)


def payload(question):
    return dict(question=question,role='customer',today='2026-10-23',previous_filters={},last_selection=[],
                history=[],catalog=[dict(ref='P1',name='Acer A315'),dict(ref='P2',name='Lenovo 15ITL6')])


def test_router_prompt_and_choice_are_unchanged_and_search_sees_only_catalog_clause():
    calls=[]
    def caller(system,data,schema,**kwargs):
        calls.append((system,data))
        if len(calls)==1:return dict(action='search')
        return dict(category='ram',brand='',continuation=False,clear_brand=False,extra_requirements=[])
    plan=StagedCatalogPlanner(caller)(payload('Tìm 3 thanh RAM dưới 3 triệu và giải thích DDR5'))
    assert calls[0][1]['question']=='Tìm 3 thanh RAM dưới 3 triệu và giải thích DDR5'
    assert calls[1][1]['request']=='Tìm 3 thanh RAM dưới 3 triệu'
    assert (plan['action'],plan['category'],plan['limit'],plan['budget_max_vnd'])==('search','ram',3,3_000_000)
    assert plan['knowledge_question']=='giải thích DDR5' and not plan['unsupported_filters']


def test_documents_route_with_explicit_catalog_clause_keeps_both_parts():
    def caller(system,data,schema,**kwargs):
        if 'action' in schema['properties']:return dict(action='documents')
        return dict(category='ram',brand='',continuation=False,clear_brand=False,extra_requirements=[])
    plan=StagedCatalogPlanner(caller)(payload('Giải thích DDR5 rồi tìm 2 thanh RAM dưới 3 triệu'))
    assert plan['action']=='search' and plan['limit']==2 and plan['knowledge_question']=='Giải thích DDR5'


def test_compare_clause_keeps_its_verb_and_both_names():
    plan=StagedCatalogPlanner(lambda *a,**k:dict(action='compare'))(
        payload('So sánh Acer A315 và Lenovo 15ITL6 rồi giải thích IPS là gì'))
    assert plan['product_refs']==['P1','P2'] and plan['knowledge_question']=='giải thích IPS là gì'


def test_short_compare_with_ordinals_splits_and_binds_last_selection():
    assert split_mixed('So máy thứ1 với thứ2 và giải thích RAM là gì')==('So máy thứ1 với thứ2','giải thích RAM là gì')
    p=payload('So máy thứ1 với thứ2 và giải thích RAM là gì')
    p['last_selection']=[dict(position=1,ref='P2'),dict(position=2,ref='P1')]
    plan=StagedCatalogPlanner(lambda *a,**k:dict(action='documents'))(p)
    assert plan['action']=='compare' and plan['product_refs']==['P2','P1']


def test_quantity_word_so_is_not_a_comparison_cue():
    assert split_mixed('Số lượng RAM và giải thích DDR5')is None


def test_unsure_router_uses_explicit_split_but_admin_route_is_kept():
    def caller(action):
        def call(system,data,schema,**kwargs):
            if 'action' in schema['properties']:return dict(action=action)
            return dict(category='ram',brand='',continuation=False,clear_brand=False,extra_requirements=[])
        return call
    question='Tìm 3 ram dưới 3000000 đồng và giải thích DDR5 là gì'
    plan=StagedCatalogPlanner(caller('clarify'))(payload(question))
    assert (plan['action'],plan['limit'],plan['budget_max_vnd'])==('search',3,3_000_000)
    assert plan['knowledge_question']=='giải thích DDR5 là gì'
    assert StagedCatalogPlanner(caller('clarify'))(payload('Bạn giúp tôi với'))['action']=='clarify'
    admin=StagedCatalogPlanner(caller('admin'))(dict(payload(question),role='admin'))
    assert admin['action']=='admin' and 'knowledge_question' not in admin


def test_single_intent_plans_have_no_extra_key():
    plan=StagedCatalogPlanner(lambda *a,**k:dict(action='documents'))(payload('DDR5 nghĩa là gì?'))
    assert 'knowledge_question' not in plan


def base_plan(**changes):
    result=dict(action='search',budget_max_vnd=3_000_000,budget_inclusive=False,limit=3,category='ram',brand='',
                continuation=False,clear_brand=False,unsupported_filters=False,product_refs=[])
    result.update(changes);return result


@pytest.fixture
def make_agent(tmp_path,monkeypatch):
    db=tmp_path/'shop.db';initialize(db)
    products=[dict(id=f'id{i}',name=f'RAM {i}',slug=f'ram-{i}',category='ram',brand='Brand',status='active',
                   variants=[dict(id=f'v{i}',sku=f'SKU{i}',name='default',price=price,status='active',available_qty=3)],
                   specs={},api_path=f'/api/products/ram-{i}',product_page_url=None)
              for i,price in enumerate([1_000_000,2_000_000,4_000_000])]
    catalog=CatalogTools(dict(schema='agent-catalog-v1',data_kind='simulation',captured_at='2026-10-23',source={'path':'fixture'},products=products))
    monkeypatch.setenv('CHATBOT_MODE','agent_tools')
    return lambda planner:Engine(db,today=date(2026,10,23),tool_agent=CatalogConversation(AgentTools(catalog,db),planner))


QUESTION='Tìm 3 thanh RAM dưới 3 triệu và giải thích DDR5'


def test_mixed_answer_runs_catalog_and_reports_disabled_documents(make_agent):
    r=make_agent(lambda p:base_plan(knowledge_question='giải thích DDR5')).ask(QUESTION)
    calls=r['tool_evidence']['calls']
    assert [c['tool'] for c in calls]==['catalog.search','documents.answer']
    assert calls[0]['arguments']['limit']==3 and calls[1]['arguments']==dict(question='giải thích DDR5')
    assert len(r['rows'])==2 and 'Tìm thấy 2/3' in r['answer']
    assert r['partial'] and r['components']['documents']['status']=='disabled'
    assert 'Phần “giải thích DDR5”' in r['answer'] and 'chưa được kết nối' in r['answer']
    assert r['tool_evidence']['data']['returned_count']==2


def test_mixed_catalog_clarification_still_reports_knowledge_part(make_agent):
    r=make_agent(lambda p:base_plan(budget_max_vnd=0,knowledge_question='giải thích DDR5')).ask('Tìm 3 thanh RAM và giải thích DDR5')
    assert r['basic_action']=='clarify' and [c['tool'] for c in r['tool_evidence']['calls']]==['documents.answer']
    assert r['partial']


@pytest.mark.parametrize('bad',[
    dict(knowledge_question='giải thích DDR4'),
    dict(knowledge_question=''),
    dict(action='documents',knowledge_question='giải thích DDR5'),
])
def test_knowledge_part_must_be_exact_span_of_catalog_request(make_agent,bad):
    r=make_agent(lambda p:base_plan(**bad)).ask(QUESTION)
    assert r['basic_action']=='unavailable' and 'tool_evidence' not in r
