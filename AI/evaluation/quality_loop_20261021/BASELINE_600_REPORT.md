# Đánh giá patch5 — hoàn tất600 lượt hỏi

Đã chạy đủ479development và121validation trên cùng mã patch5 đã đóng băng trước khi mở validation. Integrity của cả hai vòng xác nhận mã/nguồn/bank giữ nguyên. Không fine-tune, thay model, thêm chính sách/số shop hoặc nạp câu trả lời bot vào tri thức.

| Tập | Lượt | PASS_CHECKS | FAIL_CHECKS | NEEDS_REVIEW | Chấm ngữ nghĩa |
|---|---:|---:|---:|---:|---|
| Development | 479 | 422 | 4 | 53 |112 ca chọn:86PASS/26FAIL; không đại diện cả479 |
| Validation lần đầu | 121 | 102 | 4 | 15 |Đọc đủ121:112PASS/9FAIL |
| Tổng kiểm tra tự động | 600 | 524 | 8 | 68 |Không có điểm ngữ nghĩa toàn600 |

PASS_CHECKS là kiểm tra nguồn/action hẹp, không đồng nghĩa trả đủ ý. Validation được Codex đọc/chấm từng câu với câu trả lời, nguồn, rubric và hội thoại; chưa có người duyệt độc lập. Điểm112/121 chỉ cho bộ này, không phải độ chính xác thực tế.

## Validation theo vai trò

| Vai trò | PASS | FAIL | Tổng |
|---|---:|---:|---:|
| Khách hàng |49|3|52|
| Admin |63|6|69|

96 nhóm hội thoại validation,87 nhóm đạt tất cả lượt. Nhiều câu là mẫu số liệu lặp:61/121 thuộc báo cáo/mục tiêu tài chính;33 lượt là thuộc tính sản phẩm. Vì vậy tổng điểm cao không chứng minh tư vấn bán hàng hoặc suy luận kinh doanh đã tốt.

## Validation theo chủ đề

| Chủ đề | PASS | FAIL | Tổng |
|---|---:|---:|---:|
| quarter_target | 1 | 0 | 1 |
| monthly_multi | 9 | 0 | 9 |
| month_target | 3 | 0 | 3 |
| admin_boundary | 0 | 1 | 1 |
| monthly_single | 18 | 0 | 18 |
| multi_period | 30 | 0 | 30 |
| clarification | 3 | 1 | 4 |
| handoff | 1 | 0 | 1 |
| technology_reasoning | 6 | 0 | 6 |
| business_reasoning | 2 | 5 | 7 |
| missing_shop_terms | 2 | 0 | 2 |
| product_single | 11 | 0 | 11 |
| unknown_product | 3 | 0 | 3 |
| live_boundary | 2 | 0 | 2 |
| permission | 0 | 1 | 1 |
| product_context | 11 | 0 | 11 |
| product_multi | 10 | 1 | 11 |

## Các lỗi còn chặn nghiệm thu

- Q0037: yêu cầu chạy dự báo bị hỏi lại đối tượng thay vì nói rõ giới hạn công cụ; không có dự báo được chạy.
- Q0078: câu máy vừa nói chưa có đối tượng nhưng bot trả chính sách chung, chưa hỏi rõ máy nào.
- Q0124: khách hỏi doanh thu shop, bot nói thiếu dữ liệu thay vì từ chối theo quyền; không có nguồn hay số liệu riêng rò rỉ.
- Q0158: đã nêu phân khúc nhưng lại báo thiếu phân khúc, còn câu kho/khuyến mãi thừa.
- Q0223: có ngày kết thúc nhưng chưa kết luận khuyến mãi đã hết hạn theo ngày hỏi.
- Q0232: chưa phân biệt rõ ngân sách một chiến dịch với cả năm.
- Q0266: chưa đối chiếu mức biên của hai phiên bản/thời gian hiệu lực.
- Q0274: câu nguyên tắc kế toán bị hỏi lại kỳ/model không cần thiết.
- Q0328: hỏi loại case và thể tích nhưng thay loại bằng vật liệu hông.

Nhóm business_reasoning chỉ2/7PASS; đây là điểm yếu cần ưu tiên, không che bằng hàng chục câu đọc báo cáo đúng số. Những câuPASS vẫn có nội dung lặp/thừa. Không gọi bot là Best Seller hoặc nghiệm thu chỉ dựa trên112/121.

## Nguồn, dữ liệu và tốc độ

227quotechecks trên validation,0quote thiếu trong nguồn được cấp và0nguồn admin xuất hiện ở vai khách. Đây không chứng minh đúng nghĩa hoặc không có thông tin thừa. Chưa có recall@k cấpđoạn được đo độc lập, nên không gọi các source checks là recall@k.

Validation median4.547s,tổng604.565s; development median4.469s,tổng2336.088s. Không có benchmark cân bằng cache/warmup để kết luận tăng tốc. Bộ100 cũ trên cùng patch5 đạt87/100; đó là tập phát triển đã thấy, không trộn vào validation.

Kho có dữ liệu kinh doanh mô phỏng, chưa phải doanh số/chính sách thật của cửa hàng. Bot từ chối đúng nhiều điều khoản còn thiếu; vẫn cần nguồn được chủ shop xác nhận để triển khai thực tế. Không lấy báo cáo chuỗi lớn thay số shop hoặc tự học câu trả lời sai.

## Trạng thái tiếp tục

Không sửa bot hoặc chạy thêm model trong lần audit này. Validation121 đã mở; mọi sửa tiếp phải thừa nhận điều đó. Muốn xác minh mới phải phát hành nhóm holdout mới, giữ nguyên bank/gold/kết quả hiện tại. 367 lượt development chưa được chấm ngữ nghĩa đầy đủ; không được gắn PASS chỉ từ kiểm tra tự động. Xem NEXT_REVISION_PLAN.md và CURRENT.md.
