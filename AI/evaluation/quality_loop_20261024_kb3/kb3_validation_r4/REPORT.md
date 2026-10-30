# Sửa 4 câu validation còn sai bằng quy tắc tổng quát — 26/10/2026

**Lưu ý:** các quy tắc dưới đây được thiết kế sau khi đọc 4 câu sai của validation 121, nên từ lượt này **validation không còn là holdout độc lập**. Muốn đo thật cần bộ câu hỏi mới giữ riêng.

## Kết quả

| | kb3_validation_r1 | kb3_validation_r4 |
|---|---:|---:|
| Validation 121 (đọc tay) | 117/121 | **120/121** |
| Khách hàng | 51/52 | 52/52 |
| Admin | 66/69 | 68/69 |
| 479 development: số câu trả lời đổi so với lượt đầy đủ gần nhất (`kb3_period_binding_full_r1` + `kb3_unsupported_write_r1`) | — | **0** (`kb3_valrules_r3`) |

Validation đổi đúng 4 câu, 117 câu còn lại giống hệt r1 (giữ nhãn). Không câu PASS nào thành FAIL.

- Q0124 → PASS: khách hỏi doanh thu shop → từ chối theo quyền.
- Q0223 → PASS: "Không còn hạn: C-BTS áp dụng từ 2026-08-01 đến 2026-08-31; so với ngày tham chiếu 2026-10-21 là đã hết hạn", kèm đúng dòng C-BTS (trước trích nhầm C-TET).
- Q0266 → PASS: nêu cả bản v1 (laptop 5%) và v2 từ 2026-04-01 (laptop 6%).
- Q0274 → vẫn FAIL: không còn hỏi lại, nhưng trích định nghĩa giá vốn trong từ điển dữ liệu thay vì câu "Không trừ toàn bộ tiền nhập hàng vào lợi nhuận" (sales-plan). Lỗi ở khâu chọn đoạn; không thêm quy tắc riêng cho câu này để tránh học thuộc bộ validation.

## Quy tắc (shopbot/)

1. `grounded_rag.py`: người mua hỏi lãi gộp hoặc doanh thu/doanh số/chi phí vận hành **của shop/cửa hàng** → từ chối (câu "chi phí vận hành laptop" không bị chặn).
2. "kỳ/tháng/quý này" trong câu hỏi quy tắc ("… có đúng không", "được không", "có nên") không bắt hỏi lại; câu hỏi số liệu "kỳ này" và "kỳ đó" vẫn hỏi lại. Câu quy tắc mà router chỉ định tuyến vào báo cáo tháng → mở sang tài liệu quy định/kế hoạch.
3. Câu nêu hai bản ("bản quy định tháng 3 và bản từ tháng 4", "phiên bản") → cho truy xuất bản đã hết hiệu lực (admin).
4. `identifier_binding.py` (mới): mã gõ nguyên văn (C-BTS) là khóa chính xác — bỏ dòng bảng của mã khác, giữ dòng đúng mã (chèn thêm nếu bị cắt khỏi ngân sách ứng viên, không đổi thứ tự ứng viên khác); câu "còn hạn/hết hạn/còn hiệu lực" so ngày bắt đầu/kết thúc của dòng với ngày tham chiếu (hoặc hôm nay) bằng code, không để model đoán. Việc ràng mã không tự coi phần câu hỏi là đã trả lời.
5. `rag_scope.py`: đọc được ngày viết dính "hôm nay21/10/2026".

Hai phiên bản trung gian bị loại sau khi chạy: đẩy dòng có mã lên đầu danh sách làm hỏng Q0232; xóa "chưa có nguồn" khi ràng mã làm kém Q0038. Bản cuối không còn hai tác dụng phụ này.

## Kiểm thử

`tests/test_validation_rules.py` (20 test, có cách diễn đạt khác của từng quy tắc); toàn bộ 799 unit test PASS. Chấm do Claude đọc, chưa có người duyệt độc lập.
