"""One frozen mixed-catalog development batch + unchanged106 regression."""
import importlib.util
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('quality_r1_runner',ROOT/'scripts/run_quality_data_quality.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
from shopbot.de_snapshot import digest,write_new
from shopbot.monthly import exclusive
OUT=ROOT/'evaluation/agent_quality_20261024_r9';OLD=ROOT/'evaluation/agent_quality_20261024_r8'


def prepare():
 with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
  OUT.mkdir(exist_ok=False)
  names=['bank.json','new_bank.json','new_gold.json','gold_changes.json','contract_bank.json','contract_gold.json']
  for name in names:(OUT/name).write_bytes((OLD/name).read_bytes())
  reg=OUT/'regression';reg.mkdir()
  for name in ('bank.json','gold.json'):(reg/name).write_bytes((OLD/'regression'/name).read_bytes())
  cat=runner.read(runner.CAT)
  def eligible(category,budget,count):
   rows=[]
   for p in cat['products']:
    if p['category']!=category or p['status']!='active':continue
    variants=[v for v in p['variants'] if v['status']=='active' and v['available_qty']>0 and v['price']<budget]
    if variants:rows.append((min(v['price'] for v in variants),p['id']))
   return [sku for price,sku in sorted(rows)[:count]]
  mixed=[];gold={}
  def add(role,conversation,question,expected):
   key=f'Q{47+len(mixed):02}'
   mixed.append(dict(id=key,conversation=conversation,role=role,question=question));gold[key]=expected
  for role in ('customer','admin'):
   for category,budget,count,term in [('laptop',20_000_000,3,'OLED là gì'),('ram',3_000_000,3,'DDR5 là gì'),
       ('ssd',2_000_000,2,'NVMe là gì'),('monitor',10_000_000,2,'tần số quét là gì')]:
    doc='giải thích '+term
    add(role,f'mixed-{role}-{category}',f'Tìm {count} {category} dưới {budget} đồng và {doc}',
     dict(action='answer',tools=['catalog.search','documents.answer'],arguments=dict(category=category,limit=count,max_price_exclusive=budget,brand=None),
      product_ids=eligible(category,budget,count),knowledge_question=doc,partial=True,documents_status='disabled'))
  for role in ('customer','admin'):
   conversation=f'mixed-compare-{role}';ids=eligible('laptop',40_000_000,3)
   add(role,conversation,'Tìm 3 laptop dưới 40000000 đồng',dict(action='answer',tools=['catalog.search'],product_ids=ids,partial=False))
   add(role,conversation,'So máy thứ1 với thứ2 và giải thích RAM là gì',dict(action='answer',tools=['catalog.compare','documents.answer'],
    compared_product_ids=ids[:2],knowledge_question='giải thích RAM là gì',partial=True,documents_status='disabled'))
  write_new(OUT/'mixed_bank.json',mixed);write_new(OUT/'mixed_gold.json',gold)
  # Preserve the original106 list as its own immutable copied artifact.
  (OUT/'baseline106_bank.json').write_bytes((OLD/'bank.json').read_bytes())
  bank=runner.read(OUT/'bank.json');(OUT/'bank.json').write_text(json.dumps(bank+mixed,ensure_ascii=False,indent=2),encoding='utf-8')
  files=[runner.DB,runner.CAT,*runner.CURATED.rglob('*'),*[OUT/n for n in names],reg/'bank.json',reg/'gold.json',
   OUT/'mixed_bank.json',OUT/'mixed_gold.json',OUT/'baseline106_bank.json',Path(__file__),ROOT/'scripts/run_quality_data_quality.py',
   *sorted((ROOT/'shopbot').glob('*.py'))]
  write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
   config={k:os.getenv(k) for k in runner.CONFIG},today='2026-10-23',curated_pin=digest(runner.CURATED/'manifest.json'),
   protocol='Same106 questions/gold as r8 plus12 mixed development cases. New gold independently filters catalog JSON, no bot-tool oracle. No typo normalization.'))
  snap=OUT/'code_snapshot';snap.mkdir()
  for p in [*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__),ROOT/'scripts/run_quality_data_quality.py']:(snap/p.name).write_bytes(p.read_bytes())
  print('Frozen118=106 unchanged+12 mixed development turns; no model calls.')


if __name__=='__main__':
 if '--prepare-only' in sys.argv:prepare()
 else:
  original=runner.Engine
  def traced(*args,**kwargs):return original(*args,**kwargs,trace_directory=OUT/'traces')
  runner.Engine=traced;runner.OUT=OUT;runner.main()
