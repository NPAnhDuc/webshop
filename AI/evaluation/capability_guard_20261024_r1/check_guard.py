"""Frozen offline regression; intentionally incorrect advisory quality plan."""
import json
import sys
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shopbot.admin_conversation import AdminConversation

CASES=[
 ('Xóa các dòng lỗi trong dữ liệu.','file.transform'),
 ('Đọc file Excel mới rồi tự clean và ghi đè dữ liệu.','file.transform'),
 ('Đọc bảng Excel mới và chuẩn hóa các dòng, nhưng không ghi đè file gốc.','file.transform'),
 ('Làm sạch bản sao Excel, giữ nguyên dữ liệu cũ.','file.transform'),
 ('Làm sạch file Excel dữ liệu bán hàng của shop giúp tôi.','file.transform'),
 ('Top5 SKU bán chạy tháng9/2026?','sales.rank'),
 ('Mã SKU nào có doanh thu cao nhất?','sales.rank'),
 ('Chuyển sang laptop: doanh thu từng mẫu?','sales.rank'),
 ('SKU nào doanh thu cao nhất?','sales.rank'),
 ('Không xóa hay sửa gì, chỉ kiểm tra nguồn dữ liệu có đầy đủ không.',None),
 ('Nguồn shop đã đối soát chưa? Đừng clean hay thay đổi dữ liệu nhé.',None),
 ('Chỉ đọc báo cáo kiểm tra nguồn có sẵn, không nhập file mới.',None),
 ('Không clean gì cả, chỉ kiểm tra nguồn có sẵn',None),
 ('Có bao nhiêu SKU trong dữ liệu đã kiểm tra?',None),
 ('Danh mục dữ liệu có bao nhiêu mã SKU?',None),
 ('Không xếp hạng SKU, chỉ kiểm tra nguồn dữ liệu.',None),
 ('Không sửa file gốc, nhưng làm sạch bản sao Excel.','file.transform'),
 ('Kiểm tra nguồn rồi xóa các dòng lỗi.','file.transform'),
 ('Chỉ kiểm tra nguồn, không xóa hay sửa Excel.',None),
 ('Giải thích thuật ngữ chuẩn hóa dữ liệu là gì?',None),
]

class Tools:
 def __init__(self):self.calls=[]
 def execute(self,role,tool,args):
  self.calls.append(dict(tool=tool,arguments=args))
  return dict(source_id='offline-fixture',source_manifest_sha256='x',database_sha256='x',
   raw_manifest_sha256='x',reconciliation_manifest_sha256='x',contract_sha256='x',data_kind='simulation',
   row_counts=dict(products=1,financial_ledger=1,operating_expenses=1,inventory_daily=1),
   period=dict(start_inclusive='2026-01-01',end_inclusive='2026-01-31'),
   observed_financial_dates=dict(first='2026-01-01',last='2026-01-31'),parity_checks_passed=1)

def main():
 rows=[]
 for question,expected in CASES:
  tools=Tools()
  r=AdminConversation(tools,lambda _:dict(operation='data_quality',metric='overview',time_mode='missing',period_unit='none')).run(question,'admin',{},date(2026,10,24))
  actual=(r.get('capability_status') or {}).get('name')
  passed=(actual==expected and (not tools.calls if expected else len(tools.calls)==1))
  rows.append(dict(question=question,expected=expected,actual=actual,action=r['basic_action'],calls=tools.calls,passed=passed))
 out=Path(__file__).parent/sys.argv[1]
 with out.open('x',encoding='utf-8') as f:json.dump(dict(passed=sum(r['passed'] for r in rows),total=len(rows),model_calls=0,cases=rows),f,ensure_ascii=False,indent=2)
 print(f"{sum(r['passed'] for r in rows)}/{len(rows)}")
if __name__=='__main__':main()
