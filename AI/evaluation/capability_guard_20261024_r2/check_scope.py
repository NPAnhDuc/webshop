"""Development scope probes frozen before guard changes; no model calls."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shopbot.capability_guard import unsupported_capability
CASES=[
 ('Chuẩn hóa dữ liệu là gì?',None),
 ('Xóa dữ liệu có nghĩa là gì?',None),
 ('Làm sạch Excel nghĩa là gì?',None),
 ('Vì sao phải chuẩn hóa dữ liệu?',None),
 ('Hướng dẫn cách làm sạch file Excel.',None),
 ('Giải thích cách clean và chuẩn hóa dữ liệu.',None),
 ('Dữ liệu đã làm sạch chưa?',None),
 ('File Excel đã được chuẩn hóa chưa?',None),
 ('Các dòng lỗi đã xóa chưa?',None),
 ('Giải thích Excel là gì rồi xóa dữ liệu lỗi.','file.transform'),
 ('Chuẩn hóa dữ liệu là gì? Sau đó làm sạch Excel giúp tôi.','file.transform'),
 ('Không xóa hay sửa dữ liệu, chỉ kiểm tra nguồn.',None),
 ('Đừng clean hoặc chuẩn hóa file, chỉ kiểm tra dữ liệu.',None),
 ('Không clean file gốc nhưng làm sạch bản sao Excel.','file.transform'),
 ('Làm sạch file Excel được không?','file.transform'),
 ('Có thể chuẩn hóa file này giúp tôi không?','file.transform'),
 ('Xóa các dòng chưa chuẩn hóa.','file.transform'),
 ('Dữ liệu chưa làm sạch, hãy chuẩn hóa file Excel.','file.transform'),
 ('Giải thích doanh thu là gì rồi tìm top5 SKU bán chạy.','sales.rank'),
 ('Chỉ giải thích khái niệm xếp hạng doanh thu theo SKU là gì.',None),
]
rows=[]
for question,expected in CASES:
 actual=unsupported_capability(question)
 rows.append(dict(question=question,expected=expected,actual=actual,passed=actual==expected))
with (Path(__file__).parent/sys.argv[1]).open('x',encoding='utf-8') as f:
 json.dump(dict(passed=sum(r['passed'] for r in rows),total=len(rows),model_calls=0,cases=rows),f,ensure_ascii=False,indent=2)
print(sum(r['passed'] for r in rows),len(rows))
