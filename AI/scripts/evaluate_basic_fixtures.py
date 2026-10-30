"""Exercise supplied-document capabilities with isolated, explicitly fictional docs.

These policies/addresses are tests only and never published into the live shop.
"""
import json
import os
import sys
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env');os.environ['CHATBOT_MODE']='basic_rag'
from shopbot import knowledge,retrieval,basic_rag
from shopbot.store import initialize
from shopbot.engine import Engine

DOCS=[
 ('test-policy','Điều kiện mua hàng KIỂM THỬ','policy','customer',
  'Đây là điều kiện của SHOP KIỂM THỬ GIẢ LẬP, không phải cửa hàng thật.\n\nĐổi trả trong 7 ngày khi lỗi phần cứng do nhà sản xuất và có hóa đơn.\n\nBảo hành 12 tháng theo phiếu bảo hành thử nghiệm.\n\nGiao hàng trong 3–5 ngày làm việc tại khu vực thử nghiệm; nhân viên xác nhận lịch.\n\nHóa đơn VAT được yêu cầu ở bước xác nhận đơn của shop kiểm thử.\n\nTrả góp kiểm thử kỳ hạn 6 tháng, điều kiện và phí cần nhân viên xác nhận; không tự tính tiền phải trả.'),
 ('test-promo','Khuyến mãi TEST10 KIỂM THỬ','promotion','customer',
  'Chương trình KIỂM THỬ TEST10 giảm 10% cho laptop, kết thúc ngày 31/10/2026, không cộng dồn với mã khác. Đây không phải ưu đãi của cửa hàng thật.'),
 ('test-info','Thông tin SHOP KIỂM THỬ','store_info','customer',
  'Địa chỉ GIẢ LẬP: số 12 Đường Mẫu, khu vực kiểm thử. Không phải địa chỉ cửa hàng thật.\n\nGiờ mở cửa của SHOP KIỂM THỬ: 09:00–18:00 mỗi ngày. Liên hệ qua địa chỉ email test@example.invalid.'),
 ('test-shopping','Hướng dẫn đặt và tra đơn KIỂM THỬ','shopping_guide','customer',
  'Quy trình KIỂM THỬ: chọn sản phẩm, thêm vào giỏ, kiểm tra thông tin rồi gửi yêu cầu đặt hàng.\n\nTra cứu đơn kiểm thử qua trang hướng dẫn đính kèm email xác nhận. Nhập mã TEST10 ở ô mã giảm giá trước khi xác nhận đơn. Không có đơn nào được bot tạo khi chỉ đọc hướng dẫn.'),
 ('test-guide','Hướng dẫn chọn máy KIỂM THỬ','buying_guide','customer',
  'Bài hướng dẫn KIỂM THỬ: laptop học tập cân nhắc RAM 16 GB và SSD 512 GB, đối chiếu yêu cầu phần mềm của người học trước khi chọn model.\n\nĐể chọn màn hình đẹp theo bài KIỂM THỬ, đối chiếu độ phân giải, độ sáng và độ phủ màu; không suy ra chất lượng chỉ từ tên OLED hay IPS.'),
 ('test-meeting','Biên bản họp KIỂM THỬ 20/10','meeting','admin',
  'Biên bản họp KIỂM THỬ ngày 20/10/2026: Trưởng kho kiểm tra đơn nhập trước thứ Sáu. Chủ shop duyệt ngân sách chiến dịch trước khi triển khai.'),
 ('test-returns-main','Quy định đổi trả MAIN KIỂM THỬ','policy','admin',
  'Điều khoản MAIN KIỂM THỬ, có hiệu lực tháng 10/2026: laptop lỗi phần cứng do nhà sản xuất được đổi trả trong 7 ngày khi có hóa đơn.'),
 ('test-returns-faq','FAQ đổi trả KIỂM THỬ','policy','admin',
  'Điều khoản FAQ KIỂM THỬ, có hiệu lực tháng 10/2026: laptop lỗi phần cứng do nhà sản xuất được đổi trả trong 14 ngày khi có hóa đơn.'),
]
CASES=[
 ('Đổi trả trong mấy ngày, cần điều kiện gì?', 'test-policy','7 ngày','customer'),
 ('Bảo hành trong bao nhiêu tháng?', 'test-policy','12 tháng','customer'),
 ('Thời gian giao hàng của shop kiểm thử?', 'test-policy','3–5','customer'),
 ('Có yêu cầu hóa đơn VAT được không?', 'test-policy','VAT','customer'),
 ('Điều kiện và kỳ hạn trả góp kiểm thử là gì?', 'test-policy','6 tháng','customer'),
 ('Mã TEST10 giảm bao nhiêu, áp dụng gì, hết hạn khi nào?', 'test-promo','31/10/2026','customer'),
 ('Địa chỉ shop kiểm thử?', 'test-info','12 Đường Mẫu','customer'),
 ('Giờ mở cửa và cách liên hệ shop kiểm thử?', 'test-info','09:00','customer'),
 ('Đặt hàng và dùng mã giảm giá theo hướng dẫn thế nào?', 'test-shopping','ô mã giảm giá','customer'),
 ('Theo bài hướng dẫn, laptop học tập nên có cấu hình gì?', 'test-guide','16 GB','customer'),
 ('Theo hướng dẫn, màn hình đẹp cần nhìn thông số nào?', 'test-guide','độ phủ màu','customer'),
 ('Tóm tắt biên bản họp 20/10 và việc ai cần làm?', 'test-meeting','Trưởng kho','admin'),
 ('Đối chiếu quy định đổi trả MAIN và FAQ trong tháng 10/2026, có mâu thuẫn gì?', 'test-returns-main','7 ngày','admin'),
]


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('output');parser.add_argument('--only',type=int,nargs='+');args=parser.parse_args()
    out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=False)
    knowledge.ROOT=out;retrieval.ROOT=out;basic_rag.ROOT=out
    db=out/'fixture.sqlite';initialize(db);store=knowledge.KnowledgeStore(db)
    for identifier,title,kind,audience,text in DOCS:
        store.save(identifier,'# '+title+'\n\n'+text,role='admin',title=title,doc_type=kind,audience=audience,
            approved=True,effective_from='2026-01-01',effective_to='2026-10-31' if kind=='promotion' else None,authority='isolated_test_fixture')
    (out/'fixtures.json').write_text(json.dumps(DOCS,ensure_ascii=False,indent=2),encoding='utf8')
    records=[];engine=Engine(db,today=date(2026,10,20))
    for index,(q,source,term,role) in enumerate(CASES,1):
        if args.only and index not in args.only:continue
        fail=[]
        try:
            r=engine.ask(q,role)
            if term not in r['answer']:fail.append('missing fact')
            if not any(d.get('document_id')==source for d in r['sources']):fail.append('missing source')
            if '[Nguồn:' not in r['answer']:fail.append('missing citation')
            if index==13 and not r.get('rag',{}).get('potential_conflict'):fail.append('conflict not flagged')
        except Exception as exc:r={};fail.append(type(exc).__name__)
        records.append(dict(question=q,passed=not fail,failures=fail,result=r))
        (out/'results.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
        print(index,'PASS' if not fail else 'FAIL',','.join(fail),flush=True)
    summary=dict(cases=len(records),passed=sum(r['passed'] for r in records),limitations='Isolated fictional policy/address tests, not actual shop policies or held-out production accuracy.')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
