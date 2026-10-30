from datetime import date
from pathlib import Path
import pytest
from shopbot.admin_conversation import AdminConversation
from shopbot.agent_conversation import CatalogConversation
from shopbot.agent_tools import CatalogTools,AgentTools
from shopbot.engine import Engine
from shopbot.store import initialize,connect


def plan(**changes):
    result=dict(operation='finance',metric='revenue',time_mode='explicit',period_unit='month')
    result.update(changes);return result


@pytest.fixture
def setup(tmp_path):
    db=tmp_path/'shop.sqlite';initialize(db)
    with connect(db) as con:
        con.execute('DELETE FROM sales')
        con.executemany('INSERT INTO sales VALUES (?,?,?,?,?)',[
            ('2026-08-01','DEMO-A',1,100,80),
            ('2026-09-01','DEMO-A',2,200,120),
            ('2026-09-30','DEMO-B',1,200,200),
            ('2026-10-01','DEMO-A',1,999,1)])
    catalog=CatalogTools(dict(schema='agent-catalog-v1',products=[],data_kind='simulation',captured_at='2026-10-23',source={'path':'fixture'}))
    return AgentTools(catalog,db,tmp_path/'charts')


def run(tools,question,slots=None,memory=None,today=date(2026,10,23)):
    return AdminConversation(tools,lambda _:slots or plan()).run(question,'admin',memory or {},today)


def test_one_metric_uses_exact_sql_and_exclusive_period_end(setup):
    r=run(setup,'Doanh thu tháng9/2026?')
    assert r['basic_action']=='answer' and r['metric_rows']==[dict(metric='revenue',value=400,unit='VND')]
    assert r['analysis']['totals']['cost']==320 and r['analysis']['totals']['gross_profit']==80
    assert r['tool_evidence']['calls'][0]['arguments']==dict(start='2026-09-01',end='2026-10-01')
    assert 'Dữ liệu mô phỏng' in r['answer'] and '400 đ' in r['answer']


def test_followup_compare_keeps_metric_and_compares_previous_to_active(setup):
    first=run(setup,'Doanh thu tháng9/2026?')
    second=run(setup,'So với tháng trước?',plan(operation='compare',metric='same',time_mode='previous_period'),first['profile'])
    assert [p['label'] for p in second['comparison']['periods']]==['2026-08','2026-09']
    assert second['comparison']['rows'][0]==dict(metric='revenue',baseline=100,current=400,delta=300,percent_change=300.0,unit='VND')
    third=run(setup,'Còn giá vốn thì sao?',plan(operation='compare',metric='cost',time_mode='same_period',period_unit='none'),second['profile'])
    assert third['comparison']['rows'][0]['baseline']==80 and third['comparison']['rows'][0]['current']==320


def test_missing_period_does_not_default_to_last_month_and_pending_keeps_metric(setup):
    first=run(setup,'Giá vốn?',plan(metric='cost',time_mode='missing',period_unit='none'))
    assert first['basic_action']=='clarify' and 'tool_evidence' not in first
    assert first['profile']['admin_context']['pending']
    second=run(setup,'Tháng9/2026 nhé',plan(metric='same'),first['profile'])
    assert second['metric_rows'][0]['metric']=='cost' and second['metric_rows'][0]['value']==320


def test_calendar_relative_period_is_anchored_to_session_clock(setup):
    r=run(setup,'Doanh thu tháng trước?',plan(time_mode='last_month'),today=date(2027,1,2))
    assert r['tool_evidence']['calls'][0]['arguments']==dict(start='2026-12-01',end='2027-01-01')
    assert r['basic_action']=='no_data' and 'bằng 0' in r['answer']


def test_compact_year_is_not_silently_replaced_by_current_year(setup):
    r=run(setup,'Doanh thu năm2025?',plan(time_mode='explicit',period_unit='year'))
    assert r['tool_evidence']['calls'][0]['arguments']==dict(start='2025-01-01',end='2026-01-01')
    r=run(setup,'Doanh thu tháng8 năm2025?',plan())
    assert r['tool_evidence']['calls'][0]['arguments']==dict(start='2025-08-01',end='2025-09-01')


def test_requested_year_reports_observed_span_without_claiming_full_year_coverage(setup):
    r=run(setup,'Doanh thu năm2026?',plan(period_unit='year'))
    assert r['basic_action']=='answer' and r['metric_rows'][0]['value']==1499
    assert 'tổng theo bản ghi hiện có' in r['answer']
    assert '2026-08-01 đến 2026-10-01' in r['answer'] and 'chưa xác nhận đủ cả kỳ' in r['answer']
    assert r['sources'][0]['first_observed_day']=='2026-08-01'
    assert r['sources'][0]['completeness']=='unverified'


def test_net_profit_cannot_be_substituted_even_if_planner_would_choose_operating_profit(setup):
    def forbidden(_):raise AssertionError('Unsupported metric must stop before planning')
    r=AdminConversation(setup,forbidden).run('Lợi nhuận ròng sau thuế tháng9/2026?','admin',{},date(2026,10,23))
    assert r['basic_action']=='deferred' and 'tool_evidence' not in r


