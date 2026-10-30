"""Reconcile an existing captured revision into a separate NEW report folder."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.de_reconcile import reconcile_revision
from shopbot.monthly import exclusive


def main():
    parser=argparse.ArgumentParser();parser.add_argument('revision',type=Path)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        result=reconcile_revision(args.revision,args.output)
        import shopbot.de_reconcile as implementation
        snap=args.output/'code_snapshot';snap.mkdir(exist_ok=False)
        for p in [Path(__file__),Path(implementation.__file__)]: (snap/p.name).write_bytes(p.read_bytes())
        print(json.dumps(dict(passed=result['passed'],checks=len(result['checks']),totals=result['totals'],
            failed=[c['check'] for c in result['checks'] if not c['passed']]),ensure_ascii=False))
        if not result['passed']:raise SystemExit(2)


if __name__=='__main__':main()
