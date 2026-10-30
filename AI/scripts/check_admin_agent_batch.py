"""Mechanical checks only. A separate semantic review is still required."""
import argparse
from decimal import Decimal,ROUND_HALF_UP
import json
from pathlib import Path


def check(folder):
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    rows=read(folder/'results.json');gold=read(folder/'gold.json');selections={};checks={}
    for row in rows:
        i=row['id'];r=row['result'];g=gold[i];errors=[]
        if r['basic_action']!=g['action']:errors.append('action')
        if 'periods' in g:
            calls=r.get('tool_evidence',{}).get('calls',[])
            expected=g['periods']
            periods=[{k:c['arguments'][k] for k in ('start','end')} for c in calls]
            if periods!=[p['period'] for p in expected]:errors.append('periods_or_unexpected_execution')
            if g.get('metric') and g['action']=='answer':
                actual=r.get('metric_rows',[])
                keys=list(expected[0]['metrics']) if g['metric']=='overview' else [g['metric']]
                if len(actual)!=len(keys) or {v['metric'] for v in actual}!=set(keys):errors.append('metric_keys')
                for v in actual:
                    k=v['metric']
                    if g.get('compare'):
                        a,b=[p['metrics'][k] for p in expected]
                        delta=float(Decimal(str(b))-Decimal(str(a))) if k=='gross_margin_pct' else b-a
                        pct=float((Decimal(delta)*100/Decimal(a)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP)) if a>0 and k!='gross_margin_pct' else None
                        if any(v.get(key)!=val for key,val in dict(baseline=a,current=b,delta=delta,percent_change=pct).items()):errors.append('comparison_numbers:'+k)
                    elif v.get('value')!=expected[0]['metrics'][k]:errors.append('value:'+k)
                if g.get('chart'):
                    if len(calls)!=1 or calls[0]['tool']!='admin.finance_chart':errors.append('chart_tool')
                    else:
                        output=calls[0]['output']
                        if output.get('metric')!=g['metric'] or not Path(output.get('artifact','')).is_file():errors.append('chart_artifact_or_metric')
                        if sum(m['values'][g['metric']] for m in output['chart_data'])!=expected[0]['metrics'][g['metric']]:errors.append('chart_sum')
            for c,p in zip(calls,expected):
                output=c['output'];report=output.get('report',output)
                if report['quality']['source_rows']!=p['rows']:errors.append('source_row_count')
                if report['data_source']!='demo' or 'Dữ liệu mô phỏng' not in r['answer']:errors.append('provenance_label')
        else:
            data=r.get('tool_evidence',{}).get('data',{})
            filters=r['profile'].get('catalog_context',{}).get('filters',{})
            for key in ('limit','category','brand'):
                if key in g and filters.get(key)!=g[key]:errors.append('filter:'+key)
            if 'ceiling' in g:
                if filters.get('max_price_exclusive')!=g['ceiling']:errors.append('budget_bound')
                products=data.get('products',[])
                if any(not (0<p['variant']['price']<g['ceiling'] and p['variant']['available_qty']>0) for p in products):errors.append('price_or_stock')
                if len({p['id'] for p in products})!=len(products):errors.append('duplicate_products')
            if 'returned_count' in g and data.get('returned_count')!=g['returned_count']:errors.append('returned_count')
            if 'prior_positions' in g:
                previous=selections.get(row['conversation'],[])
                wanted=[previous[n] for n in g['prior_positions']] if previous else []
                if not wanted or [p['id'] for p in data.get('products',[])]!=wanted:errors.append('comparison_order')
            if 'product_ids' in g and [p['id'] for p in data.get('products',[])]!=g['product_ids']:errors.append('comparison_ids')
            if r['intent']=='products':selections[row['conversation']]=[p['id'] for p in r['rows']]
        if row['role']=='customer' and r.get('tool_evidence',{}).get('calls'):errors.append('customer_admin_execution')
        checks[i]=dict(checks_pass=not errors,errors=errors,semantic_review_required=True)
    (folder/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(checks_pass=sum(c['checks_pass'] for c in checks.values()),total=len(checks),failures={i:c['errors'] for i,c in checks.items() if c['errors']}),ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path)
    check(parser.parse_args().folder)
