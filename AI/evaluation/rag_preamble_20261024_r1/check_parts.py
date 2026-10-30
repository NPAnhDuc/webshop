"""Frozen source-frame parsing regressions, no model or source mutation."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shopbot.grounded_rag import question_parts
CASES=[
 ('Theo danh mục tham khảo, Laptop X có CPU như thế nào?',['Laptop X có CPU như thế nào']),
 ('Theo danh mục tham khảo, Bộ RAM X có thế hệ và tốc độ RAM như thế nào?',['Bộ RAM X có thế hệ','tốc độ RAM như thế nào']),
 ('Dựa trên tài liệu hiện có, MOQ là bao nhiêu?',['MOQ là bao nhiêu']),
 ('Theo nguồn của shop, ngân sách chiến dịch là bao nhiêu?',['ngân sách chiến dịch là bao nhiêu']),
 ('Căn cứ vào báo cáo, số đơn và hoàn trả là bao nhiêu?',['số đơn','hoàn trả là bao nhiêu']),
 ('Theo danh mục, RAM là 8 GB, CPU là Intel đúng không?',['RAM là 8 GB','CPU là Intel đúng không']),
 ('Theo danh mục tham khảo', ['Theo danh mục tham khảo']),
 ('Theo danh mục có CPU như thế nào, RAM bao nhiêu?',['Theo danh mục có CPU như thế nào','RAM bao nhiêu']),
 ('Giá tối đa 19,5 triệu và RAM 16 GB?',['Giá tối đa 19,5 triệu','RAM 16 GB']),
 ('Lợi nhuận hoạt động trước lãi vay và thuế là bao nhiêu?',['Lợi nhuận hoạt động trước lãi vay / thuế là bao nhiêu']),
 ('Từ báo cáo 3/2025, ghi từng chỉ tiêu: tiền hàng; phí giao.',['tiền hàng','phí giao.']),
 ('Theo danh mục tham khảo, thông số nào còn thiếu, vì sao chưa xác nhận?',['thông số nào còn thiếu','vì sao chưa xác nhận']),
]
rows=[dict(question=q,expected=e,actual=question_parts(q),passed=question_parts(q)==e) for q,e in CASES]
with (Path(__file__).parent/sys.argv[1]).open('x',encoding='utf-8') as f:json.dump(dict(model_calls=0,passed=sum(r['passed'] for r in rows),total=len(rows),cases=rows),f,ensure_ascii=False,indent=2)
print(sum(r['passed'] for r in rows),len(rows))
