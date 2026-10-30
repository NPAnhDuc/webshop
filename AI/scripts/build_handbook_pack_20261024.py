"""Build an admin knowledge pack from knowledge_base/business_ai_handbook that MATCHES the shop DB.

- Methodology modules (01, 02, 04) keep formulas and explanations; Python code blocks and
  "code" sections are removed; every document states that example numbers are illustrations.
- Module 03.1 (a Kimball schema that does not exist here) is replaced by a data dictionary
  generated from the real SQLite database (tables, columns, rows, date coverage, metric SQL).
- Module 03.2 queries are rewritten for the real SQLite schema. Every query is executed on
  the DB; metric queries must equal analyze_business (the bot's finance tool) or the build fails.
- Module 05 (system prompts) is NOT ingested: instructions inside retrieved text are data.
Nothing is published here; publish_handbook_pack_20261024.py does that after review.
"""
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.business_analysis import analyze_business
from shopbot.monthly import atomic_json

SRC=ROOT.parent/'knowledge_base/business_ai_handbook'
PACK=ROOT/'data/unstructured/handbook_20261024'
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
NOTICE=('> Tài liệu phương pháp nội bộ (handbook phân tích kinh doanh), chỉ dành cho quản lý. '
        'Mọi con số trong ví dụ là minh họa, KHÔNG phải số liệu của shop. '
        'Số liệu shop (doanh thu, giá vốn, đơn, tồn kho) chỉ lấy từ công cụ SQL/báo cáo trên database '
        'data/business_sql/scenario_v1/shop.sqlite (dữ liệu mô phỏng 01/10/2025–30/09/2026).')
METHOD=[
 ('handbook-pnl-unit-economics','01_unit_economics_and_metrics/01_ecommerce_pnl_and_unit_economics.md','P&L bán lẻ và kinh tế đơn vị: GMV, doanh thu thuần, CM1/CM2/CM3'),
 ('handbook-cac-ltv-retention','01_unit_economics_and_metrics/02_customer_acquisition_retention_metrics.md','CAC, LTV, LTV:CAC, hoàn vốn CAC, cohort và phễu chuyển đổi'),
 ('handbook-inventory-control','02_inventory_and_pricing_economics/01_inventory_control_and_supply_chain.md','Quản trị tồn kho: vòng quay, DIO, sell-through, EOQ, tồn an toàn, điểm đặt hàng lại, ABC/FSN'),
 ('handbook-pricing-elasticity','02_inventory_and_pricing_economics/02_pricing_strategies_and_elasticity.md','Định giá: co giãn cầu, hòa vốn khi đổi giá, sản phẩm mồi, 3 bậc giá, combo, thanh lý'),
 ('handbook-rfm-lifecycle','04_data_science_and_algorithms/01_rfm_segmentation_and_customer_lifecycle.md','Phân khúc RFM và hành động theo vòng đời khách hàng'),
 ('handbook-basket-clv','04_data_science_and_algorithms/02_market_basket_analysis_and_clv.md','Phân tích giỏ hàng (support, confidence, lift) và CLV xác suất'),
 ('handbook-demand-forecasting','04_data_science_and_algorithms/03_demand_forecasting_and_time_series.md','Dự báo nhu cầu: mùa vụ, thước đo sai số, baseline trước mô hình phức tạp'),
]
CODE_SECTION=re.compile(r'(mã nguồn|python|triển khai python)',re.I)


def sha(data):return hashlib.sha256(data if isinstance(data,bytes) else data.encode('utf8')).hexdigest()


def methodology(text):
    """Drop fenced code and sections whose heading is about source code; keep prose/formulas/tables."""
    text=re.sub(r'```.*?```','',text,flags=re.S)
    out=[];skip_level=None
    for line in text.splitlines():
        heading=re.match(r'^(#+)\s',line)
        if heading:
            level=len(heading[1])
            if skip_level is not None and level<=skip_level:skip_level=None
            if skip_level is None and CODE_SECTION.search(line):skip_level=level;continue
        if skip_level is None:out.append(line)
    body=re.sub(r'\n{3,}','\n\n','\n'.join(out)).strip()
    return body


