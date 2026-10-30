"""Create a NEW sanitized prototype catalog revision, never rewrite shop data."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shopbot.agent_tools import public_catalog


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=ROOT.parent/'backend/data/store_state.json')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    raw=args.source.read_bytes()
    state=json.loads(raw)
    products=public_catalog(state)
    snapshot=dict(schema='agent-catalog-v1',data_kind='simulation',
                  captured_at=datetime.now(timezone.utc).isoformat(),
                  source=dict(path=str(args.source.resolve()),sha256=hashlib.sha256(raw).hexdigest(),
                              price_observed_at=None,notice='Captured project demo data, not live commercial offers'),
                  products=products)
    args.output.mkdir(parents=True,exist_ok=False)
    (args.output/'catalog_public.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(products=len(products),output=str(args.output.resolve()),data_kind='simulation')))


if __name__=='__main__':main()
