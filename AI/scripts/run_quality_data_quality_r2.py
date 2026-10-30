"""Frozen r2 revision; preserve r1 code, bank, gold and results."""
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

OLD=ROOT/'evaluation/agent_quality_20261024_r1'
OUT=ROOT/'evaluation/agent_quality_20261024_r2'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))


def prepare():
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        OUT.mkdir(exist_ok=False)
        bank=read(OLD/'new_bank.json');gold=read(OLD/'new_gold.json')
        old_label=gold['Q12']['action'];gold['Q12']['action']='documents'
        write_new(OUT/'gold_corrections.json',dict(parent_gold_sha256=digest(OLD/'new_gold.json'),
            corrections=[dict(id='Q12',previous=old_label,corrected='documents',
                reason='Technical explanation routes to documents per existing public tool contract. Actual r1 clarify/budget still fails.')]))
        examples=[
            ('Không xóa hay sửa gì, chỉ kiểm tra nguồn dữ liệu có đầy đủ không.','answer','admin.data_quality'),
            ('Nguồn shop đã đối soát chưa? Đừng clean hay thay đổi dữ liệu nhé.','answer','admin.data_quality'),
            ('Vẽ biểu đồ lãi gộp quý3/2026, không phải doanh thu.','answer','admin.finance_chart'),
            ('RAM DDR5 là gì, giải thích dễ hiểu giúp tôi.','documents',None),
            ('Tìm cho tôi 3 thanh RAM dưới 3 triệu.','answer',None),
            ('Đọc bảng Excel mới và chuẩn hóa các dòng, nhưng không ghi đè file gốc.','deferred',None)]
        for i,(q,action,tool) in enumerate(examples,15):
            identifier=f'Q{i:02}'
            bank.append(dict(id=identifier,conversation='control-'+identifier,role='admin',question=q))
            gold[identifier]=dict(action=action,tool=tool)
        write_new(OUT/'new_bank.json',bank);write_new(OUT/'new_gold.json',gold)
        regression=OUT/'regression';regression.mkdir()
        for name in ['bank.json','gold.json']:(regression/name).write_bytes((OLD/'regression'/name).read_bytes())
        write_new(OUT/'bank.json',bank+read(regression/'bank.json'))
        snap=OUT/'code_snapshot';snap.mkdir()
        for path in (ROOT/'shopbot').glob('*.py'):(snap/path.name).write_bytes(path.read_bytes())
        files=[runner.DB,runner.CAT,*runner.CURATED.rglob('*'),OUT/'bank.json',OUT/'new_bank.json',OUT/'new_gold.json',
            regression/'bank.json',regression/'gold.json',OUT/'gold_corrections.json',Path(__file__),
            ROOT/'scripts/run_quality_data_quality.py',*sorted((ROOT/'shopbot').glob('*.py'))]
        write_new(OUT/'metadata.json',dict(files={str(p):digest(p) for p in files if p.is_file()},
            config={k:os.getenv(k) for k in runner.CONFIG},today='2026-10-23',
            curated_pin=digest(runner.CURATED/'manifest.json'),
            protocol='Development; 74 previous questions plus6 controls. Only Q12 label corrected in NEW gold. No gold in prompts. One batch.'))
        for path in [Path(__file__),ROOT/'scripts/run_quality_data_quality.py']:(snap/path.name).write_bytes(path.read_bytes())
        print('Prepared 20 new/control +60 unchanged regression; no model calls.')


if __name__=='__main__':
    if '--prepare-only' in sys.argv:prepare()
    else:
        runner.OUT=OUT
        runner.main()
