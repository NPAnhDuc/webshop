"""Replay the SAME frozen bank on a recorded candidate; never overwrite baseline."""
import hashlib,json,os,sys
from pathlib import Path
import run_adversarial_100_20261020 as runner

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'evaluation/adversarial_100_20261020'
out=Path(sys.argv[1]).resolve()
bank=json.loads((BASE/'bank.json').read_text(encoding='utf8'))
if len(sys.argv)>2:
    chosen=set(sys.argv[2].split(','));bank=[c for c in bank if c['id'] in chosen]
    assert {c['id'] for c in bank}==chosen
if not out.exists():
    out.mkdir(parents=True)
    blob=json.dumps(bank,ensure_ascii=False,indent=2)
    (out/'bank.json').write_text(blob,encoding='utf8')
    meta=json.loads((BASE/'metadata.json').read_text(encoding='utf8'))
    assert runner.sha(runner.DB)==meta['database_sha256']
    assert runner.sha(runner.KnowledgeStore(runner.DB).manifest)==meta['knowledge_sha256'],'Do not change knowledge to improve benchmark answers'
    meta.update(bank_sha256=hashlib.sha256(blob.encode()).hexdigest(),
                code_sha256={str(p.relative_to(ROOT)):runner.sha(p) for p in [ROOT/'app.py',*sorted((ROOT/'shopbot').glob('*.py'))]},
                baseline=str(BASE),pipeline='grounded',benchmark_clock='2026-10-20; frozen for fair before/after comparison',run_date='2026-10-21',
                replay_cases=len(bank))
    (out/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
os.environ['RAG_PIPELINE']='grounded'
os.environ['RAG_LOG_ORIGIN']='grounded_candidate_20261021'
runner.OUT=out
runner.main()
