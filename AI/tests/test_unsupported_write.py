from pathlib import Path
import json
from datetime import date
import pytest
from shopbot.capability_guard import unsupported_write,unsupported_capability
from shopbot.capabilities import validate_call
from shopbot.grounded_rag import answer

CASES=json.loads((Path(__file__).resolve().parents[1]/'evaluation/unsupported_write_contract_20261025_r1/contract.json').read_text(encoding='utf-8'))['cases']

@pytest.mark.parametrize('case',CASES,ids=[c['id'] for c in CASES])
def test_frozen_execution_vs_mention_contract(case):
 expected='data.mutate' if case['expected']['preflight']=='deferred' else None
 assert unsupported_write(case['question'])==expected
 if expected:assert unsupported_capability(case['question'])==expected

@pytest.mark.parametrize('case',[c for c in CASES if c['expected']['preflight']=='deferred'],ids=[c['id'] for c in CASES if c['expected']['preflight']=='deferred'])
def test_admin_write_defers_before_any_model_or_search(monkeypatch,case):
 def forbidden(*a,**k):pytest.fail('No model/search/DB action for unsupported write')
 monkeypatch.setattr('shopbot.grounded_rag.chat',forbidden)
 monkeypatch.setattr('shopbot.grounded_rag.search',forbidden)
 r=answer(case['question'],'admin',{},'unused',date(2026,10,24))
 assert r['basic_action']=='deferred'
 assert r['capability_status']==dict(name='data.mutate',status='unsupported',executed=False)
 assert not r['rows'] and not r['sources']
 assert 'chưa thực hiện' in r['answer']


def test_customer_write_is_denied_without_model(monkeypatch):
 monkeypatch.setattr('shopbot.grounded_rag.chat',lambda *a,**k:pytest.fail('No model for customer write request'))
 r=answer('UPDATE products SET price=1','customer',{},'unused',date(2026,10,24))
 assert r['basic_action']=='denied' and not r['sources'] and not r['rows']


def test_registry_has_no_executable_write_grant():
 c=validate_call('admin','data.mutate',{'question':'UPDATE products SET price=1'})
 assert c['status']=='unsupported'
 with pytest.raises(PermissionError):validate_call('customer','data.mutate',{'question':'x'})
 with pytest.raises(ValueError):validate_call('admin','data.mutate',{'question':'x','sql':'UPDATE products SET price=1'})

@pytest.mark.parametrize('question',[
 'Không UPDATE products SET price=1 hay DELETE FROM products.',
 'Giải thích UPDATE products SET price=1 có ý nghĩa gì?',
 'Ví dụ UPDATE products SET price=1 có ý nghĩa gì?',
])
def test_negative_and_educational_mentions_do_not_hijack_model_reading(monkeypatch,question):
 calls=[]
 def router(*a,**k):
  calls.append(1)
  return dict(action='outside',query=question,doc_types=[],task='lookup',private_request=False)
 monkeypatch.setattr('shopbot.grounded_rag.chat',router)
 r=answer(question,'admin',{},'unused',date(2026,10,24))
 assert calls and 'capability_status' not in r
