from datetime import date
import sqlite3
from pathlib import Path
import pytest
from shopbot.rag_scope import resolve_scope
from shopbot.rag_metrics import metric_request,answer_metrics

DB=Path(__file__).resolve().parents[1]/'data/business_sql/scenario_v1/shop.sqlite'
TODAY=date(2026,10,24)


@pytest.mark.parametrize('question,quarters,months',[
    ('Doanh thu quý 3/2026 là bao nhiêu?',['2026-Q3'],[]),
    ('Lấy mục tiêu quý4/2027 từ kế hoạch',['2027-Q4'],[]),
    ('Doanh thu Q2/2026?',['2026-Q2'],[]),
    ('Doanh thu tháng 3/2026?',[],['2026-03']),
    ('So doanh thu 7/2026 với quý 2 năm 2026',['2026-Q2'],['2026-07']),
])
def test_quarter_number_is_not_read_as_a_month(question,quarters,months):
    scope=resolve_scope(question,TODAY)
    assert (scope['quarters'],scope['months'])==(quarters,months)


@pytest.mark.parametrize('question',[
    'Doanh thu thuần quý 3/2026 của shop là bao nhiêu?','Lãi gộp tháng 8/2026 là bao nhiêu?',
    'Số đơn hàng quý 2 năm 2026?','Cho tôi biết giá vốn và lợi nhuận gộp tháng 9/2026',
])
def test_admin_metric_questions_are_bound(question):
    assert metric_request(question,'admin',resolve_scope(question,TODAY))


@pytest.mark.parametrize('question,role',[
    ('Doanh thu tháng 9/2026 là bao nhiêu?','customer'),                       # not for customers
    ('Mục tiêu doanh thu quý 3/2026 là bao nhiêu?','admin'),                    # plan, not actuals
    ('Vì sao doanh thu tháng 9/2026 giảm?','admin'),                            # causal
    ('Lợi nhuận riêng Gaming tháng 9/2026 là bao nhiêu?','admin'),              # subgroup
    ('Báo cáo tháng 9 có 1539000000 VND thực thu không?','admin'),              # claim with amount
    ('Doanh thu là gì?','admin'),                                               # no period
    ('CM2 là gì và tính thế nào?','admin'),                                     # no metric/period
])
def test_other_questions_stay_on_documents(question,role):
    assert metric_request(question,role,resolve_scope(question,TODAY)) is None


def sql(query,*args):return sqlite3.connect(f'file:{DB}?mode=ro',uri=True).execute(query,args).fetchone()[0]


def test_quarter_answer_equals_database_total_and_months():
    question='Lãi gộp quý 3 năm 2026 là bao nhiêu?'
    asked,found=metric_request(question,'admin',resolve_scope(question,TODAY))
    text,claims,coverage=answer_metrics(DB,asked,found,TODAY)
    total=sql("SELECT SUM(revenue-cost) FROM financial_ledger WHERE day>='2026-07-01' AND day<'2026-10-01'")
    assert f'{total:,}'.replace(',','.') in text and total==502202000
    for month in ('2026-07','2026-08','2026-09'):
        v=sql("SELECT SUM(revenue-cost) FROM financial_ledger WHERE substr(day,1,7)=?",month)
        assert f'{month}: {v:,}'.replace(',','.') in text.replace(',','.')
    assert coverage==[dict(period='2026-Q3',months=['2026-07','2026-08','2026-09'],missing=[])]


def test_sql_answer_is_gradable_like_document_evidence(monkeypatch):
    from shopbot.grounded_rag import answer
    from shopbot.quality_eval import grade
    result=answer('Doanh thu thuần tháng 9/2026 là bao nhiêu?','admin',{},DB,TODAY)
    assert result['basic_action']=='answer' and '1.189.908.000' in result['answer']
    source=result['sources'][0]
    for claim in result['rag']['claims']:
        for evidence in claim['evidence']:
            assert evidence['chunk_id']==source['chunk_id'] and all(q in source['text'] for q in evidence['quotes'])
    case=dict(role='admin',required=[],expected_behavior='facts',gold_document_ids=[],question='x')
    assert not [i for i in grade(case,result)['issues'] if i['cause']=='EVIDENCE_INTEGRITY']


def test_future_or_empty_periods_are_reported_not_invented():
    question='Doanh thu quý 4/2026 là bao nhiêu?'
    asked,found=metric_request(question,'admin',resolve_scope(question,TODAY))
    text,claims,_=answer_metrics(DB,asked,found,TODAY)
    assert 'chưa có' in text and not claims
