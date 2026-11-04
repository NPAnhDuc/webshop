"""Freeze a small development bank for the policy documents (run load_shop_policy_20261031.py first)."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.knowledge import KnowledgeStore
from load_shop_policy_20261031 import DB,POLICIES

OUT=ROOT/'evaluation/policy_20261031'
TODAY='2026-10-31'
W,R,I,S,P='policy-warranty','policy-returns','policy-installment','policy-shipping','policy-promotion'
LAPTOP='Laptop được bảo hành 24 tháng tại TechStore.'
SMALL='Vỏ case và chuột được bảo hành 12 tháng tại TechStore.'
PARTS='CPU, mainboard, RAM, ổ cứng, card đồ hoạ, nguồn và màn hình được bảo hành 24 tháng tại TechStore.'
FACTS=[
 ('Laptop bảo hành bao lâu?',W,LAPTOP),
 ('laptop bao hanh may thang',W,LAPTOP),
 ('chuột mua ở shop bảo hành mấy tháng',W,SMALL),
 ('RAM được bảo hành bao nhiêu tháng?',W,PARTS),
 ('Bảo hành tính từ khi nào?',W,'Thời hạn bảo hành tính từ ngày mua, tra theo số đơn hàng hoặc số điện thoại đặt hàng.'),
 ('Máy bị vào nước có được bảo hành không?',W,'Bảo hành không áp dụng khi máy bị rơi vỡ, vào nước, cháy nổ do nguồn điện ngoài, hoặc đã bị sửa chữa ngoài TechStore.'),
 ('Có vệ sinh máy miễn phí không?',W,'Vệ sinh máy và tra keo tản nhiệt được miễn phí trong thời hạn bảo hành.'),
 ('Sản phẩm lỗi thì đổi trong bao nhiêu ngày?',R,'TechStore đổi 1 đổi 1 trong 30 ngày cho sản phẩm lỗi phần cứng do nhà sản xuất, được kỹ thuật xác nhận, đủ hộp và phụ kiện.'),
 ('Đổi ý không muốn mua nữa thì trả hàng trong mấy ngày?',R,'TechStore nhận trả hàng hoàn tiền trong 7 ngày với sản phẩm chưa kích hoạt, còn nguyên tem và đủ hộp, phụ kiện.'),
 ('Trả hàng được hoàn bao nhiêu phần trăm?',R,'Trả hàng trong 7 ngày được hoàn 100% giá đã trả.'),
 ('Tiền hoàn về đâu?',R,'Tiền hoàn về đúng phương thức đã thanh toán.'),
 ('Hết hàng cùng mẫu thì đổi thế nào?',R,'Sản phẩm đổi 1 đổi 1 là sản phẩm cùng mẫu; hết hàng cùng mẫu thì đổi mẫu tương đương hoặc hoàn tiền.'),
 ('Phát hiện hàng giả thì shop đền thế nào?',R,'TechStore đền 200% giá trị sản phẩm nếu phát hiện hàng giả.'),
 ('Trả góp 0% có những kỳ hạn nào?',I,'TechStore có trả góp 0% lãi suất qua thẻ tín dụng, kỳ hạn 3, 6, 9 hoặc 12 tháng.'),
 ('Sản phẩm nào được trả góp 0%?',I,'Trả góp 0% chỉ áp dụng cho sản phẩm có nhãn "Trả góp 0%" trên web.'),
 ('Trả góp bằng CCCD lãi suất bao nhiêu?',I,'Lãi suất trả góp bằng CCCD do công ty tài chính quyết định, không phải 0%.'),
 ('Trả góp qua những ngân hàng nào?',I,'Số tiền trả hằng tháng và danh sách ngân hàng xem ở bước thanh toán hoặc hỏi nhân viên.'),
 ('Đơn bao nhiêu thì được miễn phí giao hàng?',S,'TechStore miễn phí giao hàng cho đơn từ 500.000đ.'),
 ('Đơn 300 nghìn có mất phí ship không?',S,'Đơn dưới 500.000đ tính phí giao hàng khi thanh toán.'),
 ('Giao nhanh 2 giờ áp dụng ở đâu?',S,'TechStore giao nhanh 2 giờ ở nội thành Hà Nội và TP.HCM.'),
 ('Giao về Đà Nẵng mất mấy ngày?',S,'Các tỉnh thành khác nhận hàng trong 2–4 ngày làm việc.'),
 ('Có được kiểm tra hàng trước khi nhận không?',S,'Khách được kiểm tra hàng trước khi nhận.'),
 ('Lắp PC build có mất tiền không?',S,'Lắp đặt PC build được miễn phí khi giao ở nội thành Hà Nội và TP.HCM.'),
 ('Hiện shop có khuyến mãi gì không?',P,'Tính đến 30/10/2026, TechStore không có chương trình khuyến mãi nào đang chạy.'),
 ('Giá trên web đã là giá bán chưa?',P,'Giá trên web là giá bán hiện tại của TechStore.'),
]
OTHER=[
 ('Shop có bảo hành tận nhà không?','unknown'),
 ('Giao trễ thì shop đền bao nhiêu?','unknown'),
 ('Máy 20 triệu trả góp 12 tháng mỗi tháng trả bao nhiêu?','deferred'),
]
FOLLOW=[('Laptop bảo hành bao lâu?',W,LAPTOP),('Còn chuột thì sao?',W,SMALL)]


def case(question,conversation,behavior,required,role='customer'):
    return dict(role=role,question=question,topic='shop_policy',conversation=conversation,required=required,expected_behavior=behavior,
                rubric='',gold_document_ids=sorted({r['document_id'] for r in required}),today=TODAY,split='development')


def required(identifier,quote):
    assert quote in POLICIES[identifier][1],quote
    return [dict(document_id=identifier,version=1,quote=quote)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    bank=[case(q,f'policy:{i}','facts',required(d,t)) for i,(q,d,t) in enumerate(FACTS)]
    bank+=[case(q,f'policy-other:{i}',b,[]) for i,(q,b) in enumerate(OTHER)]
    bank+=[case(q,'policy-follow','facts',required(d,t)) for q,d,t in FOLLOW]
    bank.append(case('Chính sách bảo hành laptop của shop là bao lâu?','policy-admin','facts',required(W,LAPTOP),role='admin'))
    for i,c in enumerate(bank):c['id']=f'P{i+1:03d}'
    store=KnowledgeStore(DB)
    gold=[{k:v for k,v in d.items() if k!='text'} for d in store.records() if d['document_id'] in POLICIES]
    assert len(gold)==len(POLICIES)
    OUT.mkdir(exist_ok=True)
    (OUT/'bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=1),encoding='utf8')
    (OUT/'gold_sources.json').write_text(json.dumps(gold,ensure_ascii=False,indent=1),encoding='utf8')
    meta=dict(created=TODAY,today=TODAY,database=str(DB),database_sha256=sha(DB),knowledge_manifest=str(store.manifest),knowledge_sha256=sha(store.manifest),
              bank_sha256=sha(OUT/'bank.json'),gold_sha256=sha(OUT/'gold_sources.json'),counts=dict(cases=len(bank)),splits=dict(development=len(bank)),
              note='Written with the policy text in view, so this is a development check, not held-out. Source-bound checks are not semantic correctness.')
    (OUT/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=1),encoding='utf8')
    print(len(bank))


if __name__=='__main__':main()
