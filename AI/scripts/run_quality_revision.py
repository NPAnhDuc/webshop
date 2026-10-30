"""Use the frozen quality runner on a new evaluation revision, with shared GPU lock."""
import argparse,sys
from pathlib import Path
import run_quality_loop as runner


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision-dir',type=Path,required=True)
    parser.add_argument('--preflight-only',action='store_true')
    args,remaining=parser.parse_known_args()
    revision=args.revision_dir.resolve()
    if not revision.is_relative_to(runner.ROOT/'evaluation'):
        raise SystemExit('Revision must stay inside AI/evaluation')
    if not (revision/'metadata.json').is_file():
        raise SystemExit('Frozen revision metadata required')
    lock=runner.BASE/'runner.lock'
    original_code=runner.code
    def code():
        hashes=original_code()
        path=Path(__file__).resolve()
        hashes[str(path.relative_to(runner.ROOT))]=runner.sha(path)
        return hashes
    runner.BASE=revision
    runner.code=code
    with runner.exclusive(lock):
        source=runner.read(revision/'metadata.json')
        for path,key in [(Path(source['database']),'database_sha256'),
                         (Path(source['knowledge_manifest']),'knowledge_sha256'),
                         (revision/'bank.json','bank_sha256'),(revision/'gold_sources.json','gold_sha256')]:
            assert runner.sha(path)==source[key],'Frozen revision input changed: '+path.name
        if args.preflight_only:
            print('Revision preflight passed; no model called, old600 unchanged.')
            return
        sys.argv=[sys.argv[0],*remaining]
        runner.main()


if __name__=='__main__':main()
