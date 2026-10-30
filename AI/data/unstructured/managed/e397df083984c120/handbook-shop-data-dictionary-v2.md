# Từ điển dữ liệu database shop (sinh tự động từ shop.sqlite)

> Tài liệu phương pháp nội bộ (handbook phân tích kinh doanh), chỉ dành cho quản lý. Mọi con số trong ví dụ là minh họa, KHÔNG phải số liệu của shop. Số liệu shop (doanh thu, giá vốn, đơn, tồn kho) chỉ lấy từ công cụ SQL/báo cáo trên database data/business_sql/scenario_v1/shop.sqlite (dữ liệu mô phỏng 01/10/2025–30/09/2026).

Database: data/business_sql/scenario_v1/shop.sqlite (SQLite). Dùng đúng tên bảng/cột dưới đây.

Database shop không có các bảng fact_orders, dim_customers, dim_products hay fact_daily_inventory_snapshot; các tên đó chỉ là ví dụ lược đồ Kimball trong tài liệu tham khảo.

Doanh thu thuần lấy từ bảng financial_ledger, cột revenue (dòng kind=sale dương, dòng kind=return âm).

## Bảng campaigns

Bảng campaigns có các cột: id, name, start, end, budget, discount_bps. Bảng campaigns có 3 dòng.

## Bảng customers

Bảng customers có các cột: id, segment. Bảng customers có 1200 dòng.

## Bảng financial_ledger

Bảng financial_ledger có các cột: id, day, sku, quantity, revenue, cost, kind. Bảng financial_ledger có 1748 dòng; day từ 2025-10-01 đến 2026-09-30.

## Bảng inventory_daily

Bảng inventory_daily có các cột: day, sku, quantity, value. Bảng inventory_daily có 24455 dòng; day từ 2025-10-01 đến 2026-09-30.

## Bảng inventory_moves

Bảng inventory_moves có các cột: id, day, sku, delta, cost_delta, kind, source_id. Bảng inventory_moves có 2126 dòng; day từ 2025-10-01 đến 2026-09-30.

## Bảng metadata

Bảng metadata có các cột: key, value. Bảng metadata có 9 dòng.

## Bảng monthly_targets

Bảng monthly_targets có các cột: month, revenue, gross_margin_bps. Bảng monthly_targets có 12 dòng; month từ 2025-10 đến 2026-09.

## Bảng operating_expenses

Bảng operating_expenses có các cột: id, day, category, amount, campaign_id. Bảng operating_expenses có 99 dòng; day từ 2025-10-31 đến 2026-09-30.

## Bảng order_items

Bảng order_items có các cột: id, order_id, sku, quantity, list_price, discount, revenue, cost. Bảng order_items có 1717 dòng.

## Bảng orders

Bảng orders có các cột: id, day, customer_id, channel, campaign_id. Bảng orders có 1427 dòng; day từ 2025-10-01 đến 2026-09-30.

## Bảng product_facts

Bảng product_facts có các cột: sku, record_json, segment, standard_cost, price_basis, synthetic. Bảng product_facts có 67 dòng.

## Bảng products

Bảng products có các cột: sku, name, price, stock, panel, ram, battery, weight, category. Bảng products có 67 dòng.

## Bảng purchase_lines

Bảng purchase_lines có các cột: id, po_id, sku, quantity, unit_cost. Bảng purchase_lines có 320 dòng.

## Bảng purchase_orders

Bảng purchase_orders có các cột: id, ordered_day, supplier_id, due_day. Bảng purchase_orders có 320 dòng; ordered_day từ 2025-10-06 đến 2026-09-28.

## Bảng receipts

Bảng receipts có các cột: id, line_id, day, sku, quantity, unit_cost. Bảng receipts có 317 dòng; day từ 2025-10-10 đến 2026-09-25.

## Bảng returns

Bảng returns có các cột: id, item_id, day, sku, quantity, refund, cost_reversal, restock, reason. Bảng returns có 31 dòng; day từ 2025-10-25 đến 2026-09-04.

## Bảng suppliers

Bảng suppliers có các cột: id, name, lead_days. Bảng suppliers có 2 dòng.

## Định nghĩa chỉ tiêu dùng trong báo cáo

- Doanh thu thuần: SUM(financial_ledger.revenue) theo ngày ghi sổ; dòng return mang giá trị âm.
- Giá vốn hàng bán: SUM(financial_ledger.cost). Lãi gộp: doanh thu thuần − giá vốn.
- Chi phí vận hành: SUM(operating_expenses.amount). Lợi nhuận hoạt động trước lãi vay và thuế: lãi gộp − chi phí vận hành.
- Số đơn: COUNT(orders) theo ngày đặt. Tiền hoàn: SUM(returns.refund) theo ngày hoàn.
- Kênh bán: orders.channel. Phân khúc khách: customers.segment. Mục tiêu doanh thu tháng: monthly_targets.revenue.
- Tồn kho cuối ngày: inventory_daily.quantity và value.

Không có thuế, lãi vay, chi phí quảng cáo theo từng đơn hay trạng thái giao hàng trong database; các chỉ tiêu cần những dữ liệu đó phải báo là chưa có dữ liệu.