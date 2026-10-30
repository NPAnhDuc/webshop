"""Local controlled history probe; recorded answers are inputs, never knowledge."""
import argparse,copy,hashlib,json,os,sys,time
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
os.environ['CHATBOT_MODE']='basic_rag';os.environ['RAG_PIPELINE']='grounded'
os.environ['RAG_LOG_ORIGIN']='quality_loop:history_binding_candidate_p11'
from shopbot.engine import Engine
from shopbot.monthly import exclusive,atomic_json
from shopbot.quality_eval import grade

BASE=ROOT/'evaluation/quality_loop_20261021'
OUT=ROOT/'evaluation/history_binding_20261022_r2_candidate_p11'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CONFIG_KEYS=['CHATBOT_MODE','RAG_PIPELINE','OLLAMA_MODEL','PLANNER_MODEL','OLLAMA_BASE_URL','OLLAMA_NUM_GPU','VI_EMBEDDING_URL','RAG_RERANK']

def code():
    files=[ROOT/'app.py',*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__).resolve()]
    return {str(p.relative_to(ROOT)):sha(p) for p in files}

def prepare():
    if OUT.exists():raise SystemExit('Candidate exists; preserve frozen inputs/results')
    baseline=ROOT/'evaluation/history_binding_20261022_r2'
    old=read(baseline/'metadata.json')
    # Same frozen fixture bytes; new metadata/code snapshot, never rewrite r2.
    for name,key in [('bank.json','bank_sha256'),('gold_sources.json','gold_sha256')]:
        assert sha(baseline/name)==old['source'][key],name
    assert read(baseline/'integrity.json')['unchanged']
    OUT.mkdir()
    for name in ['bank.json','gold_sources.json']:
        (OUT/name).write_bytes((baseline/name).read_bytes())
    (OUT/'run_history_binding_candidate.executed.py').write_bytes(Path(__file__).read_bytes())
    provenance=dict(old['provenance'])
    provenance.update({str(baseline/name):sha(baseline/name) for name in ['bank.json','metadata.json','results.json','human_review.json']})
    atomic_json(OUT/'metadata.json',dict(source=old['source'],provenance=provenance,counts=old['counts'],code=code(),
        config={k:os.getenv(k) for k in CONFIG_KEYS},baseline=str(baseline),
        design='Patch11 trial: exactly the same 168 controlled inputs/gold as r2 baseline. Single confirmed-product reference binding only; no facts or assistant answers copied into the standalone question. Development diagnostic, not validation or accepted production gain.'))


def verify(meta):
    source=meta['source']
    for path,key in [(OUT/'bank.json','bank_sha256'),(OUT/'gold_sources.json','gold_sha256'),(Path(source['database']),'database_sha256'),(Path(source['knowledge_manifest']),'knowledge_sha256')]:
        assert sha(path)==source[key],str(path)
    for path,expected in meta['provenance'].items():
        assert sha(Path(path))==expected,path
    assert code()==meta['code'],'Code changed during probe'
    assert {k:os.getenv(k) for k in CONFIG_KEYS}==meta['config'],'Config changed'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    with exclusive(BASE/'runner.lock'):
        if args.prepare_only:
            prepare();verify(read(OUT/'metadata.json'));print(json.dumps(read(OUT/'metadata.json')['counts']), 'No model called.');return
        meta=read(OUT/'metadata.json');verify(meta);cases=read(OUT/'bank.json')
        rows=read(OUT/'results.json') if (OUT/'results.json').exists() else []
        assert [r['id'] for r in rows]==[c['id'] for c in cases[:len(rows)]]
        engine=Engine(Path(meta['source']['database']),today=date.fromisoformat(meta['source']['today']));infra=0
        for case in cases[len(rows):]:
            verify(meta);start=time.monotonic()
            try:result=engine.ask(case['question'],case['role'],copy.deepcopy(case['input_profile']))
            except Exception as exc:result=dict(answer='',error=type(exc).__name__+': '+str(exc)[:250])
            checks=grade(case,result)
            rows.append(dict(id=case['id'],target_id=case['target_id'],variant=case['variant'],question=case['question'],seconds=round(time.monotonic()-start,3),result=result,checks=checks))
            atomic_json(OUT/'results.json',rows)
            atomic_json(OUT/'progress.json',dict(completed=len(rows),total=len(cases),last_id=case['id']))
            print(case['id'],checks['status'],flush=True)
            infra=infra+1 if any(i['cause']=='INFRASTRUCTURE' for i in checks['issues']) else 0
            if infra>=3:raise RuntimeError('Three infrastructure failures; inspect service,not knowledge')
        verify(meta);atomic_json(OUT/'integrity.json',dict(unchanged=True,cases=len(rows),code=meta['code'],bank_sha256=meta['source']['bank_sha256']))

if __name__=='__main__':main()
