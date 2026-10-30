# Bộ truy vấn SQL phân tích theo đúng schema database shop

> Tài liệu phương pháp nội bộ (handbook phân tích kinh doanh), chỉ dành cho quản lý. Mọi con số trong ví dụ là minh họa, KHÔNG phải số liệu của shop. Số liệu shop (doanh thu, giá vốn, đơn, tồn kho) chỉ lấy từ công cụ SQL/báo cáo trên database data/business_sql/scenario_v1/shop.sqlite (dữ liệu mô phỏng 01/10/2025–30/09/2026).

Các truy vấn viết cho SQLite và đã chạy trên shop.sqlite. Truy vấn lãi lỗ, đơn/hoàn và theo kênh đã được đối chiếu bằng nhau với công cụ tài chính của trợ lý cho tháng 9/2026, quý 3/2026 và cả năm. Tham số :start (gồm) và :end (không gồm) là ngày ISO; :ref là ngày tham chiếu.

## Báo cáo lãi lỗ theo tháng (khớp công cụ tài chính)

Doanh thu thuần = tổng revenue trong financial_ledger (dòng sale dương, dòng return âm). Giá vốn = tổng cost. Lãi gộp = doanh thu thuần − giá vốn. Chi phí vận hành từ operating_expenses. Lợi nhuận hoạt động trước lãi vay và thuế = lãi gộp − chi phí vận hành.

```sql
WITH ledger AS (
  SELECT substr(day,1,7) AS month, SUM(revenue) AS net_revenue, SUM(cost) AS cogs
  FROM financial_ledger WHERE day >= :start AND day < :end GROUP BY month),
opex AS (
  SELECT substr(day,1,7) AS month, SUM(amount) AS operating_expenses
  FROM operating_expenses WHERE day >= :start AND day < :end GROUP BY month)
SELECT l.month, l.net_revenue, l.cogs, l.net_revenue - l.cogs AS gross_profit,
       ROUND(100.0 * (l.net_revenue - l.cogs) / l.net_revenue, 2) AS gross_margin_pct,
       COALESCE(o.operating_expenses, 0) AS operating_expenses,
       l.net_revenue - l.cogs - COALESCE(o.operating_expenses, 0) AS operating_profit
FROM ledger l LEFT JOIN opex o ON o.month = l.month ORDER BY l.month;
```

## Số đơn, tiền hoàn và đơn vị hoàn trong kỳ

Số đơn đếm trên bảng orders theo ngày đặt. Tiền hoàn và số đơn vị hoàn lấy từ returns theo ngày hoàn. Bảng orders không có cột trạng thái giao hàng; không lọc "DELIVERED".

```sql
SELECT (SELECT COUNT(*) FROM orders WHERE day >= :start AND day < :end) AS orders,
       (SELECT COALESCE(SUM(refund), 0) FROM returns WHERE day >= :start AND day < :end) AS refunds,
       (SELECT COALESCE(SUM(quantity), 0) FROM returns WHERE day >= :start AND day < :end) AS return_units;
```

## Doanh thu thuần và lãi gộp theo kênh bán

Kênh (website, store, social) nằm ở orders. Dòng hoàn được nối về đơn gốc qua returns.item_id → order_items → orders.

```sql
SELECT o.channel, SUM(l.revenue) AS net_revenue, SUM(l.revenue - l.cost) AS gross_profit
FROM financial_ledger l
LEFT JOIN returns r ON l.kind = 'return' AND r.id = l.id
JOIN order_items i ON i.id = CASE WHEN l.kind = 'sale' THEN l.id ELSE r.item_id END
JOIN orders o ON o.id = i.order_id
WHERE l.day >= :start AND l.day < :end
GROUP BY o.channel ORDER BY net_revenue DESC;
```

## Cohort giữ chân khách hàng theo tháng mua đầu tiên

Cohort = tháng của đơn đầu tiên của khách (orders.customer_id). month_number = số tháng kể từ cohort. Tỷ lệ = khách có đơn trong tháng đó / quy mô cohort. Dùng hàm ngày của SQLite (substr, strftime), không dùng DATE_TRUNC.

```sql
WITH first AS (
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
GROUP BY a.cohort, s.customers ORDER BY a.cohort;
```

## Điểm RFM theo khách hàng (thang 1–5)

Recency = số ngày từ đơn gần nhất đến ngày tham chiếu :ref. Frequency = số đơn. Monetary = doanh thu thuần của khách (đã trừ hoàn) từ financial_ledger. NTILE(5) chia 5 nhóm; recency càng nhỏ điểm càng cao.

```sql
WITH item_customer AS (
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
FROM base ORDER BY m_score DESC, f_score DESC, r_score DESC;
```

## Tồn kho cuối kỳ, tốc độ bán 30 ngày và số ngày tồn còn lại

Tồn cuối = inventory_daily ở ngày :ref. Tốc độ bán = đơn vị bán (financial_ledger kind=sale) trong 30 ngày đến :ref chia 30. Số ngày tồn còn lại = tồn / tốc độ bán (NULL nếu không bán). Đây là ước lượng đơn giản, không phải dự báo.

```sql
WITH stock AS (SELECT sku, quantity FROM inventory_daily WHERE day = :ref),
velocity AS (
  SELECT sku, SUM(quantity) / 30.0 AS units_per_day FROM financial_ledger
  WHERE kind = 'sale' AND day > date(:ref, '-30 day') AND day <= :ref GROUP BY sku)
SELECT p.sku, p.name, p.category, s.quantity AS stock,
  ROUND(COALESCE(v.units_per_day, 0), 3) AS units_per_day,
  CASE WHEN v.units_per_day > 0 THEN ROUND(s.quantity / v.units_per_day, 1) END AS days_of_cover
FROM products p JOIN stock s ON s.sku = p.sku LEFT JOIN velocity v ON v.sku = p.sku
ORDER BY days_of_cover IS NULL, days_of_cover;
```

## Cặp sản phẩm mua cùng đơn

Hai dòng order_items cùng order_id, sku khác nhau (a < b để không đếm trùng). Số đơn chứa cả hai = support tuyệt đối. Trong dữ liệu mô phỏng phần lớn đơn chỉ có 1 dòng nên cặp rất ít.

```sql
SELECT a.sku AS sku_a, b.sku AS sku_b, COUNT(DISTINCT a.order_id) AS orders_together
FROM order_items a JOIN order_items b ON a.order_id = b.order_id AND a.sku < b.sku
GROUP BY a.sku, b.sku ORDER BY orders_together DESC LIMIT 20;
```