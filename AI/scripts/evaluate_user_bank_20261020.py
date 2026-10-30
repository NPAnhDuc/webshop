"""Frozen user-supplied 50-question acceptance run. Never feed answer hints to bot.

Raw answers first; automated checks are provisional until manual source review.
No changes to knowledge, model weights or chatbot prompts during this run.
"""
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
os.environ['CHATBOT_MODE']='basic_rag'
os.environ['RAG_LOG_ORIGIN']='user_acceptance_20261020'
from shopbot.engine import Engine
from shopbot.knowledge import KnowledgeStore

A='Lenovo LOQ Gaming 15IRH8'
B='MSI Modern 15 B12M'
FULL={26:['12450H','1255U'],37:['6%'],38:['4%','10%'],39:['không cộng dồn'],40:['90','chủ shop'],43:[],44:['1189908000','131']}
PARTIAL={1:['16'],2:['1920'],4:['2.4'],5:['HDMI'],6:[],7:[],8:['144'],9:['NVMe'],27:[],35:[],41:['4 ngày'],42:[]}
GUARDS={28:['live_product','handoff'],29:['outside'],30:['denied'],48:['deferred','answer'],49:['deferred'],50:['denied','answer']}


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    resume=len(sys.argv)>3 and sys.argv[3]=='--resume'
    source=Path(sys.argv[1]);out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=resume)
    raw=source.read_text(encoding='utf-8-sig');(out/'original.txt').write_text(raw,encoding='utf8')
    cases=[]
    for line in raw.splitlines():
        match=re.match(r'^\s*(\d+)\.\s*(.*?)\s*→\s*(.*)$',line)
        if not match:continue
        number=int(match[1]);q=match[2]
        q=re.sub(r'\[mã A\]',A,q,flags=re.I);q=re.sub(r'\[mã B\]',B,q,flags=re.I)
        q=q.replace('Nhà cung cấp [A]','Nhà cung cấp SUP-LAP')
        coverage='FULL' if number in FULL else 'PARTIAL_DATA' if number in PARTIAL else 'GUARD' if number in GUARDS else 'HISTORICAL_UNSUPPORTED' if number==46 else 'CLARIFY' if number==47 else 'MISSING_DATA'
        group='spec-A' if number<=6 else 'compare' if number in (26,27) else 'strategy' if 31<=number<=36 else 'report' if number in (43,44) else 'versions' if number in (46,47) else str(number)
        cases.append(dict(id=number,role='customer' if number<=30 else 'admin',original_question=match[2],question=q,
                          supplied_expectation=match[3],coverage_before_run=coverage,group=group))
    if [c['id'] for c in cases]!=list(range(1,51)):raise ValueError('Expected exactly questions 1..50')
    bank=json.dumps(cases,ensure_ascii=False,indent=2);(out/'bank.json').write_text(bank,encoding='utf8')
    db=ROOT/'data/business_sql/scenario_v1/shop.sqlite';store=KnowledgeStore(db)
    metadata=dict(date='2026-10-20',clock='Asia/Bangkok',mode='basic_rag',mapping=dict(product_A=A,product_B=B,supplier_A='SUP-LAP'),
        attachment_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),bank_sha256=hashlib.sha256(bank.encode()).hexdigest(),
        database_sha256=hashlib.sha256(db.read_bytes()).hexdigest(),knowledge_sha256=hashlib.sha256(store.manifest.read_bytes()).hexdigest(),
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['shopbot/basic_rag.py','shopbot/engine.py','shopbot/retrieval.py','shopbot/rag_answer.py']},
        assumptions=['Relative/current quarter means Q4/2026; do not silently substitute Q4/2025.',
                     'September means September 2026.',
                     'Questions 1–6, 26–27, 31–36, 43–44, 46–47 run with within-group conversation memory.',
                     'No answer hint after the arrow is provided to the chatbot.',
                     'A missing-data refusal is not a full functionality pass.',
                     'Question 8 supplied assertion that 144Hz only benefits gaming is not accepted without source support.'])
    if resume:
        previous=json.loads((out/'metadata.json').read_text(encoding='utf8'))
        for key in ('bank_sha256','database_sha256','knowledge_sha256','source_sha256'):
            if previous[key]!=metadata[key]:raise ValueError('Cannot resume across changes: '+key)
    else:(out/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf8')
    memories={};rows=json.loads((out/'results.json').read_text(encoding='utf8')) if resume else []
    if [r['case']['id'] for r in rows]!=list(range(1,len(rows)+1)):raise ValueError('Invalid saved prefix')
    for row in rows:
        if row['result'].get('profile'):memories[row['case']['group']]=row['result']['profile']
    engine=Engine(db,today=date(2026,10,20))
    for c in cases:
        if c['id']<=len(rows):continue
        start=time.monotonic();issues=[]
        try:
            r=engine.ask(c['question'],c['role'],memories.get(c['group']))
            memories[c['group']]=r['profile']
            if r.get('rows'):issues.append('tool rows in basic RAG')
            if c['role']=='customer' and any(s.get('audience')=='admin' for s in r['sources']):issues.append('private source leak')
            lookup={d['chunk_id']:d for d in r['sources']}
            for claim in r.get('rag',{}).get('claims',[]):
                for ev in claim.get('evidence',[]):
                    if ev['chunk_id'] not in lookup or any(q not in lookup[ev['chunk_id']]['text'] for q in ev.get('quotes',[])):issues.append('quote absent from source')
            terms=FULL.get(c['id'],PARTIAL.get(c['id'],[]))
            for term in terms:
                if term.lower() not in r['answer'].lower():issues.append('expected fact absent: '+term)
            if c['id'] in GUARDS and r.get('basic_action') not in GUARDS[c['id']]:issues.append('unexpected guard action')
            if c['id']==43 and len(r.get('rag',{}).get('claims',[]))!=5:issues.append('summary does not contain exactly 5 source claims')
            if c['id']==47 and r.get('basic_action')!='clarify':issues.append('unspecified documents not clarified')
        except Exception as exc:
            r={};issues.append(type(exc).__name__+': '+str(exc)[:200])
        rows.append(dict(case=c,seconds=round(time.monotonic()-start,2),automated_issues=issues,review_status='PENDING_MANUAL_SOURCE_REVIEW',result=r))
        (out/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
        print(c['id'],'ISSUES' if issues else 'RECORDED',','.join(issues),flush=True)
    after=dict(database_sha256=hashlib.sha256(db.read_bytes()).hexdigest(),knowledge_sha256=hashlib.sha256(store.manifest.read_bytes()).hexdigest())
    (out/'integrity.json').write_text(json.dumps(dict(before=metadata,after=after,unchanged=all(metadata[k]==v for k,v in after.items())),ensure_ascii=False,indent=2),encoding='utf8')
    print('COMPLETE: 50 raw answers recorded; manual review required',flush=True)


if __name__=='__main__':main()
