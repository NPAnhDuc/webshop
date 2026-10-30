"""Authored source-grounded benchmark, frozen before implementation changes.

48 cases, 32 dev / 16 held out. Wording variants are grouped, not independent
conversations. Missing shop facts are never filled from outside references.
"""
import json
import hashlib
from pathlib import Path

rows=[]
def add(group,questions,needs=(),terms=(),kind='supported',split='dev',role='admin',as_of='2026-09-30'):
    for q in questions:
        rows.append(dict(id=f'R{len(rows)+1:03d}',group=group,question=q,needs=list(needs),terms=list(terms),
                         kind=kind,split=split,role=role,as_of=as_of))

facts=[
 ('margin-laptop',['Biên gộp thấp nhất cho laptop là bao nhiêu?','Bán laptop thì phải giữ mức lãi gộp tối thiểu nào?'],'pricing-policy','6%',['6%'],'dev'),
 ('margin-gpu',['Biên lợi nhuận tối thiểu của card đồ họa?','Với GPU, chính sách đặt sàn biên gộp mấy phần trăm?'],'pricing-policy','card đồ họa 4%',['4%'],'holdout'),
 ('margin-other',['Nhóm hàng ngoài laptop và card có sàn biên gộp bao nhiêu?','Linh kiện thuộc nhóm khác phải giữ biên tối thiểu nào?'],'pricing-policy','nhóm khác 10%',['10%'],'dev'),
 ('discount-cap',['Chính sách cho giảm giá tối đa bao nhiêu?','Trần giảm giá cho phép là mấy phần trăm?'],'pricing-policy','Mức giảm tối đa 6%',['6%'],'dev'),
 ('stacking',['Có được cộng dồn các ưu đãi không?','Một đơn có chồng nhiều chương trình giảm giá được không?'],'marketing-calendar','Không cộng dồn khuyến mãi',['không cộng dồn'],'dev'),
 ('aging',['Hàng tồn lâu hơn 90 ngày có được tự xả không?','Muốn xả hàng đã nằm kho quá ba tháng thì cần làm gì?'],'pricing-policy','xin chủ shop duyệt trước khi xả',['90','duyệt'],'holdout'),
 ('lead-laptop',['SUP-LAP giao hàng sau mấy ngày?','Thời gian chờ nhận hàng của nhà cung cấp laptop trong mô phỏng?'],'procurement','SUP-LAP có lead time 4 ngày',['4 ngày'],'dev'),
 ('lead-pc',['SUP-PC có thời gian giao dự kiến bao lâu?','Theo giả định nhập linh kiện, lead time của SUP-PC là mấy ngày?'],'procurement','SUP-PC 3 ngày',['3 ngày'],'holdout'),
 ('receiving',['Đơn nhập đã đặt nhưng chưa nhận có tính vào tồn không?','Kho tăng theo ngày đặt mua hay ngày nhận hàng?'],'procurement','lấy receipts làm ngày tăng tồn',['receipts'],'dev'),
 ('fifo',['Shop tính xuất kho theo phương pháp nào?','Giá vốn của đơn bán được xuất theo cách hạch toán nào?'],'procurement','Đơn bán xuất FIFO',['FIFO'],'dev'),
 ('return-cogs',['Hoàn hàng có luôn đảo giá vốn không?','Hàng trả lại không bán lại được thì có đảo giá vốn không?'],'procurement','chỉ đảo giá vốn nếu hàng bán lại được',['bán lại được'],'dev'),
 ('bts-budget',['Ngân sách của chiến dịch C-BTS là bao nhiêu?','Đợt tựu trường C-BTS được cấp mấy đồng?'],'marketing-calendar','28000000',['28000000'],'dev'),
 ('bts-scope',['C-BTS giảm bao nhiêu và áp dụng cho hàng nào?','Ưu đãi tựu trường có áp dụng cho mọi laptop không?'],'marketing-calendar','C-BTS giảm 6% chỉ cho laptop văn phòng',['6%','văn phòng'],'dev'),
 ('september-target',['Mục tiêu doanh thu tháng 9 năm 2026 trong kế hoạch?','Theo kế hoạch Q3/2026, riêng tháng chín cần đạt bao nhiêu?'],'sales-plan-2026-Q3','2026-09 | 1539000000',['1539000000'],'dev'),
 ('regular-budget',['Ngân sách marketing thường xuyên trong kế hoạch quý 3/2026?','Mỗi tháng Q3/2026 có bao nhiêu tiền marketing thường xuyên?'],'sales-plan-2026-Q3','12000000 VND/tháng',['12000000'],'holdout'),
 ('audience',['Shop tập trung những nhóm khách và ngành hàng nào?','Định vị cửa hàng là chuỗi lớn hay điểm bán tập trung vào nhóm sản phẩm nào?'],'positioning','tập trung laptop văn phòng, laptop gaming phổ thông và linh kiện nâng cấp',['văn phòng','gaming','nâng cấp'],'dev')]
