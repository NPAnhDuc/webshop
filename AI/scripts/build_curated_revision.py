"""Build a NEW internal analytics revision from an eligible frozen simulation."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shopbot.de_curated import build_curated
from shopbot.monthly import exclusive


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('revision',type=Path)
    parser.add_argument('--reconciliation',type=Path,required=True)
    parser.add_argument('--eligibility',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        result=build_curated(args.revision,args.reconciliation,args.eligibility,args.output)
        import shopbot.de_curated as implementation
        import shopbot.de_contract as contract
        import shopbot.de_snapshot as snapshot
        import shopbot.de_audit as audit
        snap=args.output/'code_snapshot';snap.mkdir(exist_ok=False)
        for path in [Path(__file__),Path(implementation.__file__),Path(contract.__file__),
                     Path(snapshot.__file__),Path(audit.__file__)]:
            (snap/path.name).write_bytes(path.read_bytes())
        print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__': main()
