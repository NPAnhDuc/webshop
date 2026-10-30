import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
# Seed labels are hand-authored; not claimed to be model-verified or training-ready.
seeds={
'products':['Laptop tầm 20 triệu màn hình đẹp','tim laptop duoi 15tr pin tot','DEMO-A còn hàng không?','So sánh DEMO-A và DEMO-B','máy tính xách tay nhẹ để học','có laptop OLED 20tr ko'],
'documents':['Bảo hành bao lâu?','đổi trả thế nào','tra gop duoc ko','Khuyến mãi laptop hiện nay?','Chính sách bảo hành của shop','có hỗ trợ trả góp không'],
'handoff':['Cho nói chuyện nhân viên','Tôi muốn gặp người thật','nhan vien tu van giup','gọi người thật đi'],
'clarify':['Hôm nay thời tiết sao?','Viết bài thơ','Tư vấn chứng khoán','Hướng dẫn nấu ăn','Xin chào','Tôi chưa biết cần gì']}
questions={'intent':{'type':'choice','instructions':'Chọn ý định câu hỏi tiếng Việt của khách hàng.','criteria':{
'products':'Tư vấn laptop, giá, tồn kho, so sánh sản phẩm','documents':'Bảo hành, đổi trả, trả góp, chính sách',
'handoff':'Yêu cầu nói chuyện nhân viên','clarify':'Ngoài phạm vi hoặc cần làm rõ'}}}
folder=root/'data'/'structured'/'training'/'routing-seeds';folder.mkdir(parents=True,exist_ok=True)
records=[]
for label,texts in seeds.items():
 for text in texts:
  records.append({'state':text,'questions':questions,'labels':{'intent':label}})
(folder/'seeds.jsonl').write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in records)+'\n',encoding='utf-8')
(folder/'README.md').write_text('# Routing seeds\n\n22 ví dụ gán nhãn thủ công, theo schema Kev. Chưa đủ để finetune hoặc đánh giá chất lượng tổng quát. Chưa chia train/test: phải thu thập độc lập theo shop và thời gian, duyệt nhãn, tăng số lượng trước khi train. Không chia ngẫu nhiên các paraphrase cùng một mẫu. Không tự động dùng hội thoại chứa thông tin cá nhân để train.\n',encoding='utf-8')
print(f'{len(records)} routing seed records created')
