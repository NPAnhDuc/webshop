"""Consistent synthetic shop documents, separate from external research reports."""
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/business_sql/scenario_v1'


def build():
    folder=OUT/'documents';folder.mkdir(exist_ok=True)
    con=sqlite3.connect(OUT/'shop.sqlite');con.row_factory=sqlite3.Row
    docs=[]
    def add(doc_id,title,body,audience='admin',version=1,start='2025-10-01',end=None,status='approved',kind='strategy'):
        filename=doc_id+f'-v{version}.md'
        text=f'# {title}\n\nDỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.\n\n'+body
        (folder/filename).write_text(text,encoding='utf-8')
        docs.append(dict(document_id=doc_id,title=title,source=filename,version=version,
                         effective_from=start,effective_to=end,status=status,audience=audience,
                         authority='synthetic_shop_document',data_kind='demo',doc_type=kind,text=text))
    targets=list(con.execute('SELECT * FROM monthly_targets ORDER BY month'))
    groups={}
    for row in targets:
        year,month=map(int,row['month'].split('-'));key=f'{year}-Q{(month-1)//3+1}'
        groups.setdefault(key,[]).append(row)
    for quarter,rows in groups.items():
        target=sum(r['revenue'] for r in rows)
        body=(f'## Mục tiêu doanh thu\n\nKỳ: {quarter}. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: {target} VND. '
              'Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.\n\n'
              '| Tháng | Doanh thu mục tiêu (VND) |\n|---|---:|\n'+
              '\n'.join(f"| {r['month']} | {r['revenue']} |" for r in rows)+
              '\n\n## Theo dõi và giới hạn\n\nĐối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. '
              'Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. '
              'Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.\n\n'
              '## Ngân sách\n\nMarketing thường xuyên 12000000 VND/tháng; chiến dịch có ngân sách riêng. '
              'Chủ shop phải duyệt trước mọi thay đổi giá và đơn nhập hàng.')
        # Keep plans retrievable for historical questions; period encoded explicitly.
        add('sales-plan-'+quarter,'Kế hoạch bán hàng '+quarter,body,kind='sales_plan')
        add('sales-plan-'+quarter+'-draft','BẢN NHÁP kế hoạch '+quarter,
            f'Chưa duyệt. Mục tiêu dự thảo {target+200000000} VND. Không dùng làm mục tiêu chính thức.',status='draft')
    for row in con.execute('SELECT * FROM monthly_pnl ORDER BY month'):
        month=row['month']
        body=(f"## Kết quả kỳ {month}\n\nDoanh thu thuần: {row['net_revenue']} VND. "
              f"Giá vốn: {row['net_cogs']} VND. Lợi nhuận gộp: {row['gross_profit']} VND. "
              f"Chi phí vận hành: {row['operating_expenses']} VND. "
              f"Lợi nhuận hoạt động trước lãi vay và thuế: {row['operating_profit_before_interest_tax']} VND. "
              f"Đơn hàng: {row['order_count']}. Sản phẩm hoàn trả: {row['return_units']}.\n\n"
              '## Nguồn và nhận định\n\nNguồn: view monthly_pnl trong shop.sqlite, dữ liệu mô phỏng. '
              'Báo cáo mô tả kết quả, chưa xác lập nguyên nhân. Khi cần số mới phải truy vấn SQL. '
              'Không đưa báo cáo các tháng giữ riêng vào tập huấn luyện để học thuộc số liệu.')
        year,m=map(int,month.split('-'))
        available=f'{year+1}-01-01' if m==12 else f'{year}-{m+1:02d}-01'
        add('monthly-report-'+month,'Báo cáo tháng '+month,body,start=available,kind='monthly_report')
    body='## Lịch chiến dịch\n\n| Mã | Chiến dịch | Bắt đầu | Kết thúc | Ngân sách (VND) | Giảm giá (basis points) |\n|---|---|---|---|---:|---:|\n'
    for c in con.execute('SELECT * FROM campaigns ORDER BY start'):
        body+=f"| {c['id']} | {c['name']} | {c['start']} | {c['end']} | {c['budget']} | {c['discount_bps']} |\n"
    body+='\n## Phạm vi\n\nC-BTS giảm 6% chỉ cho laptop văn phòng; C-BUNDLE giảm 2%; C-TET giảm 3%. '
    body+='Không cộng dồn khuyến mãi. Doanh thu gắn campaign_id là doanh thu liên quan chiến dịch, không phải phần tăng thêm do quảng cáo. '
    body+='Không dùng ROAS để khẳng định lợi nhuận hoặc quan hệ nhân quả.'
    add('marketing-calendar','Lịch marketing và cách đo',body,kind='marketing')
    add('pricing-policy','Quy định giá và biên gộp',
        '## Ràng buộc\n\nBiên lợi nhuận gộp tối thiểu cho laptop 5%, card đồ họa 4%, nhóm khác 10%. '
        'Mức giảm tối đa 6%; không cộng dồn. Hàng tồn trên 90 ngày phải xem dữ liệu tuổi tồn và xin chủ shop duyệt trước khi xả. '
        'Đây là ràng buộc đề xuất; không tự thực hiện giảm giá.',version=1,end='2026-03-31',kind='policy')
    add('pricing-policy','Quy định giá và biên gộp',
        '## Ràng buộc\n\nTừ 2026-04-01, biên gộp tối thiểu cho laptop 6%, card đồ họa 4%, nhóm khác 10%. '
        'Mức giảm tối đa 6%; không cộng dồn. Hàng tồn trên 90 ngày phải xem dữ liệu tuổi tồn và xin chủ shop duyệt trước khi xả. '
        'Kiểm tra biên sau giảm từ giá vốn FIFO; không hứa mức giá nếu chưa được duyệt.',version=2,start='2026-04-01',kind='policy')
    procurement_body=(
        '## Nhà cung cấp giả lập\n\nSUP-LAP có lead time 4 ngày, SUP-PC 3 ngày. '
        'Đơn nhập chưa nhận không tính là tồn kho; lấy receipts làm ngày tăng tồn. '
        'Mức đặt lại trong simulator: laptop 1 sản phẩm, nhóm khác 3; đặt lên 4 laptop hoặc 8 linh kiện. '
        'Các ngưỡng này là giả định mô phỏng, chưa tối ưu thực tế.\n\n'
        '## Hạch toán\n\nĐơn bán xuất FIFO. Hoàn có thể nhập lại kho hoặc không; chỉ đảo giá vốn nếu hàng bán lại được. '
        'Không xác nhận tương thích Build PC khi nguồn thiếu socket/kích thước/điện năng.')
    add('procurement','Quy trình nhập hàng',procurement_body)
    supplier_names={r['id']:r['name'] for r in con.execute('SELECT * FROM suppliers')}
    clarified=procurement_body.replace('SUP-LAP có lead time 4 ngày, SUP-PC 3 ngày.',
        f"Theo bảng suppliers: {supplier_names['SUP-LAP']} SUP-LAP có lead time 4 ngày, SUP-PC 3 ngày ({supplier_names['SUP-PC']}).")
    add('procurement','Quy trình nhập hàng',clarified,version=2)
    add('positioning','Định vị shop và giới hạn suy luận',
        '## Phân khúc\n\nMột điểm bán, 5 người kể cả chủ shop; tập trung laptop văn phòng, laptop gaming phổ thông và linh kiện nâng cấp. '
        'Bán tại cửa hàng, website và social. Chỉ nhận định sản phẩm bán chạy theo kỳ từ SQL, không gắn nhãn hot chỉ từ hãng. '
        'Không lấy doanh thu FPT Shop hoặc MWG làm doanh thu cửa hàng này.\n\n'
        '## Số liệu chưa đủ\n\nChưa mô hình hóa lãi vay, thuế thu nhập hay nghĩa vụ VAT; không kết luận lợi nhuận sau thuế. '
        'Cần dữ liệu thật để đánh giá dự báo và quyết định kinh doanh.')
    add('customer-policy','Chính sách dùng cho shop giả lập',
        '## Đổi trả và bảo hành\n\nChính sách này chỉ dùng demo. Khi bán thật cần chủ shop duyệt điều kiện theo từng SKU. '
        'Không lấy thời hạn bảo hành của cửa hàng nước ngoài áp dụng cho shop Việt Nam. '
        'Khách muốn xác nhận bảo hành hoặc thanh toán cần liên hệ nhân viên.',audience='customer',kind='policy')
    (folder/'manifest.json').write_text(json.dumps(docs,ensure_ascii=False,indent=2),encoding='utf-8')
    con.close()
    print(json.dumps({'documents':len(docs),'approved_for_synthetic_test':sum(d['status']=='approved' for d in docs),'draft_excluded':sum(d['status']=='draft' for d in docs)}))


if __name__=='__main__': build()
