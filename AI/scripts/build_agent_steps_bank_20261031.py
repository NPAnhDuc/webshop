"""Build the multi-step notebook-agent evaluation bank using SQL gold answers."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data/business_sql/scenario_v1/shop.sqlite"
OUTPUT = ROOT / "evaluation/agent_steps_20261031/bank.json"
OLD_BANK = ROOT / "evaluation/notebook_agent_20261030/bank.json"
KINDS = {"int", "pct", "months"}
ZERO_IDS = {"d18", "d19", "d20", "t18", "t19", "t20"}

# Each ID range is a separate design group: comparisons, rankings, filtered
# rollups, chained multi-step analysis, and explicit zero/no-match answers.
ITEMS = [
    # Period comparisons (8)
    ("d01", "dev", "int", "Doanh thu thuần kênh website quý 1/2026 giảm bao nhiêu đồng so với quý 4/2025?", "WITH q AS (SELECT CASE WHEN l.day<'2026-01-01' THEN '2025-Q4' ELSE '2026-Q1' END qtr,SUM(l.revenue) revenue FROM financial_ledger l LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id WHERE l.day BETWEEN '2025-10-01' AND '2026-03-31' AND o.channel='website' GROUP BY qtr) SELECT (SELECT revenue FROM q WHERE qtr='2026-Q1')-(SELECT revenue FROM q WHERE qtr='2025-Q4')"),
    ("d02", "dev", "pct", "Tiền hoàn hàng quý 1/2026 tăng hay giảm bao nhiêu phần trăm so với quý cuối năm 2025? Làm tròn 2 chữ số thập phân.", "WITH q AS (SELECT CASE WHEN day<'2026-01-01' THEN '2025-Q4' ELSE '2026-Q1' END qtr,SUM(ABS(refund)) amount FROM returns WHERE day BETWEEN '2025-10-01' AND '2026-03-31' GROUP BY qtr) SELECT 100.0*((SELECT amount FROM q WHERE qtr='2026-Q1')-(SELECT amount FROM q WHERE qtr='2025-Q4'))/(SELECT amount FROM q WHERE qtr='2025-Q4')"),
    ("d03", "dev", "int", "Nửa đầu kỳ bán ròng nhiều hơn nửa sau bao nhiêu sản phẩm? Tính từ 2025-10 đến 2026-03 so với 2026-04 đến 2026-09.", "WITH h AS (SELECT CASE WHEN day<'2026-04-01' THEN 'first' ELSE 'second' END period,SUM(quantity) units FROM financial_ledger WHERE day BETWEEN '2025-10-01' AND '2026-09-30' GROUP BY period) SELECT (SELECT units FROM h WHERE period='first')-(SELECT units FROM h WHERE period='second')"),
    ("d04", "dev", "pct", "Lãi gộp tháng 2026-08 tăng bao nhiêu phần trăm so với tháng 2026-07? Làm tròn 2 chữ số thập phân.", "WITH m AS (SELECT substr(day,1,7) month,SUM(revenue-cost) gp FROM financial_ledger WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY month) SELECT 100.0*((SELECT gp FROM m WHERE month='2026-08')-(SELECT gp FROM m WHERE month='2026-07'))/(SELECT gp FROM m WHERE month='2026-07')"),
    ("t01", "test", "int", "Doanh thu thuần quý 2/2026 tăng hay giảm bao nhiêu đồng so với quý 1/2026?", "WITH q AS (SELECT CASE WHEN day<'2026-04-01' THEN 'q1' ELSE 'q2' END period,SUM(revenue) revenue FROM financial_ledger WHERE day BETWEEN '2026-01-01' AND '2026-06-30' GROUP BY period) SELECT (SELECT revenue FROM q WHERE period='q2')-(SELECT revenue FROM q WHERE period='q1')"),
    ("t02", "test", "pct", "Tổng chi phí vận hành quý 3/2026 thay đổi bao nhiêu phần trăm so với quý 2/2026? Làm tròn 2 chữ số thập phân.", "WITH q AS (SELECT CASE WHEN day<'2026-07-01' THEN 'q2' ELSE 'q3' END period,SUM(amount) amount FROM operating_expenses WHERE day BETWEEN '2026-04-01' AND '2026-09-30' GROUP BY period) SELECT 100.0*((SELECT amount FROM q WHERE period='q3')-(SELECT amount FROM q WHERE period='q2'))/(SELECT amount FROM q WHERE period='q2')"),
    ("t03", "test", "int", "Số đơn hàng quý 1/2026 so với quý 4/2025 tăng hay giảm bao nhiêu đơn?", "WITH q AS (SELECT CASE WHEN day<'2026-01-01' THEN 'old' ELSE 'new' END period,COUNT(*) n FROM orders WHERE day BETWEEN '2025-10-01' AND '2026-03-31' GROUP BY period) SELECT (SELECT n FROM q WHERE period='new')-(SELECT n FROM q WHERE period='old')"),
    ("t04", "test", "pct", "Doanh thu thuần quý 3/2026 tăng bao nhiêu phần trăm so với quý 2/2026? Làm tròn 2 chữ số thập phân.", "WITH q AS (SELECT CASE WHEN day<'2026-07-01' THEN 'q2' ELSE 'q3' END period,SUM(revenue) revenue FROM financial_ledger WHERE day BETWEEN '2026-04-01' AND '2026-09-30' GROUP BY period) SELECT 100.0*((SELECT revenue FROM q WHERE period='q3')-(SELECT revenue FROM q WHERE period='q2'))/(SELECT revenue FROM q WHERE period='q2')"),
    # Rankings (8)
    ("d05", "dev", "months", "Xep 3 thang co so don nhieu nhat trong nua dau nam 2026, tu cao xuong thap.", "SELECT strftime('%Y-%m',day) FROM orders WHERE day BETWEEN '2026-01-01' AND '2026-06-30' GROUP BY strftime('%Y-%m',day) ORDER BY COUNT(*) DESC,strftime('%Y-%m',day) LIMIT 3"),
    ("d06", "dev", "months", "Tháng nào có doanh thu thuần từ kênh mạng xã hội thấp nhất trong quý 2/2026?", "SELECT substr(l.day,1,7) FROM financial_ledger l LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id WHERE o.channel='social' AND l.day BETWEEN '2026-04-01' AND '2026-06-30' GROUP BY substr(l.day,1,7) ORDER BY SUM(l.revenue),substr(l.day,1,7) LIMIT 1"),
    ("d07", "dev", "months", "Trong quý 3/2026, ba tháng nào có số tiền hoàn nhiều nhất, xếp từ nhiều xuống ít?", "SELECT substr(day,1,7) FROM returns WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY substr(day,1,7) ORDER BY SUM(ABS(refund)) DESC,substr(day,1,7) LIMIT 3"),
    ("d08", "dev", "months", "Tim 2 thang trong ca ky co so luot nhap kho lon nhat, tinh theo so dong nhan hang.", "SELECT substr(day,1,7) FROM receipts GROUP BY substr(day,1,7) ORDER BY COUNT(*) DESC,substr(day,1,7) LIMIT 2"),
    ("t05", "test", "months", "Trong q1/2026, xếp ba tháng có lg cao nhất từ trên xuống dưới.", "SELECT substr(day,1,7) FROM financial_ledger WHERE day BETWEEN '2026-01-01' AND '2026-03-31' GROUP BY substr(day,1,7) ORDER BY SUM(revenue-cost) DESC,substr(day,1,7) LIMIT 3"),
    ("t06", "test", "months", "Tháng nào trong nửa cuối kỳ có giá trị hàng nhận về thấp nhất?", "SELECT substr(day,1,7) FROM receipts WHERE day BETWEEN '2026-04-01' AND '2026-09-30' GROUP BY substr(day,1,7) ORDER BY SUM(quantity*unit_cost),substr(day,1,7) LIMIT 1"),
    ("t07", "test", "months", "Ba tháng có doanh thu thuần từ laptop cao nhất trong năm 2026 là những tháng nào, xếp giảm dần?", "SELECT substr(l.day,1,7) FROM financial_ledger l JOIN products p ON p.sku=l.sku WHERE p.category='laptop' AND l.day BETWEEN '2026-01-01' AND '2026-09-30' GROUP BY substr(l.day,1,7) ORDER BY SUM(l.revenue) DESC,substr(l.day,1,7) LIMIT 3"),
    ("t08", "test", "months", "Tháng nào đứng thứ hai về số đơn trong toàn bộ kỳ?", "SELECT substr(day,1,7) FROM orders GROUP BY substr(day,1,7) ORDER BY COUNT(*) DESC,substr(day,1,7) LIMIT 1 OFFSET 1"),
    # Filter then aggregate (8)
    ("d09", "dev", "int", "Trong quý 1/2026, doanh thu thuần các đơn qua website có áp dụng chương trình giảm giá là bao nhiêu?", "SELECT COALESCE(SUM(l.revenue),0) FROM financial_ledger l LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id JOIN campaigns c ON c.id=o.campaign_id WHERE o.channel='website' AND c.discount_bps>0 AND l.day BETWEEN '2026-01-01' AND '2026-03-31'"),
    ("d10", "dev", "int", "Cộng chi phí lương (gồm cả lương chủ shop) và điện nước trong nửa đầu 2026 là bao nhiêu đồng?", "SELECT COALESCE(SUM(amount),0) FROM operating_expenses WHERE category IN ('payroll_including_owner','utilities') AND day BETWEEN '2026-01-01' AND '2026-06-30'"),
    ("d11", "dev", "int", "Trong quý 2/2026, đơn của khách phân khúc doanh nghiệp mang về bao nhiêu doanh thu thuần?", "SELECT COALESCE(SUM(l.revenue),0) FROM financial_ledger l LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id JOIN customers c ON c.id=o.customer_id WHERE c.segment='business' AND l.day BETWEEN '2026-04-01' AND '2026-06-30'"),
    ("d12", "dev", "int", "Tổng tiền hoàn cho các lượt đổi trả giả lập trong cả kỳ là bao nhiêu?", "SELECT COALESCE(SUM(ABS(refund)),0) FROM returns WHERE reason='đổi trả giả lập'"),
    ("t09", "test", "int", "Trong quý 3/2026, doanh thu thuần từ nhóm laptop bán qua website là bao nhiêu đồng?", "SELECT COALESCE(SUM(l.revenue),0) FROM financial_ledger l JOIN products p ON p.sku=l.sku LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id WHERE p.category='laptop' AND o.channel='website' AND l.day BETWEEN '2026-07-01' AND '2026-09-30'"),
    ("t10", "test", "int", "Cộng giá trị thuần đơn hàng qua mạng xã hội trong quý 1/2026 của khách thân thiết (`loyal`), được bao nhiêu?", "SELECT COALESCE(SUM(l.revenue),0) FROM financial_ledger l JOIN products p ON p.sku=l.sku LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id JOIN customers c ON c.id=o.customer_id WHERE o.channel='social' AND c.segment='loyal' AND l.day BETWEEN '2026-01-01' AND '2026-03-31'"),
    ("t11", "test", "int", "Trong q3/2026, tong gia tri hang nhan tu nha cung cap co thoi gian giao dung 4 ngay la bao nhieu?", "SELECT COALESCE(SUM(r.quantity*r.unit_cost),0) FROM receipts r JOIN purchase_lines l ON l.id=r.line_id JOIN purchase_orders po ON po.id=l.po_id JOIN suppliers s ON s.id=po.supplier_id WHERE s.lead_days=4 AND r.day BETWEEN '2026-07-01' AND '2026-09-30'"),
    ("t12", "test", "pct", "Trong quý 2/2026, tiền hoàn của các đơn từ cửa hàng chiếm bao nhiêu phần trăm toàn bộ tiền hoàn quý đó? Làm tròn 2 chữ số thập phân.", "WITH r AS (SELECT SUM(ABS(x.refund)) amount,o.channel FROM returns x JOIN order_items i ON i.id=x.item_id JOIN orders o ON o.id=i.order_id WHERE x.day BETWEEN '2026-04-01' AND '2026-06-30' GROUP BY o.channel) SELECT 100.0*COALESCE((SELECT amount FROM r WHERE channel='store'),0)/(SELECT SUM(amount) FROM r)"),
    # Three or more dependent steps (10)
    # d13: lựa từ 10 danh mục còn 1 danh mục doanh thu đứng đầu.
    ("d13", "dev", "int", "Tìm danh mục có doanh thu thuần cao nhất trong quý 1/2026, rồi cho biết danh mục đó bán ròng bao nhiêu đơn vị trong quý?", "WITH rev AS (SELECT p.category,SUM(l.revenue) revenue FROM financial_ledger l JOIN products p ON p.sku=l.sku WHERE l.day BETWEEN '2026-01-01' AND '2026-03-31' GROUP BY p.category), topcat AS (SELECT category FROM rev ORDER BY revenue DESC,category LIMIT 1), units AS (SELECT p.category,SUM(l.quantity) quantity FROM financial_ledger l JOIN products p ON p.sku=l.sku WHERE l.day BETWEEN '2026-01-01' AND '2026-03-31' GROUP BY p.category) SELECT units.quantity FROM topcat JOIN units USING(category)"),
    # d14: lọc 6 tháng còn 3 tháng có nhiều đơn nhất.
    ("d14", "dev", "pct", "Lấy ba tháng có số đơn cao nhất trong nửa đầu 2026, tính doanh thu thuần của ba tháng đó chiếm bao nhiêu phần trăm doanh thu thuần nửa kỳ? Làm tròn 2 chữ số thập phân.", "WITH m AS (SELECT substr(l.day,1,7) month,SUM(l.revenue) revenue,COUNT(DISTINCT o.id) orders FROM financial_ledger l LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id WHERE l.day BETWEEN '2026-01-01' AND '2026-06-30' GROUP BY month), topm AS (SELECT month FROM m ORDER BY orders DESC,month LIMIT 3) SELECT 100.0*SUM(m.revenue)/(SELECT SUM(revenue) FROM m) FROM m JOIN topm USING(month)"),
    # d15: lọc 3 kênh còn 1 kênh đứng đầu về số đơn.
    ("d15", "dev", "int", "Xác định kênh có số đơn cao nhất quý 2/2026; trong kênh đó, tổng tiền hoàn khách nhận được là bao nhiêu?", "WITH counts AS (SELECT channel,COUNT(*) n FROM orders WHERE day BETWEEN '2026-04-01' AND '2026-06-30' GROUP BY channel), topchannel AS (SELECT channel FROM counts ORDER BY n DESC,channel LIMIT 1) SELECT COALESCE(SUM(ABS(r.refund)),0) FROM topchannel t JOIN orders o ON o.channel=t.channel JOIN order_items i ON i.order_id=o.id JOIN returns r ON r.item_id=i.id WHERE r.day BETWEEN '2026-04-01' AND '2026-06-30'"),
    # d16: xếp 2 nhà cung cấp, lọc còn 1 nhà cung cấp nhận hàng trị giá cao nhất.
    ("d16", "dev", "int", "Tim nha cung cap nhan hang tri gia cao nhat trong nam 2026 roi cho biet tong gia tri hang da nhan tu nha cung cap do.", "WITH val AS (SELECT po.supplier_id,SUM(r.quantity*r.unit_cost) amount FROM receipts r JOIN purchase_lines l ON l.id=r.line_id JOIN purchase_orders po ON po.id=l.po_id WHERE r.day BETWEEN '2026-01-01' AND '2026-09-30' GROUP BY po.supplier_id), ranked AS (SELECT supplier_id,amount FROM val ORDER BY amount DESC,supplier_id LIMIT 1) SELECT amount FROM ranked"),
    # d17: lọc 9 tháng còn 2 tháng vượt ngưỡng 120 triệu; truy vấn trả cả hai.
    ("d17", "dev", "months", "Trong các tháng năm 2026 có chi phí vận hành trên 120 triệu, liệt kê tất cả tháng theo lãi gộp từ cao xuống thấp.", "WITH exp AS (SELECT substr(day,1,7) month,SUM(amount) amount FROM operating_expenses WHERE day BETWEEN '2026-01-01' AND '2026-09-30' GROUP BY month), eligible AS (SELECT month FROM exp WHERE amount>120000000), gp AS (SELECT substr(day,1,7) month,SUM(revenue-cost) amount FROM financial_ledger WHERE day BETWEEN '2026-01-01' AND '2026-09-30' GROUP BY month) SELECT gp.month FROM eligible JOIN gp USING(month) ORDER BY gp.amount DESC,gp.month"),
    # t13: lọc 10 danh mục còn 1 danh mục doanh thu đạt điều kiện và thấp nhất trong số đó.
    ("t13", "test", "int", "Trong nhóm danh mục có doanh thu thuần cao hơn mức bình quân các danh mục quý 3/2026, danh mục có doanh thu thuần thấp nhất bán ròng bao nhiêu sản phẩm?", "WITH rev AS (SELECT p.category,SUM(l.revenue) revenue FROM financial_ledger l JOIN products p ON p.sku=l.sku WHERE l.day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY p.category), eligible AS (SELECT category FROM rev WHERE revenue>(SELECT AVG(revenue) FROM rev)), chosen AS (SELECT category FROM eligible JOIN rev USING(category) ORDER BY revenue,category LIMIT 1) SELECT SUM(l.quantity) FROM financial_ledger l JOIN products p ON p.sku=l.sku JOIN chosen c USING(category) WHERE l.day BETWEEN '2026-07-01' AND '2026-09-30'"),
    # t14: lọc 62 sản phẩm còn 3 sản phẩm bán nhiều nhất trước khi đếm hoàn.
    ("t14", "test", "int", "Tìm ba sản phẩm có nhiều đơn vị bán ròng nhất trong quý 1/2026. Trong ba sản phẩm ấy, mặt hàng nào có số lượt hoàn cao nhất, và số lượt hoàn là bao nhiêu?", "WITH sold AS (SELECT sku,SUM(quantity) qty FROM financial_ledger WHERE day BETWEEN '2026-01-01' AND '2026-03-31' GROUP BY sku), top3 AS (SELECT sku FROM sold ORDER BY qty DESC,sku LIMIT 3), returned AS (SELECT item_id,sku FROM returns WHERE day BETWEEN '2026-01-01' AND '2026-03-31'), counts AS (SELECT t.sku,COUNT(r.item_id) n FROM top3 t LEFT JOIN returned r USING(sku) GROUP BY t.sku) SELECT MAX(n) FROM counts"),
    # t15: lọc 3 kênh còn 2 kênh có doanh thu thuần trên trung bình.
    ("t15", "test", "pct", "Quý 2/2026, xét các kênh có dt thuần trên mức bình quân của kênh; dt thuần của kênh lớn nhất chiếm bao nhiêu phần trăm tổng của các kênh đạt điều kiện? Làm tròn 2 chữ số thập phân.", "WITH rev AS (SELECT o.channel,SUM(l.revenue) revenue FROM financial_ledger l LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id WHERE l.day BETWEEN '2026-04-01' AND '2026-06-30' GROUP BY o.channel), eligible AS (SELECT channel,revenue FROM rev WHERE revenue>(SELECT AVG(revenue) FROM rev)) SELECT 100.0*MAX(revenue)/(SELECT SUM(revenue) FROM eligible) FROM eligible"),
    # t16: lọc 3 tháng còn 1 tháng có tỷ lệ hoàn cao hơn mức quý.
    ("t16", "test", "int", "Tính tỷ lệ lượt hoàn (theo ngày hoàn) trên số đơn (theo ngày đặt) của từng tháng quý 3/2026; trong các tháng cao hơn tỷ lệ chung của quý, doanh thu thuần thấp nhất là bao nhiêu?", "WITH om AS (SELECT substr(day,1,7) month,COUNT(*) orders FROM orders WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY month), rm AS (SELECT substr(day,1,7) month,COUNT(*) returns FROM returns WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY month), totals AS (SELECT (SELECT COUNT(*) FROM returns WHERE day BETWEEN '2026-07-01' AND '2026-09-30') returns,(SELECT COUNT(*) FROM orders WHERE day BETWEEN '2026-07-01' AND '2026-09-30') orders), eligible AS (SELECT om.month FROM om LEFT JOIN rm USING(month),totals WHERE 1.0*COALESCE(rm.returns,0)/om.orders>1.0*totals.returns/totals.orders), rev AS (SELECT substr(day,1,7) month,SUM(revenue) revenue FROM financial_ledger WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY month) SELECT MIN(revenue) FROM rev JOIN eligible USING(month)"),
    # t17: lọc 3 tháng còn 1 tháng có lượng bán ròng cao hơn mức bình quân.
    ("t17", "test", "months", "Loc cac thang q3/2026 co luong ban rong cao hon trung binh thang, roi xep theo doanh thu thuan tu cao xuong.", "WITH m AS (SELECT substr(day,1,7) month,SUM(quantity) units,SUM(revenue) revenue FROM financial_ledger WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY month), eligible AS (SELECT month,revenue FROM m WHERE units>(SELECT AVG(units) FROM m)) SELECT month FROM eligible ORDER BY revenue DESC,month"),
    # Explicit zero / no matching rows (6); scalar SQL always returns 0.
    ("d18", "dev", "int", "Trong quý 1/2026 có bao nhiêu ổ cứng nội bộ bị hoàn do lỗi lô SSD giả lập? Nếu không có thì ghi 0.", "SELECT COUNT(*) FROM returns r JOIN products p ON p.sku=r.sku WHERE p.category='internal-hard-drive' AND r.reason='lỗi lô SSD giả lập' AND r.day BETWEEN '2026-01-01' AND '2026-03-31'"),
    ("d19", "dev", "int", "Có bao nhiêu đơn nhập từ nhà cung cấp có thời gian giao trên 100 ngày? Nếu không có thì ghi 0.", "SELECT COUNT(*) FROM purchase_orders po JOIN suppliers s ON s.id=po.supplier_id WHERE s.lead_days>100"),
    ("d20", "dev", "int", "Trong quý 2/2026 có bao nhiêu laptop bị hoàn do lỗi lô SSD giả lập? Nếu không có thì tính là 0.", "SELECT COUNT(*) FROM returns r JOIN products p ON p.sku=r.sku WHERE p.category='laptop' AND r.reason='lỗi lô SSD giả lập' AND r.day BETWEEN '2026-04-01' AND '2026-06-30'"),
    ("t18", "test", "int", "Shop có bán sản phẩm nào trong danh mục sách điện tử ở nửa cuối 2026 không? Trả số sản phẩm, bằng 0 nếu không có.", "SELECT COUNT(DISTINCT l.sku) FROM financial_ledger l JOIN products p ON p.sku=l.sku WHERE p.category='ebook' AND l.kind='sale' AND l.day BETWEEN '2026-04-01' AND '2026-09-30'"),
    ("t19", "test", "int", "Trong quý 3/2026 có đơn nào dùng chiến dịch giảm giá 100% không? Đếm số đơn, không có thì là 0.", "SELECT COUNT(DISTINCT o.id) FROM orders o JOIN campaigns c ON c.id=o.campaign_id WHERE c.discount_bps=10000 AND o.day BETWEEN '2026-07-01' AND '2026-09-30'"),
    ("t20", "test", "int", "Có bao nhiêu đơn quý 3/2026 mà tổng tiền giảm giá vượt tổng giá niêm yết các món trong đơn? Nếu không có thì ghi 0.", "WITH discounts AS (SELECT order_id,SUM(discount) discount,SUM(list_price*quantity) listed FROM order_items GROUP BY order_id) SELECT COUNT(*) FROM discounts d JOIN orders o ON o.id=d.order_id WHERE d.discount>d.listed AND o.day BETWEEN '2026-07-01' AND '2026-09-30'"),
]


def build() -> list[dict[str, str]]:
    rows = [dict(zip(("id", "split", "kind", "question", "expected_sql"), row)) for row in ITEMS]
    if len(rows) != 40 or sum(r["split"] == "dev" for r in rows) != 20:
        raise ValueError("Bank must contain 20 dev and 20 test rows")
    if len({r["id"] for r in rows}) != len(rows) or any(r["kind"] not in KINDS for r in rows):
        raise ValueError("Duplicate IDs or unsupported kind")
    old_questions = {r["question"].strip().casefold() for r in json.loads(OLD_BANK.read_text(encoding="utf-8"))}
    if any(r["question"].strip().casefold() in old_questions for r in rows):
        raise ValueError("Question duplicates the existing bank")
    conn = sqlite3.connect(DB_PATH.resolve().as_uri() + "?mode=ro", uri=True)
    try:
        for row in rows:
            sql = row["expected_sql"].lstrip().lower()
            if not (sql.startswith("select") or sql.startswith("with")) or ";" in sql.rstrip(";"):
                raise ValueError(f"Non-read-only SQL for {row['id']}")
            values = conn.execute(row["expected_sql"]).fetchall()
            if not values or any(value is None for result in values for value in result):
                raise ValueError(f"Empty/NULL gold result for {row['id']}")
            if row["kind"] == "months" and not all(isinstance(result[0], str) for result in values):
                raise ValueError(f"Expected text labels for {row['id']}")
            if row["kind"] != "months" and (len(values) != 1 or len(values[0]) != 1):
                raise ValueError(f"Expected one scalar for {row['id']}")
            if row["kind"] != "months":
                gold = values[0][0]
                if row["id"] in ZERO_IDS and gold != 0:
                    raise ValueError(f"Zero-group answer is not zero for {row['id']}: {gold}")
                if row["id"] not in ZERO_IDS and gold == 0:
                    raise ValueError(f"Nonzero group has a zero answer for {row['id']}")
    finally:
        conn.close()
    return rows


if __name__ == "__main__":
    bank = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(bank)} rows to {OUTPUT}")
