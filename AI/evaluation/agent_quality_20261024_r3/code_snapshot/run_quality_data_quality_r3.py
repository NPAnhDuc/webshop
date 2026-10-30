"""Frozen staged-planner development evaluation; no changes to prior revisions."""
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
OUT=ROOT/'evaluation/agent_quality_20261024_r3'
OLD=ROOT/'evaluation/agent_quality_20261024_r2'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))


def prepare():
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        OUT.mkdir(exist_ok=False);bank=read(OLD/'new_bank.json');gold=read(OLD/'new_gold.json')
        examples=[
            ('Danh mục dữ liệu có bao nhiêu mã SKU?','answer','admin.data_quality'),
            ('Mã SKU nào có doanh thu cao nhất?','deferred',None),
            ('Chỉ đọc báo cáo kiểm tra nguồn có sẵn, không nhập file mới.','answer','admin.data_quality'),
            ('Làm sạch bản sao Excel, giữ nguyên dữ liệu cũ.','deferred',None)]
        for i,(question,action,tool) in enumerate(examples,21):
            identifier=f'Q{i:02}'
            bank.append(dict(id=identifier,conversation='control-'+identifier,role='admin',question=question))
            gold[identifier]=dict(action=action,tool=tool)
        write_new(OUT/'new_bank.json',bank);write_new(OUT/'new_gold.json',gold)
        regression=OUT/'regression';regression.mkdir()
        for name in ['bank.json','gold.json']:(regression/name).write_bytes((OLD/'regression'/name).read_bytes())
        (OUT/'gold_corrections.json').write_bytes((OLD/'gold_corrections.json').read_bytes())
        write_new(OUT/'bank.json',bank+read(regression/'bank.json'))
        snap=OUT/'code_snapshot';snap.mkdir()
        for path in (ROOT/'shopbot').glob('*.py'):(snap/path.name).write_bytes(path.read_bytes())
        files=[runner.DB,runner.CAT,*runner.CURATED.rglob('*'),OUT/'bank.json',OUT/'new_bank.json',OUT/'new_gold.json',
            OUT/'gold_corrections.json',regression/'bank.json',regression/'gold.json',Path(__file__),
            ROOT/'scripts/run_quality_data_quality.py',*sorted((ROOT/'shopbot').glob('*.py'))]
        write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
            config={k:os.getenv(k) for k in runner.CONFIG},today='2026-10-23',
            curated_pin=digest(runner.CURATED/'manifest.json'),
            protocol='Development; same80 previous questions/gold plus4 controls. Existing Q12 correction retained. No gold in prompts. One model batch.'))
        for path in [Path(__file__),ROOT/'scripts/run_quality_data_quality.py']:(snap/path.name).write_bytes(path.read_bytes())
        print('Prepared24 new/control +60 regression; no model calls.')


if __name__=='__main__':
    if '--prepare-only' in sys.argv:prepare()
    else:
        runner.OUT=OUT;runner.main()
