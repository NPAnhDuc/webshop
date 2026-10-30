"""Run once, or watch for ready monthly batches. No weight training."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from shopbot.layout import ROOT
from shopbot.monthly import MonthlyUpdater, atomic_json, local_today, read_json, exclusive


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--month')
    parser.add_argument('--allow-current',action='store_true')
    parser.add_argument('--watch',action='store_true')
    parser.add_argument('--interval',type=int,default=60)
    parser.add_argument('--refresh-references',action='store_true')
    args=parser.parse_args()
    load_dotenv(ROOT/'.env')
    db=(ROOT/os.getenv('SHOP_DATABASE','data/structured/shop.db')).resolve()
    while True:
        try:
            updater=MonthlyUpdater(db)
            results=[updater.process(args.month,args.allow_current)] if args.month else updater.run_pending()
            atomic_json(ROOT/'runtime/monthly/worker-status.json',{'checked_at':time.time(),'results':results,'training_weights':False})
            if args.refresh_references:
                marker=ROOT/'runtime/monthly/reference-refresh.json'
                current=local_today().strftime('%Y-%m')
                if read_json(marker,{}).get('month')!=current:
                    from fetch_reference_docs import main as fetch
                    records=fetch()
                    atomic_json(marker,{'month':current,'documents':len(records)})
            if not args.watch or any(r['status']!='unchanged' for r in results):
                print(json.dumps(results,ensure_ascii=True),flush=True)
        except Exception as exc:
            atomic_json(ROOT/'runtime/monthly/worker-error.json',{'error':str(exc),'checked_at':time.time()})
            if not args.watch:raise
        if not args.watch:return
        time.sleep(max(10,args.interval))


if __name__=='__main__':
    if '--watch' in sys.argv:
        with exclusive(ROOT/'runtime/monthly/worker.lock'):
            atomic_json(ROOT/'runtime/monthly/worker-instance.json',{'pid':os.getpid(),'started_at':time.time()})
            main()
    else:main()
