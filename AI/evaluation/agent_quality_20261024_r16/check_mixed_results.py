"""Mechanical checks against independent catalog gold; review prose separately."""
import json
from pathlib import Path
OUT=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
gold=read(OUT/'mixed_gold.json');traces={p.stem:read(p) for p in (OUT/'traces').rglob('*.json')}
checks={}
for row in read(OUT/'results.json'):
 if row['id'] not in gold:continue
 r=row['result'];g=gold[row['id']];calls=traces[r['trace_id']]['calls'];errors=[]
 if r['basic_action']!=g['action']:errors.append('action')
 if [c['tool'] for c in calls]!=g['tools']:errors.append('tools')
 # Documents wired (r15+): the knowledge part must really execute and be reported.
 docs=[c for c in calls if c['tool']=='documents.answer']
 status=docs[0]['output'].get('status') if docs else None
 if g.get('knowledge_question'):
  if len(docs)!=1 or docs[0]['arguments']!=dict(question=g['knowledge_question']):errors.append('knowledge_span')
  if not docs or docs[0]['output'].get('executed') is not True or status not in ('answered','no_source'):errors.append('documents_not_executed')
  if r.get('components',{}).get('documents',{}).get('status')!=status:errors.append('component_status')
  if '“'+g['knowledge_question']+'”' not in r['answer']:errors.append('silent_omission')
  if bool(r.get('partial'))!=(status!='answered'):errors.append('partial_status')
 elif bool(r.get('partial')):errors.append('partial_status')
 if 'product_ids' in g:
  if [p['id'] for p in r.get('rows',[])]!=g['product_ids']:errors.append('independent_product_ids')
 if 'arguments' in g:
  search=[c for c in calls if c['tool']=='catalog.search']
  if not search or search[0]['arguments']!=g['arguments']:errors.append('search_operands')
 if 'compared_product_ids' in g:
  compare=[c for c in calls if c['tool']=='catalog.compare']
  if not compare or compare[0]['arguments']!=dict(product_ids=g['compared_product_ids']):errors.append('comparison_refs')
 if g['action']=='answer' and not r['sources']:errors.append('catalog_source')
 checks[row['id']]=dict(checks_pass=not errors,errors=errors,semantic_review_required=True)
with (OUT/'mixed_checks.json').open('x',encoding='utf-8') as f:json.dump(checks,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=sum(c['checks_pass'] for c in checks.values()),total=len(checks),failures={k:v['errors'] for k,v in checks.items() if not v['checks_pass']})))
