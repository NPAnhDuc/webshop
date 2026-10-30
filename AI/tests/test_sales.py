import pytest
from shopbot.sales import advise,validate,rank_candidates
from shopbot.store import CustomerTools,initialize,connect
from shopbot.engine import Engine


def decision(changes=None,**kwargs):
    return dict(reset=False,changes=changes or {},clear=[],action='recommend',indices=[],
                needs_benchmark=False,**kwargs)


@pytest.fixture
def customer(tmp_path):
    db=tmp_path/'shop.db'
    initialize(db)
    return CustomerTools(db)


def ask(customer,changes=None,profile=None,**kwargs):
    d=decision(changes)
    d.update(kwargs)
    q='tư vấn '
    if changes:
        if 'max_price' in changes:q+=f" tối đa {changes['max_price']/1_000_000} triệu"
        if 'min_ram' in changes:q+=f" RAM {changes['min_ram']}GB"
        if 'max_weight' in changes:q+=f" nặng tối đa {changes['max_weight']}kg"
    return advise(q,profile or {},customer,planner=lambda _:d,ranker=lambda q,p,rows:(rows[:3],False))


def test_budget_stock_and_evidence(customer):
    r=ask(customer,dict(category='laptop',max_price=19_000_000,min_ram=16,panel='OLED'))
    assert [v['sku'] for v in r['rows']]==['DEMO-A']
    assert '18.900.000 đ' in r['answer'] and '70 Wh' in r['answer']
    assert all('cost' not in v for v in r['rows'])


def test_followup_retains_then_clears_constraints(customer):
    a=ask(customer,dict(category='laptop',max_price=20_000_000,panel='OLED',usage='study'))
    b=ask(customer,dict(max_price=15_000_000),a['profile'])
    assert not b['rows'] and b['profile']['sales_requirements']['panel']=='OLED'
    c=ask(customer,profile=b['profile'],clear=['panel'])
    assert [v['sku'] for v in c['rows']]==['DEMO-C']
    assert c['profile']['sales_requirements']['usage']=='study'


def test_empty_match_does_not_relax_and_unknown_weight_excluded(customer):
    r=ask(customer,dict(category='laptop',max_price=1_000_000))
    assert r['sales']['status']=='no_match' and not r['rows']
    with connect(customer.path) as db:
        db.execute("UPDATE products SET weight=NULL WHERE sku='DEMO-A'")
    r=ask(customer,dict(category='laptop',max_weight=1.4))
    assert [v['sku'] for v in r['rows']]==['DEMO-C','DEMO-E']


def test_named_sold_out_not_recommended(customer):
    d=decision(dict(category='laptop',max_price=20_000_000));d['action']='detail'
    r=advise('DEMO-F còn hàng?',{},customer,planner=lambda _:d)
    assert r['rows'][0]['stock']==0 and 'hết hàng' in r['answer']
    assert 'Nếu ưu tiên' not in r['answer']


def test_comparison_references_and_price_difference(customer):
    a=ask(customer,dict(category='laptop',max_price=20_000_000))
    b=ask(customer,profile=a['profile'],action='compare',indices=[1,2])
    assert len(b['rows'])==2 and '4.000.000 đ' in b['answer']
    c=ask(customer,action='compare',indices=[2])
    assert c['sales']['status']=='clarify' and not c['rows']


def test_category_brand_ram_and_budget_conflict(customer):
    a=ask(customer,dict(category='mouse'))
    assert not a['rows']
    r=ask(customer,dict(category='laptop',brand='không tồn tại'))
    assert not r['rows']
    assert not ask(customer,dict(category='laptop',min_ram=64))['rows']
    r=ask(customer,profile={'sales_requirements':{'category':'laptop','min_price':20_000_000,'max_price':10_000_000}})
    assert r['sales']['status']=='clarify'


def test_game_performance_not_invented(customer):
    r=ask(customer,dict(category='laptop',usage='gaming',max_price=25_000_000),needs_benchmark=True)
    assert r['rows'] and 'chưa cam kết FPS' in r['answer']
    assert '60 FPS' not in r['answer']


def test_reset_and_missing_category(customer):
    a=ask(customer,dict(category='laptop',brand='ASUS'))
    b=ask(customer,dict(max_price=20_000_000),a['profile'],reset=True)
    assert b['sales']['status']=='clarify' and 'brand' not in b['profile']['sales_requirements']


def test_new_filter_does_not_use_stale_rewritten_names(customer):
    d=decision(dict(category='laptop',max_price=1_000_000))
    r=advise('rẻ dưới 1 triệu',{},customer,'Laptop mẫu A OLED 14',planner=lambda _:d)
    assert not r['rows']


@pytest.mark.parametrize('changes',[{'max_price':True},{'max_price':-1},{'panel':'MAGIC'},
    {'category':'internal_admin'},{'min_ram':1000},{'brand':'x'*41},{'max_weight':float('nan')}])
def test_reject_invalid_model_constraints(changes):
    with pytest.raises(ValueError):validate(decision(changes))


def test_engine_uses_sales_and_no_second_unguarded_generation(customer,monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER','ollama')
    monkeypatch.setenv('CONVERSATION_MODE','legacy')
    monkeypatch.setattr('shopbot.sales.chat',lambda *a,**k:decision(dict(category='laptop',max_price=19_000_000)))
    r=Engine(customer.path).ask('Laptop dưới 19 triệu')
    assert r['sales']['status']=='answered' and 'Tư vấn bán hàng local' in r['mode']
    assert r['profile']['last_skus']


def test_ranker_cannot_inject_products(customer,monkeypatch):
    rows=customer.products()
    monkeypatch.setattr('shopbot.sales.chat',lambda *a,**k:{'skus':['FAKE-FREE-GPU']})
    selected,ranked=rank_candidates('gaming',{'usage':'gaming'},rows)
    assert not ranked and selected==rows[:3]
    monkeypatch.setattr('shopbot.sales.chat',lambda *a,**k:{'skus':[rows[-1]['sku'],rows[0]['sku']]})
    selected,ranked=rank_candidates('gaming',{'usage':'gaming'},rows)
    assert ranked and selected==[rows[-1],rows[0]]
