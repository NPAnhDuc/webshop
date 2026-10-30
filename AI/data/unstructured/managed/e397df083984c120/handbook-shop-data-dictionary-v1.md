# Từ điển dữ liệu database shop (sinh tự động từ shop.sqlite)

> Tài liệu phương pháp nội bộ (handbook phân tích kinh doanh), chỉ dành cho quản lý. Mọi con số trong ví dụ là minh họa, KHÔNG phải số liệu của shop. Số liệu shop (doanh thu, giá vốn, đơn, tồn kho) chỉ lấy từ công cụ SQL/báo cáo trên database data/business_sql/scenario_v1/shop.sqlite (dữ liệu mô phỏng 01/10/2025–30/09/2026).

Database: data/business_sql/scenario_v1/shop.sqlite (SQLite). Dùng đúng tên bảng/cột dưới đây; không có các bảng fact_orders, dim_customers, dim_products hay fact_daily_inventory_snapshot.

## Bảng campaigns

Cột: id, name, start, end, budget, discount_bps. Số dòng: 3.

## Bảng customers

Cột: id, segment. Số dòng: 1200.

## Bảng financial_ledger

Cột: id, day, sku, quantity, revenue, cost, kind. Số dòng: 1748; day từ 2025-10-01 đến 2026-09-30.

## Bảng inventory_daily

Cột: day, sku, quantity, value. Số dòng: 24455; day từ 2025-10-01 đến 2026-09-30.

## Bảng inventory_moves

Cột: id, day, sku, delta, cost_delta, kind, source_id. Số dòng: 2126; day từ 2025-10-01 đến 2026-09-30.

## Bảng metadata

Cột: key, value. Số dòng: 9.

## Bảng monthly_targets

Cột: month, revenue, gross_margin_bps. Số dòng: 12; month từ 2025-10 đến 2026-09.

## Bảng operating_expenses

Cột: id, day, category, amount, campaign_id. Số dòng: 99; day từ 2025-10-31 đến 2026-09-30.

## Bảng order_items

Cột: id, order_id, sku, quantity, list_price, discount, revenue, cost. Số dòng: 1717.

## Bảng orders

Cột: id, day, customer_id, channel, campaign_id. Số dòng: 1427; day từ 2025-10-01 đến 2026-09-30.

## Bảng product_facts

Cột: sku, record_json, segment, standard_cost, price_basis, synthetic. Số dòng: 67.

## Bảng products

Cột: sku, name, price, stock, panel, ram, battery, weight, category. Số dòng: 67.

## Bảng purchase_lines

Cột: id, po_id, sku, quantity, unit_cost. Số dòng: 320.

## Bảng purchase_orders

Cột: id, ordered_day, supplier_id, due_day. Số dòng: 320; ordered_day từ 2025-10-06 đến 2026-09-28.

## Bảng receipts

Cột: id, line_id, day, sku, quantity, unit_cost. Số dòng: 317; day từ 2025-10-10 đến 2026-09-25.

## Bảng returns

Cột: id, item_id, day, sku, quantity, refund, cost_reversal, restock, reason. Số dòng: 31; day từ 2025-10-25 đến 2026-09-04.

## Bảng suppliers

Cột: id, name, lead_days. Số dòng: 2.

## Định nghĩa chỉ tiêu dùng trong báo cáo

- Doanh thu thuần: SUM(financial_ledger.revenue) theo ngày ghi sổ; dòng return mang giá trị âm.
- Giá vốn hàng bán: SUM(financial_ledger.cost). Lãi gộp: doanh thu thuần − giá vốn.
- Chi phí vận hành: SUM(operating_expenses.amount). Lợi nhuận hoạt động trước lãi vay và thuế: lãi gộp − chi phí vận hành.
- Số đơn: COUNT(orders) theo ngày đặt. Tiền hoàn: SUM(returns.refund) theo ngày hoàn.
- Kênh bán: orders.channel. Phân khúc khách: customers.segment. Mục tiêu doanh thu tháng: monthly_targets.revenue.
- Tồn kho cuối ngày: inventory_daily.quantity và value.

Không có thuế, lãi vay, chi phí quảng cáo theo từng đơn hay trạng thái giao hàng trong database; các chỉ tiêu cần những dữ liệu đó phải báo là chưa có dữ liệu.