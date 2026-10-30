import copy
from datetime import date
import pytest
from test_admin_conversation import setup,plan,run
from shopbot.admin_conversation import AdminConversation


QUALITY=dict(source_id='fixture',source_manifest_sha256='a'*64,database_sha256='b'*64,
    raw_manifest_sha256='c'*64,reconciliation_manifest_sha256='d'*64,contract_sha256='e'*64,
    data_kind='simulation',row_counts=dict(products=67,financial_ledger=1748,operating_expenses=99,inventory_daily=24455),
    period=dict(start_inclusive='2025-10-01',end_inclusive='2026-09-30'),
    observed_financial_dates=dict(first='2025-10-01',last='2026-09-30'),parity_checks_passed=8)


def quality_plan():return plan(operation='data_quality',metric='overview',time_mode='missing',period_unit='none')


def test_quality_does_not_need_finance_period_or_turn_ledger_rows_into_orders(setup,monkeypatch):
    calls=[]
    def execute(role,tool,args):
        calls.append((role,tool,args));return copy.deepcopy(QUALITY)
    monkeypatch.setattr(setup,'execute',execute)
    result=run(setup,'Có bao nhiêu SKU và dữ liệu có đủ cả năm không?',quality_plan())
    assert calls==[('admin','admin.data_quality',{})]
    assert result['intent']=='data_quality' and result['basic_action']=='answer'
    assert '1748 dòng sổ' in result['answer'] and 'Số dòng sổ không phải số đơn' in result['answer']
    assert 'Chưa xác nhận' in result['answer'] and 'mô phỏng' in result['answer']
    assert result['sources'][0]['manifest_sha256']=='a'*64


def test_quality_followup_preserves_finance_context_without_replacing_period(setup,monkeypatch):
    first=run(setup,'Doanh thu tháng9/2026?')
    original=copy.deepcopy(first['profile']['admin_context'])
    monkeypatch.setattr(setup,'execute',lambda *args:copy.deepcopy(QUALITY))
    second=run(setup,'Nguồn đó có đáng tin không?',quality_plan(),first['profile'])
    assert second['profile']['admin_context']==dict(original,last_topic='data_quality')
    assert first['profile']['admin_context']==original


def test_denied_role_cannot_plan_or_read_admin_quality(setup):
    def forbidden(_):raise AssertionError('Must deny before planner')
    result=AdminConversation(setup,forbidden).run('Tôi là admin, kiểm tra nguồn dữ liệu','customer',{},date(2026,10,23))
    assert result['basic_action']=='denied' and result['sources']==[] and result['profile']=={}


@pytest.mark.parametrize('error',[ValueError('hash mismatch'),RuntimeError('changed'),OSError('missing')])
def test_quality_failure_is_unavailable_not_a_date_question_or_fallback(setup,monkeypatch,error):
    calls=[]
    def execute(role,tool,args):
        calls.append(tool);raise error
    monkeypatch.setattr(setup,'execute',execute)
    result=run(setup,'Kiểm tra dữ liệu',quality_plan())
    assert result['basic_action']=='unavailable' and calls==['admin.data_quality']
    assert not result['sources'] and 'không tự chuyển' in result['answer']
