# Patch4 — thử giới hạn lịch sử sản phẩm, đã loại

21/10/2026. Một thử nghiệm giữa các round: khi sản phẩm đã xác định, chỉ đưa câu hỏi trước và chủ đề đã xác nhận vào router/selector; không đưa câu trả lời cũ do bot sinh. Profile/giao diện vẫn giữ nguyên lịch sử. Mục tiêu là tránh lặp sai thuộc tính theo lượt gần nhất. Không đổi prompt, nhãn trường, nguồn, gold, model hoặc config.

179 test qua (50.40s), gồm kiểm tra cả hai tầng vẫn nhận đúng sản phẩm/câu hỏi và không sửa history người dùng, kèm đối chứng admin. Log AI/runtime/tests-quality-patch4.log. Sau đó chạy duy nhất candidate_v4_targeted với 89 ID giống patch2, đầy đủ tiền tố hội thoại, chỉ development. 121 validation chưa mở. Hai round đều integrity unchanged=true.

| Kiểm tra tự động | Patch2 | Patch4 thử nghiệm |
|---|---:|---:|
| PASS_CHECKS | 77 | 74 |
| FAIL_CHECKS | 5 | 8 |
| NEEDS_REVIEW | 7 | 7 |

**Không áp dụng patch4. Đã phục hồi mã và test về đúng bản patch2; mọi hash mã đang dùng khớp candidate_v2_targeted.** Bản mã/test thử lưu ở candidate_v4_targeted/source_snapshot/. Giữ raw và decision.json, không sửa gold/đáp án để nâng điểm. 179 test thuộc bản thử bị loại; mã đang dùng vẫn có 177 test qua ở patch2.

Đã đọc lại: Q0301 sửa được (vật liệu hông Corsair 4000D), nhưng Q0300 và Q0446 lại hỏi model dù có ngữ cảnh; Q0373 thiếu bố trí bộ RAM Kingston; Q0478 trả hướng dẫn Photoshop thay vì bố trí RAM G.Skill. Bốn suy giảm không chấp nhận được. Q0396 vẫn thiếu loại case, không được gọi là sửa xong.

45 review trong tập chọn: 32 câu trả lời và trích dẫn giống hệt patch2, kế thừa có ghi rõ; 13 câu thay đổi đã đọc lại. 37 PASS/8 FAIL; không ngoại suy thành độ chính xác toàn 479. PASS_CHECKS và review ngữ nghĩa tách riêng, vẫn ghi nhận nội dung thừa (ví dụ SSD trong câu RAM).

Khách hàng (66 lượt): PASS_CHECKS 58→55, FAIL_CHECKS 2→5, NEEDS_REVIEW 6→6. Admin (23 lượt): 19/3/1 không đổi. Ngân hàng có chủ đích, không phải mẫu thực tế đại diện.

## Theo chủ đề — kiểm tra nguồn/action, không là điểm nghĩa

| Chủ đề | Lượt | Patch2 PASS/FAIL/REVIEW | Patch4 PASS/FAIL/REVIEW |
|---|---:|---:|---:|
| admin_boundary | 3 | 2/1/0 | 2/1/0 |
| missing_period | 2 | 2/0/0 | 2/0/0 |
| monthly_single | 2 | 2/0/0 | 2/0/0 |
| multi_period | 3 | 3/0/0 | 3/0/0 |
| quarter_target | 2 | 2/0/0 | 2/0/0 |
| clarification | 2 | 2/0/0 | 2/0/0 |
| handoff | 2 | 2/0/0 | 2/0/0 |
| live_boundary | 2 | 2/0/0 | 2/0/0 |
| missing_shop_terms | 4 | 0/0/4 | 0/0/4 |
| permission | 4 | 4/0/0 | 4/0/0 |
| product_single | 15 | 15/0/0 | 15/0/0 |
| unknown_product | 5 | 5/0/0 | 5/0/0 |
| monthly_multi | 4 | 2/2/0 | 2/2/0 |
| technology_reasoning | 2 | 0/0/2 | 0/0/2 |
| business_reasoning | 1 | 0/0/1 | 0/0/1 |
| month_target | 6 | 6/0/0 | 6/0/0 |
| product_context | 15 | 14/1/0 | 11/4/0 |
| product_multi | 15 | 14/1/0 | 14/1/0 |

## Thời gian và bước tiếp

Median 4.750s→4.297s, tổng 511.889s→402.702s; warmup/cache chưa cân bằng. Không đánh đổi độ đúng lấy tốc độ, không kết luận tăng tốc của bản đang dùng từ thử nghiệm bị loại.

Loại bỏ câu trả lời cũ quá rộng làm mất tín hiệu hữu ích cho router, trong khi vẫn không giúp chọn đúng thuộc tính. Bước sau cần ngữ cảnh có cấu trúc và/hoặc tách yêu cầu con khỏi lời dẫn, không chỉ thêm nhãn hay xóa lịch sử. Có thể chọn lỗi tài chính Q0267/Q0352 để sửa việc biến phần dẫn báo cáo thành một câu hỏi con và bỏ sót chỉ tiêu; nguồn đã có đủ, không phải thiếu data. Chỉ một sửa có căn cứ và một batch cần thiết mỗi lần thức. Sau chốt mã cần đầy đủ 479 development, 100 hồi quy bằng round mới, rồi mới 121 validation.
