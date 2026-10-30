# Tiếp tục — 21/10/2026, đang thử patch6; hồi quy100 đang chạy

## Kiểm tra trước mọi thao tác

Đọc LOOP_PLAN.md. Kiểm CẢ run_quality_loop.py VÀ run_quality_regression.py trong workspace. Nếu bất kỳ batch còn chạy: không sửa code/data/model/config/runner hoặc mở batch khác; giữ im lặng khi tiến độ không đổi.

Batch hiện tại: run_quality_regression.py --round old100_patch6, PID launcher1752 (child có thể khác). stdout AI/runtime/quality-old100-patch6.out.log; stderr quality-old100-patch6.err.log. Dùng cùng runner.lock/GPU với qualityloop. Xem old100_patch6/results.json (ghi từng câu) và integrity.json (chỉ có khi hoàn tất), không có progress.json. Preflight đã qua trước khi chạy thật. Đây là batch duy nhất trong lần thức11:00UTC.

## Sửa đang thử — một bước có căn cứ

Patch6 sửa bộ nhận ứng viên retrieval: BM25 đã tham gia RRF nhưng trước đó ứng viên vẫn bị loại nếu TF-IDF<=0.08 và dense<=0.45, dù BM25 có khớp. Nay giữ thêm top_k ứng viên BM25 điểm dương trước khi fusion; không thay score/nguồn/gold, không bỏ phân quyền/hiệu lực/duyệt tài liệu. Không thêm từ khóa tên shop/SKU/ID hoặc đáp án vào mã.

Đã tái hiện câu đối chiếu chính sách giá v1/v2: trước sửa chỉ có customer-policy; sau sửa có thêm pricing-policy v1/v2 đúng nguồn. Đây mới là cải thiện tìm nguồn, chưa là cải thiện câu trả lời.182 test qua46.48s (AI/runtime/tests-quality-patch6.log), gồm test điểm dense/TF-IDF thấp nhưng có khớp mã BM25, không nhận tài liệu nháp hoặc rò nguồn admin cho khách.

Bản trước sửa: patch6_before_code/retrieval.py. Test mới: AI/tests/test_retrieval_candidates.py. Nếu loại patch6, giữ snapshot mã/test thử rồi phục hồi retrieval.py; test riêng cho ứng viên thử phải lưu cùng artifact, không để test của bản bị loại làm bộ active lỗi. Không sửa/rollback trong khi batch còn chạy.

## Đã chốt kết quả trước patch6

- Bank600 (545 lời văn,454 nhóm):479development/121validation. Bank/gold và SQL/manifest vẫn chốt hash; chưa mở validation. Dữ liệu shop mô phỏng. Không finetune hoặc thêm tri thức mới trong các round này.
- candidate_v1 full479:413 PASS_CHECKS /13 FAIL_CHECKS /53 NEEDS_REVIEW. candidate_v5_development full479:422/4/53, integrity unchanged=true. Đây là kiểm tra nguồn/action, không là điểm ngữ nghĩa. So v1 có11 lỗi sửa và2 suy giảm Q0191/Q0396; riêng89 đã có patch2 chỉ sửa2 lỗi tài chính Q0267/Q0352, không suy giảm trong89.27 câu đổi cách tách liệt kê đều qua kiểm tra hẹp.181 test bot patch5 đã qua.
- Review v5 có112 ca chọn:86PASS/26FAIL (100 kế thừa câu và trích dẫn nguyên vẹn,12 đọc lại), đã xem hết57 ca gắn cờ/semantic. Không ngoại suy thành độ chính xác toàn479. Xem PATCH5_REPORT.md và candidate_v5_development/comparison.json, human_review.json.
- old100_patch5_retry1 hoàn tất100 và integrity=true. Chấm cùng rubric v7:87/100, khách47/50,admin40/50; v7 là85/100. SửaC06/C44, không có PASS→FAIL.87 câu/trích dẫn giống hệt nên kế thừa review,13 câu thay đổi đọc lại.213 quotechecks,0integrityissues. Median4.93s,tổng541.55s; không cân bằng warmup/cache. Chi tiết old100_patch5_retry1/review.json,summary.json,REPORT.md. Đây là bộ phát triển đã thấy, không phải validation/độ chính xác thực tế.
- 13FAIL trên100 patch5: C03,C29,C35,A15,A20,A23,A29,A30,A35,A39,A40,A44,A50. C03 vẫn chưa nêu rõ giới hạn nâng RAM SKU, A29/A30 sai phạm vi phiên bản, A40 thiếu phân biệt mục tiêu/thực tế bằng số, A39/A50 thiếu giới hạn nhân quả/phạm vi số liệu. Không nâng điểm vì có câu cảnh báo chung hoặc trích nguồn.
- Patch3 (nhãn loại/thể tích) và patch4 (xóa rộng câu trả lời cũ khỏi context) đều đã loại và phục hồi; không thử lại nguyên giả thuyết. Snapshot/decision/raw và PATCH3_REPORT/PATCH4_REPORT giữ nguyên. Patch5 đang là fallback đã kiểm toàn development/hồi quy100, chưa nghiệm thu.

## Khi old100_patch6 xong

1. Kiểm đủ100, integrity và stderr; process chết mà chưa integrity không là hoàn tất. Không có3 lỗi hạ tầng liên tiếp mới tiếp tục chấm. Không coi model unavailable là thiếu kiến thức.
2. So trực tiếp patch6 với **87/100 patch5**, không chỉ v7 85. Kế thừa review chỉ khi câu trả lời và trích dẫn nguyên vẹn, ghi rõ phương pháp; đọc thay đổi và nguồn. Ưu tiên A29/A30 nhưng phải kiểm các hồi quy khác, cả khách/admin. Không dùng nguồn tìm được làm PASS ngữ nghĩa.
3. Nếu tốt hơn, vẫn cần full479 trên patch6 trước chốt; nếu không tốt hơn/suy giảm thì cân nhắc loại và phục hồi snapshot sau batch. Mỗi lần tối đa một sửa và một batch cần thiết; không sửa tiếp trong cùng round. Chưa mở121validation.
4. Viết PATCH6_REPORT/CURRENT/STATUS/REPORT và thêm hỗ trợreporter sau khi batch dừng. report_quality_status.py đã biết v5 và old100_patch5; chưa biết patch6 nên không chạy làm mất phần patch6 đang ghi tay khi batch còn chạy.
5. Sau chốt development mới mở121 validation một lần. Không dùng validation để sửa trước; nếu sửa sau validation thì phải ghi bộ đó đã mở và tạo nhóm mới để xác minh.

## Giới hạn và hạ tầng

Không subagents/deploy/fine-tune/Colab/API trả phí/nhắn người khác. Chỉ báo cải thiện đo được/suy giảm nghiêm trọng/lỗi chặn/cần dữ liệu thật; im lặng khi đang chạy hoặc không đổi. Queue interactive/evaluation/unattributed tách riêng, unknown không coi khách thật; không tự học câu bot. Tri thức mới chỉ nguồn chính thức và revision mới; KNOWLEDGE_GAPS.md vẫn cần chính sách thật từ shop.

Runner hồi quy mới sao nguyên bank/gold vào round mới, giữ clock20/10 như bộ100 cũ, kiểm cả raw-byte và normalized legacy hash. old100_patch5 đầu tiên lỗi CRLF/LF ởpreflight,0câu model, artifact/log lỗi được giữ; retry1 hoàn tất là kết quả hợp lệ. Không chạy đè runner baseline OUT. Khi resume phải giữ mã/config/hash, đổi mã dùng tên round mới.
