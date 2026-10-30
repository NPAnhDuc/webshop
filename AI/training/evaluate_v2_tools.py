"""Tutor round: ask the real Engine and compare with independently checked SQL.

Evaluation failures are queued, never auto-added to train or 'corrected' by an LLM.
No network model is necessary to test arithmetic, ACL or read-only tool behavior.
"""
import json
import os
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from shopbot.engine import Engine


def evaluate():
    os.environ['LLM_PROVIDER']='demo';os.environ['KEV_BASE_URL']=''
    engine=Engine(ROOT/'data/business_sql/scenario_v1/shop.sqlite')
    cases=[json.loads(line) for line in (HERE/'v2/data/tool_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    mapping={'net_revenue':('totals','revenue'),'net_cogs':('totals','cost'),
             'gross_profit':('totals','gross_profit'),'operating_expenses':('financial','operating_expenses'),
             'operating_profit_before_interest_tax':('financial','operating_profit_before_interest_tax'),
             'order_count':('financial','orders'),'return_units':('financial','return_units'),
             'purchases_received':('financial','purchases_received')}
    results=[]
    for case in cases:
        result=engine.ask(case['question'],'admin')
        section,field=mapping[case['field']]
        actual=result.get('analysis',{}).get(section,{}).get(field)
        correct=actual==case['expected_value']
        results.append(dict(case_id=case['id'],question=case['question'],split=case['split'],
                            expected=case['expected_value'],actual=actual,passed=correct,
                            failure_type=None if correct else ('routing_or_tool_contract' if 'analysis' not in result else 'arithmetic'),
                            sources=result.get('sources',[])))
    out=HERE/'v2/results';out.mkdir(exist_ok=True)
    summary={'scope':'Deterministic SQL tool execution, not generation/retrieval/model accuracy',
             'cases':len(results),'passed':sum(r['passed'] for r in results),
             'split_scores':{split:{'count':sum(r['split']==split for r in results),
                                   'passed':sum(r['passed'] and r['split']==split for r in results)} for split in ('train','validation','test')},
             'synthetic':True}
    (out/'tool-evaluation.json').write_text(json.dumps({'summary':summary,'results':results},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'tutor-failure-queue.json').write_text(json.dumps([r for r in results if not r['passed']],ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))
    return summary


if __name__=='__main__': evaluate()
