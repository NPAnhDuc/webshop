"""Run the unchanged quality_loop runner on the expansion bank (--split development|validation|all).
The validation split is locked: run it for promote decisions only."""
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('run_quality_loop',ROOT/'scripts/run_quality_loop.py')
loop=importlib.util.module_from_spec(spec);spec.loader.exec_module(loop)
loop.BASE=ROOT/'evaluation/expansion_20261029'
if __name__=='__main__':loop.main()
