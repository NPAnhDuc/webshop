# MODULE 3.2: BỘ TRUY VẤN SQL BÁN LẺ THỰC CHIẾN (PRODUCTION RETAIL SQL QUERIES)

---

## 1. TRUY VẤN 1: PHÂN TÍCH NHÓM THUẦN TẬP COHORT GIỮ CHÂN KHÁCH HÀNG (COHORT RETENTION TRIANGLE)
Truy vấn này theo dõi tỷ lệ phần trăm khách hàng quay lại mua sắm trong các tháng tiếp theo (Month 1, Month 2, ..., Month 12) sau lần mua hàng đầu tiên.

```sql
WITH customer_first_orders AS (
    -- Xác định tháng phát sinh đơn hàng đầu tiên của từng khách
    SELECT 
        customer_key,
        DATE_TRUNC('month', MIN(created_at)) AS cohort_month
    FROM fact_orders
    WHERE order_status = 'DELIVERED'
    GROUP BY customer_key
),
customer_activities AS (
    -- Ghi nhận các tháng phát sinh giao dịch thành công của khách
    SELECT DISTINCT
        o.customer_key,
        f.cohort_month,
        DATE_TRUNC('month', o.created_at) AS order_month,
        -- Tính khoảng cách số tháng từ lúc gia nhập
        (EXTRACT(YEAR FROM o.created_at) - EXTRACT(YEAR FROM f.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM o.created_at) - EXTRACT(MONTH FROM f.cohort_month)) AS month_number
    FROM fact_orders o
    INNER JOIN customer_first_orders f ON o.customer_key = f.customer_key
    WHERE o.order_status = 'DELIVERED'
),
cohort_sizes AS (
    -- Đếm quy mô tổng số khách hàng của từng Cohort ban đầu
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_key) AS total_cohort_customers
    FROM customer_first_orders
    GROUP BY cohort_month
)
SELECT 
    TO_CHAR(a.cohort_month, 'YYYY-MM') AS cohort,
    s.total_cohort_customers,
    ROUND(COUNT(DISTINCT CASE WHEN a.month_number = 0 THEN a.customer_key END) * 100.0 / s.total_cohort_customers, 1) AS m0_pct,
    ROUND(COUNT(DISTINCT CASE WHEN a.month_number = 1 THEN a.customer_key END) * 100.0 / s.total_cohort_customers, 1) AS m1_pct,
    ROUND(COUNT(DISTINCT CASE WHEN a.month_number = 2 THEN a.customer_key END) * 100.0 / s.total_cohort_customers, 1) AS m2_pct,
    ROUND(COUNT(DISTINCT CASE WHEN a.month_number = 3 THEN a.customer_key END) * 100.0 / s.total_cohort_customers, 1) AS m3_pct,
    ROUND(COUNT(DISTINCT CASE WHEN a.month_number = 6 THEN a.customer_key END) * 100.0 / s.total_cohort_customers, 1) AS m6_pct,
    ROUND(COUNT(DISTINCT CASE WHEN a.month_number = 12 THEN a.customer_key END) * 100.0 / s.total_cohort_customers, 1) AS m12_pct
FROM customer_activities a
INNER JOIN cohort_sizes s ON a.cohort_month = s.cohort_month
GROUP BY a.cohort_month, s.total_cohort_customers
ORDER BY a.cohort_month DESC;
```

---

## 2. TRUY VẤN 2: TRÍCH XUẤT CHỈ SỐ VÀ CHIA PHÂN VỊ RFM (RECENCY, FREQUENCY, MONETARY)
Truy vấn tính toán số ngày chưa mua hàng (Recency), tổng số đơn hoàn thành (Frequency) và tổng số tiền đã chi tiêu (Monetary), sau đó dùng hàm cửa sổ `NTILE(5)` để chia thành các thang điểm từ 1 đến 5.

