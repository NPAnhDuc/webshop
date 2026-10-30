"""Validate frozen evaluation oracle, NOT chatbot behavior or accuracy."""
from fractions import Fraction
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cases=json.loads((ROOT/'contract_cases.json').read_text(encoding='utf-8'))
assert len(cases)==20 and len({c['id'] for c in cases})==20
numeric=0
for c in cases:
 e=c['expected']
 assert e['approval_granted'] is False and e['mutation_allowed'] is False
 if e.get('operation')=='compare_policy_percentage':
  numeric+=1
  delta=Fraction(e['requested_percent'])-Fraction(e['cap_percent'])
  assert e['relation']==('above' if delta>0 else 'equal' if delta==0 else 'below')
  assert Fraction(e['absolute_difference_percentage_points'])==abs(delta)
protocol=json.loads((ROOT/'protocol.json').read_text(encoding='utf-8'))
for s in protocol['source_files']:
 assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
print(json.dumps(dict(contract_count=len(cases),numeric_oracles_checked=numeric,boundary_contracts=len(cases)-numeric,source_hashes_match=True,chatbot_tests_run=0,model_calls=0,semantic_accuracy=None)))
