"""Write a new audit revision without changing the source SQLite/catalog."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shopbot.de_audit import audit_database


def main():
    parser=argparse.ArgumentParser();parser.add_argument('database',type=Path)
    parser.add_argument('--catalog',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise ValueError('Audit revision exists; choose a new output folder')
    result=audit_database(args.database,args.catalog)
    args.output.mkdir(parents=True,exist_ok=False)
    snapshot=args.output/'code_snapshot';snapshot.mkdir()
    import shopbot.de_audit as implementation
    for path in [Path(__file__),Path(implementation.__file__)]:
        (snapshot/path.name).write_bytes(path.read_bytes())
    for name,data in [('audit.json',result),('quarantine.json',result['quarantine_samples'])]:
        (args.output/name).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],checks=len(result['checks']),
        failed=[c['check'] for c in result['checks'] if not c['passed']],output=str(args.output)),ensure_ascii=False))
    if not result['passed']:raise SystemExit(2)


if __name__=='__main__':main()
