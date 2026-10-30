# Patch9: chấm nghĩa đủ479,450PASS/29FAIL

Batch `candidate_v9_development` đã hoàn tất479/479, integrity unchanged=true, không còn runner. Cùng IDs, nguồn/gold/model và đồng hồ21/10/2026 với `candidate_v5_development`. Không chạy lại validation121 đã mở hoặc24reserved revision3.

Kiểm tra tự động giữ nguyên **422PASS_CHECKS/4FAIL_CHECKS/53NEEDS_REVIEW**, không có ID đổi trạng thái so patch5. 112ca đã có review đều có answer/action/source objects giống hệt nên kế thừa, có provenance.15ca thay source objects được đọc cả trước/sau; đều đủ số liệu đúng hai kỳ và đúng nguồn, không có lỗi mới được xác nhận.914trích đoạn có trong nguồn/phiên bản đã chốt,0quoteissues/0private-sourceleaks. Các kiểm tra này không thay chấm nghĩa.

Lượt đọc đầu có75ca mới:60ca trước đây chưa chấm (cohort_01) và15ca output thay đổi, cả75đạt nội dung chính. Lượt cohort_02đọc thêm90ca:87PASS/3FAIL. Ba lỗi chọn claim phụ từ laptop/chuột/CPU-GPU sai đối tượng dù trường chính đúng, đều PASS_CHECKS. Chúng có sẵn ởpatch5, không phải hồi quy mới. [Phát hiện và giả thuyết nguyên nhân](COHORT_02_FINDINGS.md). Có thông số/cảnh báo thừa ở các câu khác, ghi secondary issue; không gọi là hoàn hảo. Trạng thái nghĩa được Codex chọn sau đọc câu hỏi, đáp án, lịch sử và nguồn, không suy từ checks; không có người duyệt độc lập.

**Coverage đã đủ479/479**:112kế thừa +367đọc mới. Cohort03có110PASS,cohort04có92PASS sau đọc câu/đáp án/lịch sử/nguồn,khôngtựsuytừchecks. Theo rubric nội dung chính: **450PASS/29FAIL**, khách231/248,admin219/231;330/358nhóm hội thoại đạt mọi lượt.53câu có secondary issue. Một số câu đúng ý chính vẫn dài dòng hoặc thêm mẫu thiết bị khác được nêu rõ tên; không gọi là đáp án hoàn hảo. Ba claim phụ sai đối tượng ởcohort02vẫnFAIL. Toàn văn review và provenance nằmtronghuman_review.json/cohort snapshots.

Đây là **điểm development**, không phải độ đúng khách thật hoặc kiểm tra độc lập. Có102câu so hai kỳ và66câu đọc một chỉ tiêu tháng; nhóm lập luận kinh doanh chỉ6/17, giải thích công nghệ19/28. Không gộp450/479củapatch9với112/121validationcủapatch5thành điểm600cho một mã. Tăng coverage không phải bot tự học tốt hơn; dữ liệu shop vẫn mô phỏng.

Tổng2264.654giây, trung vị4.422giây so2336.088/4.469ởpatch5. Cache/warmupkhôngkiểmsoát,khôngquychênhlệchchoriêngpatch9. Mã không đổi,193unit đã qua trước batch; lần đọc này không sửa bot/data/model/config, không chạy thêm model batch.

Giữ candidate để hoàn thành kiểm tra; chưa nghiệm thu. Hồi quy100trênpatch9giữ87PASS/13FAIL,24targeted18PASS/6FAIL. Không gán112/121validationcủapatch5chopatch9.24reserved vẫn chưa hỏi.

Audit đã xong và baseline được khóa tại `../patch10_before_code/BASELINE_PATCH9.json`,trước sửa tiếp. Ưu tiên một sửa nguyên nhân đã thấy ởtrace: phần dẫn nguồn bị tách thành P1ảo rồi lấp bằng bằng chứng không liên quan. Giữ toàn bộ câu gốc/kỳ/chủ đề, không xóa câu hỏi thật. Bản sửa cần test phản chứng và mộtbatchcùng479so baseline; không mởreserved. Raw/bank/gold/review cũ giữ nguyên.450/479thuộcpatch9,không gán cho candidate mới trước kiểm lại.
