# Tiếp tục — 21/10/2026, patch5 đã chốt để đo; validation121 đang chạy

## Trước mọi thao tác

Đọc LOOP_PLAN.md và kiểm CẢ run_quality_loop.py/run_quality_regression.py của workspace. Bất kỳ batch còn chạy: không sửa code/data/model/config/runner, không mở batch khác; giữ im lặng khi tiến độ không đổi.

Batch hiện tại: run_quality_loop.py --round validation_v1 --split validation; PID launcher22876, child có thể khác. stdout AI/runtime/quality-validation-v1.out.log; stderr quality-validation-v1.err.log. progress/results ở validation_v1/, integrity.json chỉ có khi hoàn tất. Đây là batch duy nhất lần thức11:56UTC. Không chỉnh lỗi giữa lượt.

## Validation đã mở — không còn là bộ kín cho vòng sửa tiếp

Đã đóng băng patch5 tại DEVELOPMENT_FREEZE_PATCH5.json TRƯỚC khi mở validation lần đầu. Chưa dùng câu/đáp án validation để chọn hoặc sửa patch5. Đóng băng là chốt ứng viên để ĐO, không nghiệm thu: vẫn biết lỗi trên development/bộ100. Mã active khớp từng hash candidate_v5_development; không đổi nguồn/gold/SQL/model/config.

Kể từ lúc chạy validation_v1, coi121 câu là đã mở cho đánh giá. Khi batch xong: chấm và báo cáo trung thực, không sửa bank/gold để nâng điểm. Nếu tiếp tục sửa mã sau khi xem validation, phải đánh dấu bộ này đã mở và tạo nhóm holdout MỚI cho lần xác minh mới, không gọi lại121 cũ là kiểm tra mù. Cùng kho nguồn nên validation cũng không phải đánh giá của người độc lập.

## Kết quả nền đã chốt

- Ngân hàng600 lượt,545 lời văn/454 nhóm;479development/121validation. Giữ bank/gold và kết quả cũ, source hash không đổi. Dữ liệu shop mô phỏng; không tự chế chính sách thật, không fine-tune trong các vòng này.
- v1 full479:413 PASS_CHECKS/13 FAIL_CHECKS/53 NEEDS_REVIEW. Patch5 full479:422/4/53, integrity=true. So v1 có11 lỗi sửa và2 suy giảm Q0191/Q0396 (tác động kết hợp patch2+5). Riêng89 cópatch2:77/5/7→79/3/7; sửa số đơn/chi phí Q0267/Q0352, không suy giảm trong89.27 câu đổi cách tách liệt kê qua kiểm tra hẹp.181 test patch5 qua49.23s. PASS_CHECKS không là điểm nghĩa.
- V5 review112 ca chọn:86PASS/26FAIL;100 kế thừa câu/trích dẫn nguyên vẹn,12 đọc lại. Đã xem hết57 ca gắn cờ/semantic. Không ngoại suy tỷ lệ đúng toàn479.
- Hồi quy old100_patch5_retry1:87/100 theo cùng rubric v7(85/100), khách47/admin40. SửaC06/C44, không có hồi quy từPASS.87 câu/trích dẫn giống hệt được kế thừa,13 thay đổi đọc lại.213 quotechecks,0 integrityissues. Median4.93s,tổng541.55s; chưa thí nghiệm tốc độ cân bằng cache.
-13 FAIL cũ: C03,C29,C35,A15,A20,A23,A29,A30,A35,A39,A40,A44,A50. Thiếu giới hạnSKU/nângRAM, đối chiếu phiên bản, phân biệt kế hoạch/thực tế, MOQ và giới hạn nhân quả/phạm vi. Không nâng điểm bằng cảnh báo chung.

## Lần thức11:56UTC — audit và loại patch6, không thêm sửa mới

- old100_patch6 đủ100/integrity=true. Chấm72 câu/trích dẫn giống hệt theo kế thừa,28 đọc lại:76/100, khách39/admin37, so patch5 là87. Không sửa được caFAIL;11 hồi quy C19/C21/C23/C24/C27/C28/C30/C33/A11/A34/A37. Có lỗi sai SKU/kỳ nghiêm trọng dù0quote/quyềnissues. Chi tiết PATCH6_REPORT.md và old100_patch6/review.json/summary.json/decision.json.
- Đã loại patch6, lưu source_snapshot/retrieval.py và test_retrieval_candidates.py, phục hồi retrieval.py từ patch6_before_code, bỏ test riêng bản thử khỏi bộ active. Tất cả hash mã khớp v5;181 test active vẫn là bộ đã qua,182 là của bản bị loại. Không thay nguồn/gold/model. Không tiếp tục mở rộng admission BM25 kiểu blanket vì recall tăng nhưng mất precision.
- Không sửa bot mới trong lần thức này. Chọn chốt patch5 để đo121 validation, một batch đang chạy. Người dùng được báo suy giảm bản thử và đã phục hồi trước khi mở validation.

## Khi validation_v1 hoàn tất

1. Kiểm đủ121, integrity, lỗi hạ tầng. Nếu process chết thiếuintegrity đọcstderr/rows và ghi chưa hoàn tất; không gắn lỗi worker thành thiếu dữ liệu.
2. Chấm NGỮ NGHĨA tất cả121 theo rubric/nguồn và ngữ cảnh hội thoại. Không dùng PASS_CHECKS làm PASS nghĩa; FAIL_CHECKS cũng kiểm nguồn tương đương. Chú ý phần thiếu, saiSKU/kỳ, quyền, phiên bản và câu bịa; các mẫu tài chính lặp không đại diện mọi tư vấn. Không sửa code/gold khi đang chấm bộ này.
3. Báo riêng development479 và validation121, theo khách/admin/chủ đề/nhóm, source/action checks vs semantic, thời gian/cache. Không trộn87/100 cũ thành điểm600. Ghi giới hạn chính sách shop còn thiếu và dữ liệu mô phỏng. Cập nhật CURRENT/REPORT/STATUS và báo cáo tổng600 đúng phạm vi.
4. Sau khi chấm xong mới chọn sửa từ lỗi có căn cứ. Nếu dùng kết quả validation để sửa thì thừa nhận đã mở, phát hành nhóm câu xác minh mới. Không tuyên bố hoàn hảo/nghiệm thu nếu lỗi còn rõ. Không tự học câu bot sai.
5. Mỗi lần thức tối đa một sửa và một batch cần thiết. report_quality_status.py hiện biết v5/old100_patch5, chưa có kết quả patch6/validation; không chạy làm mất phần ghi tay khi batch còn chạy. Sau batch mới thêm hỗ trợreporter.

## Giới hạn

Không subagents/deploy/finetune/Colab/API trả phí/nhắn người khác. Chỉ thông báo cải thiện đo được/suy giảm nghiêm trọng/lỗi chặn/cần xác nhận data thật, im lặng khi đang chạy hoặc không đổi. Queue interactive/evaluation/unattributed tách riêng; unknown không là khách thật. Tri thức mới phải nguồn chính thức/revision mới. KNOWLEDGE_GAPS.md chờ điều khoản thật, không bịa.

Runner hồi quy100 dùng round mới, giữ clock20/10 như bộ cũ, kiểm raw-byte và normalized LF hash. old100_patch5 đầu lỗiCRLF/LF ởpreflight0câu model, retry1 là kết quả hợp lệ. Qualityloop validation dùng clock21/10 như bank600. Hai runner cùngkhóa runner.lock, không chạy chồngGPU.