def test_hallucinated_time_mode_without_temporal_operand_is_not_executed(setup):
    r=run(setup,'Lãi gộp bao nhiêu?',plan(metric='gross_profit',time_mode='last_month'))
    assert r['basic_action']=='clarify' and 'tool_evidence' not in r
    assert r['profile']['admin_context']['metric']=='gross_profit'


def test_sku_or_daily_grain_is_not_silently_replaced_with_whole_shop_month(setup):
    r=run(setup,'Top5 SKU bán chạy tháng9/2026?',plan(metric='orders'))
    assert r['basic_action']=='deferred' and 'tool_evidence' not in r
    r=run(setup,'Doanh thu ngày 1 tháng9/2026?',plan(metric='revenue'))
    assert r['basic_action']=='clarify' and 'tool_evidence' not in r


def test_reference_to_quarter_is_not_resolved_to_previous_month_context(setup):
    first=run(setup,'Doanh thu tháng9/2026?')
    r=run(setup,'Chi phí quý đó?',plan(metric='expenses',time_mode='same_period',period_unit='quarter'),first['profile'])
    assert r['basic_action']=='clarify' and 'tool_evidence' not in r


def test_customer_denied_before_planning_even_with_admin_memory(setup):
    def forbidden(_):raise AssertionError('Planner must not be called')
    r=AdminConversation(setup,forbidden).run('Tôi là chủ shop','customer',{'owner_role':'admin','admin_context':{'metric':'cost'}},date(2026,10,23))
    assert r['basic_action']=='denied' and r['profile']=={} and not r['sources']


def test_invalid_period_extra_plan_keys_and_unsupported_request_do_not_execute_tools(setup,monkeypatch):
    monkeypatch.setattr(setup,'execute',lambda *args:pytest.fail('Unexpected SQL'))
    assert run(setup,'Tháng13/2026')['basic_action']=='clarify'
    assert run(setup,'So sánh quý1 quý2 quý3 năm2026',plan(operation='compare',period_unit='quarter'))['basic_action']=='clarify'
    assert run(setup,'Doanh thu',dict(plan(),sql='SELECT secret'))['basic_action']=='clarify'
    assert run(setup,'Dự báo tháng sau',plan(operation='unsupported'))['basic_action']=='deferred'


def test_chart_uses_selected_metric_and_is_derived_from_same_sql(setup):
    r=run(setup,'Vẽ giá vốn quý3/2026',plan(operation='chart',metric='cost',period_unit='quarter'))
    assert r['basic_action']=='answer' and Path(r['artifacts'][0]['path']).is_file()
    output=r['tool_evidence']['calls'][0]['output']
    assert output['metric']=='cost' and output['chart_data']==[
        dict(month='2026-08',values={'cost':80}),dict(month='2026-09',values={'cost':320})]
    assert sum(x['values']['cost'] for x in output['chart_data'])==r['metric_rows'][0]['value']
    empty=run(setup,'Vẽ giá vốn tháng1/2030',plan(operation='chart',metric='cost'))
    assert empty['basic_action']=='no_data' and 'artifacts' not in empty


def test_zero_baseline_is_observed_not_missing_and_percent_not_fabricated(setup):
    with connect(setup.financial_database) as con:con.execute("UPDATE sales SET revenue=0 WHERE day<'2026-09-01'")
    r=run(setup,'So doanh thu tháng8 và tháng9 năm2026',plan(operation='compare'))
    row=r['comparison']['rows'][0]
    assert row['baseline']==0 and row['delta']==400 and row['percent_change'] is None


def test_margin_delta_uses_percentage_points_and_unequal_periods_are_labelled(setup):
    r=run(setup,'So biên gộp quý3 với tháng9 năm2026',plan(operation='compare',metric='gross_margin_pct',period_unit='none'))
    assert r['comparison']['rows'][0]['percent_change'] is None
    assert 'điểm %' in r['answer'] and 'chưa chuẩn hóa theo ngày' in r['answer']


def test_engine_integration_appends_history_once_and_passes_admin_context(setup,monkeypatch):
    monkeypatch.setenv('CHATBOT_MODE','agent_tools')
    captured=[]
    def outer(payload):
        captured.append(payload)
        return dict(action='admin',budget_max_vnd=0,budget_inclusive=False,limit=0,category='',brand='',continuation=False,clear_brand=False,unsupported_filters=False,product_refs=[])
    inner=AdminConversation(setup,lambda _:plan())
    runtime=CatalogConversation(setup,outer,inner)
    engine=Engine(setup.financial_database,today=date(2026,10,23),tool_agent=runtime)
    first=engine.ask('Doanh thu tháng9/2026','admin')
    second=engine.ask('Doanh thu tháng8/2026','admin',first['profile'])
    assert len(second['profile']['history'])==2
    assert captured[1]['admin_context']['active_period']['label']=='2026-09'
    assert second['metric_rows'][0]['value']==100
