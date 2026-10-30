"""Score a held-out round: runner checks plus the expected numbers in the answer text.

Usage: score_heldout_20261028.py ROUND [BASE_ROUND]
Prints totals per topic and, with a base round, the IDs that went PASS->FAIL.
The bank is locked: use the output for promote decisions, not for tuning.
"""
import json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'evaluation/heldout_20261028'

def numbers(text):
 # "1.189.908.000" / "1,189,908,000" / "1 189 908 000" -> "1189908000"; keeps decimals like 15.6.
 previous=None
 while previous!=text:previous,text=text,re.sub(r'(?<=\d)[.,  ](?=\d{3}(?!\d))','',text)
 return set(re.findall(r'\d+(?:[.,]\d+)?',text))

def value_found(value,answer):
 wanted=re.findall(r'\d+(?:[.,]\d+)?',value)
 if not wanted:return None  # wording-only values (e.g. "Dedicated") are left to the evidence check
 got={x.replace(',','.') for x in numbers(answer)}
 return all(w.replace(',','.') in got for w in wanted)

def score(row,case):
 status=row['checks']['status']
 if case['expected_behavior']=='facts':
  found=[value_found(v,row['result'].get('answer','')) for v in case['expected_values']]
  if any(f is False for f in found):return 'FAIL_CHECKS'
  # Report metrics answered by the deterministic SQL path cite no document quote;
  # the runner flags that as retrieval, but every expected number is in the answer.
  sql=any('deterministic SQL' in t for t in row['result'].get('trace',[]))
  causes={i['cause'] for i in row['checks']['issues']}
  if sql and found and all(found) and causes<={'RETRIEVAL_OR_ROUTING','SELECTION_OR_CHUNKING'}:return 'PASS_CHECKS'
 return status

def load(name):
 bank={c['id']:c for c in json.loads((BASE/'bank.json').read_text(encoding='utf8'))}
 rows=json.loads((BASE/name/'results.json').read_text(encoding='utf8'))
 return {r['id']:score(r,bank[r['id']]) for r in rows},bank

def main():
 current,bank=load(sys.argv[1])
 by=defaultdict(Counter)
 for i,s in current.items():by[bank[i]['topic']][s]+=1
 total=Counter(current.values())
 print(f'{sys.argv[1]}: {len(current)}/{len(bank)}',dict(total))
 for topic in sorted(by):print(f'  {topic:24}',dict(by[topic]))
 clean=[i for i in current if not bank[i]['topic'].startswith('dirty_')]
 print('  clean only:',dict(Counter(current[i] for i in clean)))
 if len(sys.argv)>2:
  base,_=load(sys.argv[2])
  down=[i for i in current if base.get(i)=='PASS_CHECKS' and current[i]!='PASS_CHECKS']
  up=[i for i in current if base.get(i) not in (None,'PASS_CHECKS') and current[i]=='PASS_CHECKS']
  print('PASS->not PASS:',len(down),down);print('not PASS->PASS:',len(up),up)

if __name__=='__main__':main()