# Real-schema queries. 'check' compares with the bot finance tool for the given period.
QUERIES=[
 dict(id='monthly_pnl',title='Báo cáo lãi lỗ theo tháng (khớp công cụ tài chính)',
      explain='Doanh thu thuần = tổng revenue trong financial_ledger (dòng sale dương, dòng return âm). Giá vốn = tổng cost. Lãi gộp = doanh thu thuần − giá vốn. Chi phí vận hành từ operating_expenses. Lợi nhuận hoạt động trước lãi vay và thuế = lãi gộp − chi phí vận hành.',
      sql='''WITH ledger AS (
  SELECT substr(day,1,7) AS month, SUM(revenue) AS net_revenue, SUM(cost) AS cogs
  FROM financial_ledger WHERE day >= :start AND day < :end GROUP BY month),
opex AS (
  SELECT substr(day,1,7) AS month, SUM(amount) AS operating_expenses
  FROM operating_expenses WHERE day >= :start AND day < :end GROUP BY month)
SELECT l.month, l.net_revenue, l.cogs, l.net_revenue - l.cogs AS gross_profit,
       ROUND(100.0 * (l.net_revenue - l.cogs) / l.net_revenue, 2) AS gross_margin_pct,
       COALESCE(o.operating_expenses, 0) AS operating_expenses,
       l.net_revenue - l.cogs - COALESCE(o.operating_expenses, 0) AS operating_profit
FROM ledger l LEFT JOIN opex o ON o.month = l.month ORDER BY l.month;''',check='pnl'),
 dict(id='orders_refunds',title='Số đơn, tiền hoàn và đơn vị hoàn trong kỳ',
      explain='Số đơn đếm trên bảng orders theo ngày đặt. Tiền hoàn và số đơn vị hoàn lấy từ returns theo ngày hoàn. Bảng orders không có cột trạng thái giao hàng; không lọc "DELIVERED".',
      sql='''SELECT (SELECT COUNT(*) FROM orders WHERE day >= :start AND day < :end) AS orders,
       (SELECT COALESCE(SUM(refund), 0) FROM returns WHERE day >= :start AND day < :end) AS refunds,
       (SELECT COALESCE(SUM(quantity), 0) FROM returns WHERE day >= :start AND day < :end) AS return_units;''',check='orders'),
 dict(id='revenue_by_channel',title='Doanh thu thuần và lãi gộp theo kênh bán',
      explain='Kênh (website, store, social) nằm ở orders. Dòng hoàn được nối về đơn gốc qua returns.item_id → order_items → orders.',
      sql='''SELECT o.channel, SUM(l.revenue) AS net_revenue, SUM(l.revenue - l.cost) AS gross_profit
FROM financial_ledger l
LEFT JOIN returns r ON l.kind = 'return' AND r.id = l.id
JOIN order_items i ON i.id = CASE WHEN l.kind = 'sale' THEN l.id ELSE r.item_id END
JOIN orders o ON o.id = i.order_id
WHERE l.day >= :start AND l.day < :end
GROUP BY o.channel ORDER BY net_revenue DESC;''',check='channels'),
 dict(id='cohort_retention',title='Cohort giữ chân khách hàng theo tháng mua đầu tiên',
      explain='Cohort = tháng của đơn đầu tiên của khách (orders.customer_id). month_number = số tháng kể từ cohort. Tỷ lệ = khách có đơn trong tháng đó / quy mô cohort. Dùng hàm ngày của SQLite (substr, strftime), không dùng DATE_TRUNC.',
      sql='''WITH first AS (
  SELECT customer_id, MIN(substr(day,1,7)) AS cohort FROM orders GROUP BY customer_id),
activity AS (
  SELECT DISTINCT o.customer_id, f.cohort,
    (CAST(substr(o.day,1,4) AS INT) - CAST(substr(f.cohort,1,4) AS INT)) * 12
      + CAST(substr(o.day,6,2) AS INT) - CAST(substr(f.cohort,6,2) AS INT) AS month_number
  FROM orders o JOIN first f ON f.customer_id = o.customer_id),
size AS (SELECT cohort, COUNT(*) AS customers FROM first GROUP BY cohort)
SELECT a.cohort, s.customers,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_number = 0 THEN customer_id END) / s.customers, 1) AS m0_pct,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_number = 1 THEN customer_id END) / s.customers, 1) AS m1_pct,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_number = 3 THEN customer_id END) / s.customers, 1) AS m3_pct,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN month_number = 6 THEN customer_id END) / s.customers, 1) AS m6_pct
FROM activity a JOIN size s ON s.cohort = a.cohort
GROUP BY a.cohort, s.customers ORDER BY a.cohort;''',check='cohort'),
 dict(id='rfm_scores',title='Điểm RFM theo khách hàng (thang 1–5)',
      explain='Recency = số ngày từ đơn gần nhất đến ngày tham chiếu :ref. Frequency = số đơn. Monetary = doanh thu thuần của khách (đã trừ hoàn) từ financial_ledger. NTILE(5) chia 5 nhóm; recency càng nhỏ điểm càng cao.',
      sql='''WITH item_customer AS (
  SELECT i.id AS item_id, o.customer_id FROM order_items i JOIN orders o ON o.id = i.order_id),
money AS (
  SELECT ic.customer_id, SUM(l.revenue) AS monetary
  FROM financial_ledger l
  LEFT JOIN returns r ON l.kind = 'return' AND r.id = l.id
  JOIN item_customer ic ON ic.item_id = CASE WHEN l.kind = 'sale' THEN l.id ELSE r.item_id END
  GROUP BY ic.customer_id),
base AS (
  SELECT o.customer_id, CAST(julianday(:ref) - julianday(MAX(o.day)) AS INT) AS recency_days,
         COUNT(*) AS frequency, m.monetary
  FROM orders o JOIN money m ON m.customer_id = o.customer_id GROUP BY o.customer_id)
SELECT customer_id, recency_days, frequency, monetary,
  NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
  NTILE(5) OVER (ORDER BY frequency) AS f_score,
  NTILE(5) OVER (ORDER BY monetary) AS m_score
FROM base ORDER BY m_score DESC, f_score DESC, r_score DESC;''',check='rfm'),
 dict(id='stock_runway',title='Tồn kho cuối kỳ, tốc độ bán 30 ngày và số ngày tồn còn lại',
      explain='Tồn cuối = inventory_daily ở ngày :ref. Tốc độ bán = đơn vị bán (financial_ledger kind=sale) trong 30 ngày đến :ref chia 30. Số ngày tồn còn lại = tồn / tốc độ bán (NULL nếu không bán). Đây là ước lượng đơn giản, không phải dự báo.',
      sql='''WITH stock AS (SELECT sku, quantity FROM inventory_daily WHERE day = :ref),
velocity AS (
  SELECT sku, SUM(quantity) / 30.0 AS units_per_day FROM financial_ledger
  WHERE kind = 'sale' AND day > date(:ref, '-30 day') AND day <= :ref GROUP BY sku)
SELECT p.sku, p.name, p.category, s.quantity AS stock,
  ROUND(COALESCE(v.units_per_day, 0), 3) AS units_per_day,
  CASE WHEN v.units_per_day > 0 THEN ROUND(s.quantity / v.units_per_day, 1) END AS days_of_cover
FROM products p JOIN stock s ON s.sku = p.sku LEFT JOIN velocity v ON v.sku = p.sku
ORDER BY days_of_cover IS NULL, days_of_cover;''',check='stock'),
 dict(id='bought_together',title='Cặp sản phẩm mua cùng đơn',
      explain='Hai dòng order_items cùng order_id, sku khác nhau (a < b để không đếm trùng). Số đơn chứa cả hai = support tuyệt đối. Trong dữ liệu mô phỏng phần lớn đơn chỉ có 1 dòng nên cặp rất ít.',
      sql='''SELECT a.sku AS sku_a, b.sku AS sku_b, COUNT(DISTINCT a.order_id) AS orders_together
FROM order_items a JOIN order_items b ON a.order_id = b.order_id AND a.sku < b.sku
GROUP BY a.sku, b.sku ORDER BY orders_together DESC LIMIT 20;''',check='pairs'),
]


