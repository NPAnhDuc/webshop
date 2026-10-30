"""Mechanical checks for buyer_run r1 against the bank's independent catalog oracle.

Route/tool success is reported apart from answered knowledge; prose needs human review.
"""
import collections
import json
import re
import statistics
import sys
from pathlib import Path
OUT=Path(sys.argv[1])
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
traces={p.stem:read(p) for p in (OUT/'traces').rglob('*.json')}
rows=read(OUT/'results.json')
checks={};by_family=collections.defaultdict(collections.Counter);errors_count=collections.Counter()
actions=collections.defaultdict(collections.Counter)


def calls_of(r):
    t=traces.get(r.get('trace_id'))
    return t['calls'] if t else []


def num_in(answer,value):
    if isinstance(value,(int,float)):
        v=str(value).rstrip('0').rstrip('.') if isinstance(value,float) else str(value)
        return re.search(r'(?<![\d.,])'+re.escape(v)+r'(?![\d])',answer.replace(',','.')) is not None
    return str(value).casefold() in answer.casefold()


for row in rows:
    r=row['result'];e=row['expected'];fam=row['family'];errs=[];calls=calls_of(r);tools=[c['tool'] for c in calls]
    actions[fam][r['basic_action']]+=1
    cap=e.get('capability')
    if cap=='catalog.search':
        s=[c for c in calls if c['tool']=='catalog.search']
        if r['basic_action']!='answer' or not s:errs.append('no_search')
        else:
            a=s[0]['arguments']
            if a.get('category')!=e['category']:errs.append('category')
            if a.get('max_price_exclusive')!=e['budget_vnd']+int(e['inclusive']):errs.append('budget')
            if a.get('limit')!=e['requested_count']:errs.append('count')
            if [p['id'] for p in r.get('rows',[])]!=e['expected_product_ids']:errs.append('product_ids')
            if e['shortage'] and f"{len(e['expected_product_ids'])}/{e['requested_count']}" not in r['answer']:errs.append('shortage_not_stated')
    elif cap=='catalog.compare':
        c=[c for c in calls if c['tool']=='catalog.compare']
        if e.get('clarify_if_fewer_than_two') and len(e['product_ids'])<2:
            # Previous search returned one item: asking again is the correct outcome.
            if r['basic_action']!='clarify' or c:errs.append('should_clarify_fewer_than_two')
        elif r['basic_action']!='answer' or not c:errs.append('no_compare')
        elif c[0]['arguments'].get('product_ids')!=e['product_ids']:
            errs.append('compare_refs' if set(c[0]['arguments'].get('product_ids',[]))!=set(e['product_ids']) else 'compare_order')
        else:
            out=c[0]['output'];table={x['field']:x['values'] for x in out.get('comparison',[])}
            for field,values in e.get('fields',{}).items():
                if field in table and table[field]!=values:errs.append('field_'+field)
    elif cap=='documents.answer':
        if 'documents.answer' not in tools:errs.append('not_routed_documents')
        if r.get('sources') and 'documents.answer' not in tools:errs.append('unsourced_claim')
        errs.append('knowledge_not_answered')  # registered-disabled is never answered knowledge
    elif fam=='product_fact':
        if e['missing']:
            unit={'battery_wh':'wh','weight_kg':'kg','refresh_hz':'hz'}.get(e['field'])
            if unit and re.search(r'\d\s*'+unit+r'\b',r['answer'].casefold()):errs.append('possibly_invented_missing')
            errs.append('fact_tool_missing')
        else:
            if not num_in(r['answer'],e['catalog_value']):errs.append('value_not_answered')
    elif fam=='consultation':
        s=[c for c in calls if c['tool']=='catalog.search']
        budget=re.search(r'(\d+)\s*triệu',row['question'])
        if s and budget and s[0]['arguments'].get('max_price_exclusive',0)>int(budget[1])*1_000_000+1:errs.append('budget_exceeded')
        errs.append('needs_semantic_review')
    for x in errs:errors_count[(fam,x)]+=1
    ok=not errs
    by_family[fam]['pass' if ok else 'fail']+=1
    checks[row['id']]=dict(family=fam,action=r['basic_action'],tools=tools,checks_pass=ok,errors=errs)

summary=dict(turns=len(rows),
    by_family={k:dict(v) for k,v in by_family.items()},
    actions={k:dict(v) for k,v in actions.items()},
    errors={f'{k[0]}:{k[1]}':v for k,v in errors_count.most_common()},
    median_seconds=statistics.median(r['seconds'] for r in rows),max_seconds=max(r['seconds'] for r in rows))
(OUT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=1),encoding='utf-8')
(OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=1))
