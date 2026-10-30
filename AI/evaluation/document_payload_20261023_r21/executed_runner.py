"""Observe unchanged production retrieval/selector for opened development cases."""
import argparse
import copy
import hashlib
import json
import os
import sys
import time
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / '.env')
os.environ['CHATBOT_MODE'] = 'basic_rag'
os.environ['RAG_PIPELINE'] = 'grounded'
os.environ['RAG_LOG_ORIGIN'] = 'quality_loop:document_payload_r21'
from shopbot.engine import Engine
from shopbot.monthly import atomic_json, exclusive
from shopbot.quality_eval import grade
import shopbot.grounded_rag as grounded

BASE = ROOT / 'evaluation/quality_loop_20261021'
OUT = ROOT / 'evaluation/document_payload_20261023_r21'
IDS = {'Q0017','Q0071','Q0128','Q0156','Q0194','Q0221',
       'Q0239','Q0257','Q0281','Q0302','Q0344','Q0351'}
CONFIG = ['CHATBOT_MODE','RAG_PIPELINE','OLLAMA_MODEL','PLANNER_MODEL',
          'OLLAMA_BASE_URL','OLLAMA_NUM_GPU','VI_EMBEDDING_URL','RAG_RERANK']
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def code():
    return {str(p.relative_to(ROOT)):sha(p) for p in
            [ROOT/'app.py', *sorted((ROOT/'shopbot').glob('*.py')), Path(__file__).resolve()]}


def verify(meta):
    assert code() == meta['code'], 'Code changed; stop'
    assert {k:os.getenv(k) for k in CONFIG} == meta['config'], 'Config changed'
    for path, value in meta['files'].items():
        assert sha(Path(path)) == value, path


def prepare():
    assert not OUT.exists(), 'Preserve prior revision'
    source = read(BASE/'metadata.json')
    bank = read(BASE/'bank.json')
    cases = [c for c in bank if c['id'] in IDS]
    assert len(cases) == 12 and all(c['split']=='development' for c in cases)
    assert all(sum(c['conversation']==d['conversation'] for d in bank)==1 for c in cases)
    patch9 = read(ROOT/'evaluation/quoted_clauses_20261023_r20_v2/metadata.json')['code']
    assert all(sha(ROOT/k)==v for k,v in patch9.items()), 'Production must be restored patch9'
    paths = [BASE/'bank.json', BASE/'gold_sources.json', BASE/'metadata.json',
             BASE/'candidate_v9_development/results.json', BASE/'candidate_v9_development/human_review.json',
             Path(source['database']), Path(source['knowledge_manifest'])]
    OUT.mkdir()
    atomic_json(OUT/'bank.json', cases)
    paths.append(OUT/'bank.json')
    atomic_json(OUT/'metadata.json', dict(source=source, code=code(),
        config={k:os.getenv(k) for k in CONFIG}, files={str(p):sha(p) for p in paths},
        design='Observational only: unchanged patch9, twelve opened development single-turn inputs. '
               'Record exact local chat payload/response and search results; no prompt/schema/model intervention. '
               'Six baseline FAIL and six PASS controls; no independent validation, no gold/model-output learning.'))
    (OUT/'executed_runner.py').write_bytes(Path(__file__).read_bytes())
    verify(read(OUT/'metadata.json'))


@contextmanager
def capture(case_id):
    original_post, original_search = requests.post, grounded.search
    events = []
    def observed_post(url, *args, **kwargs):
        response = original_post(url, *args, **kwargs)
        if isinstance(url,str) and url.rstrip('/').endswith('/api/chat'):
            try:
                reply = response.json()
            except ValueError:
                reply = {'raw_error_body':response.text[:4000]}
            events.append(dict(kind='chat', request=copy.deepcopy(kwargs.get('json',{})),
                               response=reply, http_status=response.status_code))
        return response
    def observed_search(*args, **kwargs):
        documents = original_search(*args, **kwargs)
        events.append(dict(kind='search', query=args[0], role=args[1],
                           options={k:str(v) if isinstance(v,(date,Path)) else v for k,v in kwargs.items()},
                           documents=copy.deepcopy(documents)))
        return documents
    requests.post, grounded.search = observed_post, observed_search
    try:
        yield
    finally:
        requests.post, grounded.search = original_post, original_search
        # Observation contains only local request/response JSON, never headers/auth.
        path = OUT/'trace.json'
        prior = read(path) if path.exists() else []
        prior.append(dict(case_id=case_id, events=events))
        atomic_json(path, prior)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    with exclusive(BASE/'runner.lock'):
        if args.prepare_only:
            prepare()
            print('Twelve observational development inputs frozen; no model called.')
            return
        meta = read(OUT/'metadata.json')
        verify(meta)
        cases = read(OUT/'bank.json')
        rows = read(OUT/'results.json') if (OUT/'results.json').exists() else []
        assert [r['id'] for r in rows] == [c['id'] for c in cases[:len(rows)]]
        engine = Engine(Path(meta['source']['database']), today=date.fromisoformat(meta['source']['today']))
        infra = 0
        for case in cases[len(rows):]:
            verify(meta)
            start = time.monotonic()
            try:
                with capture(case['id']):
                    result = engine.ask(case['question'], case['role'], None)
            except Exception as exc:
                result = dict(answer='', error=type(exc).__name__+': '+str(exc)[:250])
            checks = grade(case, result)
            rows.append(dict(id=case['id'], question=case['question'], role=case['role'],
                             seconds=round(time.monotonic()-start,3), result=result, checks=checks))
            atomic_json(OUT/'results.json', rows)
            atomic_json(OUT/'progress.json', dict(completed=len(rows),total=len(cases)))
            print(case['id'], checks['status'], flush=True)
            infra = infra+1 if any(i['cause']=='INFRASTRUCTURE' for i in checks['issues']) else 0
            if infra>=3:
                raise RuntimeError('Three infrastructure errors; stop, not a knowledge failure')
        verify(meta)
        atomic_json(OUT/'integrity.json', dict(unchanged=True, cases=len(rows), code=meta['code']))


if __name__ == '__main__':
    main()
