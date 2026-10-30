"""Admin handbook development bank: knowledge questions must cite the handbook; shop numbers
must equal the database; handbook illustration numbers and non-existent tables must not be
presented as shop facts. basic_rag (web default) mode, server date frozen. Development only.
"""
import argparse
import copy
import json
import os
import re
import sqlite3
import sys
import time
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
os.environ['CHATBOT_MODE']='basic_rag';os.environ['RAG_PIPELINE']='grounded'
from shopbot.engine import Engine
from shopbot.monthly import atomic_json

DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
def q(sql):return sqlite3.connect(f'file:{DB}?mode=ro',uri=True).execute(sql).fetchone()[0]
BANK=[
 ('H01','CM2 là gì và tính thế nào?','handbook-pnl-unit-economics',None,[]),
 ('H02','Phân biệt GMV và doanh thu thuần giúp tôi.','handbook-pnl-unit-economics',None,[]),
 ('H03','Tỷ lệ LTV trên CAC bao nhiêu thì được xem là tốt?','handbook-cac-ltv-retention',None,[]),
 ('H04','Thời gian hoàn vốn CAC tính thế nào?','handbook-cac-ltv-retention',None,[]),
 ('H05','Vòng quay tồn kho tính bằng công thức nào?','handbook-inventory-control',None,[]),
 ('H06','Điểm đặt hàng lại ROP là gì?','handbook-inventory-control',None,[]),
 ('H07','Tồn kho an toàn được tính ra sao?','handbook-inventory-control',None,[]),
 ('H08','EOQ là gì?','handbook-inventory-control',None,[]),
 ('H09','Độ co giãn của cầu theo giá nghĩa là gì?','handbook-pricing-elasticity',None,[]),
 ('H10','Nếu giảm giá 10% thì sản lượng phải tăng bao nhiêu để giữ nguyên lãi gộp?','handbook-pricing-elasticity',None,[]),
 ('H11','Phân khúc RFM gồm những thành phần nào?','handbook-rfm-lifecycle',None,[]),
 ('H12','Chỉ số lift trong phân tích giỏ hàng nói lên điều gì?','handbook-basket-clv',None,[]),
 ('H13','Đánh giá sai số dự báo nhu cầu nên dùng thước đo nào?','handbook-demand-forecasting',None,[]),
 ('H14','Trong database của shop, doanh thu thuần lấy từ bảng nào?','handbook-shop-data-dictionary',None,['fact_orders']),
 ('H15','Viết câu SQL tính doanh thu thuần theo kênh bán cho database shop.','handbook-shop-sql-queries',None,['fact_orders','DATE_TRUNC']),
 ('H16','Doanh thu thuần tháng 9/2026 của shop là bao nhiêu?',None,('revenue_2026_09',q("SELECT SUM(revenue) FROM financial_ledger WHERE day>='2026-09-01' AND day<'2026-10-01'")),['500 triệu','500.000.000']),
 ('H17','Lãi gộp quý 3 năm 2026 là bao nhiêu?',None,('gross_profit_2026_q3',q("SELECT SUM(revenue-cost) FROM financial_ledger WHERE day>='2026-07-01' AND day<'2026-10-01'")),[]),
 ('H18','Tháng 9/2026 shop có bao nhiêu đơn hàng?',None,('orders_2026_09',q("SELECT COUNT(*) FROM orders WHERE day>='2026-09-01' AND day<'2026-10-01'")),[]),
 ('H19','Shop đang có doanh thu khoảng 500 triệu mỗi tháng đúng không?',None,None,['500 triệu/tháng','đúng, doanh thu','doanh thu khoảng 500 triệu']),
 ('H20','Bảng fact_orders trong database shop có những cột nào?','handbook-shop-data-dictionary',None,['fact_orders có các cột','order_status']),
]


def numbers(text):
    return {int(re.sub(r'[.,\s]','',m)) for m in re.findall(r'\d{1,3}(?:[.,]\d{3})+|\d+',text)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--today',default='2026-10-24')
    args=parser.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    engine=Engine(DB,today=date.fromisoformat(args.today));rows=[]
    for identifier,question,doc,fact,forbidden in BANK:
        start=time.monotonic();r=engine.ask(question,'admin',{})
        cited=[s.get('document_id') for s in r.get('sources',[])];errors=[]
        if doc and doc not in cited:errors.append('expected_document_not_cited')
        if fact:
            got=numbers(r['answer'])
            if got and fact[1] not in got:errors.append('shop_number_mismatch')
            if not got:errors.append('no_number_given')
        low=r['answer'].casefold()
        errors+=[f'forbidden:{f}' for f in forbidden if f.casefold() in low]
        rows.append(dict(id=identifier,question=question,expected_document=doc,expected_fact=fact,cited=cited,
                         basic_action=r.get('basic_action'),answerability=r.get('rag',{}).get('answerability'),
                         answer=r['answer'],checks_pass=not errors,errors=errors,seconds=round(time.monotonic()-start,2)))
        atomic_json(out/'results.json',rows);print(identifier,'PASS' if not errors else errors,rows[-1]['seconds'],flush=True)
    atomic_json(out/'summary.json',dict(passed=sum(r['checks_pass'] for r in rows),total=len(rows),today=args.today,
        note='Mechanical checks; read answers before accepting. Development bank written with the handbook visible.'))


if __name__=='__main__':main()
