# Trạng thái tiếp tục — 21/10/2026, patch5 full479 xong; đang hồi quy100

## Việc phải kiểm tra trước

Đọc LOOP_PLAN.md và kiểm CẢ run_quality_loop.py LẪN run_quality_regression.py của workspace. Nếu bất kỳ batch còn chạy: không sửa code/data/model/config, không mở batch khác và giữ im lặng nếu trạng thái không đổi. Batch đang chạy là run_quality_regression.py --round old100_patch5_retry1; stdout AI/runtime/quality-old100-patch5-retry1.out.log, stderr quality-old100-patch5-retry1.err.log. PID launcher lúc mở12048; child có thể khác. Cùng khóa runner.lock/GPU với vòng600. Hồi quy ghi results.json sau mỗi câu, integrity.json khi xong; không có progress.json.

## Bản đang thử

Patch5 dựa trên mã patch2, chỉ sửa question_parts: với cú pháp liệt kê rõ, bỏ phần dẫn nguồn và lời yêu cầu liệt kê khỏi các ý cần trả lời. Câu hỏi gốc và confirmed_periods vẫn nguyên vẹn trong payload. Không thêm tên SKU, chỉ tiêu/đáp án chuẩn hoặc ID benchmark vào mã. Không đổi lịch sử sản phẩm, prompt, source labels, model, data hay gold.

Đối chiếu hàm trước/sau chỉ trên development: 27 câu monthly_multi đổi cách tách; các chủ đề khác không đổi (patch5_impact.json). Lỗi quan sát Q0267/Q0352 trước đó có một P giả là Từ báo cáo..., khiến chọn nhầm giá vốn/bỏ số đơn hoặc chi phí dù nguồn đã đủ. Chưa kết luận sửa được cho đến khi đọc câu trả lời thật.

181 test passed trong49.23s, log AI/runtime/tests-quality-patch5.log. Snapshot trước sửa: patch5_before_code/grounded_rag.py và test_grounded_rag.py. Đã chạy đúng một bước sửa và mở đúng một batch toàn479 development trong lần thức08:57UTC. Không mở121 validation, không chạy100 hồi quy trong cùng lần này.

## Lịch sử cần giữ đúng

- Ngân hàng600 lượt (300 khách/300 admin),545 lời văn khác nhau,454 nhóm;479 development/121 validation. Bank/gold và nguồn chốt hash. Chưa mở validation. SQL là mô phỏng, không số thật/chính sách thật được tự xác nhận.
- baseline_80:57 PASS_CHECKS/10 FAIL_CHECKS/13 NEEDS_REVIEW. candidate_v1 full479 hoàn tất, integrity unchanged=true:413/13/53. Trên cùng80 baseline:66/1/13. Không gọi PASS_CHECKS là đúng ngữ nghĩa.
- candidate_v1 có91 review có chủ đích (toàn66 ca cần xem +9 lỗi cũ đã sửa +15 mẫu theo topic +1 đối chứng):56PASS/35FAIL, không ngoại suy.
- Patch2 sửa ngữ cảnh sản phẩm/giữ thuộc tính,177 test đã qua. candidate_v2_targeted89 lượt:77/5/7 so v1 cùng89 là69/13/7.9 lỗi sửa,1 mớiQ0396;4 lỗi cũQ0055/Q0267/Q0301/Q0352.45 review40PASS/5FAIL trong tập chọn. Chưa nghiệm thu toàn bộ.
- Patch3 thử nhãn loại/thể tích:89 lượt vẫn77/5/7, sửaQ0396 nhưng làm hỏngQ0473; đã loại, phục hồi patch2. Patch4 thử xóa câu trả lời cũ khỏi payload sản phẩm:74/8/7, sửaQ0301 nhưng hỏngQ0300/Q0373/Q0446/Q0478; đã loại, phục hồi patch2. Không thử lại nguyên hai giả thuyết. Giữ snapshot/decision/raw tại từng round, chi tiết PATCH3_REPORT.md/PATCH4_REPORT.md.179 test của mỗi bản thử không phải kết quả mã active patch2.
- Mốc v7 85/100 là lịch sử. Chưa full100 trên mã cuối; C03/C06/A15/A39 và C31 thiếu giới hạn số luồng chưa chứng minh sửa xong. Runner adversarial100 cũ đóng cứng baselineOUT/metadata, không chạy đè; cần round mới.

## Khi candidate_v5_development xong

