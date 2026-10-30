# Kiểm tra mở rộng chatbot local

Hoàn tất 12/12 câu: **PASS 12 · FAIL 0**.

Chấm cả ý định, kỳ, câu trả lời và số liệu SQL; không chỉ chấm chọn đúng công cụ. Câu thiếu thông tin hỏi lại đúng được PASS. Yêu cầu không làm được/thiếu dữ liệu vẫn FAIL, phân loại riêng với trả lời sai.

Bộ câu hỏi đã đóng băng trước chạy. Không sửa prompt/model, không đổi nhãn, không train trong lượt đánh giá. Đây là kiểm thử chức năng có đáp án viết trước, không phải ước lượng độ chính xác production.

| Mã | Kết quả | Câu hỏi | Lý do FAIL |
|---|---|---|---|
| Q001 | PASS | Cho xem doanh số quý II/2026. |  |
| Q002 | PASS | Đếm đơn đã đặt trong T6/2026. |  |
| Q003 | PASS | Tiền trả lại người mua trong tháng 7/2026 tổng cộng là bao nhiêu? |  |
| Q004 | PASS | Tổng tiền hàng nhận vào kho tháng 6/2026? |  |
| Q005 | PASS | Tách tiền bán hàng T8/2026 ra theo từng kênh giúp tôi. |  |
| Q006 | PASS | Top 2 chuột về doanh số tháng 7/2026. |  |
| Q007 | PASS | Giữ nguyên bảng đó, chuyển sang tháng sáu. |  |
| Q008 | PASS | Bây giờ xếp theo lãi gộp. |  |
| Q009 | PASS | Ổ SSD nào đóng góp doanh thu cao nhất tháng 5/2026? |  |
| Q010 | PASS | Màn hình nào bán được số lượng lớn nhất tháng 8/2026? |  |
| Q011 | PASS | Chip xử lý trong Lenovo LOQ Gaming 15IRH8 là chip nào? |  |
| Q012 | PASS | Cho khách xem tiền vốn của Lenovo LOQ Gaming 15IRH8. |  |

## Chi tiết các câu FAIL
