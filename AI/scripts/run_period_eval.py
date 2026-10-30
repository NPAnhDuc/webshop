"""Admin period bank (basic_rag): every expected number is computed by independent SQL on
shop.sqlite. A quarter answer passes if it states the DB quarter total or all three DB
monthly values; a month answer must state the DB monthly value; numbers from a wrong
period (another month) fail. Development only; written after the quarter bugs were seen.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
os.environ['CHATBOT_MODE']='basic_rag';os.environ['RAG_PIPELINE']='grounded'
from shopbot.engine import Engine
from shopbot.monthly import atomic_json

DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
CON=sqlite3.connect(f'file:{DB}?mode=ro',uri=True)
METRIC={'revenue':('SUM(revenue)','financial_ledger'),'gross_profit':('SUM(revenue-cost)','financial_ledger'),
        'cost':('SUM(cost)','financial_ledger'),'orders':('COUNT(*)','orders')}
WORDS={'revenue':'doanh thu thuần','gross_profit':'lãi gộp','cost':'giá vốn','orders':'số đơn hàng'}


def value(metric,start,end):
    expr,table=METRIC[metric]
    return CON.execute(f'SELECT {expr} FROM {table} WHERE day>=? AND day<?',(start,end)).fetchone()[0]


def month_bounds(y,m):return f'{y}-{m:02}-01',(f'{y+1}-01-01' if m==12 else f'{y}-{m+1:02}-01')


def bank():
    cases=[]
    quarter_forms=['quý {q}/{y}','quý {q} năm {y}','Q{q}/{y}','quý{q}/{y}']
    for i,(metric,q,y) in enumerate([('revenue',3,2026),('gross_profit',3,2026),('revenue',2,2026),('gross_profit',1,2026),
                                     ('cost',3,2026),('orders',2,2026),('revenue',4,2025),('gross_profit',2,2026)]):
        form=quarter_forms[i%len(quarter_forms)].format(q=q,y=y)
        months=[month_bounds(y,m) for m in range(3*q-2,3*q+1)]
        cases.append(dict(id=f'P{len(cases)+1:02}',kind='quarter',question=f'{WORDS[metric].capitalize()} {form} của shop là bao nhiêu?',
                          total=value(metric,months[0][0],months[-1][1]),monthly=[value(metric,a,b) for a,b in months],
                          wrong=[value(metric,*month_bounds(y,q))] if q!=3*q-2 else []))
    for metric,m,y in [('revenue',7,2026),('gross_profit',8,2026),('orders',3,2026),('cost',12,2025),('revenue',3,2026),('gross_profit',4,2026)]:
        a,b=month_bounds(y,m)
        cases.append(dict(id=f'P{len(cases)+1:02}',kind='month',question=f'{WORDS[metric].capitalize()} tháng {m}/{y} là bao nhiêu?',
                          total=value(metric,a,b),monthly=[],wrong=[]))
    return cases


def numbers(text):return {int(re.sub(r'[.,\s]','',m)) for m in re.findall(r'\d{1,3}(?:[.,]\d{3})+|\d+',text)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--today',default='2026-10-24')
    args=parser.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    engine=Engine(DB,today=date.fromisoformat(args.today));rows=[]
    for case in bank():
        start=time.monotonic();r=engine.ask(case['question'],'admin',{});got=numbers(r['answer'])
        if case['kind']=='quarter':
            ok=case['total'] in got or all(v in got for v in case['monthly'])
            wrong=[v for v in case['wrong'] if v in got and v not in case['monthly']]
        else:
            ok=case['total'] in got;wrong=[]
        errors=([] if ok else ['db_value_missing'])+(['wrong_period_value'] if wrong else [])
        rows.append(dict(**case,answer=r['answer'],sources=[s.get('document_id') for s in r.get('sources',[])],
                         checks_pass=not errors,errors=errors,seconds=round(time.monotonic()-start,2)))
        atomic_json(out/'results.json',rows);print(case['id'],case['question'],'PASS' if not errors else errors,flush=True)
    atomic_json(out/'summary.json',dict(passed=sum(r['checks_pass'] for r in rows),total=len(rows),today=args.today))


if __name__=='__main__':main()