```sql
WITH customer_rfm_raw AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.phone_number,
        -- Recency: Số ngày kể từ đơn hàng thành công gần nhất đến hiện tại
        CURRENT_DATE - MAX(o.created_at::DATE) AS recency_days,
        -- Frequency: Tổng số đơn hàng giao thành công
        COUNT(DISTINCT o.order_id) AS frequency,
        -- Monetary: Tổng doanh thu thuần khách đã chi trả
        SUM(o.total_order_value) AS monetary_total
    FROM dim_customers c
    INNER JOIN fact_orders o ON c.customer_key = o.customer_key
    WHERE o.order_status = 'DELIVERED'
    GROUP BY c.customer_id, c.customer_name, c.phone_number
),
rfm_scored AS (
    SELECT 
        customer_id,
        customer_name,
        phone_number,
        recency_days,
        frequency,
        monetary_total,
        -- R score: Mua càng gần đây điểm càng cao (1 = mua rất lâu rồi, 5 = mới mua)
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- F score: Mua càng nhiều đơn điểm càng cao
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        -- M score: Chi tiêu càng nhiều điểm càng cao
        NTILE(5) OVER (ORDER BY monetary_total ASC) AS m_score
    FROM customer_rfm_raw
)
SELECT 
    customer_id,
    customer_name,
    phone_number,
    recency_days,
    frequency,
    monetary_total,
    r_score,
    f_score,
    m_score,
    -- Gắn nhãn phân khúc khách hàng tự động
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'CHAMPIONS (Khách hàng VIP)'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'LOYAL CUSTOMERS (Khách trung thành)'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'RECENT NEW CUSTOMERS (Khách mới tiềm năng)'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'AT RISK (Khách VIP sắp rời bỏ)'
        WHEN r_score = 1 AND f_score = 1 THEN 'LOST (Khách đã mất)'
        ELSE 'AVERAGE (Khách hàng phổ thông)'
    END AS segment_label
FROM rfm_scored
ORDER BY monetary_total DESC;
```

---

## 3. TRUY VẤN 3: TÍNH TỐC ĐỘ BÁN & SỐ NGÀY TỒN KHO CÒN LẠI (STOCK RUNWAY & REORDER ALERT)
Truy vấn tính tốc độ bán trung bình ngày trong 30 ngày gần nhất (Daily Run Rate), so sánh với lượng tồn khả dụng trong kho để tính Số ngày tồn còn lại (Days of Supply) và gắn cờ cảnh báo:

```sql
WITH sales_velocity_30d AS (
    -- Tính tổng số lượng bán ra của từng sản phẩm trong 30 ngày qua
    SELECT 
        i.product_key,
        SUM(i.quantity) AS units_sold_30d,
        ROUND(SUM(i.quantity)::NUMERIC / 30.0, 2) AS avg_daily_velocity
    FROM fact_order_items i
    INNER JOIN fact_orders o ON i.order_id = o.order_id
    WHERE o.order_status = 'DELIVERED'
      AND o.created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY i.product_key
),
current_stock AS (
    -- Lấy tồn kho khả dụng mới nhất từ bảng ảnh chụp hàng ngày
    SELECT 
        product_key,
        units_available,
        total_inventory_value
    FROM fact_daily_inventory_snapshot
    WHERE date_key = (SELECT MAX(date_key) FROM fact_daily_inventory_snapshot)
)
SELECT 
    p.product_id AS sku,
    p.product_name,
    p.category,
    COALESCE(s.units_available, 0) AS stock_on_hand,
    COALESCE(v.avg_daily_velocity, 0.0) AS daily_velocity,
    -- Tính số ngày tồn kho còn lại (Stock Runway)
    CASE 
        WHEN COALESCE(v.avg_daily_velocity, 0) = 0 THEN 999
        ELSE ROUND(COALESCE(s.units_available, 0) / v.avg_daily_velocity, 1)
    END AS days_of_inventory_left,
    -- Cảnh báo hành động cho AI
    CASE 
        WHEN COALESCE(s.units_available, 0) = 0 THEN 'OUT_OF_STOCK: Hết hàng khẩn cấp'
        WHEN COALESCE(v.avg_daily_velocity, 0) > 0 AND (COALESCE(s.units_available, 0) / v.avg_daily_velocity) <= 7 
            THEN 'CRITICAL_REORDER: Tồn dưới 7 ngày, đặt hàng ngay'
        WHEN COALESCE(v.avg_daily_velocity, 0) > 0 AND (COALESCE(s.units_available, 0) / v.avg_daily_velocity) <= 15 
            THEN 'WARNING: Tồn dưới 15 ngày, chuẩn bị PO'
        WHEN COALESCE(v.avg_daily_velocity, 0) = 0 OR (COALESCE(s.units_available, 0) / v.avg_daily_velocity) > 60 
            THEN 'OVERSTOCK: Đọng vốn > 60 ngày, kích hoạt thanh lý'
        ELSE 'HEALTHY: Tồn kho an toàn'
    END AS inventory_health_status
FROM dim_products p
LEFT JOIN current_stock s ON p.product_key = s.product_key
LEFT JOIN sales_velocity_30d v ON p.product_key = v.product_key
WHERE p.is_current = TRUE
ORDER BY days_of_inventory_left ASC;
```

