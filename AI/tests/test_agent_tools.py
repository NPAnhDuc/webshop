import copy
import json
import pytest
from shopbot.agent_tools import public_catalog,CatalogTools,AgentTools


def state():
    products=[];inventory={}
    for i in range(7):
        identifier=f'p{i}';variant=f'v{i}'
        products.append(dict(id=identifier,name=f'Laptop {i}',slug=f'laptop-{i}',categorySlug='laptop',
                             brandName='Brand',status='active',price=1,
                             variants=[dict(id=variant,sku=f'SKU{i}',name='default',price=10_000_000+i*1_000_000,
                                            status='active',costPrice=7_654_321)],
                             specs=dict(ram_gb=8+i,weight_kg=1+i/10,private_cost=12345)))
        inventory[variant]=dict(productId=identifier,qtyOnHand=5,qtyReserved=1)
    return dict(products=products,inventory=inventory,orders=[dict(phone='private')],settings=dict(secret='private'))


def catalog(raw=None):
    return CatalogTools(dict(schema='agent-catalog-v1',data_kind='simulation',captured_at='2026-10-23T00:00:00Z',
                             source={'path':'fixture'},products=public_catalog(raw or state())))


def test_public_projection_never_leaks_finance_or_identity_fields():
    encoded=json.dumps(public_catalog(state()))
    assert all(value not in encoded for value in ['costPrice','7654321','private_cost','phone','secret','private'])


def test_budget_is_strict_and_returns_five_distinct_products():
    result=catalog().search(15_000_000,limit=5)['data']
    assert len(result['products'])==5 and len({p['id'] for p in result['products']})==5
    assert all(p['variant']['price']<15_000_000 for p in result['products'])
    assert result['total_matching']==5


def test_never_uses_unavailable_cheap_variant_to_recommend_expensive_available_one():
    raw=state();raw['products'][0]['variants'].append(dict(id='expensive',sku='exp',name='expensive',price=30_000_000,status='active'))
    raw['inventory']['v0']['qtyReserved']=5
    raw['inventory']['expensive']=dict(productId='p0',qtyOnHand=2,qtyReserved=0)
    result=catalog(raw).search(20_000_000)['data']['products']
    assert 'p0' not in {p['id'] for p in result}


def test_short_result_is_reported_instead_of_inventing_products_or_links():
    result=catalog().search(11_000_000,limit=5)
    assert result['data']['returned_count']==1
    assert result['data']['products'][0]['product_page_url'] is None
    assert result['data_kind']=='simulation' and result['data']['products'][0]['api_path']=='/api/products/laptop-0'


def test_comparison_numeric_deltas_and_missing_values_are_deterministic():
    result=catalog().compare(['p0','p1'])['data']
    ram=next(r for r in result['comparison'] if r['field']=='ram_gb')
    panel=next(r for r in result['comparison'] if r['field']=='panel')
    assert ram['second_minus_first']==1
    assert panel['missing']==[True,True] and panel['second_minus_first'] is None
    assert result['winner'] is None
    assert result['comparison'][0]['second_minus_first']==1_000_000


def test_comparison_needs_explicit_variant_when_product_has_multiple_choices():
    raw=state();other=copy.deepcopy(raw['products'][0]['variants'][0]);other.update(id='other',price=30_000_000)
    raw['products'][0]['variants'].append(other)
    c=catalog(raw)
    with pytest.raises(ValueError,match='ambiguous'):c.compare(['p0','p1'])
    result=c.compare(['p0','p1'],variant_ids=['other','v1'])
    assert result['data']['comparison'][0]['values']==[30_000_000,11_000_000]


def test_role_is_not_an_llm_argument_and_customer_cannot_call_finance():
    tools=AgentTools(catalog(),'not-opened.sqlite')
    with pytest.raises(PermissionError):tools.execute('customer','admin.finance',dict(start='2026-01-01',end='2026-02-01'))
    with pytest.raises(ValueError):tools.execute('customer','catalog.search',dict(max_price_exclusive=20_000_000,role='admin'))
    with pytest.raises(ValueError):tools.execute('admin','admin.finance',dict(start='2026-01-01',end='2026-02-01',sql='DROP TABLE sales'))


def test_admin_finance_uses_validated_period_and_server_owned_database(monkeypatch):
    calls=[]
    monkeypatch.setattr('shopbot.agent_tools.analyze_business',lambda db,a,b:calls.append((db,a,b)) or {'totals':{'revenue':10}})
    tools=AgentTools(catalog(),'server-owned.sqlite')
    result=tools.execute('admin','admin.finance',dict(start='2026-01-01',end='2026-02-01'))
    assert calls==[('server-owned.sqlite','2026-01-01','2026-02-01')] and result['totals']['revenue']==10
    with pytest.raises(ValueError):tools.execute('admin','admin.finance',dict(start='2026-02-01',end='2026-01-01'))


def test_invalid_inventory_is_flagged_not_silently_fixed():
    raw=state();raw['inventory']['v0']['qtyReserved']=9
    with pytest.raises(ValueError,match='reconcile'):public_catalog(raw)


def test_snapshot_mutation_does_not_change_the_callers_source():
    raw=state();before=copy.deepcopy(raw);c=catalog(raw)
    response=c.search(20_000_000);response['data']['products'][0]['name']='changed'
    assert raw==before and c.search(20_000_000)['data']['products'][0]['name']=='Laptop 0'


def test_chart_is_admin_only_and_cannot_receive_model_selected_output_path():
    tools=AgentTools(catalog(),'not-opened.sqlite')
    with pytest.raises(PermissionError):tools.execute('customer','admin.finance_chart',dict(start='2026-01-01',end='2026-02-01'))
    with pytest.raises(ValueError):tools.execute('admin','admin.finance_chart',dict(start='2026-01-01',end='2026-02-01',path='outside.png'))
