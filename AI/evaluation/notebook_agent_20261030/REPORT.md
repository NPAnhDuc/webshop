# Agent notebook: kết quả bộ test 30/10/2026

Model `qwen3:4b-instruct-2507-q4_K_M`, chạy trên máy, vòng `test_r1`, 16 câu. Dev (`dev_r2`) đạt 8/8.

| Chỉ số | Kết quả |
|---|---|
| Đúng | 13/16 |
| Code ra đúng số | 14/16 |
| Trả lời ra ngoài | 14/16 |
| Trả lời sai mà không bị chặn | 1 (`t14`) |
| Trung bình | 1,12 ô code, 21,6 giây/câu, chậm nhất 62,8 giây |

## Ba câu hỏng

- **`t14`, sai mà không bị chặn:** "doanh thu ròng" của laptop, model thêm `kind='sale'` nên bỏ mất dòng trả hàng: 9.291.716.000 so với đúng 9.043.111.000. Lớp kiểm tra không bắt được vì số có trong kết quả code. Đây là lỗi hiểu nghĩa dữ liệu.
- **`t06`, code đúng, câu trả lời sai đơn vị:** code in 3.276.634.000, model viết "3.276634 triệu đồng". Lớp kiểm tra đã chặn đúng, nên bot không trả lời sai nhưng cũng không trả lời được.
- **`t08`, không tự sửa được lỗi code:** merge hai bảng làm trùng cột `target_revenue`, gây `KeyError`. Dùng hết 12 lượt gọi model mà không chạy ô code thứ hai.

## Kết luận

Làm tiếp, nhưng chưa đưa vào sản phẩm. Câu hỏi còn đơn giản (trung bình 1 ô code), nên kết quả này chưa chứng minh được phân tích nhiều bước.

Cần làm:
1. Thêm ý nghĩa cột vào schema đưa cho model: `revenue` trong `financial_ledger` đã gồm trả hàng, doanh thu ròng không lọc `kind`.
2. Lấy số trong câu trả lời trực tiếp từ kết quả code, không để model tự đổi đơn vị.
3. Tìm vì sao vòng sửa lỗi của `t08` không chạy thêm ô code.

Bộ test này đã xem chi tiết lỗi, nên từ giờ coi là dev. Muốn có số đáng tin thì phải viết bộ test mới, gồm cả câu nhiều bước.
