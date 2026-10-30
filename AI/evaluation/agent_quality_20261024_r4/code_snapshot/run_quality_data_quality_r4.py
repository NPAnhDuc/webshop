"""Same84-turn regression after deterministic count fix; trace every actual turn."""
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
OUT=ROOT/'evaluation/agent_quality_20261024_r4'
OLD=ROOT/'evaluation/agent_quality_20261024_r3'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))


def prepare():
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        OUT.mkdir(exist_ok=False)
        for name in ['bank.json','new_bank.json','new_gold.json','gold_corrections.json']:
            (OUT/name).write_bytes((OLD/name).read_bytes())
        regression=OUT/'regression';regression.mkdir()
        for name in ['bank.json','gold.json']:(regression/name).write_bytes((OLD/'regression'/name).read_bytes())
        files=[runner.DB,runner.CAT,*runner.CURATED.rglob('*'),OUT/'bank.json',OUT/'new_bank.json',OUT/'new_gold.json',
            OUT/'gold_corrections.json',regression/'bank.json',regression/'gold.json',Path(__file__),
            ROOT/'scripts/run_quality_data_quality.py',*sorted((ROOT/'shopbot').glob('*.py'))]
        write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
            config={k:os.getenv(k) for k in runner.CONFIG},today='2026-10-23',
            curated_pin=digest(runner.CURATED/'manifest.json'),
            protocol='Same84 questions and gold as r3. Deterministic count fix+result contract+structured traces, no prompt changes. Development only. Q19 canonical catalog category is ram, not research taxonomy memory.'))
        snap=OUT/'code_snapshot';snap.mkdir()
        for path in [*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__),ROOT/'scripts/run_quality_data_quality.py']:
            (snap/path.name).write_bytes(path.read_bytes())
        print('Frozen84 unchanged cases; real per-turn traces enabled only in evaluation.')


if __name__=='__main__':
    if '--prepare-only' in sys.argv:prepare()
    else:
        original=runner.Engine
        def traced_engine(*args,**kwargs):
            return original(*args,**kwargs,trace_directory=OUT/'traces')
        runner.Engine=traced_engine;runner.OUT=OUT;runner.main()