1. Kiểm integrity, lỗi hạ tầng và đủ479; không nhầm batch bị dừng là xong. Mã/config/hash đổi thì tên round mới, không ghi đè kết quả cũ.
2. So toàn479 với candidate_v1 (đó là cả tác động patch2+patch5). Riêng89ID đã có patch2 so trực tiếp v2/v5 để tách patch5; không lấy điểm cả479 v1 so89 v5. So27 câu đổi question_parts với v1; đọc lại Q0267/Q0352, ca chuyển xấu và mẫu PASS_CHECKS.
3. Chấm ngữ nghĩa tách PASS_CHECKS; có thể kế thừa review nếu câu trả lời kèm trích dẫn nguyên vẹn và ghi rõ phương pháp. Không dùng validation để sửa; không nạp câu bot vào tri thức.
4. Cập nhật PATCH5_REPORT.md/CURRENT.md/STATUS.json/REPORT.md. report_quality_status.py hiện chỉ biết tới patch4; sau batch mới thêm hỗ trợv5, tránh chạy nó làm mất trạng tháiv5 đã ghi tay khi batch đang chạy.
5. Nếu suy giảm thì đọc nguyên nhân và có thể loại/khôi phục snapshot; không âm thầm sửa tiếp trong cùng batch. Nếu bản tốt hơn, vẫn cần full100 hồi quy và chấm các câu thiếu ý trước nghiệm thu/validation. Mỗi lần thức tối đa một sửa/một batch cần thiết.

## Giới hạn

Không subagents/deploy/fine-tune/Colab/API trả phí/nhắn người khác. Chỉ thông báo cải thiện đo được, suy giảm nghiêm trọng/lỗi chặn hoặc cần xác nhận dữ liệu thật. Queue tách interactive/evaluation/unattributed, unknown không phải khách thật. Tri thức mới chỉ nguồn chính thức, revision mới; xem KNOWLEDGE_GAPS.md, không chế chính sách/số shop.

## Lần thức10:01UTC — đã audit v5, đang hồi quy100

- candidate_v5_development đủ479, integrity unchanged=true. So v1 cùng479:413/13/53 →422/4/53 (PASS_CHECKS/FAIL_CHECKS/NEEDS_REVIEW),11 lỗi sửa và2 suy giảm kết hợp Q0191/Q0396. So RIÊNG89 có patch2:77/5/7 →79/3/7; Q0267/Q0352 trả đủ đúng số, không suy giảm kiểm tra trong89.27 câu đổi cách tách đều PASS_CHECKS. Không gọi đó là độ đúng ngữ nghĩa.
- Đã chấm112 ca có chủ đích:86PASS/26FAIL;100 kế thừa câu và trích dẫn nguyên vẹn,12 đọc lại. Đã xem hết57 ca gắn cờ/semantic. Q0191 mới trả CPU model thay số nhân; Q0396 vẫn thiếu loại case. Q0330 có giới hạn SKU nhưng thiếu khả năng hai khe DDR5 nên FAIL nội dung. Q0130 trả đúng giới hạn chưa tính thuế nên PASS. Xem human_review.json, comparison.json và PATCH5_REPORT.md.
- Quyết định: giữ patch5 để hồi quy, chưa nghiệm thu.181 test của bot qua từ lượt trước, không sửa bot trong lần này. Đã thêm runner hạ tầng run_quality_regression.py để chạy bộ100 cũ vào thư mục mới, sao nguyên bank/gold, chốt hash nguồn/mã, cùng khóa với qualityloop, dừng3 lỗi hạ tầng liên tiếp. --help đã kiểm tra. Không chạy đè baseline/v7. Đồng hồ bộ100 giữ20/10/2026 như bản cũ để so cùng điều kiện.
- Đã mở duy nhất một batch old100_patch5_retry1, chưa mở121 validation. Khi còn chạy không sửa mã của runner/base/bot/model/data/config hoặc mở batch khác. Nếu chưa có integrity mà process dừng: đọc stderr/rows, không coi là hoàn tất.
- Khi100 xong: chấm theo rubric và so với final_v7 trên cùng100 ID, ưu tiên C03/C06/C44/A39/A15/C31 nhưng phải xem cả các câu khác. Không lấy85/100 v7 làm điểm của bản mới; không tự nâng điểm vì nguồn/quote checks qua. Viết báo cáo CURRENT/REPORT/STATUS; sau đó chọn một nguyên nhân chung từ các lỗi nghĩa (26 trong tập chọn) nếu còn cần sửa trước chốt development. Không dùng validation để sửa ban đầu.
- report_quality_status.py đã hỗ trợ comparison.json v5; chưa có phầnold100, nên đọc trực tiếp thư mục old100_patch5_retry1 khi tiếp tục. Không đổi raw/gold hoặc nguồn cũ. Người dùng đã được báo cải thiện đo được từ479 và hai câu financialmulti, không báo độ chính xác toàn bộ.

- Lưu ý hạ tầng hồi quy: lần mở old100_patch5 dừng ngay preflight,0 câu model, do wrapper so hash byte CRLF với hash văn bản LF của runner cũ. Không phải bank bị sửa. Đã giữ nguyên thư mục/log thất bại, sửa wrapper lưu/kiểm cả raw-byte và normalized hash, dùng round mới old100_patch5_retry1. --preflight-only đã qua trước khi chạy thật. Chỉ một batch thực hỏi model được mở trong lần thức này. Round retry dùng code mới đóng băng, không sửa khi chạy.
