"""One bounded same-case development replay; no worker startup or model change."""
import importlib.util,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('preamble_quality_loop',ROOT/'scripts/run_quality_loop.py')
loop=importlib.util.module_from_spec(spec);spec.loader.exec_module(loop)
loop.BASE=ROOT/'evaluation/quality_loop_20261024_kb2'
# The prior rerank batch's trace confirms this stage was active. Freeze the flag
# explicitly here, since the legacy runner metadata did not record this flag.
os.environ['RAG_EVIDENCE_RERANK']='1'
old_code=loop.code
def code():
    return dict(old_code(),**{str(Path(__file__).relative_to(ROOT)):loop.sha(Path(__file__)),
        'evaluation/rag_preamble_20261024_r1/protocol.json':loop.sha(ROOT/'evaluation/rag_preamble_20261024_r1/protocol.json')})
loop.code=code
if __name__=='__main__':
    with loop.exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        with loop.exclusive(loop.BASE/'runner.lock'):loop.main()
