"""Live local model evaluation. Separate from deterministic mocked unit tests."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import sys
import time
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from shopbot.engine import Engine

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--model',required=True);parser.add_argument('--output',required=True)
    parser.add_argument('--advisory',action='store_true')
    args=parser.parse_args();os.environ.update(PLANNER_MODEL=args.model,CONVERSATION_MODE='semantic',LLM_PROVIDER='demo')
    os.environ['VI_UNDERSTANDING_URL']='http://127.0.0.1:8011' if args.advisory else ''
    engine=Engine(ROOT/'data/business_sql/scenario_v1/shop.sqlite',today=date(2026,10,19))
    scenarios=[
        [('doanh thu tháng 9 năm 2026','revenue','2026-09',None),
         ('tháng đó sản phẩm nào bán chạy nhất','top_products','2026-09','units'),
         ('theo doanh thu cơ','top_products','2026-09','revenue'),
         ('còn quý trước?','top_products','2026-Q3','revenue')],
        [('tháng đó sản phẩm nào bán chạy nhất','clarify',None,None),
         ('tháng 9 năm 2026 nhé','top_products','2026-09',None)],
        [('tháng 9 năm 2026 sản phẩm nào bán chạy','top_products','2026-09','units'),
         ('lùi về kỳ ngay trước đó','top_products','2026-08',None)],
        [('doanh thu tháng 7 năm 2026','revenue','2026-07',None),
         ('tháng đó hàng nào khách mua nhiều nhất?','top_products','2026-07','units')],
        [('tháng trước shop thu bao nhiêu từ bán hàng?','revenue','2026-09',None)],
        [('vẽ sơ đồ lời lỗ quý 3 năm 2026','business_analysis','2026-Q3',None)],
        [('tôi nên làm gì từ doanh thu tháng trước và quý trước để kinh doanh tháng tới?','planning',None,None)],
        [('cái kia thế nào?','clarify',None,None)],
        [('so sánh doanh thu tháng 9 với tháng 8 năm 2026','compare','2026-09','revenue')],
    ]
    results=[]
    for group,turns in enumerate(scenarios):
        memory={}
        for question,intent,period,metric in turns:
            started=time.monotonic();result=engine.ask(question,'admin',memory);memory=result['profile']
            actual=result.get('plan',{});periods=actual.get('periods',[])
            passed=result['intent']==intent and (not period or bool(periods) and periods[0]['label']==period) and (not metric or actual.get('metric')==metric)
            row={'group':group,'question':question,'expected':{'intent':intent,'period':period,'metric':metric},
                'actual_intent':result['intent'],'plan':actual,'passed':passed,'seconds':time.monotonic()-started,
                'answer':result['answer'],'sources':result['sources'],'rows':result['rows']}
            results.append(row);print(json.dumps({k:row[k] for k in ('question','actual_intent','passed','seconds')},ensure_ascii=True),flush=True)
    folder=Path(args.output);folder.parent.mkdir(parents=True,exist_ok=True)
    folder.write_text(json.dumps({'model':args.model,'vietnamese_advisory':args.advisory,'reference_date':'2026-10-19','passed':sum(r['passed'] for r in results),'total':len(results),
        'scope':'Small authored integration pilot; not production accuracy. Numeric results are computed from synthetic SQL data.', 'results':results},ensure_ascii=False,indent=2),encoding='utf-8')
    print('RESULT',sum(r['passed'] for r in results),'/',len(results),flush=True)

if __name__=='__main__': main()
