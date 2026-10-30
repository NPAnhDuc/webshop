"""Read-only, reproducible business analysis. Monetary totals remain integer VND.

This application skill does not fit a neural network or execute model-written SQL.
It uses the validated sales ledger; gross profit is never labelled net profit.
"""
from .store import connect, dataset_source


def analyze_business(path, start, end):
    with connect(path, readonly=True) as con:
        accounting = con.execute("SELECT 1 FROM sqlite_master WHERE name='financial_ledger' AND type='table'").fetchone() is not None
        invalid = ("quantity IS NULL OR revenue IS NULL OR cost IS NULL OR "
                   "NOT ((kind='sale' AND quantity>0 AND revenue>=0 AND cost>=0) OR "
                   "(kind='return' AND quantity<0 AND revenue<=0 AND cost<=0))") if accounting else (
                   "revenue IS NULL OR cost IS NULL OR quantity IS NULL OR quantity<0 OR revenue<0 OR cost<0 "
                   "OR (quantity=0 AND (revenue<>0 OR cost<>0))")
        ledger = 'financial_ledger' if accounting else 'sales'
        quality = dict(con.execute(f'''SELECT COUNT(*) AS source_rows,
            MIN(day) AS first_observed_day, MAX(day) AS last_observed_day,
            SUM(CASE WHEN {invalid} THEN 1 ELSE 0 END) AS invalid_rows
            FROM {ledger} WHERE day>=? AND day<?''', (start, end)).fetchone())
        if quality['invalid_rows']:
            raise ValueError('Số liệu thiếu hoặc không hợp lệ; cần kiểm tra trước khi phân tích.')
        # Aggregate before joining so duplicate dimension records cannot inflate totals.
        rows = [dict(r) for r in con.execute('''WITH ledger AS (
            SELECT sku, SUM(quantity) AS units, SUM(revenue) AS revenue,
                SUM(cost) AS cost, SUM(revenue-cost) AS gross_profit
            FROM sales WHERE day>=? AND day<? GROUP BY sku)
            SELECT l.*, p.name, p.category FROM ledger l
            LEFT JOIN products p ON p.sku=l.sku ORDER BY l.revenue DESC, l.sku''', (start, end))]
        monthly = [dict(r) for r in con.execute('''SELECT substr(day,1,7) AS month,
            SUM(quantity) AS units, SUM(revenue) AS revenue,
            SUM(cost) AS cost, SUM(revenue-cost) AS gross_profit
            FROM sales WHERE day>=? AND day<? GROUP BY month ORDER BY month''', (start, end))]
        financial = None
        if accounting:
            expenses = con.execute('SELECT COALESCE(SUM(amount),0) FROM operating_expenses WHERE day>=? AND day<?',(start,end)).fetchone()[0]
            refunds = con.execute('SELECT COALESCE(SUM(refund),0),COALESCE(SUM(quantity),0) FROM returns WHERE day>=? AND day<?',(start,end)).fetchone()
            receipts = con.execute('SELECT COALESCE(SUM(quantity*unit_cost),0) FROM receipts WHERE day>=? AND day<?',(start,end)).fetchone()[0]
            orders = con.execute('SELECT COUNT(*) FROM orders WHERE day>=? AND day<?',(start,end)).fetchone()[0]
            targets = con.execute("SELECT COALESCE(SUM(revenue),0) FROM monthly_targets WHERE month||'-01'>=? AND month||'-01'<?",(start,end)).fetchone()[0]
            financial = dict(operating_expenses=expenses,refunds=refunds[0],return_units=refunds[1],
                             purchases_received=receipts,orders=orders,target_revenue=targets,
                             accounting_basis='FIFO; loại trừ VAT; chưa mô hình hóa lãi vay và thuế thu nhập')
            financial['channels']=[dict(row) for row in con.execute('''SELECT o.channel,SUM(l.revenue) AS net_revenue,
                SUM(l.revenue-l.cost) AS gross_profit FROM financial_ledger l
                LEFT JOIN returns r ON l.kind='return' AND r.id=l.id
                JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END
                JOIN orders o ON o.id=i.order_id WHERE l.day>=? AND l.day<? GROUP BY o.channel ORDER BY net_revenue DESC''',(start,end))]
            snapshot=con.execute('SELECT MAX(day) FROM inventory_daily WHERE day<?',(end,)).fetchone()[0]
            financial['inventory_as_of']=snapshot
            financial['closing_inventory_value']=con.execute('SELECT COALESCE(SUM(value),0) FROM inventory_daily WHERE day=?',(snapshot,)).fetchone()[0] if snapshot else None
    totals = {k: sum(r[k] for r in rows) for k in ('units', 'revenue', 'cost', 'gross_profit')}
    totals['gross_margin_pct'] = round(totals['gross_profit'] / totals['revenue'] * 100, 2) if totals['revenue'] else None
    for row in rows:
        row['gross_margin_pct'] = round(row['gross_profit'] / row['revenue'] * 100, 2) if row['revenue'] else None
        row['revenue_share_pct'] = round(row['revenue'] / totals['revenue'] * 100, 2) if totals['revenue'] else None
    if financial:
        financial['operating_profit_before_interest_tax']=totals['gross_profit']-financial['operating_expenses']
        financial['target_attainment_pct']=round(totals['revenue']/financial['target_revenue']*100,2) if financial['target_revenue'] else None
    return {'totals': totals, 'products': rows, 'monthly': monthly, 'quality': quality,'financial':financial,
            'period': {'start_inclusive': start, 'end_exclusive': end},
            'data_source': dataset_source(path), 'net_profit': None,
            'limitations': (['Đã trừ hoàn trả và chi phí vận hành mô phỏng; chưa tính lãi vay và thuế thu nhập nên không gọi là lợi nhuận ròng.'] if accounting else ['Chưa có chi phí vận hành, thuế, phí và đối soát hoàn trả để tính lợi nhuận ròng.'])+[
                            'Ngày đầu/cuối có bản ghi không chứng minh dữ liệu cả kỳ đã đầy đủ.',
                            'Biến động doanh thu chưa chứng minh nguyên nhân hay hiệu quả marketing.']}


