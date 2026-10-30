"""Registry revision: same84 questions plus22 frozen multi-turn contracts, one batch."""
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
OUT=ROOT/'evaluation/agent_quality_20261024_r5';OLD=ROOT/'evaluation/agent_quality_20261024_r4'
CONTRACT=ROOT/'evaluation/regression_contract_20261024_r1/conversation_cases_r2.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))


def prepare():
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        OUT.mkdir(exist_ok=False);bank=read(OLD/'new_bank.json');gold=read(OLD/'new_gold.json')
        for identifier in ['Q12','Q18']:gold[identifier]['tool']='documents.answer'
        write_new(OUT/'gold_changes.json',dict(parent_sha256=digest(OLD/'new_gold.json'),
            changes='Q12,Q18 now call registered disabled documents.answer; answer/action unchanged. No other old gold changes.'))
        write_new(OUT/'new_bank.json',bank);write_new(OUT/'new_gold.json',gold)
        contract_gold={};contract_bank=[]
        for session in read(CONTRACT)['sessions']:
            for turn in session['turns']:
                identifier=f'Q{25+len(contract_bank):02}'
                contract_bank.append(dict(id=identifier,conversation='contract-'+session['id'],role=turn['role'],question=turn['question']))
                contract_gold[identifier]=turn['expected']
        write_new(OUT/'contract_bank.json',contract_bank);write_new(OUT/'contract_gold.json',contract_gold)
        regression=OUT/'regression';regression.mkdir()
        for name in ['bank.json','gold.json']:(regression/name).write_bytes((OLD/'regression'/name).read_bytes())
        write_new(OUT/'bank.json',bank+contract_bank+read(regression/'bank.json'))
        files=[runner.DB,runner.CAT,*runner.CURATED.rglob('*'),CONTRACT,OUT/'bank.json',OUT/'new_bank.json',OUT/'new_gold.json',
            OUT/'gold_changes.json',OUT/'contract_bank.json',OUT/'contract_gold.json',regression/'bank.json',regression/'gold.json',
            Path(__file__),ROOT/'scripts/run_quality_data_quality.py',*sorted((ROOT/'shopbot').glob('*.py'))]
        write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
            config={k:os.getenv(k) for k in runner.CONFIG},today='2026-10-23',curated_pin=digest(runner.CURATED/'manifest.json'),
            protocol='Development; same84 questions plus22 previously frozen contracts. Documents registered-disabled; not connected RAG. One local batch, gold not in prompts.'))
        snap=OUT/'code_snapshot';snap.mkdir()
        for path in [*sorted((ROOT/'shopbot').glob('*.py')),Path(__file__),ROOT/'scripts/run_quality_data_quality.py']:
            (snap/path.name).write_bytes(path.read_bytes())
        print('Frozen106-turn bank with independent contract gold; no model calls.')


if __name__=='__main__':
    if '--prepare-only' in sys.argv:prepare()
    else:
        original=runner.Engine
        def traced_engine(*args,**kwargs):return original(*args,**kwargs,trace_directory=OUT/'traces')
        runner.Engine=traced_engine;runner.OUT=OUT;runner.main()
