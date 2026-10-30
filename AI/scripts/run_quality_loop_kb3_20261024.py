"""Run the unchanged quality_loop runner against the 24/10 knowledge revision folder."""
import importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('run_quality_loop',ROOT/'scripts/run_quality_loop.py')
loop=importlib.util.module_from_spec(spec);spec.loader.exec_module(loop)
loop.BASE=ROOT/'evaluation/quality_loop_20261024_kb3'
if __name__=='__main__':loop.main()
