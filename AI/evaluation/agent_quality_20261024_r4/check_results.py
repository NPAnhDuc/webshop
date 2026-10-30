"""Mechanical checks; semantic review is recorded separately. Preserve old checker/gold."""
import json
from pathlib import Path
import runpy
import statistics

OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
source=(OUT.parents[1]/'scripts/check_admin_agent_batch.py').read_text(encoding='utf-8')
old="c['arguments'][k]";new="c['arguments'].get(k)"
assert source.count(old)==1
adapted=OUT/'regression_checker.py'
with adapted.open('x',encoding='utf-8') as stream:stream.write(source.replace(old,new))
runpy.run_path(str(adapted),run_name='frozen_regression_checker')['check'](OUT/'regression')
gold=read(OUT/'new_gold.json');rows=read(OUT/'results.json');checks={}
for row in rows:
    if row['id'] not in gold:continue
    expected=gold[row['id']];result=row['result'];errors=[]
    calls=result.get('tool_evidence',{}).get('calls',[])
    if result['basic_action']!=expected['action']:errors.append('action')
    if [c['tool'] for c in calls]!=([expected['tool']] if expected['tool'] else []):errors.append('tool')
    if expected['tool']=='admin.data_quality':
        if calls and calls[0]['arguments']!={}:errors.append('arguments')
        if not result.get('sources'):errors.append('source')
        if 'Chưa xác nhận dữ liệu bán hàng đầy đủ' not in result['answer']:errors.append('coverage_claim')
    if row['id'] in ('Q04','Q13'):
        expected_metric,number=('revenue',1189908000) if row['id']=='Q04' else ('orders',131)
        if result.get('metric_rows')!=[dict(metric=expected_metric,value=number,unit='VND' if expected_metric=='revenue' else 'đơn')]:errors.append('numbers')
        if not calls or calls[0]['arguments']!=dict(start='2026-09-01',end='2026-10-01'):errors.append('period')
    if row['id']=='Q17':
        if not calls or calls[0]['arguments']!=dict(start='2026-07-01',end='2026-10-01',metric='gross_profit'):errors.append('chart_args')
        if not result.get('artifacts'):errors.append('missing_chart')
        if not calls or sum(x['values']['gross_profit'] for x in calls[0]['output'].get('chart_data',[]))!=502202000:errors.append('chart_numbers')
    if row['id']=='Q19':
        filters=result.get('profile',{}).get('catalog_context',{}).get('filters',{})
        if filters.get('limit')!=3 or filters.get('category')!='ram' or filters.get('max_price_exclusive')!=3000000:errors.append('catalog_args')
        if len(result.get('rows',[]))!=3:errors.append('catalog_count')
    checks[row['id']]=dict(checks_pass=not errors,errors=errors,semantic_review_required=True)
with (OUT/'checks.json').open('x',encoding='utf-8') as stream:json.dump(checks,stream,ensure_ascii=False,indent=2)
reg=read(OUT/'regression/checks.json')
summary=dict(new_checks_pass=sum(c['checks_pass'] for c in checks.values()),new_total=len(checks),
    regression_checks_pass=sum(c['checks_pass'] for c in reg.values()),regression_total=len(reg),
    median_seconds=statistics.median(r['seconds'] for r in rows),max_seconds=max(r['seconds'] for r in rows),
    integrity=read(OUT/'integrity.json'),accepted_for_application=False,
    note='Same84 questions/gold as r3. Q19 checker category corrected to canonical catalog ram; old failure still fails the independent count criterion. Structured traces enabled. Mechanical checks do not replace semantic review.')
with (OUT/'summary.json').open('x',encoding='utf-8') as stream:json.dump(summary,stream,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False))
