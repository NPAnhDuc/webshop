# Patch2 — nhớ đúng sản phẩm, giữ đúng thuộc tính

Ngày 21/10/2026. Candidate thử nghiệm, chưa nghiệm thu. Chỉ dùng development; 121 validation chưa mở. Không thay SQL, tài liệu, model hoặc gold để làm đẹp điểm.

## Đối chiếu cùng 89 lượt có đủ lịch sử hội thoại

| Kiểm tra tự động | candidate_v1 | candidate_v2_targeted |
|---|---:|---:|
| PASS_CHECKS | 69 | 77 |
| FAIL_CHECKS | 13 | 5 |
| NEEDS_REVIEW | 7 | 7 |

Chọn lỗi đã quan sát và đối chứng, không phải mẫu ngẫu nhiên. Đây không phải tỷ lệ chính xác ngữ nghĩa toàn 479/600. Cả hai vòng đều giữ nguyên bank/gold/nguồn trong suốt batch, integrity unchanged=true. 89 lượt gồm 23 admin và 66 khách, lịch sử cùng nhóm được giữ đầy đủ; không đưa đáp án chuẩn vào bot.

Đã đọc lại và xác nhận **9 lỗi được sửa**: Q0125, Q0164, Q0210, Q0247, Q0300, Q0373, Q0411, Q0446, Q0467. Các câu hỏi bộ RAM đã trả số thanh và dung lượng mỗi thanh; VRAM giữ đúng GPU; độ trễ đầu tiên không bị thay bằng CAS; một số câu vật liệu hông đã nối đúng case trước đó. Còn câu tham khảo thừa, không coi phần này đã hoàn hảo.

**1 suy giảm đã xác nhận: Q0396.** V1 trả đủ loại ATX Mid Tower và thể tích 48.6L của Corsair 4000D Airflow; patch2 trả thể tích nhưng thay loại bằng vật liệu hông. Giữ nguyên raw, đánh FAIL, chưa nghiệm thu patch2. Không sửa tiếp trong lần thức này.

**4 lỗi cũ còn nguyên:** Q0055 định tuyến yêu cầu UPDATE thành ngoài phạm vi (không có ghi SQL); Q0267 thiếu số đơn hàng; Q0301 hỏi lại sản phẩm dù có hội thoại; Q0352 thiếu chi phí vận hành. Hai câu số liệu có thông tin trong nguồn, không phải thiếu dữ liệu; cần cải thiện tách yêu cầu con/chọn đủ đoạn.

Đã chấm riêng 45 câu patch2: 40 PASS, 5 FAIL, gồm cả 7 câu ngữ nghĩa và các ca lỗi/đối chứng đã đọc. Đây là tập chọn có chủ đích, không lấy 40/45 làm độ chính xác chung. Xem candidate_v2_targeted/human_review.json. Với v1, đã đọc 91 câu: toàn bộ 66 câu FAIL_CHECKS/NEEDS_REVIEW, 9 lỗi cũ đã sửa, 15 mẫu PASS_CHECKS theo chủ đề và đối chứng hồi quy Q0396. 56 PASS/35 FAIL trong tập chọn, không ngoại suy.

## Mã và kiểm thử

Một bước sửa nguyên nhân chung: tách chủ đề sản phẩm khỏi tiêu đề bài tham khảo, bảo toàn thuộc tính câu hỏi gốc, truyền sản phẩm đã xác định cho tầng chọn chứng cứ và bổ sung nhãn trường từ schema. Không hardcode ID hoặc đáp án câu kiểm thử. Bản trước sửa tại patch2_before_code/. Runner thêm --ids-file để chọn ca và tự lấy đủ lịch sử; từ chối ID ngoài split.

173 kiểm thử lõi passed (44.62s), 4 AppTest passed (13.74s). Logs: AI/runtime/tests-quality-patch2-b.log và tests-quality-patch2-ui.log. Unit tests không thay thế việc chấm câu trả lời thật.

Trên cùng 89 lượt: median 4.859s → 4.750s, nhưng tổng thời gian 419.317s → 511.889s. Có lượt đầu 40.469s và một số câu nhiều thuộc tính chậm hơn; chưa có thí nghiệm cache/warmup cân bằng, **chưa kết luận tốc độ được cải thiện**.

## Bước tiếp theo

Ưu tiên sửa việc chọn đủ thuộc tính và suy giảm Q0396 ở lượt sau; xem cả nguyên nhân hỏi lại Q0301. Chỉ chọn một sửa có căn cứ và một batch cần thiết. Sau ổn định phải chạy đầy đủ development bằng round mới và hồi quy 100 cũ; sau đó mới mở 121 validation. Không lấy mốc lịch sử v7 85/100 làm kết quả của mã hiện tại.
