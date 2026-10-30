import copy
import pytest
from shopbot.admin_state import metric_reference_plan
from test_admin_conversation import setup,run,plan
from shopbot.admin_conversation import AdminConversation
from datetime import date


def confirmed(operation='compare'):
    periods=[dict(start='2026-08-01',end='2026-09-01',label='2026-08',unit='month'),
             dict(start='2026-09-01',end='2026-10-01',label='2026-09',unit='month')]
    return dict(metric='revenue',operation=operation,active_period=periods[-1],
        comparison_periods=periods if operation=='compare' else [],pending=False)


@pytest.mark.parametrize('question,metric',[
    ('Còn giá vốn thì sao?','cost'),('Còn giá vốn?','cost'),('con lai gop','gross_profit'),
    ('Biên lãi gộp kỳ đó thế nào?','gross_margin_pct'),('Tiền hoàn khách tháng đó?','refunds')])
def test_literal_metric_reference_keeps_confirmed_operation_periods_without_mutation(question,metric):
    state=confirmed();before=copy.deepcopy(state)
    assert metric_reference_plan(question,state)==dict(operation='compare',metric=metric,time_mode='same_period',period_unit='none')
    assert state==before


@pytest.mark.parametrize('question',[
    'Giá vốn laptop?','Giá vốn tháng8/2026?','Không xem giá vốn nữa','Giá vốn và doanh thu?',
    'Xóa giá vốn','Giá vốn từng sản phẩm','Dự báo giá vốn','Giá vốn năm đó?'])
def test_scope_action_period_or_ambiguous_changes_are_not_literal_followups(question):
    assert metric_reference_plan(question,confirmed()) is None


@pytest.mark.parametrize('change',[{'pending':True},{'active_period':None},{'operation':'unsupported'},
    {'entity':'sku'},{'comparison_periods':[]},
    {'active_period':dict(start='2026-13-01',end='2026-10-01',label='bad',unit='month')}])
def test_unconfirmed_invalid_or_other_entity_state_cannot_be_bound(change):
    assert metric_reference_plan('Còn giá vốn?',dict(confirmed(),**change)) is None


def test_finance_after_quality_keeps_last_finance_operation_not_quality():
    state=dict(confirmed('finance'),last_topic='data_quality')
    assert metric_reference_plan('Còn giá vốn tháng đó?',state)['operation']=='finance'


def test_confirmed_comparison_survives_incorrect_advisory_plan(setup):
    first=run(setup,'Doanh thu tháng9/2026?')
    second=run(setup,'So với tháng trước?',plan(operation='compare',metric='same',time_mode='previous_period'),first['profile'])
    def should_not_plan(_):raise AssertionError('Literal reference must use confirmed state')
    result=AdminConversation(setup,should_not_plan).run('Còn giá vốn?', 'admin',second['profile'],date(2026,10,23))
    assert result['basic_action']=='answer'
    assert result['comparison']['rows'][0]['baseline']==80 and result['comparison']['rows'][0]['current']==320
    assert result['state_resolution']['method']=='confirmed_metric_reference'


def test_role_change_clears_state_before_literal_reference(setup):
    def missing(_):return plan(operation='clarify',time_mode='missing',period_unit='none')
    result=AdminConversation(setup,missing).run('Còn giá vốn?','admin',dict(owner_role='customer',admin_context=confirmed()),date(2026,10,23))
    assert result['basic_action']=='clarify' and 'state_resolution' not in result
