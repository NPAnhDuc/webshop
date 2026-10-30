"""Score an expansion round with the held-out rules (expected numbers must be in the answer).

Usage: score_expansion_20261029.py ROUND [BASE_ROUND]
Totals per split and topic; with a base round, the IDs that went PASS->not PASS.
Validation IDs are listed only as a count: that split is locked.
"""
import importlib.util,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('score_heldout',ROOT/'scripts/score_heldout_20261028.py')
held=importlib.util.module_from_spec(spec);spec.loader.exec_module(held)
held.BASE=ROOT/'evaluation/expansion_20261029'

def main():
 current,bank=held.load(sys.argv[1])
 for split in ('development','validation'):
  ids=[i for i in current if bank[i]['split']==split]
  if not ids:continue
  print(f'{split}: {len(ids)}',dict(Counter(current[i] for i in ids)))
  by=defaultdict(Counter)
  for i in ids:by[bank[i]['topic']][current[i]]+=1
  for topic in sorted(by):print(f'  {topic:26}',dict(by[topic]))
 if len(sys.argv)>2:
  base,_=held.load(sys.argv[2])
  for split in ('development','validation'):
   down=[i for i in current if bank[i]['split']==split and base.get(i)=='PASS_CHECKS' and current[i]!='PASS_CHECKS']
   up=[i for i in current if bank[i]['split']==split and base.get(i) not in (None,'PASS_CHECKS') and current[i]=='PASS_CHECKS']
   show=(lambda ids:ids) if split=='development' else (lambda ids:'(locked)')
   print(f'{split} PASS->not PASS: {len(down)}',show(down),f'| not PASS->PASS: {len(up)}',show(up))

if __name__=='__main__':main()
