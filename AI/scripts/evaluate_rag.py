"""Evaluate retrieval and grounded document answers independently of SQL/routing."""
import argparse
from collections import Counter
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
from shopbot.retrieval import search,normalize
from shopbot.engine import Engine


def compact(text):return re.sub(r'\s+',' ',normalize(text)).strip()


def term_present(term,answer):
    if term.isdigit():
        value=int(term)
        candidates=[term,f'{value:,}'.replace(',','.'),f'{value:,}']
        if value and value%1_000_000==0:candidates += [str(value//1_000_000)+' trieu']
        if value and value%1_000_000_000==0:candidates += [str(value//1_000_000_000)+' ty']
        return any(re.search(r'(?<!\d)'+re.escape(c)+r'(?!\d)',compact(answer)) for c in candidates)
    return compact(term) in compact(answer)


def evaluate(case,docs,result):
    needs=case['needs'];answer=result['answer'];matched=[];document_hits=[]
    for need in needs:
        alternatives=[need]+case.get('equivalent_evidence',[])
        candidates=[d for d in docs if any(d.get('document_id')==n['document'] and
                    (not n.get('version') or d.get('version')==n['version']) for n in alternatives)]
        document_hits.append(bool(candidates))
        matched.append(any(d.get('document_id')==n['document'] and compact(n['quote']) in compact(d['text']) for d in candidates for n in alternatives))
    unavailable=bool(re.search(r'chua (?:co|du|tim|xac|quy)|khong (?:co|du|tim|xac)|can chu shop duyet|lien he nhan vien',compact(answer)))
    permissions=all(d.get('audience')!='admin' for d in docs) if case['role']=='customer' else True
    facts=all(term_present(t,answer) for t in case['terms'])
    kind=case['kind'];answer_ok=permissions and (facts if kind=='supported' else facts and unavailable if kind=='partial' else unavailable if kind=='missing' else permissions)
    unwarranted=kind=='supported' and result.get('rag',{}).get('answerability') in ('partial','none','unverified')
    if unwarranted:answer_ok=False
    return dict(required_passages=len(needs),passages_found=sum(matched),documents_found=sum(document_hits),
                all_evidence_found=all(matched) if needs else None,facts_present=facts,
                answer_pass=answer_ok,abstention=unavailable,unnecessary_abstention=unwarranted,permissions_ok=permissions,
                words=len(answer.split()),citations=len(re.findall(r'\[Nguồn:',answer)),
                synthesis=result.get('rag',{}),truncated=sum(bool(d.get('embedding_truncated')) for d in docs))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    parser.add_argument('--split',choices=['dev','holdout','all'],default='dev');parser.add_argument('--retrieval-only',action='store_true')
    args=parser.parse_args();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=False)
    bank=ROOT/'evaluation/rag_v1/bank.json';cases=json.loads(bank.read_text(encoding='utf8'))
    errata_path=bank.with_name('errata.json');errata=json.loads(errata_path.read_text(encoding='utf8')) if errata_path.exists() else {'changes':{}}
    cases=[dict(c,**{k:v for k,v in errata['changes'].get(c['id'],{}).items() if k!='reason'}) for c in cases]
    cases=[c for c in cases if args.split=='all' or c['split']==args.split]
    db=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
    metadata=dict(bank_sha256=hashlib.sha256(bank.read_bytes()).hexdigest(),errata_sha256=hashlib.sha256(errata_path.read_bytes()).hexdigest() if errata_path.exists() else None,database_sha256=hashlib.sha256(db.read_bytes()).hexdigest(),
        split=args.split,cases=len(cases),retrieval_only=args.retrieval_only,reranker=os.getenv('RAG_RERANK','0'),answer_mode=os.getenv('RAG_ANSWER_MODE','extractive'),sources={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in [ROOT/'shopbot/retrieval.py',ROOT/'shopbot/chunking.py',ROOT/'shopbot/engine.py',ROOT/'shopbot/rag_answer.py'] if p.exists()},
        limitations='Authored synthetic-shop benchmark; wording-family variants are not independent customer conversations. No SQL or routing score included.')
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf8')
    rows=[];started=time.monotonic()
    with (out/'results.jsonl').open('w',encoding='utf8') as log:
        for case in cases:
            tick=time.monotonic()
            try:
                docs=search(case['question'],case['role'],db_path=db,as_of=date.fromisoformat(case['as_of']))
                state=dict(question=case['question'],role=case['role'],intent='documents',sources=docs,rows=[],profile={},plan={},
                           answer='\n\n'.join(d['text']+f"\n[Nguồn: {d['source']}, đoạn {d['section']}]" for d in docs) if docs else 'Chưa tìm thấy tài liệu phù hợp.',trace=[])
                result=state if args.retrieval_only else dict(state,**Engine(db).compose(state))
                score=evaluate(case,docs,result)
                row=dict(id=case['id'],group=case['group'],split=case['split'],question=case['question'],kind=case['kind'],score=score,
                         answer=result['answer'],sources=docs,seconds=time.monotonic()-tick)
            except Exception as exc:row=dict(id=case['id'],split=case['split'],question=case['question'],error=type(exc).__name__+': '+str(exc))
            rows.append(row);log.write(json.dumps(row,ensure_ascii=False)+'\n');log.flush()
            if len(rows)%8==0:print('DONE',len(rows),'/',len(cases),flush=True)
    scored=[r['score'] for r in rows if 'score' in r];denominator=sum(s['required_passages'] for s in scored)
    summary=dict(metadata,completed=len(rows),errors=sum('error' in r for r in rows),
        passage_recall=sum(s['passages_found'] for s in scored)/denominator if denominator else None,
        document_recall=sum(s['documents_found'] for s in scored)/denominator if denominator else None,
        all_evidence_pass=sum(s['all_evidence_found'] is True for s in scored),
        answer_pass=sum(s['answer_pass'] for s in scored),permissions_pass=sum(s['permissions_ok'] for s in scored),
        average_answer_words=sum(s['words'] for s in scored)/len(scored) if scored else 0,
        retrieval_truncations=sum(s['truncated'] for s in scored),elapsed_seconds=time.monotonic()-started,
        by_kind={kind:dict(cases=len(group:=[r for r in rows if r.get('kind')==kind]),passed=sum(r['score']['answer_pass'] for r in group)) for kind in Counter(c['kind'] for c in cases)})
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    print('SUMMARY',json.dumps({k:v for k,v in summary.items() if k not in ('sources','limitations')},ensure_ascii=True),flush=True)


if __name__=='__main__':main()
