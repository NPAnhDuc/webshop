"""Same106 frozen questions/gold; deterministic scope of explanatory and completed-status mentions only."""
import importlib.util
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('quality_r1_runner',ROOT/'scripts/run_quality_data_quality.py')
runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
from shopbot.de_snapshot import digest,write_new
from shopbot.monthly import exclusive
OUT=ROOT/'evaluation/agent_quality_20261024_r8';OLD=ROOT/'evaluation/agent_quality_20261024_r7'


def prepare():
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        OUT.mkdir(exist_ok=False)
        names=['bank.json','new_bank.json','new_gold.json','gold_changes.json','contract_bank.json','contract_gold.json']
        for name in names:(OUT/name).write_bytes((OLD/name).read_bytes())
        regression=OUT/'regression';regression.mkdir()
        for name in ['bank.json','gold.json']:(regression/name).write_bytes((OLD/'regression'/name).read_bytes())
        files=[runner.DB,runner.CAT,*runner.CURATED.rglob('*'),*[OUT/n for n in names],regression/'bank.json',regression/'gold.json',
            Path(__file__),ROOT/'scripts/run_quality_data_quality.py',*sorted((ROOT/'shopbot').glob('*.py'))]
        write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
            config={k:os.getenv(k) for k in runner.CONFIG},today='2026-10-23',curated_pin=digest(runner.CURATED/'manifest.json'),
            protocol='Same106 cases/gold as r5, no changes. Definitions and completed-status questions are not execution commands; independent later execution clauses remain blocked. No prompt changes. Development only.'))
        snap=OUT/'code_snapshot';snap.mkdir()
        for path in [*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__),ROOT/'scripts/run_quality_data_quality.py']:
            (snap/path.name).write_bytes(path.read_bytes())
        print('Frozen106 unchanged cases/gold; no model calls.')


if __name__=='__main__':
    if '--prepare-only' in sys.argv:prepare()
    else:
        original=runner.Engine
        def traced_engine(*args,**kwargs):return original(*args,**kwargs,trace_directory=OUT/'traces')
        runner.Engine=traced_engine;runner.OUT=OUT;runner.main()
