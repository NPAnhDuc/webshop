from datetime import date
import pytest
from shopbot.period_binding import bind_monthly_parts

TODAY=date(2026,10,24)
PARTS={'P1':'Doanh thu thuần tháng 5/2026','P2':'tháng 8/2026'}
Q='Đặt cạnh nhau doanh thu thuần tháng 5/2026 và tháng 8/2026'
SCOPE={'months':['2026-05','2026-08'],'quarters':[]}
def f(month,value=100,metric='Doanh thu thuần',**extra):
 source=dict(document_id='monthly-report-'+month,doc_type='monthly_report',version=1)
 source.update(extra)
 return dict(source=source,text=f'{metric}: {value} VND.')
FRAG={'may':f('2026-05'),'aug':f('2026-08')}

@pytest.mark.parametrize('selected',[
 {'P1':['aug'],'P2':['may']},
 {'P1':['may','aug'],'P2':['aug','may']},
 {'P1':['may'],'P2':['aug']},
])
def test_swapped_overbroad_and_correct(selected):
 bound,trace=bind_monthly_parts(Q,PARTS,selected,FRAG,SCOPE,TODAY)
 assert bound=={'P1':['may'],'P2':['aug']}
 assert len(trace)==2
 assert set(i for ids in bound.values() for i in ids)<=set(i for ids in selected.values() for i in ids)


def test_unselected_available_fact_cannot_be_invented_into_reply():
 bound,_=bind_monthly_parts(Q,PARTS,{'P1':['may'],'P2':['may']},FRAG,SCOPE,TODAY)
 assert bound=={'P1':['may'],'P2':[]}


def test_wrong_metric_never_moved_into_shared_revenue_part():
 fragments=dict(may=f('2026-05'),cost=f('2026-08',80,'Giá vốn'))
 bound,_=bind_monthly_parts(Q,PARTS,{'P1':['may'],'P2':['cost']},fragments,SCOPE,TODAY)
 assert bound['P2']==[]


def test_mixed_metrics_use_local_fields_not_global_guess():
 q='Doanh thu thuần tháng 5/2026 và giá vốn tháng 8/2026'
 parts=dict(P1='Doanh thu thuần tháng 5/2026',P2='Giá vốn tháng 8/2026')
 fragments=dict(rev=f('2026-05'),cost=f('2026-08',80,'Giá vốn'))
 bound,_=bind_monthly_parts(q,parts,{'P1':['cost'],'P2':['rev']},fragments,SCOPE,TODAY)
 assert bound=={'P1':['rev'],'P2':['cost']}


def test_bare_month_inherits_unique_confirmed_year():
 q='Doanh thu thuần tháng 11/2025 và tháng 12'
 parts=dict(P1='Doanh thu thuần tháng 11/2025',P2='tháng 12')
 fragments=dict(nov=f('2025-11'),dec=f('2025-12'))
 bound,_=bind_monthly_parts(q,parts,{'P1':['dec'],'P2':['nov']},fragments,{'months':['2025-11','2025-12']},TODAY)
 assert bound=={'P1':['nov'],'P2':['dec']}


def test_conflicting_source_period_metadata_cannot_supply_fact():
 fragments=dict(may=f('2026-05'),aug=f('2026-08',period='2026-05'))
 bound,_=bind_monthly_parts(Q,PARTS,{'P1':['may'],'P2':['aug']},fragments,SCOPE,TODAY)
 assert bound['P2']==[]

@pytest.mark.parametrize('q',[
 'Vì sao doanh thu thuần tháng 5/2026 giảm?',
 'Giải thích doanh thu thuần tháng 5/2026 là gì?',
 'Mục tiêu doanh thu thuần tháng 5/2026 bao nhiêu?',
])
def test_explanations_and_targets_are_not_numeric_field_rebinding(q):
 selected={'P1':['aug']}
 assert bind_monthly_parts(q,{'P1':q},selected,FRAG,SCOPE,TODAY)==(selected,[])
