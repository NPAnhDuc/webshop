from datetime import date
import pytest
from shopbot.conversation import prepare_turn, interval, clean_memory, resolve_time
from shopbot.engine import Engine
from shopbot.store import initialize, connect
from shopbot.store import AdminTools

TODAY=date(2026,10,19)

def plan(intent='top_products',mode='same_period',unit='month',metric='units'):
    return dict(intent=intent,time_mode=mode,period_unit=unit,metric=metric,limit=3,standalone_question='',clarification='')

def prepare(q,memory=None,chosen=None,role='admin',today=TODAY):
    return prepare_turn(q,role,memory or {},today,planner=lambda *args: chosen or plan())

def test_deictic_requires_anchor_and_keeps_pending():
    result=prepare('Tháng đó sản phẩm nào bán chạy?')
    assert result['intent']=='clarify'
    assert result['profile']['pending_intent']=='top_products'
    again=prepare('cái đó ấy',result['profile'],plan('clarify'))
    assert again['profile']['pending_intent']=='top_products'
    resumed=prepare('Tháng 9 năm 2026',again['profile'],plan(mode='explicit'))
    assert resumed['plan']['periods']==[interval(2026,9,'month')]
    assert 'pending_intent' not in resumed['profile']

@pytest.mark.parametrize('month',[2,7,9,12])
def test_deictic_uses_actual_anchor(month):
    result=prepare('Tháng đó sản phẩm nào bán chạy?',{'active_period':interval(2026,month,'month')})
    assert result['plan']['periods'][0]==interval(2026,month,'month')

def test_explicit_replaces_anchor_and_metric_correction_keeps_it():
    a=prepare('Tháng 9 năm 2026 sản phẩm nào bán chạy',{'active_period':interval(2025,12,'month')},plan(mode='explicit'))
    b=prepare('Theo doanh thu cơ',a['profile'],plan(metric='revenue'))
    assert b['plan']['periods']==[interval(2026,9,'month')]
    assert b['plan']['metric']=='revenue'

def test_calendar_relative_and_previous_anchor_are_different():
    memory={'active_period':interval(2026,7,'month')}
    assert prepare('tháng trước',memory,plan(mode='last_month'))['plan']['periods']==[interval(2026,9,'month')]
    assert prepare('kỳ trước đó',memory,plan(mode='previous_period'))['plan']['periods']==[interval(2026,6,'month')]
    assert prepare('tháng trước',chosen=plan(mode='last_month'),today=date(2026,1,2))['plan']['periods']==[interval(2025,12,'month')]
    assert prepare('quý trước',chosen=plan(mode='last_quarter',unit='quarter'),today=date(2026,1,2))['plan']['periods']==[interval(2025,4,'quarter')]

def test_invalid_and_ambiguous_periods():
    with pytest.raises(ValueError): prepare('tháng 13 năm 2026',chosen=plan(mode='explicit'))
    assert prepare('tháng 9 và tháng 8 năm 2026',chosen=plan(mode='explicit'))['intent']=='clarify'
    assert prepare('tháng đó',{'active_period':interval(2026,3,'quarter')})['intent']=='clarify'

def test_role_separation_and_acl():
    private={'owner_role':'admin','active_period':interval(2026,9,'month'),'history':[{'question':'private','answer':'private'}]}
    assert clean_memory(private,'customer')=={'owner_role':'customer','history':[]}
    assert prepare('xếp hạng',private,role='customer')['intent']=='denied'

def test_comparison_requires_two_periods():
    p=plan('compare',mode='explicit',metric='revenue')
    assert prepare('so sánh tháng 8 năm 2026',chosen=p)['intent']=='clarify'
    r=prepare('so với tháng 8 năm 2026',{'active_period':interval(2026,9,'month')},p)
    assert [v['label'] for v in r['plan']['periods']]==['2026-09','2026-08']

def test_comparison_clarification_remembers_first_period():
    first=prepare('so sánh tháng 9 năm 2026',chosen=plan('compare','explicit',metric='revenue'))
    second=prepare('với tháng 8 năm 2026',first['profile'],plan('compare','explicit',metric='revenue'))
    assert [p['label'] for p in second['plan']['periods']]==['2026-09','2026-08']
    third=prepare('còn lợi nhuận gộp',second['profile'],plan('compare','same_period',metric='gross_profit'))
    assert third['plan']['periods']==second['plan']['periods']

def test_historical_inventory_never_uses_current_snapshot(tmp_path):
    path=tmp_path/'snapshot.db';initialize(path)
    with connect(path) as db:
        db.execute('CREATE TABLE inventory_daily(day TEXT,sku TEXT,quantity INTEGER,value INTEGER)')
        db.executemany('INSERT INTO inventory_daily VALUES (?,?,?,?)',[
            ('2026-08-31','DEMO-A',4,100),('2026-09-30','DEMO-A',9,200)])
    tools=AdminTools(path)
    assert tools.inventory()[0]['stock']==9
    assert tools.inventory('2026-08-31')[0]['stock']==4
    assert tools.inventory('2026-10-31')==[]

def test_best_product_preserves_ties(tmp_path):
    path=tmp_path/'ties.db';initialize(path)
    with connect(path) as db:
        db.execute('DELETE FROM sales')
        db.executemany('INSERT INTO sales VALUES (?,?,?,?,?)',[
            ('2026-09-01','DEMO-A',8,800,500),('2026-09-01','DEMO-B',8,900,600),('2026-09-01','DEMO-C',7,700,400)])
    rows=AdminTools(path).top_products('2026-09-01','2026-10-01','units',1)
    assert {row['sku'] for row in rows}=={'DEMO-A','DEMO-B'}
    assert all(row['tied_count']==2 for row in rows)

def test_engine_multiturn_matches_sql_and_bounds_history(tmp_path,monkeypatch):
    import shopbot.conversation as conversation
    monkeypatch.setenv('CONVERSATION_MODE','semantic')
    monkeypatch.setenv('LLM_PROVIDER','demo')
    path=tmp_path/'shop.db';initialize(path)
    chosen=plan('revenue','explicit',metric='revenue')
    monkeypatch.setattr(conversation,'semantic_plan',lambda *args: dict(chosen))
    engine=Engine(path,today=TODAY)
    first=engine.ask('doanh thu tháng 9 năm 2026','admin')
    chosen=plan()
    second=engine.ask('tháng đó sản phẩm nào bán chạy nhất','admin',first['profile'])
    with connect(path,readonly=True) as db:
        expected=[dict(v) for v in db.execute("SELECT s.sku,p.name,SUM(s.quantity) units,SUM(s.revenue) revenue,SUM(s.revenue-s.cost) gross_profit FROM sales s JOIN products p ON p.sku=s.sku WHERE day>='2026-09-01' AND day<'2026-10-01' GROUP BY s.sku,p.name ORDER BY units DESC,s.sku LIMIT 3")]
    assert [{k:row[k] for k in expected[0]} for row in second['rows']]==expected
    assert '2026-09-01' in second['answer']
    chosen=plan(metric='revenue')
    third=engine.ask('theo doanh thu cơ','admin',second['profile'])
    assert third['plan']['metric']=='revenue'
    assert third['plan']['periods']==second['plan']['periods']
    assert [v['revenue'] for v in third['rows']]==sorted([v['revenue'] for v in third['rows']],reverse=True)
    for _ in range(8): third=engine.ask('vẫn theo doanh thu','admin',third['profile'])
    assert len(third['profile']['history'])==6
