# Patch5 — đã kiểm toàn 479 development

21/10/2026. Sửa một nguyên nhân: không biến phần dẫn nguồn và lời liệt kê thành một yêu cầu con giả. Giữ đầy đủ câu hỏi gốc/phạm vi kỳ trong payload; không thêm đáp án/ID/SKU vào bot. Nguồn/gold/SQL/model/config không đổi.181 test phần mềm qua49.23s, log AI/runtime/tests-quality-patch5.log. Batch479 hoàn tất, integrity unchanged=true.

Toàn479 cùng ID: trước {'PASS_CHECKS': 413, 'NEEDS_REVIEW': 53, 'FAIL_CHECKS': 13}, sau {'PASS_CHECKS': 422, 'NEEDS_REVIEW': 53, 'FAIL_CHECKS': 4}.11 lỗi kiểm tra được sửa,2 suy giảm Q0191/Q0396 so v1 (tác động kết hợp patch2+5). Riêng89 đã có patch2: {'PASS_CHECKS': 77, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 5} → {'PASS_CHECKS': 79, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 3}; Q0267/Q0352 sửa được, không có chuyển PASS_CHECKS→FAIL_CHECKS trong89. Còn4 lỗi Q0055/Q0191/Q0301/Q0396. Không gọi các số này là độ đúng ngữ nghĩa.181 test mã qua; chưa nghiệm thu, chưa mở121 validation. [Chi tiết](PATCH5_REPORT.md).

Đã đọc lại: báo cáo1/2026 trả đủ126 đơn và4 sản phẩm hoàn trả; báo cáo10/2025 trả đủ108627410 chi phí vận hành và36078590 lãi hoạt động. Không còn trả giá vốn không được hỏi hoặc báo thiếu phần dẫn giả. Cả27 câu development đổi cách tách đều PASS_CHECKS; chưa dùng điều đó làm PASS ngữ nghĩa toàn bộ.

Chấm112 câu có chủ đích:86 PASS/26 FAIL.100 review được kế thừa vì câu trả lời kèm trích dẫn giống nguyên văn v1 hoặcv2;12 câu được đọc/chấm lại. Bao gồm toàn57 FAIL_CHECKS/NEEDS_REVIEW và các mẫu/đối chứng đã đọc. Đây không là mẫu ngẫu nhiên; không báo86/112 thành độ chính xác chung. Vẫn lỗi giải thích sai phạm vi/thiếu giới hạn SKU và nội dung thừa, kể cả khi có nguồn. Review tại candidate_v5_development/human_review.json.

Q0191 hỏi số nhân Dell Latitude nhưng chỉ trả tên CPU; Q0396 thiếu loại case. Hai lỗi thuộc so sánh kết hợp từ v1, chưa có full479 patch2 để quy nguyên nhân riêng. Trên89 có v2 thì patch5 chỉ sửa hai lỗi tài chính. Giữ bản này để chạy hồi quy, chưa nghiệm thu hoặc validation.

## Theo vai trò — kiểm tra nguồn/action

| Vai trò | Lượt | V1 PASS/FAIL/REVIEW | V5 PASS/FAIL/REVIEW |
|---|---:|---:|---:|
| customer | 248 | 202/10/36 | 209/3/36 |
| admin | 231 | 211/3/17 | 213/1/17 |

## Theo chủ đề — kiểm tra nguồn/action

| Chủ đề | Lượt | V1 PASS/FAIL/REVIEW | V5 PASS/FAIL/REVIEW |
|---|---:|---:|---:|
| admin_boundary | 3 | 2/1/0 | 2/1/0 |
| business_reasoning | 17 | 0/0/17 | 0/0/17 |
| missing_period | 4 | 4/0/0 | 4/0/0 |
| monthly_single | 66 | 66/0/0 | 66/0/0 |
| multi_period | 102 | 102/0/0 | 102/0/0 |
| quarter_target | 3 | 3/0/0 | 3/0/0 |
| clarification | 6 | 6/0/0 | 6/0/0 |
| handoff | 4 | 4/0/0 | 4/0/0 |
| live_boundary | 8 | 8/0/0 | 8/0/0 |
| missing_shop_terms | 8 | 0/0/8 | 0/0/8 |
| permission | 9 | 9/0/0 | 9/0/0 |
| product_single | 56 | 56/0/0 | 56/0/0 |
| technology_reasoning | 28 | 0/0/28 | 0/0/28 |
| unknown_product | 17 | 17/0/0 | 17/0/0 |
| monthly_multi | 27 | 25/2/0 | 27/0/0 |
| month_target | 9 | 9/0/0 | 9/0/0 |
| product_context | 56 | 48/8/0 | 54/2/0 |
| product_multi | 56 | 54/2/0 | 55/1/0 |

Median toàn479: 4.719s → 4.469s; tổng 2357.347s → 2336.088s. Không cân bằng warmup/cache, không kết luận cải thiện tốc độ do patch5.

Bước hiện tại: chạy bộ100 cũ trong round mới old100_patch5_retry1, không ghi đè baseline/v7. Giữ đồng hồ20/10 như bộ cũ để so cùng điều kiện; dữ liệu vẫn mô phỏng. Chỉ một batch trong lần thức này, không sửa bot thêm. Chưa mở121 validation.