def run(con,sql,**params):
    cur=con.execute(sql,params);cols=[c[0] for c in cur.description]
    return [dict(zip(cols,row)) for row in cur.fetchall()]


def verify(con):
    """Execute every query; cross-check metric queries against analyze_business."""
    checks={}
    for start,end in [('2026-09-01','2026-10-01'),('2026-07-01','2026-10-01'),('2025-10-01','2026-10-01')]:
        tool=analyze_business(str(DB),start,end)
        pnl=run(con,QUERIES[0]['sql'],start=start,end=end)
        assert sum(r['net_revenue'] for r in pnl)==tool['totals']['revenue'],(start,'revenue')
        assert sum(r['cogs'] for r in pnl)==tool['totals']['cost'],(start,'cost')
        assert sum(r['gross_profit'] for r in pnl)==tool['totals']['gross_profit'],(start,'gross_profit')
        assert round(sum(r['operating_expenses'] for r in pnl),2)==round(tool['financial']['operating_expenses'],2),(start,'opex')
        orders=run(con,QUERIES[1]['sql'],start=start,end=end)[0]
        assert (orders['orders'],orders['refunds'],orders['return_units'])==(tool['financial']['orders'],tool['financial']['refunds'],tool['financial']['return_units']),(start,'orders')
        channels={r['channel']:(r['net_revenue'],r['gross_profit']) for r in run(con,QUERIES[2]['sql'],start=start,end=end)}
        assert channels=={r['channel']:(r['net_revenue'],r['gross_profit']) for r in tool['financial']['channels']},(start,'channels')
        checks[f'{start}..{end}']=dict(revenue=tool['totals']['revenue'],gross_profit=tool['totals']['gross_profit'],
                                      orders=tool['financial']['orders'],channels=len(channels),equal_to_finance_tool=True)
    cohort=run(con,QUERIES[3]['sql'])
    assert cohort and all(r['m0_pct']==100.0 for r in cohort),'cohort month 0 must be 100%'
    rfm=run(con,QUERIES[4]['sql'],ref='2026-09-30')
    assert len(rfm)==con.execute('SELECT COUNT(DISTINCT customer_id) FROM orders').fetchone()[0]
    assert all(1<=r[k]<=5 for r in rfm for k in ('r_score','f_score','m_score'))
    assert sum(r['monetary'] for r in rfm)==con.execute('SELECT SUM(revenue) FROM financial_ledger').fetchone()[0],'RFM monetary must reconcile to ledger'
    stock=run(con,QUERIES[5]['sql'],ref='2026-09-30')
    assert len(stock)==con.execute("SELECT COUNT(*) FROM inventory_daily WHERE day='2026-09-30'").fetchone()[0]
    pairs=run(con,QUERIES[6]['sql'])
    checks.update(cohort_rows=len(cohort),rfm_customers=len(rfm),rfm_monetary_reconciled=True,
                  stock_rows=len(stock),bought_together_pairs=len(pairs))
    return checks


