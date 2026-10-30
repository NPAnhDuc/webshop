"""Assess a simulation contract without publishing or switching a chatbot source."""
import argparse
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from shopbot.de_contract import assess_curated_contract
from shopbot.monthly import exclusive


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('revision', type=Path)
    parser.add_argument('--reconciliation', type=Path, required=True)
    parser.add_argument('--assumptions', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    with exclusive(ROOT/'evaluation/quality_loop_20261021/runner.lock'):
        result = assess_curated_contract(args.revision, args.reconciliation, args.assumptions, args.output)
        import shopbot.de_contract as implementation
        snap = args.output/'code_snapshot'
        snap.mkdir(exist_ok=False)
        for path in [Path(__file__), Path(implementation.__file__)]:
            (snap/path.name).write_bytes(path.read_bytes())
        print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
