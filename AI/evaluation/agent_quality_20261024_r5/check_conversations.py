"""Mechanical contract checks; human review and end-to-end session scoring are separate."""
import json
from pathlib import Path
OUT=Path(__file__).parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
rows=read(OUT/'results.json');gold=read(OUT/'contract_gold.json')
traces={p.stem:read(p) for p in (OUT/'traces').rglob('*.json')}
oracle=read(OUT.parent/'regression_contract_20261024_r1/independent_sql_oracle.json')['periods']
numbers={(p['start'],p['end_exclusive']):p for p in oracle}
checks={}
for row in rows:
    if row['id'] not in gold:continue
    r=row['result'];g=gold[row['id']];errors=[];calls=r.get('tool_evidence',{}).get('calls',[])
    trace=traces[r['trace_id']]
    if 'action' in g and r['basic_action']!=g['action']:errors.append('action')
    if g.get('calls')==[] and calls:errors.append('unexpected_call')
    if g.get('calls'):
        if [dict(tool=c['tool'],arguments=c['arguments']) for c in calls]!=g['calls']:errors.append('calls_or_periods')
    if 'operation' in g and r.get('admin_plan',{}).get('operation')!=g['operation']:errors.append('operation')
    if g.get('reuse_comparison_periods'):
        wanted=[dict(start='2026-08-01',end='2026-09-01'),dict(start='2026-09-01',end='2026-10-01')]
        if [c['arguments'] for c in calls]!=wanted:errors.append('lost_comparison_periods')
    capability=g.get('capability')
    if capability and g.get('supported') is not False and 'references' not in g:
        if len(calls)!=1 or calls[0]['tool']!=capability:errors.append('capability')
        elif 'arguments' in g and calls[0]['arguments']!=g['arguments']:errors.append('arguments')
    if 'references' in g:
        last=trace['state_before'].get('catalog_context',{}).get('last_selection',[])
        if len(last)<2:
            if r['basic_action']!='clarify' or calls:errors.append('unsafe_reference')
        elif not calls or calls[0]['tool']!='catalog.compare':errors.append('comparison')
    if g.get('route')=='documents':
        if r['basic_action']!='documents' or not calls or calls[0]['output'].get('status')!='disabled':errors.append('document_route_or_status')
    if g.get('required_capabilities'):
        if set(c['tool'] for c in calls)!=set(g['required_capabilities']):errors.append('mixed_capabilities_not_addressed')
    if g.get('preserve_active_finance_period'):
        before=trace['state_before'].get('admin_context',{}).get('active_period')
        after=trace['state_after'].get('admin_context',{}).get('active_period')
        if not before or before!=after:errors.append('finance_context_lost')
    metric=g.get('metric')
    if metric:
        actual=r.get('metric_rows',[])
        if len(actual)!=1 or actual[0]['metric']!=metric:errors.append('metric')
        elif len(calls)==1 and calls[0]['tool']=='admin.finance':
            args=calls[0]['arguments'];expected=numbers[(args['start'],args['end'])][metric]
            if actual[0].get('value')!=expected:errors.append('independent_sql_number')
    checks[row['id']]=dict(checks_pass=not errors,errors=errors)
with (OUT/'conversation_checks.json').open('x',encoding='utf-8') as f:json.dump(checks,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(passed=sum(v['checks_pass'] for v in checks.values()),total=len(checks),failures={k:v['errors'] for k,v in checks.items() if not v['checks_pass']})))