def format_business_report(report):
    def money(value):
        return f'{value:,.0f}'.replace(',', '.') + ' đ'
    if not report['quality']['source_rows']:
        return 'Không có dữ liệu cho kỳ này; chưa thể kết luận doanh thu bằng không.'
    t = report['totals']
    margin = f"{t['gross_margin_pct']:.2f}%" if t['gross_margin_pct'] is not None else 'không xác định vì doanh thu bằng 0'
    label = 'mô phỏng' if report['data_source'] == 'demo' else 'đã nhập'
    text = (f"Doanh thu: **{money(t['revenue'])}**. Giá vốn: **{money(t['cost'])}**. "
            f"Lợi nhuận gộp: **{money(t['gross_profit'])}**. Biên lợi nhuận gộp: **{margin}**. "
            f"Số lượng bán: **{t['units']}**.\n\n"
            f"Nguồn: {report['quality']['source_rows']} dòng bán hàng {label}; "
            f"{report['period']['start_inclusive']} ≤ ngày < {report['period']['end_exclusive']}. "
            'Lợi nhuận gộp = doanh thu − giá vốn; biên gộp = lợi nhuận gộp / doanh thu.\n\n')
    top = report['products'][0]
    share = f"{top['revenue_share_pct']:.2f}%" if top['revenue_share_pct'] is not None else 'chưa xác định tỷ trọng'
    text += f"SKU có doanh thu cao nhất: **{top['sku']}**, {money(top['revenue'])} ({share}). "
    f=report.get('financial')
    if f:
        text += (f"\n\nDoanh thu trên đã trừ hoàn trả **{money(f['refunds'])}**. "
                 f"Chi phí vận hành: **{money(f['operating_expenses'])}**. "
                 f"Lợi nhuận hoạt động trước lãi vay và thuế: **{money(f['operating_profit_before_interest_tax'])}**. "
                 f"Có **{f['orders']} đơn**, **{f['return_units']} sản phẩm hoàn trả**. "
                 f"Giá trị hàng đã nhận từ nhà cung cấp: **{money(f['purchases_received'])}** "
                 '(không trừ lần nữa vào lợi nhuận vì giá vốn đã tính theo FIFO). ')
        if f['target_revenue']:
            text += f"Mục tiêu mô phỏng: **{money(f['target_revenue'])}**; đạt **{f['target_attainment_pct']}%**. "
            gap=f['target_revenue']-t['revenue']
            if gap>0:
                text += f"Còn thiếu **{money(gap)}** so với kế hoạch. Kiểm tra đóng góp từng SKU và lịch hết hàng trước khi đề xuất tăng chi quảng cáo. "
        best=max(report['products'],key=lambda r:r['gross_profit'])
        text += f"SKU đóng góp lợi nhuận gộp lớn nhất: **{best['sku']}**, **{money(best['gross_profit'])}**; đây là kết quả quan sát, chưa chứng minh ngân sách tăng thêm sẽ có hiệu quả. "
        if f['closing_inventory_value'] is not None:
            text+=f"Giá vốn tồn kho tại {f['inventory_as_of']}: **{money(f['closing_inventory_value'])}**. "
        text+='\n\nDoanh thu thuần theo kênh: '+', '.join(f"{c['channel']}: {money(c['net_revenue'])}" for c in f['channels'])+'.'
    losses = [r for r in report['products'] if r['gross_profit'] < 0]
    if losses:
        text += 'Cần kiểm tra SKU có lợi nhuận gộp âm: ' + ', '.join(r['sku'] for r in losses) + '. '
    return text + '\n\n' + ' '.join(report['limitations'])
