"""Run the frozen old 100 in a NEW round, without overwriting baseline artifacts."""
import argparse,hashlib,json,os,re
from pathlib import Path
import run_adversarial_100_20261020 as legacy
from shopbot.monthly import exclusive

ROOT=legacy.ROOT
BASE=ROOT/'evaluation/quality_loop_20261021'
ORIGINAL=ROOT/'evaluation/adversarial_100_20261020'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round',required=True)
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9_-]+',args.round):
        raise SystemExit('Invalid round name')
    out=BASE/args.round
    with exclusive(BASE/'runner.lock'):
        out.mkdir(exist_ok=True)
        for name in ['bank.json','gold_sources.json']:
            target=out/name
            if target.exists():
                assert target.read_bytes()==(ORIGINAL/name).read_bytes(),'Frozen bank/gold changed'
            else:
                target.write_bytes((ORIGINAL/name).read_bytes())
        files=[ROOT/'app.py',*sorted((ROOT/'shopbot').glob('*.py')),
               Path(legacy.__file__).resolve(),Path(__file__).resolve()]
        meta=dict(clock='2026-10-20 Asia/Bangkok (same clock as frozen old100)',
                  mode='basic_rag',pipeline='grounded',
                  bank_sha256=hashlib.sha256((out/'bank.json').read_text(encoding='utf8').encode()).hexdigest(),
                  bank_file_sha256=sha(out/'bank.json'),
                  gold_sha256=sha(out/'gold_sources.json'),database_sha256=sha(legacy.DB),
                  knowledge_sha256=sha(legacy.KnowledgeStore(legacy.DB).manifest),
                  code_sha256={str(p.relative_to(ROOT)):sha(p) for p in files})
        path=out/'metadata.json'
        if path.exists():
            assert json.loads(path.read_text(encoding='utf8'))==meta,'Round changed; use a new name'
        else:
            legacy.atomic_json(path,meta)
        os.environ['CHATBOT_MODE']='basic_rag'
        os.environ['RAG_PIPELINE']='grounded'
        os.environ['RAG_LOG_ORIGIN']='old_regression:'+args.round
        legacy.OUT=out
        original_verify=legacy.verify
        def verify(value):
            original_verify(value)
            assert sha(out/'bank.json')==value['bank_file_sha256'],'Bank bytes changed'
            assert sha(out/'gold_sources.json')==value['gold_sha256'],'Gold changed'
        legacy.verify=verify
        verify(meta)
        if args.preflight_only:
            print('Preflight passed: frozen bank bytes, normalized legacy hash, gold, source and code.')
            return
        original_write=legacy.atomic_json
        def persist(path,value):
            original_write(path,value)
            if path.name=='results.json' and len(value)>=3 and all(
                    not r.get('result') or r['result'].get('basic_action')=='unavailable'
                    for r in value[-3:]):
                raise RuntimeError('Three infrastructure failures; stop for inspection')
        legacy.atomic_json=persist
        legacy.main()


if __name__=='__main__':
    main()
