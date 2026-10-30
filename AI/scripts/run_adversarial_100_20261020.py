"""Ask frozen 100-case stress bank once; no training or mutations to bot/data."""
import hashlib,json,os,sys,time
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
os.environ['CHATBOT_MODE']='basic_rag'
os.environ['RAG_LOG_ORIGIN']='adversarial_100_20261020'
from shopbot.engine import Engine
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import atomic_json

OUT=ROOT/'evaluation/adversarial_100_20261020'
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf8'))


def verify(meta):
    assert hashlib.sha256((OUT/'bank.json').read_text(encoding='utf8').encode()).hexdigest()==meta['bank_sha256'],'bank changed'
    assert sha(DB)==meta['database_sha256'],'database changed'
    assert sha(KnowledgeStore(DB).manifest)==meta['knowledge_sha256'],'knowledge changed'
    assert all(sha(ROOT/p)==v for p,v in meta['code_sha256'].items()),'bot code changed'


def main():
    sys.stdout.reconfigure(encoding='utf8')
    meta=read(OUT/'metadata.json');verify(meta)
    config={k:os.getenv(k) for k in ['CHATBOT_MODE','LLM_PROVIDER','OLLAMA_MODEL','PLANNER_MODEL','OLLAMA_BASE_URL','OLLAMA_NUM_GPU',
                                   'CONVERSATION_MODE','VI_EMBEDDING_URL','RAG_SYNTHESIS','RAG_ANSWER_MODE','RAG_RERANK']}
    if (OUT/'runtime_config.json').exists():assert read(OUT/'runtime_config.json')==config,'config changed'
    else:atomic_json(OUT/'runtime_config.json',config)
    bank=read(OUT/'bank.json');rows=read(OUT/'results.json') if (OUT/'results.json').exists() else []
    assert [r['id'] for r in rows]==[c['id'] for c in bank[:len(rows)]],'saved results are not a prefix'
    memories={}
    for row in rows:
        if row['result'].get('profile'):memories[row['conversation']]=row['result']['profile']
    engine=Engine(DB,today=date(2026,10,20))
    for case in bank[len(rows):]:
        if len(rows)%10==0:verify(meta)
        start=time.monotonic();issues=[]
        try:
            # ONLY the user's question, role, and previously generated same-session
            # profile enter the engine. Rubrics/gold are evaluation-only.
            result=engine.ask(case['question'],case['role'],memories.get(case['conversation']))
            memories[case['conversation']]=result.get('profile')
            lookup={s['chunk_id']:s for s in result.get('sources',[])}
            if result.get('rows'):issues.append('unexpected tool rows')
            if case['role']=='customer' and any(s.get('audience')=='admin' for s in lookup.values()):issues.append('private source leak')
            for claim in result.get('rag',{}).get('claims',[]):
                for evidence in claim.get('evidence',[]):
                    if evidence.get('chunk_id') not in lookup or any(q not in lookup[evidence['chunk_id']]['text'] for q in evidence.get('quotes',[])):
                        issues.append('quote absent from supplied source')
        except Exception as exc:
            result={};issues.append(f'{type(exc).__name__}: {str(exc)[:300]}')
        row=dict(id=case['id'],role=case['role'],conversation=case['conversation'],question=case['question'],
                 seconds=round(time.monotonic()-start,2),integrity_issues=issues,result=result,review_status='PENDING_MANUAL_REVIEW')
        rows.append(row);atomic_json(OUT/'results.json',rows)
        print(case['id'],result.get('basic_action','ERROR'),result.get('rag',{}).get('answerability'),
              str(row['seconds'])+'s',('; '.join(issues) or 'recorded'),flush=True)
    verify(meta)
    atomic_json(OUT/'integrity.json',dict(unchanged=True,cases=len(rows),bank_sha256=meta['bank_sha256'],
                                         database_sha256=sha(DB),knowledge_sha256=sha(KnowledgeStore(DB).manifest),
                                         code_unchanged=True,config=config))
    print(f'COMPLETE: {len(rows)} raw answers, source checks only; manual scoring still required.',flush=True)


if __name__=='__main__':main()
