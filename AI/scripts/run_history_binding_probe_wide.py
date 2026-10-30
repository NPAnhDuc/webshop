"""Local controlled history probe; recorded answers are inputs, never knowledge."""
import argparse,copy,hashlib,json,os,sys,time
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
os.environ['CHATBOT_MODE']='basic_rag';os.environ['RAG_PIPELINE']='grounded'
os.environ['RAG_LOG_ORIGIN']='quality_loop:history_binding_probe_r2'
from shopbot.engine import Engine
from shopbot.monthly import exclusive,atomic_json
from shopbot.quality_eval import grade

BASE=ROOT/'evaluation/quality_loop_20261021'
OUT=ROOT/'evaluation/history_binding_20261022_r2'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
CONFIG_KEYS=['CHATBOT_MODE','RAG_PIPELINE','OLLAMA_MODEL','PLANNER_MODEL','OLLAMA_BASE_URL','OLLAMA_NUM_GPU','VI_EMBEDDING_URL','RAG_RERANK']

def code():
    files=[ROOT/'app.py',*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__).resolve()]
    return {str(p.relative_to(ROOT)):sha(p) for p in files}

def prepare():
    if OUT.exists():raise SystemExit('Probe exists; do not overwrite frozen fixtures')
    original={r['id']:r for r in read(BASE/'candidate_v9_development/results.json')}
    brief={r['id']:r for r in read(BASE/'candidate_v10_development/results.json')}
    bank={c['id']:c for c in read(BASE/'bank.json')};cases=[]
    targets=[c for c in bank.values() if c.get('topic')=='product_context' and c.get('split')=='development']
    assert len(targets)==56
    for target_case in targets:
        target=target_case['id']
        parents=[c for c in bank.values() if c.get('conversation')==target_case['conversation'] and c.get('topic')=='product_single']
        assert len(parents)==1,target
        parent=parents[0]['id']
        assert parents[0]['split']=='development'
        assert list(original).index(parent)<list(original).index(target)
        assert list(brief).index(parent)<list(brief).index(target)
        title=original[parent]['result']['profile']['rag_product_subject']
        assert brief[parent]['result']['profile']['rag_product_subject']==title
        assert title and title in bank[parent]['question']
        for variant,source in [('original_history',original),('brief_history',brief),('explicit_subject_brief_history',brief)]:
            profile=copy.deepcopy(source[parent]['result']['profile'])
            assert len(profile.get('history',[]))==1
            assert profile['history'][0]['question']==source[parent]['question']
            case=copy.deepcopy(bank[target]);question=case['question']
            if variant=='explicit_subject_brief_history':
                assert 'sản phẩm vừa nói' in question
                question=question.replace('sản phẩm vừa nói',title)
            case.update(id=target+'_'+variant,question=question,conversation=target+'_'+variant,
                        variant=variant,parent_id=parent,target_id=target,input_profile=profile,
                        input_provenance=dict(round='candidate_v9_development' if source is original else 'candidate_v10_development',parent_id=parent,
                            note='Recorded previous model response as untrusted conversation input, not a knowledge publication or a gold answer. No desired answer supplied to Engine.'))
            cases.append(case)
    OUT.mkdir()
    (OUT/'run_history_binding_probe_wide.executed.py').write_bytes(Path(__file__).read_bytes())
    provenance_paths=[BASE/'bank.json',BASE/'gold_sources.json',BASE/'metadata.json',BASE/'candidate_v9_development/results.json',BASE/'candidate_v10_development/results.json']
    provenance={str(p):sha(p) for p in provenance_paths}
    counts=dict(targets=len(targets),scenarios=len(cases),distinct_question_texts=len({c['question'] for c in cases}),
        distinct_input_profiles=len({json.dumps(c['input_profile'],sort_keys=True,ensure_ascii=False) for c in cases}),
        identical_parent_profiles=sum(original[c['parent_id']]['result']['profile']==brief[c['parent_id']]['result']['profile'] for c in cases if c['variant']=='original_history'))

    atomic_json(OUT/'bank.json',cases)
    (OUT/'gold_sources.json').write_bytes((BASE/'gold_sources.json').read_bytes())
    source=read(BASE/'metadata.json')
    source.update(bank_sha256=sha(OUT/'bank.json'),gold_sha256=sha(OUT/'gold_sources.json'))
    atomic_json(OUT/'metadata.json',dict(source=source,provenance=provenance,counts=counts,code=code(),config={k:os.getenv(k) for k in CONFIG_KEYS},
        design='All 56 already-opened development product_context groups, three controlled variants each. Recorded patch10 histories are alternate histories, not necessarily shorter in every case. Explicit current-question subject comes only from matching confirmed profile entity; no desired fact is inserted. Recorded responses are untrusted inputs, never gold/knowledge/training. Baseline on unchanged patch9 before any resolver repair; not independent validation.'))

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