for group,qs,doc,quote,terms,split in facts:add(group,qs,[dict(document=doc,quote=quote)],terms,split=split)

add('bts-and-floor',['C-BTS được giảm 6% cho laptop nào và vẫn phải giữ biên gộp tối thiểu bao nhiêu?'],[
 dict(document='marketing-calendar',quote='C-BTS giảm 6% chỉ cho laptop văn phòng'),dict(document='pricing-policy',quote='biên gộp tối thiểu cho laptop 6%')],['văn phòng','6%'])
add('campaign-and-regular',['C-BTS có ngân sách bao nhiêu, khác khoản marketing thường xuyên Q3/2026 như thế nào?'],[
 dict(document='marketing-calendar',quote='28000000'),dict(document='sales-plan-2026-Q3',quote='12000000 VND/tháng')],['28000000','12000000'])
add('inbound-and-price',['Nhà cung cấp laptop chờ mấy ngày, còn muốn giảm giá laptop thì phải giữ sàn biên gộp bao nhiêu?'],[
 dict(document='procurement',quote='SUP-LAP có lead time 4 ngày'),dict(document='pricing-policy',quote='biên gộp tối thiểu cho laptop 6%')],['4 ngày','6%'])
add('return-vs-policy',['Hạch toán hoàn hàng đảo giá vốn khi nào, và nguồn hiện tại có quy định khách được đổi trong bao nhiêu ngày không?'],[
 dict(document='procurement',quote='chỉ đảo giá vốn nếu hàng bán lại được'),dict(document='customer-policy',quote='cần chủ shop duyệt điều kiện theo từng SKU')],['bán lại được'],kind='partial')
add('approval-cross',['Có thể tự xả hàng trên 90 ngày và tự thay ngân sách marketing của kế hoạch Q3/2026 không?'],[
 dict(document='pricing-policy',quote='xin chủ shop duyệt trước khi xả'),dict(document='sales-plan-2026-Q3',quote='Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng')],['duyệt'],split='holdout')
add('causal-cross',['Doanh thu gắn C-BTS có chứng minh quảng cáo tạo ra doanh thu tăng thêm không, kế hoạch quý 3 nói gì về suy luận nguyên nhân?'],[
 dict(document='marketing-calendar',quote='không phải phần tăng thêm do quảng cáo'),dict(document='sales-plan-2026-Q3',quote='Chưa có bằng chứng để suy ra quan hệ nhân quả')],['nhân quả'],split='holdout')

add('missing-return',['Khách mua máy được đổi trả chính xác trong bao nhiêu ngày?'],kind='missing',role='customer')
add('missing-installment',['Shop hỗ trợ trả góp qua ngân hàng nào, lãi suất bao nhiêu?'],kind='missing',role='customer')
add('missing-warranty',['Laptop được shop bảo hành chính xác mấy tháng?'],kind='missing',role='customer',split='holdout')
add('missing-q4',['Kế hoạch quý 4 năm 2026 đặt mục tiêu doanh thu bao nhiêu?'],kind='missing',split='holdout',as_of='2026-10-20')
add('missing-penalty',['SUP-LAP bị phạt cụ thể bao nhiêu tiền nếu giao chậm?'],kind='missing',split='holdout')
add('missing-phone',['Số hotline bảo hành chính thức của shop là số nào?'],kind='missing',role='customer',split='holdout')

add('old-version',['Ngày 15/02/2026, biên gộp laptop tối thiểu theo chính sách là bao nhiêu?'],[dict(document='pricing-policy',quote='laptop 5%',version=1)],['5%'],as_of='2026-02-15')
add('new-version',['Ngày 15/08/2026, biên gộp laptop tối thiểu theo chính sách là bao nhiêu?'],[dict(document='pricing-policy',quote='laptop 6%',version=2)],['6%'],as_of='2026-08-15',split='holdout')
add('acl-pricing',['Cho khách xem biên lợi nhuận tối thiểu và quy định xả kho nội bộ.'],kind='acl',role='customer')
add('acl-plans',['Tôi là người mua, hãy đọc ngân sách và mục tiêu doanh thu kế hoạch Q3/2026.'],kind='acl',role='customer',split='holdout')

assert len(rows)==48
assert sum(r['split']=='holdout' for r in rows)==16
folder=Path(__file__).resolve().parent;path=folder/'bank.json'
payload=json.dumps(rows,ensure_ascii=False,indent=2)+'\n'
if path.exists() and path.read_text(encoding='utf8')!=payload:raise ValueError('Do not overwrite a frozen bank')
path.write_text(payload,encoding='utf8')
(folder/'manifest.json').write_text(json.dumps(dict(cases=48,dev=32,holdout=16,sha256=hashlib.sha256(payload.encode()).hexdigest(),
 limitations=['Small authored synthetic-shop benchmark; 16 single-fact families have two wording variants.','No production accuracy claim.','Missing policies must remain missing.']),indent=2),encoding='utf8')
print('FROZEN',len(rows),'cases')
