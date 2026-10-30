"""Frozen mixed contract with advisory slots injected; real read-only tools."""
import json,sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shopbot.agent_conversation import CatalogConversation
from shopbot.agent_tools import AgentTools,CatalogTools
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
catalog=read(ROOT/'data/agent_platform_20261023/catalog_v1/catalog_public.json')
CASES=[('laptop',20_000_000,3,'OLED là gì'),('ram',3_000_000,3,'DDR5 là gì'),
 ('ssd',2_000_000,2,'NVMe là gì'),('monitor',10_000_000,2,'tần số quét là gì')]
rows=[]
for role in ('customer','admin'):
 for category,budget,count,term in CASES:
  question=f'Tìm {count} {category} dưới {budget} đồng và giải thích {term}'
  plan=dict(action='search_documents',budget_max_vnd=budget,budget_inclusive=False,limit=count,
   category=category,brand='',continuation=False,clear_brand=False,unsupported_filters=False,product_refs=[],
   catalog_question=question.split(' và ')[0],knowledge_question='giải thích '+term)
  tools=AgentTools(CatalogTools(catalog),None)
  with tools.capture_calls() as calls:
   r=CatalogConversation(tools,lambda _:plan).run(question,role,{},date(2026,10,23))
  independent=sorted([p for p in catalog['products'] if p['category']==category and p['status']=='active'
   and any(v['status']=='active' and v['available_qty']>0 and v['price']<budget for v in p['variants'])],
   key=lambda p:(min(v['price'] for v in p['variants'] if v['status']=='active' and v['available_qty']>0),p['id']))[:count]
  passed=(r['basic_action']=='answer' and r.get('partial') is True and
   [c['tool'] for c in calls]==['catalog.search','documents.answer'] and
   [p['id'] for p in r['rows']]==[p['id'] for p in independent] and
   r.get('components',{}).get('documents',{}).get('status')=='disabled' and
   'chưa được kết nối' in r['answer'])
  rows.append(dict(role=role,question=question,passed=passed,action=r['basic_action'],
   partial=r.get('partial'),components=r.get('components'),calls=[dict(tool=c['tool'],arguments=c['arguments']) for c in calls],answer=r['answer']))
with (Path(__file__).parent/sys.argv[1]).open('x',encoding='utf-8') as f:
 json.dump(dict(total=len(rows),passed=sum(x['passed'] for x in rows),model_calls=0,cases=rows),f,ensure_ascii=False,indent=2)
print(sum(x['passed'] for x in rows),len(rows))
