"""One frozen local batch of the300-turn buyer development bank (r2) on the r11 agent code.

Development only: gold never enters prompts, results are not training data.
Stops only on a model outage (3 consecutive turns without any model reply),
not on validation failures, so the whole bank's error surface is visible.
"""
import argparse
import copy
from datetime import date
import json
import os
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from shopbot.agent_tools import AgentTools,CatalogTools,GroundedDocuments
import requests as _requests
from shopbot.agent_conversation import CatalogConversation
from shopbot.curated_reader import CuratedReader
from shopbot.engine import Engine
from shopbot.monthly import atomic_json,exclusive
from shopbot.de_snapshot import digest,write_new

OUT=ROOT/'evaluation/buyer_run_20261024_r5'
BANK=ROOT/'evaluation/buyer_expansion_20261024_r2/bank.jsonl'
CURATED=ROOT/'data/de_pipeline/retail_sim_v1/curated_20261024_r1'
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
CAT=ROOT/'data/agent_platform_20261023/catalog_v1/catalog_public.json'
CONFIG=['OLLAMA_BASE_URL','OLLAMA_MODEL','OLLAMA_NUM_GPU']
read=lambda p:json.loads(p.read_text(encoding='utf-8'))


def worker():
    info=_requests.get(os.environ['VI_EMBEDDING_URL'].rstrip('/')+'/health',timeout=5).json()
    return dict(model=info['model'],revision=info['revision'],max_tokens=info['max_tokens'])


def prepare():
    OUT.mkdir(exist_ok=False)
    (OUT/'bank.jsonl').write_bytes(BANK.read_bytes())
    files=[DB,CAT,*CURATED.rglob('*'),OUT/'bank.jsonl',Path(__file__),*sorted((ROOT/'shopbot').glob('*.py'))]
    write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
        config={k:os.getenv(k) for k in CONFIG},today='2026-10-23',curated_pin=digest(CURATED/'manifest.json'),
        bank_sha256=digest(BANK),code='r15 agent (r14 + documents.answer via grounded RAG)',embedding_worker=worker(),
        protocol='300 buyer development turns, customer role, CHATBOT_MODE=agent_tools. Not independent validation. No typo feature.'))
    snap=OUT/'code_snapshot';snap.mkdir()
    for p in [*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__)]:(snap/p.name).write_bytes(p.read_bytes())
    print('Frozen300 buyer turns; no model calls.')


def main():
    meta=read(OUT/'metadata.json')
    def verify():
        assert meta['config']=={k:os.getenv(k) for k in CONFIG}
        assert all(digest(Path(p))==sha for p,sha in meta['files'].items()),'Input/code changed'
    verify();os.environ['CHATBOT_MODE']='agent_tools'
    assert worker()==meta['embedding_worker'],'Embedding worker changed'
    tools=AgentTools(CatalogTools(read(CAT)),DB,OUT/'charts',curated_reader=CuratedReader(CURATED,meta['curated_pin']),
        documents=GroundedDocuments(DB,date.fromisoformat(meta['today'])))
    engine=Engine(DB,today=date.fromisoformat(meta['today']),tool_agent=CatalogConversation(tools),trace_directory=OUT/'traces')
    import requests
    post=requests.post;calls=[]
    def observe(url,**kwargs):
        response=post(url,**kwargs);body=response.json()
        calls.append(dict(done_reason=body.get('done_reason'),prompt_eval_count=body.get('prompt_eval_count'),
            eval_count=body.get('eval_count'),content=body.get('message',{}).get('content')))
        return response
    requests.post=observe
    bank=[json.loads(line) for line in (OUT/'bank.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    rows=read(OUT/'results.json') if (OUT/'results.json').exists() else []
    assert [r['id'] for r in rows]==[c['id'] for c in bank[:len(rows)]]
    memory={r['conversation']:r['result']['profile'] for r in rows};outage=0
    for case in bank[len(rows):]:
        verify();calls.clear();start=time.monotonic()
        result=engine.ask(case['question'],case['role'],copy.deepcopy(memory.get(case['conversation'])))
        memory[case['conversation']]=result['profile']
        rows.append(dict(**case,result=result,seconds=round(time.monotonic()-start,3),model_calls=copy.deepcopy(calls)))
        atomic_json(OUT/'results.json',rows);atomic_json(OUT/'progress.json',dict(completed=len(rows),total=len(bank)))
        print(case['id'],result['basic_action'],rows[-1]['seconds'],flush=True)
        outage=outage+1 if result['basic_action']=='unavailable' and not any(c.get('content') for c in calls) else 0
        if outage>=3:raise RuntimeError('Three turns without model reply; stop')
    verify();write_new(OUT/'integrity.json',dict(unchanged=True,turns=len(rows)))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true')
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        prepare() if parser.parse_args().prepare_only else main()
