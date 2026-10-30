# Shop giả lập — 67 sản phẩm, một năm

**Toàn bộ giao dịch, giá shop, tồn, giá vốn, chi phí và khách hàng trong gói này là mô phỏng.**
Thông số sản phẩm giữ nguyên nguồn công khai; không giả nhận doanh thu thật của shop.

- Kỳ: **01/10/2025–30/09/2026**.
- **67/67 SKU có bán**; mã SKU chính là ID trong `../../product_sql/products.sqlite`.
- 1.427 đơn bán, 1.717 dòng bán, 320 đơn đặt nhập, 317 phiếu nhận, 31 lượt hoàn.
- 365 ngày tồn kho cho từng SKU; 99 khoản chi.

Mở `shop.sqlite` bằng DB Browser for SQLite/DBeaver, hoặc import `shop.sqlite.sql`
vào database trống. Bản CSV nằm trong `csv/`.

```sql
SELECT * FROM monthly_pnl ORDER BY month;
SELECT p.sku,p.name,SUM(l.quantity) net_units,SUM(l.revenue) net_revenue,
       SUM(l.revenue-l.cost) gross_profit
FROM financial_ledger l JOIN products p ON p.sku=l.sku
GROUP BY p.sku ORDER BY net_revenue DESC;
SELECT * FROM purchase_orders p
JOIN purchase_lines l ON l.po_id=p.id
LEFT JOIN receipts r ON r.line_id=l.id;
SELECT * FROM inventory_daily WHERE day='2026-09-30';
```

`assumptions.json` nêu giả định và `source_profile.json` nêu thống kê dữ liệu tham
khảo. `validation_report.json` kiểm tra toàn vẹn, FIFO, tiền và matching SKU.
`monthly_summary.json` là kết quả từ SQL, không phải số được gõ tay.

`documents/` chứa kế hoạch, chính sách, marketing và báo cáo cùng scenario.
`evaluation_only/` là đáp án ẩn cho người chấm; **không đưa vào RAG hoặc train**.

Nguồn giá USD của linh kiện không phải giá thị trường Việt Nam; giá VND trong
gói này là giả định. Số liệu chưa VAT, chưa mô hình hóa lãi vay và thuế thu nhập.
Không gọi lợi nhuận hoạt động trước lãi vay/thuế là lợi nhuận sau thuế.

Không sửa từng dòng CSV rồi coi SQLite đã đổi. Muốn đổi giả định, tạo phiên bản
scenario mới bằng simulator và chạy lại đối soát. Không chạy generator lên cơ
sở dữ liệu thật. Quy trình ETL dữ liệu thực phải giữ đủ bán, nhập, hoàn và chi phí.

Thiết kế và luồng huấn luyện: `../../../DATA_AND_TRAINING_V2.md`.
