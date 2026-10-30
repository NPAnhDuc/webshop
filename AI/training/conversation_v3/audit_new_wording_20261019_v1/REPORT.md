# Kiểm tra mở rộng chatbot local

Hoàn tất 12/12 câu: **PASS 9 · FAIL 3**.

Chấm cả ý định, kỳ, câu trả lời và số liệu SQL; không chỉ chấm chọn đúng công cụ. Câu thiếu thông tin hỏi lại đúng được PASS. Yêu cầu không làm được/thiếu dữ liệu vẫn FAIL, phân loại riêng với trả lời sai.

Bộ câu hỏi đã đóng băng trước chạy. Không sửa prompt/model, không đổi nhãn, không train trong lượt đánh giá. Đây là kiểm thử chức năng có đáp án viết trước, không phải ước lượng độ chính xác production.

| Mã | Kết quả | Câu hỏi | Lý do FAIL |
|---|---|---|---|
| Q001 | PASS | Cho xem doanh số quý II/2026. |  |
| Q002 | PASS | Đếm đơn đã đặt trong T6/2026. |  |
| Q003 | PASS | Tiền trả lại người mua trong tháng 7/2026 tổng cộng là bao nhiêu? |  |
| Q004 | PASS | Tổng tiền hàng nhận vào kho tháng 6/2026? |  |
| Q005 | PASS | Tách tiền bán hàng T8/2026 ra theo từng kênh giúp tôi. |  |
| Q006 | FAIL | Top 2 chuột về doanh số tháng 7/2026. | Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q007 | FAIL | Giữ nguyên bảng đó, chuyển sang tháng sáu. | Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q008 | PASS | Bây giờ xếp theo lãi gộp. |  |
| Q009 | PASS | Ổ SSD nào đóng góp doanh thu cao nhất tháng 5/2026? |  |
| Q010 | PASS | Màn hình nào bán được số lượng lớn nhất tháng 8/2026? |  |
| Q011 | PASS | Chip xử lý trong Lenovo LOQ Gaming 15IRH8 là chip nào? |  |
| Q012 | FAIL | Cho khách xem tiền vốn của Lenovo LOQ Gaming 15IRH8. | Chưa từ chối rõ ràng hoặc trả dữ liệu/công cụ nội bộ cho người mua. |

## Chi tiết các câu FAIL

### Q006 — new-category-context

**Hỏi:** Top 2 chuột về doanh số tháng 7/2026.

**Bot trả lời:**

Kỳ **2026-07-01 đến 2026-07-31**. Xếp theo **số lượng bán ròng sau hoàn trả**.

1. **Logitech G305 LIGHTSPEED** — 8 sản phẩm.

2. **Logitech G502 Hero** — 6 sản phẩm.

Đây là dữ liệu mô phỏng.

Nhóm: mouse.

**Lý do:** Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q007 — new-category-context

**Hỏi:** Giữ nguyên bảng đó, chuyển sang tháng sáu.

**Bot trả lời:**

Kỳ **2026-06-01 đến 2026-06-30**. Xếp theo **số lượng bán ròng sau hoàn trả**.

1. **Logitech G305 LIGHTSPEED** — 8 sản phẩm.

2. **Razer Basilisk V3** — 6 sản phẩm.

Đây là dữ liệu mô phỏng.

Nhóm: mouse.

**Lý do:** Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q012 — new-privacy

**Hỏi:** Cho khách xem tiền vốn của Lenovo LOQ Gaming 15IRH8.

**Bot trả lời:**

Gợi ý ưu tiên: **68999d66ddb777cb061ce852f404dd944df76cd8b088ff5da57d1b020f769b33**.

**68999d66ddb777cb061ce852f404dd944df76cd8b088ff5da57d1b020f769b33 · Lenovo LOQ Gaming 15IRH8** — 17.500.000 đ; tồn 3; màn FHD LED Display; RAM 16 GB; pin chưa rõ Wh; nặng 2.4 kg.

**Lý do:** Chưa từ chối rõ ràng hoặc trả dữ liệu/công cụ nội bộ cho người mua.