def dictionary(con):
    lines=['# Từ điển dữ liệu database shop (sinh tự động từ shop.sqlite)','',NOTICE,'',
           'Database: data/business_sql/scenario_v1/shop.sqlite (SQLite). Dùng đúng tên bảng/cột dưới đây.','',
           'Database shop không có các bảng fact_orders, dim_customers, dim_products hay fact_daily_inventory_snapshot; '
           'các tên đó chỉ là ví dụ lược đồ Kimball trong tài liệu tham khảo.','',
           'Doanh thu thuần lấy từ bảng financial_ledger, cột revenue (dòng kind=sale dương, dòng kind=return âm).','']
    for (table,) in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        cols=[r[1] for r in con.execute(f'PRAGMA table_info({table})')]
        count=con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
        span=''
        for col in ('day','ordered_day','month'):
            if col in cols:
                lo,hi=con.execute(f'SELECT MIN({col}),MAX({col}) FROM {table}').fetchone();span=f'; {col} từ {lo} đến {hi}';break
        # Each sentence names its table: fragments are selected one sentence at a time.
        lines.append(f'## Bảng {table}\n\nBảng {table} có các cột: {", ".join(cols)}. Bảng {table} có {count} dòng{span}.\n')
    lines+=['## Định nghĩa chỉ tiêu dùng trong báo cáo','',
            '- Doanh thu thuần: SUM(financial_ledger.revenue) theo ngày ghi sổ; dòng return mang giá trị âm.',
            '- Giá vốn hàng bán: SUM(financial_ledger.cost). Lãi gộp: doanh thu thuần − giá vốn.',
            '- Chi phí vận hành: SUM(operating_expenses.amount). Lợi nhuận hoạt động trước lãi vay và thuế: lãi gộp − chi phí vận hành.',
            '- Số đơn: COUNT(orders) theo ngày đặt. Tiền hoàn: SUM(returns.refund) theo ngày hoàn.',
            '- Kênh bán: orders.channel. Phân khúc khách: customers.segment. Mục tiêu doanh thu tháng: monthly_targets.revenue.',
            '- Tồn kho cuối ngày: inventory_daily.quantity và value.','',
            'Không có thuế, lãi vay, chi phí quảng cáo theo từng đơn hay trạng thái giao hàng trong database; '
            'các chỉ tiêu cần những dữ liệu đó phải báo là chưa có dữ liệu.']
    return '\n'.join(lines)


