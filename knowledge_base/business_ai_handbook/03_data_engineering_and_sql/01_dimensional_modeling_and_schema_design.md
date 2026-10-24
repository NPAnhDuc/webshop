# MODULE 3.1: KỸ THUẬT DỮ LIỆU & THIẾT KẾ MÔ HÌNH HÓA DỮ LIỆU BÁN LẺ (DIMENSIONAL MODELING)

---

## 1. PHƯƠNG PHÁP LUẬN MÔ HÌNH HÓA DỮ LIỆU (RALPH KIMBALL STAR SCHEMA)
Để hệ thống AI có thể truy vấn dữ liệu kinh doanh một cách chính xác, tốc độ cao và không bị sai lệch số liệu, cơ sở dữ liệu phân tích cần được thiết kế theo **Mô hình Dấu Sao (Star Schema)** của Ralph Kimball, bao gồm 2 thực thể cốt lõi:
1. **Bảng Chi Tiết Giao Dịch (Fact Tables)**: Lưu trữ các sự kiện kinh doanh phát sinh theo thời gian thực (đơn hàng, chi tiết đơn hàng, biến động tồn kho, chi phí quảng cáo). Hầu hết các cột là các chỉ số định lượng có thể cộng gộp (additive measures: doanh thu, giá vốn, số lượng).
2. **Bảng Chiều Không Gian (Dimension Tables)**: Lưu trữ thông tin bối cảnh dùng để lọc (filter), nhóm (group by) và phân đoạn dữ liệu (khách hàng, sản phẩm, kênh bán hàng, thời gian).

---

## 2. KIẾN TRÚC 3 TẦNG DỮ LIỆU PHÂN TÍCH (ANALYTICS MEDALLION / DBT LAYERS)

```
[HỆ THỐNG GIAO DỊCH GỐC (OLTP)]
   │ (PostgreSQL, SQLite, Webhook Sàn TMĐT, CSV Kế toán)
   ▼
[TẦNG 1: STAGING (stg_)]
   • Trích xuất thô, chuẩn hóa kiểu dữ liệu (Date, Timestamp, Cast số nguyên/thực)
   • Chuẩn hóa tên trường (lowercase, snake_case), xử lý chuỗi rác
   ▼
[TẦNG 2: INTERMEDIATE (int_)]
   • Nối các bảng logic, làm sạch dữ liệu trùng lặp (Deduplication)
   • Tính toán các cột phái sinh ban đầu (Net Revenue = Gross - Discount)
   ▼
[TẦNG 3: ANALYTICS MARTS (dim_ & fct_)]
   • Bảng Fact và Dimension hoàn chỉnh phục vụ trực tiếp cho AI truy vấn và BI Dashboard
```

---

## 3. THIẾT KẾ LƯỢC ĐỒ CƠ SỞ DỮ LIỆU CHUẨN (PRODUCTION DDL)

Dưới đây là mã DDL hoàn chỉnh, tương thích tối đa với cả **PostgreSQL** và **SQLite** (dùng cho AI Local), bao gồm toàn bộ ràng buộc và chỉ mục (Indexes) để tăng tốc độ truy vấn lên gấp 50 lần:

### 3.1. Bảng Chiều Sản Phẩm (SCD Type 2: Theo Dõi Biến Động Giá & Chi Phí Theo Thời Gian)
Khi sản phẩm thay đổi giá nhập hoặc giá bán niêm yết, phương pháp SCD Type 2 giúp AI tính toán chính xác lợi nhuận lịch sử mà không làm sai lệch các đơn hàng trong quá khứ.

