"""Capture explicit local sources into a NEW raw revision and run staging audit."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shopbot.de_snapshot import capture_raw,stage_audit
from shopbot.monthly import exclusive


def main():
    parser=argparse.ArgumentParser();parser.add_argument('database',type=Path)
    parser.add_argument('--catalog',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);parser.add_argument('--source-id',required=True)
    args=parser.parse_args()
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        capture_raw(args.database,args.catalog,args.output,args.source_id)
        result=stage_audit(args.output)
        snapshot=args.output/'code_snapshot';snapshot.mkdir(exist_ok=False)
        import shopbot.de_snapshot as implementation
        import shopbot.de_audit as auditor
        for path in [Path(__file__),Path(implementation.__file__),Path(auditor.__file__)]:
            (snapshot/path.name).write_bytes(path.read_bytes())
        print(json.dumps(result,ensure_ascii=False))
        if result['status']=='quarantined':raise SystemExit(2)


if __name__=='__main__':main()