---

## 4. TRUY VẤN 4: KHAI PHÁ CẶP SẢN PHẨM MUA CÙNG NHAU (CROSS-SELL & BUNDLE AFFINITY)
Tìm kiếm các cặp sản phẩm thường xuyên xuất hiện cùng nhau trong cùng một đơn hàng (`order_id`) để AI gợi ý thiết kế combo hoặc tính năng gợi ý mua kèm ở trang thanh toán.

```sql
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(DISTINCT item1.order_id) AS times_bought_together,
    ROUND(COUNT(DISTINCT item1.order_id)::NUMERIC / 
        (SELECT COUNT(DISTINCT order_id) FROM fact_order_items)::NUMERIC * 100.0, 2) AS pair_support_pct
FROM fact_order_items item1
INNER JOIN fact_order_items item2 
    ON item1.order_id = item2.order_id 
    AND item1.product_key < item2.product_key -- Tránh trùng lặp đảo vị trí (A-B và B-A)
INNER JOIN dim_products p1 ON item1.product_key = p1.product_key
INNER JOIN dim_products p2 ON item2.product_key = p2.product_key
GROUP BY p1.product_name, p2.product_name
HAVING COUNT(DISTINCT item1.order_id) >= 10 -- Chỉ lấy cặp có tối thiểu 10 đơn mua chung
ORDER BY times_bought_together DESC
LIMIT 20;
```

---

## 5. TRUY VẤN 5: DOANH THU & BIÊN LỢI NHUẬN TRƯỢT 7 NGÀY (ROLLING 7-DAY METRICS & MOM GROWTH)
Sử dụng hàm cửa sổ (Window Functions) để làm mượt số liệu theo chu kỳ tuần, loại bỏ biến động nhiễu của các ngày cuối tuần và phát hiện sự sụt giảm doanh thu.

```sql
WITH daily_financials AS (
    SELECT 
        d.full_date,
        COUNT(DISTINCT o.order_id) AS daily_orders,
        SUM(o.total_order_value) AS daily_revenue,
        SUM(i.total_cogs) AS daily_cogs,
        SUM(o.total_order_value - i.total_cogs - o.marketplace_fee - o.packaging_cost) AS daily_cm1
    FROM dim_dates d
    LEFT JOIN fact_orders o ON d.date_key = o.date_key AND o.order_status = 'DELIVERED'
    LEFT JOIN fact_order_items i ON o.order_id = i.order_id
    WHERE d.full_date BETWEEN CURRENT_DATE - INTERVAL '60 days' AND CURRENT_DATE
    GROUP BY d.full_date
)
SELECT 
    full_date,
    daily_orders,
    daily_revenue,
    -- Trung bình trượt 7 ngày của doanh thu
    ROUND(AVG(daily_revenue) OVER (
        ORDER BY full_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_7d_avg_revenue,
    -- Trung bình trượt 7 ngày của Lãi gộp CM1
    ROUND(AVG(daily_cm1) OVER (
        ORDER BY full_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 0) AS rolling_7d_avg_cm1,
    -- Tỷ lệ biên CM1 trượt 7 ngày
    ROUND(
        (SUM(daily_cm1) OVER (ORDER BY full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) / 
         NULLIF(SUM(daily_revenue) OVER (ORDER BY full_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 0)) * 100.0, 2
    ) AS rolling_7d_cm1_margin_pct,
    -- So sánh với cùng ngày tuần trước (Doanh thu ngày hôm nay vs 7 ngày trước)
    ROUND(
        (daily_revenue - LAG(daily_revenue, 7) OVER (ORDER BY full_date))::NUMERIC / 
        NULLIF(LAG(daily_revenue, 7) OVER (ORDER BY full_date), 0)::NUMERIC * 100.0, 2
    ) AS wow_growth_pct
FROM daily_financials
ORDER BY full_date DESC;
```