def sql_doc():
    parts=['# Bộ truy vấn SQL phân tích theo đúng schema database shop','',NOTICE,'',
           'Các truy vấn viết cho SQLite và đã chạy trên shop.sqlite. Truy vấn lãi lỗ, đơn/hoàn và theo kênh '
           'đã được đối chiếu bằng nhau với công cụ tài chính của trợ lý cho tháng 9/2026, quý 3/2026 và cả năm. '
           'Tham số :start (gồm) và :end (không gồm) là ngày ISO; :ref là ngày tham chiếu.','']
    for q in QUERIES:
        parts+=[f"## {q['title']}",'',q['explain'],'','```sql',q['sql'],'```','']
    return '\n'.join(parts)


def main():
    commit=subprocess.run(['git','-C',str(ROOT.parent),'log','-1','--format=%H','--','knowledge_base'],capture_output=True,text=True).stdout.strip()
    (PACK/'curated').mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(f'file:{DB}?mode=ro',uri=True)
    checks=verify(con);notes=[]
    for identifier,relative,title in METHOD:
        source=SRC/relative;raw=source.read_text(encoding='utf8')
        body=f'# {title}\n\n{NOTICE}\n\n'+methodology(raw)
        path=PACK/'curated'/f'{identifier}.md';path.write_text(body+'\n',encoding='utf8')
        notes.append(dict(document_id=identifier,title=title,doc_type='glossary',audience='admin',category='all',
                          authority='internal_methodology',source_file=str(source.relative_to(ROOT.parent)),
                          source_sha256=sha(raw),source_commit=commit,file=str(path.relative_to(PACK)),sha256=sha(path.read_bytes()),
                          words=len(body.split()),transform='removed fenced code and code-heading sections; added illustration notice'))
    for identifier,title,doc_type,text,origin in [
        ('handbook-shop-data-dictionary','Từ điển dữ liệu database shop: bảng, cột, phạm vi ngày và định nghĩa chỉ tiêu','procedure',dictionary(con),'generated from shop.sqlite (replaces handbook module 03.1)'),
        ('handbook-shop-sql-queries','Bộ truy vấn SQL phân tích theo đúng schema database shop','procedure',sql_doc(),'rewritten from handbook module 03.2 for the real SQLite schema; executed and cross-checked')]:
        path=PACK/'curated'/f'{identifier}.md';path.write_text(text+'\n',encoding='utf8')
        notes.append(dict(document_id=identifier,title=title,doc_type=doc_type,audience='admin',category='all',
                          authority='internal_methodology',source_file=origin,source_commit=commit,
                          file=str(path.relative_to(PACK)),sha256=sha(path.read_bytes()),words=len(text.split())))
    atomic_json(PACK/'knowledge_notes.json',notes)
    atomic_json(PACK/'verification.json',dict(database=str(DB),database_sha256=sha(DB.read_bytes()),checks=checks,
        excluded=['05_ai_agent_and_system_prompts/* (system prompts: instructions must not enter retrieved evidence)',
                  '03_data_engineering_and_sql/01_dimensional_modeling_and_schema_design.md (schema not present; replaced by generated dictionary)',
                  'all Python code blocks and code sections']))
    print(json.dumps(dict(documents=len(notes),words=sum(n['words'] for n in notes),checks=checks),ensure_ascii=False,indent=1))


if __name__=='__main__':main()
