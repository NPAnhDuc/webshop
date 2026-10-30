from datetime import date
import pytest
from shopbot.agent_tools import CatalogTools,AgentTools
from shopbot.agent_conversation import CatalogConversation
from shopbot.catalog_planner import StagedCatalogPlanner,product_fact_request
from shopbot.engine import Engine
from shopbot.store import initialize

CATALOG=[dict(ref='P1',name='Acer Aspire 3 A315-59-56VC'),dict(ref='P2',name='MSI GeForce RTX 3060 Ventus 2X 12G'),
         dict(ref='P3',name='Corsair RM750e (2025)'),dict(ref='P4',name='Acer Aspire 3')]


@pytest.mark.parametrize('question,expected',[
    ('Acer Aspire 3 A315-59-56VC RAM bao nhiêu GB?',('P1','ram_gb')),
    ('acer aspire 3 a315-59-56vc pin được mấy Wh vậy',('P1','battery_wh')),
    ('Máy Acer Aspire 3 A315-59-56VC dùng loại RAM gì, DDR4 hay DDR5?',('P1','ram_type')),
    ('MSI GeForce RTX 3060 Ventus 2X 12G VRAM bao nhiêu GB?',('P2','vram_gb')),
    ('MSI GeForce RTX 3060 Ventus 2X 12G cần nguồn công suất bao nhiêu W?',('P2','recommended_psu_w')),
    ('Corsair RM750e (2025) công suất bao nhiêu W?',('P3','psu_watt')),
    ('Acer Aspire 3 A315-59-56VC nặng bao nhiêu?',('P1','weight_kg')),
])
def test_one_named_product_and_field_bind_exactly(question,expected):
    assert product_fact_request(question,CATALOG)==expected


@pytest.mark.parametrize('question',[
    'Acer Aspire 3 A315-59-56VC có tốt không?',                          # no known field
    'So sánh Acer Aspire 3 A315-59-56VC với Corsair RM750e (2025) RAM',  # two products
    'Acer Aspire 3 A315-59-56VC so với máy khác RAM thế nào?',          # comparison
    'Tìm 3 laptop RAM 16GB dưới 20 triệu',                               # no product named
    'Mua 2 máy Acer Aspire 3 A315-59-56VC RAM 8GB',                       # purchase operands
    'Acer Aspire 5 RAM bao nhiêu?',                                      # not in catalog
])
def test_other_requests_keep_the_routed_path(question):
    assert product_fact_request(question,CATALOG) is None


def test_nested_shorter_name_is_the_same_mention():
    # "Acer Aspire 3" is inside the longer exact model name; still one product.
    assert product_fact_request('Acer Aspire 3 A315-59-56VC RAM bao nhiêu GB?',CATALOG)[0]=='P1'
    assert product_fact_request('Acer Aspire 3 RAM bao nhiêu GB?',CATALOG)==('P4','ram_gb')


def planner_payload(question,role='customer'):
    return dict(question=question,role=role,today='2026-10-23',previous_filters={},last_selection=[],history=[],catalog=CATALOG)


@pytest.mark.parametrize('routed',['documents','search','clarify','compare','outside'])
def test_fact_lookup_overrides_public_routes_without_slot_model(routed):
    calls=[]
    def caller(system,data,schema,**kwargs):
        calls.append(data);return dict(action=routed)
    plan=StagedCatalogPlanner(caller)(planner_payload('Acer Aspire 3 A315-59-56VC RAM bao nhiêu GB?'))
    assert (plan['action'],plan['product_refs'],plan['fact_fields'])==('facts',['P1'],['ram_gb'])
    assert len(calls)==1


@pytest.mark.parametrize('routed',['admin','handoff'])
def test_admin_and_handoff_routes_are_kept(routed):
    plan=StagedCatalogPlanner(lambda *a,**k:dict(action=routed))(planner_payload('Acer Aspire 3 A315-59-56VC RAM bao nhiêu GB?','admin'))
    assert plan['action']==routed and 'fact_fields' not in plan


def catalog_tools():
    products=[dict(id='id1',name='Máy Một',slug='may-1',category='laptop',brand='B',status='active',
                   variants=[dict(id='v1',sku='S1',name='default',price=10_000_000,status='active',available_qty=2)],
                   specs=dict(ram_gb=8,supported_form_factors=['ATX','mATX']),api_path='/api/products/may-1',product_page_url=None),
              dict(id='id2',name='Máy Hai',slug='may-2',category='laptop',brand='B',status='inactive',
                   variants=[],specs={},api_path='/api/products/may-2',product_page_url=None)]
    return CatalogTools(dict(schema='agent-catalog-v1',data_kind='simulation',captured_at='2026-10-23',source={'path':'fixture'},products=products))


def test_tool_reports_missing_and_rejects_unknown_fields_or_products():
    tools=catalog_tools()
    data=tools.product_facts('id1',['ram_gb','battery_wh'])['data']
    assert data['facts']==[dict(field='ram_gb',value=8,missing=False),dict(field='battery_wh',value=None,missing=True)]
    for args in [('id1',['price']),('id1',[]),('id1',['ram_gb','ram_gb']),('id2',['ram_gb']),('nope',['ram_gb'])]:
        with pytest.raises(ValueError):tools.product_facts(*args)


def plan(**changes):
    result=dict(action='facts',budget_max_vnd=0,budget_inclusive=False,limit=0,category='',brand='',continuation=False,
                clear_brand=False,unsupported_filters=False,product_refs=['P1'],fact_fields=['ram_gb'])
    result.update(changes);return result


@pytest.fixture
def make_agent(tmp_path,monkeypatch):
    db=tmp_path/'shop.db';initialize(db)
    monkeypatch.setenv('CHATBOT_MODE','agent_tools')
    return lambda planner:Engine(db,today=date(2026,10,23),tool_agent=CatalogConversation(AgentTools(catalog_tools(),db),planner))


def test_answer_renders_exact_value_and_never_fills_missing(make_agent):
    r=make_agent(lambda p:plan(fact_fields=['ram_gb','battery_wh','supported_form_factors'])).ask('Máy Một RAM, pin, mainboard?')
    assert r['basic_action']=='answer' and r['intent']=='facts'
    assert '- RAM: 8 GB' in r['answer'] and '- Chuẩn mainboard hỗ trợ: ATX, mATX' in r['answer']
    assert '- Pin: chưa có thông tin trong bản ghi' in r['answer'] and 'Wh' not in r['answer']
    assert [c['tool'] for c in r['tool_evidence']['calls']]==['catalog.product_facts'] and r['sources']


@pytest.mark.parametrize('bad',[
    dict(fact_fields=['price']),dict(product_refs=['P1','P2']),dict(product_refs=[]),
    dict(action='search'),
])
def test_invalid_fact_plans_are_rejected(make_agent,bad):
    r=make_agent(lambda p:plan(**bad)).ask('Máy Một RAM bao nhiêu?')
    assert r['basic_action']=='unavailable' and 'tool_evidence' not in r


def test_customer_role_can_read_public_facts_but_plan_cannot_widen_role(make_agent):
    r=make_agent(lambda p:plan()).ask('Máy Một RAM bao nhiêu?',role='customer')
    assert r['tool_evidence']['calls'][0]['arguments']==dict(product_id='id1',fields=['ram_gb'])
