# Patch3 — thử nhãn thuộc tính, không áp dụng

21/10/2026. Thử bổ sung ba nhãn schema cho loại sản phẩm, thể tích ngoài và chuẩn thiết kế, tránh các bằng chứng đều mang ID chung product. Không thay nguồn, SQL, gold, model hoặc đáp án kiểm thử. Bản mã thử và hai test bổ sung được lưu tại candidate_v3_targeted/source_snapshot/.

179 kiểm thử mã qua (AI/runtime/tests-quality-patch3.log). Sau đó chỉ chạy một batch 89 lượt development, cùng ID và lịch sử với patch2. Cả hai round integrity unchanged=true. Không chạy thêm batch, không mở validation.

| Kiểm tra tự động | Patch2 | Patch3 thử nghiệm |
|---|---:|---:|
| PASS_CHECKS | 77 | 77 |
| FAIL_CHECKS | 5 | 5 |
| NEEDS_REVIEW | 7 | 7 |

Chấm lại cho thấy Q0396 đã trả đủ loại ATX Mid Tower và thể tích 48.6L, nhưng Q0473 lại mất loại Mini ITX Desktop của Deepcool CH160, chỉ trả vật liệu hông/thể tích. Vậy đổi nhãn chỉ chuyển lỗi sang câu khác, chưa khắc phục nguyên nhân chọn đủ ý. Không coi unit test hoặc PASS_CHECKS là độ chính xác ngữ nghĩa.

45 ca đã có review: 42 câu trả lời kèm trích dẫn giống hệt patch2 nên kế thừa đánh giá và ghi rõ phương pháp; 3 câu thay đổi được đọc lại (Q0126 PASS có nhiễu, Q0396 PASS có nhiễu, Q0473 FAIL). Kết quả tập chọn vẫn 40 PASS/5 FAIL, không phải mẫu ngẫu nhiên hay điểm chung.

Median 4.750s → 4.516s, tổng 511.889s → 424.736s. Không kiểm soát warmup/cache nên không kết luận tăng tốc nhờ thay nhãn.

**Quyết định: không áp dụng patch3; đã phục hồi mã về đúng từng hash của candidate_v2_targeted.** Hai test riêng cho nhãn thử cũng được lưu cùng snapshot rồi gỡ khỏi bộ đang dùng. Không xóa/sửa raw kết quả hay tiêu chí. Kiểm tra mã đang dùng vẫn là 173 core +4 AppTest đã qua ở patch2; 179 là kết quả cho bản thử bị loại.

Bước tiếp theo: cần xử lý việc câu nhắc lại thuộc tính bị lấy theo trường ở lượt gần nhất, và tách yêu cầu thực khỏi lời dẫn/nhắc lại. Chọn một sửa tổng quát có unit phản chứng và kiểm lại cùng ca/đối chứng; không thêm đáp án, tên SKU hoặc ID vào quy tắc. Q0301 là router hỏi lại trước truy xuất dù profile đã giữ đúng Corsair; không phải thiếu dữ liệu. Sau ổn định cần toàn 479 development và 100 hồi quy, sau đó mới validation.