```sql
CREATE TABLE dim_products (
    product_key INTEGER PRIMARY KEY,           -- Khóa nhân tạo (Surrogate Key)
    product_id VARCHAR(50) NOT NULL,            -- Mã sản phẩm tự nhiên (SKU / Natural Key)
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,             -- Danh mục: CPU, VGA, RAM, Mainboard...
    brand VARCHAR(100) NOT NULL,                -- Intel, AMD, ASUS, Corsair...
    current_cost_price DECIMAL(15, 2) NOT NULL, -- Giá vốn nhập hàng hiện tại (COGS)
    current_retail_price DECIMAL(15, 2) NOT NULL,-- Giá bán lẻ niêm yết (MSRP)
    weight_grams INTEGER DEFAULT 500,           -- Khối lượng để tính cước vận chuyển
    is_active BOOLEAN DEFAULT TRUE,
    valid_from TIMESTAMP NOT NULL,              -- Thời điểm bắt đầu áp dụng mức giá
    valid_to TIMESTAMP,                         -- Thời điểm hết hiệu lực (NULL = hiện tại)
    is_current BOOLEAN DEFAULT TRUE             -- TRUE nếu là bản ghi mới nhất
);

CREATE INDEX idx_dim_products_sku ON dim_products (product_id, is_current);
CREATE INDEX idx_dim_products_category ON dim_products (category);
```

---

### 3.2. Bảng Chiều Khách Hàng (dim_customers)
```sql
CREATE TABLE dim_customers (
    customer_key INTEGER PRIMARY KEY,
    customer_id VARCHAR(50) UNIQUE NOT NULL,    -- SĐT hoặc UUID khách hàng
    customer_name VARCHAR(150),
    phone_number VARCHAR(20),
    email VARCHAR(100),
    province_city VARCHAR(100),                 -- Tỉnh/Thành phố: Hà Nội, TP.HCM, Đà Nẵng...
    region VARCHAR(50),                         -- Miền Bắc, Miền Trung, Miền Nam
    first_order_date DATE,                      -- Ngày phát sinh đơn đầu tiên (Xác định Cohort)
    rfm_segment VARCHAR(50) DEFAULT 'New',      -- Phân khúc RFM: Champions, At-Risk, Loyal...
    total_lifetime_orders INTEGER DEFAULT 0,
    total_lifetime_spend DECIMAL(15, 2) DEFAULT 0.00
);

CREATE INDEX idx_dim_customers_phone ON dim_customers (phone_number);
CREATE INDEX idx_dim_customers_cohort ON dim_customers (first_order_date);
CREATE INDEX idx_dim_customers_rfm ON dim_customers (rfm_segment);
```

---

### 3.3. Bảng Chiều Thời Gian (dim_dates)
Đặc biệt quan trọng với thị trường Việt Nam để phân tích các mùa vụ cao điểm: Ngày trả lương (15 và cuối tháng), Ngày Siêu Sale đôi (9.9, 10.10, 11.11, 12.12), Black Friday và Tết Nguyên Đán.

```sql
CREATE TABLE dim_dates (
    date_key INTEGER PRIMARY KEY,               -- Định dạng YYYYMMDD (ví dụ: 20261024)
    full_date DATE UNIQUE NOT NULL,
    day_of_week INTEGER NOT NULL,               -- 1 = Thứ Hai, 7 = Chủ Nhật
    day_name VARCHAR(20) NOT NULL,
    day_of_month INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_payday BOOLEAN NOT NULL,                 -- TRUE nếu rơi vào ngày 15 hoặc cuối tháng
    is_double_day_sale BOOLEAN NOT NULL,        -- TRUE nếu là 09-09, 10-10, 11-11, 12-12
    is_holiday_vietnam BOOLEAN NOT NULL         -- TRUE nếu là ngày lễ Tết theo quy định
);

CREATE INDEX idx_dim_dates_full_date ON dim_dates (full_date);
```

---

### 3.4. Bảng Fact Chi Tiết Đơn Hàng (fact_order_items - Hạt Dữ Liệu Cấp Sản Phẩm)
Lưu chi tiết từng món hàng trong một đơn, phục vụ tính toán Lãi gộp CM1 và phân tích giỏ hàng (Market Basket Analysis).

