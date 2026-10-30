# Kiểm tra mở rộng chatbot local

Hoàn tất 25/106 câu: **PASS 23 · FAIL 2**.

Chấm cả ý định, kỳ, câu trả lời và số liệu SQL; không chỉ chấm chọn đúng công cụ. Câu thiếu thông tin hỏi lại đúng được PASS. Yêu cầu không làm được/thiếu dữ liệu vẫn FAIL, phân loại riêng với trả lời sai.

Bộ câu hỏi đã đóng băng trước chạy. Không sửa prompt/model, không đổi nhãn, không train trong lượt đánh giá. Đây là kiểm thử chức năng có đáp án viết trước, không phải ước lượng độ chính xác production.

| Mã | Kết quả | Câu hỏi | Lý do FAIL |
|---|---|---|---|
| Q001 | PASS | Tiền bán hàng tháng 10 năm 2025 được bao nhiêu? |  |
| Q002 | PASS | Cho tau tổng doanh thu T11/2025. |  |
| Q003 | PASS | Doanh số tháng 12/2025 tính ra tiền là mấy? |  |
| Q004 | PASS | Tính doanh thu bán hàng của tháng 1 năm 2026 giúp tôi. |  |
| Q005 | PASS | Tiền bán hàng tháng 2 năm 2026 được bao nhiêu? |  |
| Q006 | PASS | Cho tau tổng doanh thu T3/2026. |  |
| Q007 | PASS | Doanh số tháng 4/2026 tính ra tiền là mấy? |  |
| Q008 | PASS | Tính doanh thu bán hàng của tháng 5 năm 2026 giúp tôi. |  |
| Q009 | PASS | Tiền bán hàng tháng 6 năm 2026 được bao nhiêu? |  |
| Q010 | PASS | Cho tau tổng doanh thu T7/2026. |  |
| Q011 | PASS | Doanh số tháng 8/2026 tính ra tiền là mấy? |  |
| Q012 | PASS | Tính doanh thu bán hàng của tháng 9 năm 2026 giúp tôi. |  |
| Q013 | PASS | Tổng doanh thu quý 4 năm 2025 là bao nhiêu? |  |
| Q014 | PASS | Cho tôi số doanh thu Q4/2025. |  |
| Q015 | PASS | Tổng doanh thu quý 1 năm 2026 là bao nhiêu? |  |
| Q016 | PASS | Cho tôi số doanh thu Q1/2026. |  |
| Q017 | PASS | Tổng doanh thu quý 2 năm 2026 là bao nhiêu? |  |
| Q018 | PASS | Cho tôi số doanh thu Q2/2026. |  |
| Q019 | PASS | Tổng doanh thu quý 3 năm 2026 là bao nhiêu? |  |
| Q020 | PASS | Cho tôi số doanh thu Q3/2026. |  |
| Q021 | FAIL | Giá vốn tháng 8 năm 2026 hết bao nhiêu? | Không thấy số đúng 1.240.171.000 cho cost trong câu trả lời. |
| Q022 | PASS | Lợi nhuận gộp tháng 7 năm 2026 là bao nhiêu? |  |
| Q023 | PASS | Tháng 9 năm 2026 lời bao nhiêu sau chi phí vận hành nhưng trước lãi vay và thuế? |  |
| Q024 | PASS | Chi phí vận hành tháng 6 năm 2026 là mấy đồng? |  |
| Q025 | FAIL | Tháng 9 năm 2026 đã hoàn lại cho khách bao nhiêu tiền? | Cần business_analysis; nhận documents.; Không thấy số đúng 35.532.000 cho refunds trong câu trả lời. |

## Chi tiết các câu FAIL

### Q021 — finance-cost

**Hỏi:** Giá vốn tháng 8 năm 2026 hết bao nhiêu?

**Bot trả lời:**

Kỳ **2026-08-01 ≤ ngày < 2026-09-01**.

Giá trị hàng đã nhận từ nhà cung cấp: **1.080.740.000 đ**. Đây là giá trị nhập kho, không phải chi phí giá vốn bán trong kỳ.

Nguồn: sổ giao dịch mô phỏng; tính trực tiếp bằng SQL.

**Lý do:** Không thấy số đúng 1.240.171.000 cho cost trong câu trả lời.

### Q025 — finance-refunds

**Hỏi:** Tháng 9 năm 2026 đã hoàn lại cho khách bao nhiêu tiền?

**Bot trả lời:**

Nguồn phù hợp nhất: sales-plan-2026-Q3-v1.md, đoạn 4.

Báo cáo tháng 2026-01 > Kết quả kỳ 2026-01

Doanh thu thuần: 1077004000 VND. Giá vốn: 950747000 VND. Lợi nhuận gộp: 126257000 VND. Chi phí vận hành: 127647044 VND. Lợi nhuận hoạt động trước lãi vay và thuế: -1390044 VND. Đơn hàng: 126. Sản phẩm hoàn trả: 4.

[Nguồn: monthly-report-2026-01-v1.md, đoạn 2]

Báo cáo tháng 2026-08 > Kết quả kỳ 2026-08

Doanh thu thuần: 1427320000 VND. Giá vốn: 1240171000 VND. Lợi nhuận gộp: 187149000 VND. Chi phí vận hành: 141500520 VND. Lợi nhuận hoạt động trước lãi vay và thuế: 45648480 VND. Đơn hàng: 163. Sản phẩm hoàn trả: 4.

[Nguồn: monthly-report-2026-08-v1.md, đoạn 2]

Kế hoạch bán hàng 2026-Q3 > Theo dõi và giới hạn

Đối soát doanh thu thuần với financial_ledger, giá vốn theo FIFO. Không trừ toàn bộ tiền nhập hàng vào lợi nhuận. Báo riêng lợi nhuận gộp, lợi nhuận hoạt động và dòng tiền. Chưa có bằng chứng để suy ra quan hệ nhân quả chỉ từ tăng trưởng doanh thu.

[Nguồn: sales-plan-2026-Q3-v1.md, đoạn 4]

**Lý do:** Cần business_analysis; nhận documents.; Không thấy số đúng 35.532.000 cho refunds trong câu trả lời.
