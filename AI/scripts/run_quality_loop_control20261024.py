"""CONTROL run: unchanged quality_loop runner, date 24/10, 5 gap documents hidden at retrieval.

Evaluation-only runtime filter; production code, knowledge store and web are untouched.
"""
import importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('run_quality_loop',ROOT/'scripts/run_quality_loop.py')
loop=importlib.util.module_from_spec(spec);spec.loader.exec_module(loop)
loop.BASE=ROOT/'evaluation/quality_loop_20261024_control'
HIDDEN=set(json.loads((loop.BASE/'metadata.json').read_text(encoding='utf-8'))['hidden_documents'])
import shopbot.retrieval as retrieval
original=retrieval.active_documents
def without_gap_pack(documents,*args,**kwargs):
    return [d for d in original(documents,*args,**kwargs) if d.get('document_id') not in HIDDEN]
retrieval.active_documents=without_gap_pack
if __name__=='__main__':loop.main()