```sql
CREATE TABLE fact_order_items (
    order_item_key INTEGER PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,              -- Khóa liên kết đơn hàng
    date_key INTEGER NOT NULL REFERENCES dim_dates(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customers(customer_key),
    product_key INTEGER NOT NULL REFERENCES dim_products(product_key),
    quantity INTEGER NOT NULL,
    unit_cost_price DECIMAL(15, 2) NOT NULL,    -- Giá vốn tại thời điểm bán
    unit_selling_price DECIMAL(15, 2) NOT NULL, -- Giá bán thực tế trên đơn
    item_discount_amount DECIMAL(15, 2) DEFAULT 0,
    gross_revenue DECIMAL(15, 2) NOT NULL,      -- quantity * unit_selling_price
    net_revenue DECIMAL(15, 2) NOT NULL,        -- gross_revenue - item_discount_amount
    total_cogs DECIMAL(15, 2) NOT NULL,         -- quantity * unit_cost_price
    gross_profit DECIMAL(15, 2) NOT NULL        -- net_revenue - total_cogs
);

CREATE INDEX idx_fact_items_order ON fact_order_items (order_id);
CREATE INDEX idx_fact_items_date ON fact_order_items (date_key);
CREATE INDEX idx_fact_items_prod ON fact_order_items (product_key);
```

---

### 3.5. Bảng Fact Đơn Hàng Tổng Thể (fact_orders - Hạt Dữ Liệu Cấp Đơn Hàng)
Lưu trữ toàn bộ thông tin dòng tiền, phương thức thanh toán, phí vận chuyển và trạng thái đối soát.

```sql
CREATE TABLE fact_orders (
    order_key INTEGER PRIMARY KEY,
    order_id VARCHAR(50) UNIQUE NOT NULL,
    date_key INTEGER NOT NULL REFERENCES dim_dates(date_key),
    customer_key INTEGER NOT NULL REFERENCES dim_customers(customer_key),
    sales_channel VARCHAR(50) NOT NULL,         -- Website, Shopee, TikTokShop, Facebook, POS
    payment_method VARCHAR(50) NOT NULL,        -- COD, VNPAY, Momo, Chuyển khoản, Thẻ tín dụng
    order_status VARCHAR(50) NOT NULL,          -- DELIVERED, RETURNED, CANCELLED, SHIPPING
    total_order_value DECIMAL(15, 2) NOT NULL,  -- Tổng tiền khách trả
    shipping_fee_charged DECIMAL(15, 2) DEFAULT 0,
    shipping_cost_paid DECIMAL(15, 2) DEFAULT 0,-- Tiền cước thực trả cho đơn vị vận chuyển
    marketplace_fee DECIMAL(15, 2) DEFAULT 0,   -- Phí sàn TMĐT khấu trừ
    packaging_cost DECIMAL(15, 2) DEFAULT 0,    -- Phí đóng gói
    is_cod_returned BOOLEAN DEFAULT FALSE,      -- TRUE nếu đơn bị hoàn COD
    created_at TIMESTAMP NOT NULL,
    delivered_at TIMESTAMP
);

CREATE INDEX idx_fact_orders_status ON fact_orders (order_status);
CREATE INDEX idx_fact_orders_channel ON fact_orders (sales_channel);
CREATE INDEX idx_fact_orders_date ON fact_orders (date_key);
```

---

### 3.6. Bảng Fact Ảnh Chụp Tồn Kho Hàng Ngày (fact_daily_inventory_snapshot)
Ghi lại trạng thái tồn kho vào cuối mỗi ngày, là dữ liệu đầu vào để tính Vòng quay tồn kho (ITR) và phát hiện hàng ứ đọng (Deadstock).

```sql
CREATE TABLE fact_daily_inventory_snapshot (
    snapshot_key INTEGER PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES dim_dates(date_key),
    product_key INTEGER NOT NULL REFERENCES dim_products(product_key),
    units_on_hand INTEGER NOT NULL,             -- Số lượng vật lý trong kho
    units_reserved INTEGER DEFAULT 0,           -- Đã có khách đặt nhưng chưa xuất
    units_available INTEGER NOT NULL,           -- units_on_hand - units_reserved
    total_inventory_value DECIMAL(15, 2) NOT NULL, -- units_on_hand * unit_cost_price
    days_without_sales INTEGER DEFAULT 0        -- Số ngày liên tiếp không có đơn bán
);

CREATE UNIQUE INDEX idx_inv_snapshot_daily ON fact_daily_inventory_snapshot (date_key, product_key);
```
