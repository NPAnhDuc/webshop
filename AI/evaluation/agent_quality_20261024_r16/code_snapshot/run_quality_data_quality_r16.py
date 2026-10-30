"""Same118 turns as r9-r14; r15 + bare documents reference binds to user's prior knowledge clause."""
import importlib.util
from datetime import date
import os
from pathlib import Path
import sys
import requests
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('quality_r1_runner',ROOT/'scripts/run_quality_data_quality.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
from shopbot.agent_tools import AgentTools,GroundedDocuments
from shopbot.de_snapshot import digest,write_new
from shopbot.monthly import exclusive
OUT=ROOT/'evaluation/agent_quality_20261024_r16'
R8=ROOT/'evaluation/agent_quality_20261024_r8';R9=ROOT/'evaluation/agent_quality_20261024_r9'


def worker():
    info=requests.get(os.environ['VI_EMBEDDING_URL'].rstrip('/')+'/health',timeout=5).json()
    return dict(model=info['model'],revision=info['revision'],max_tokens=info['max_tokens'])


def prepare():
 with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
  OUT.mkdir(exist_ok=False)
  names=['new_bank.json','new_gold.json','gold_changes.json','contract_bank.json','contract_gold.json']
  for name in names:(OUT/name).write_bytes((R8/name).read_bytes())
  mixed=['bank.json','mixed_bank.json','mixed_gold.json','baseline106_bank.json']
  for name in mixed:(OUT/name).write_bytes((R9/name).read_bytes())
  reg=OUT/'regression';reg.mkdir()
  for name in ('bank.json','gold.json'):(reg/name).write_bytes((R8/'regression'/name).read_bytes())
  files=[runner.DB,runner.CAT,*runner.CURATED.rglob('*'),*[OUT/n for n in names+mixed],reg/'bank.json',reg/'gold.json',
   Path(__file__),ROOT/'scripts/run_quality_data_quality.py',*sorted((ROOT/'shopbot').glob('*.py'))]
  write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
   config={k:os.getenv(k) for k in runner.CONFIG},today='2026-10-23',curated_pin=digest(runner.CURATED/'manifest.json'),
   embedding_worker=worker(),rag={k:os.getenv(k) for k in ('RAG_SYNTHESIS','RAG_ANSWER_MODE','RAG_RERANK','RAG_PIPELINE')},
   protocol='Same118 turns/gold. documents.answer enabled via GroundedDocuments (stateless, role-filtered). Old documents gold expects disabled; review separately.'))
  snap=OUT/'code_snapshot';snap.mkdir()
  for p in [*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__),ROOT/'scripts/run_quality_data_quality.py']:(snap/p.name).write_bytes(p.read_bytes())
  print('Frozen118 with documents enabled; no model calls.')


if __name__=='__main__':
 if '--prepare-only' in sys.argv:prepare()
 else:
  meta=runner.read(OUT/'metadata.json');assert worker()==meta['embedding_worker'],'Embedding worker changed'
  runner.AgentTools=lambda *a,**k:AgentTools(*a,**k,documents=GroundedDocuments(runner.DB,date.fromisoformat(meta['today'])))
  original=runner.Engine
  def traced(*args,**kwargs):return original(*args,**kwargs,trace_directory=OUT/'traces')
  runner.Engine=traced;runner.OUT=OUT;runner.main()
