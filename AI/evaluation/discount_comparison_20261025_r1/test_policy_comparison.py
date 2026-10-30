from datetime import date
from fractions import Fraction
from pathlib import Path
import json
import pytest
from shopbot.policy_comparison import current_discount_comparison,compare_policy_percentage

CASES=json.loads((Path(__file__).resolve().parents[1]/'evaluation/discount_contract_20261025_r1/contract_cases.json').read_text(encoding='utf-8'))

def fragment(cap='6',**updates):
 s=dict(doc_type='policy',status='approved',audience='admin',authority='synthetic_shop_document',effective_from='2026-04-01',effective_to=None,title='Quy định giá và biên gộp',source='policy.md',version=2,chunk_id='c',section=1)
 s.update(updates)
 return dict(source=s,text=f'Mức giảm tối đa {cap}%; không cộng dồn.')

@pytest.mark.parametrize('case',CASES,ids=[c['id'] for c in CASES])
def test_frozen_discount_contract_adapter(case):
 r=current_discount_comparison(case['question'],case['role'],{},dict(x=fragment()),date(2026,10,24))
 e=case['expected']
 if e.get('operation'):
  assert r is not None
  for k in ['relation','approval_granted','mutation_allowed']:assert r[k]==e[k]
  for k in ['requested_percent','cap_percent','absolute_difference_percentage_points']:assert Fraction(r[k])==Fraction(e[k])
  assert r['evidence_id']=='x' and r['quote']==e['source_quote']
 else:assert r is None

@pytest.mark.parametrize('updates',[
 {'status':'draft'},{'audience':'customer'},{'authority':'internal_methodology'},
 {'effective_to':'2026-09-30'},{'effective_from':'2026-11-01'},
 {'title':'Quy định Q3/2026'},{'title':'Quy định quý 3/2026'},
 {'doc_type':'sales_plan'},{'effective_from':None},
])
def test_unapproved_expired_future_or_quarterly_evidence_rejected(updates):
 assert current_discount_comparison('Giảm7%, đối chiếu trần.','admin',{},dict(x=fragment(**updates)),date(2026,10,24)) is None


def test_conflicting_caps_do_not_pick_first():
 assert current_discount_comparison('Giảm7%, đối chiếu trần.','admin',{},dict(x=fragment(),y=fragment('8')),date(2026,10,24)) is None


def test_cap_is_source_operand_not_hardcoded():
 r=current_discount_comparison('Giảm7%, đối chiếu trần.','admin',{},dict(x=fragment('3,5')),date(2026,10,24))
 assert r['cap_percent']=='3.5' and r['absolute_difference_percentage_points']=='3.5'


def test_conditional_or_margin_text_is_not_generic_discount_cap():
 for text in ['Biên gộp tối thiểu6%.','Mức giảm tối đa6% nếu nhập thêm hàng.']:
  f=fragment();f['text']=text
  assert current_discount_comparison('Giảm7%, đối chiếu trần.','admin',{},dict(x=f),date(2026,10,24)) is None


def test_explicit_historical_period_requires_separate_binding():
 assert current_discount_comparison('Giảm7%, đối chiếu trần.','admin',{'quarters':['2026-Q3']},dict(x=fragment()),date(2026,10,24)) is None

@pytest.mark.parametrize('rate',['NaN','Infinity','-1','101'])
def test_typed_calculation_refuses_invalid_rates(rate):
 with pytest.raises(ValueError):compare_policy_percentage(rate,'6')
