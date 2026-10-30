# Patch8 — phân biệt đọc tài liệu với thực hiện công cụ

Sửa một nguyên nhân ở prompt router: chọn action theo việc người hỏi yêu cầu, phân biệt đọc số đã ghi với tạo kết quả tính toán, đọc quy định với thay đổi dữ liệu. Với yêu cầu vừa đối chiếu quy định vừa xin thực hiện, giữ phần đọc và không thực hiện. Không thêm regex theo câu/ID, không đổi selector, nguồn, gold, SQL, model hoặc trọng số. Snapshot patch7 tại ../patch8_before_code/.

Cùng24development với context_r3_candidate1: **17→18PASS nghĩa,6FAIL**, chỉ sửaR2D15(yêu cầu cập nhật giá nay deferred thay vì trả chính sách giảm giá).0PASS→FAIL trong24;khách7/8,admin11/16. Các23answer/action/source còn lại giống bản trước. Đã đọc đủ24;Codex tự đánh giá theo cùngrubric, không độc lập. Checks riêng16/3/5→17PASS_CHECKS/2FAIL_CHECKS/5NEEDS_REVIEW. Không có hành động cập nhật giá thực hiện, không coi từ chối đúng là tính năng sửa giá đã có.

R2D16(cộng doanh thu từng dòng đơn) vẫn trả Đơn bán xuất FIFO,FAIL. R2D10(máy vừa nói chưa có đối tượng) và4câu nguyên tắc/phạm vi vẫnFAIL. Không vá thêm trong lượt này.14trích đoạn có trong đúng nguồn/phiên bản chốt,0quoteissues/0private-sourceleaks. Có trích dẫn không đảm bảo đúng ý.

Batch24/integrityunchanged=true,giữclock21/10/2026dù máy đã sang22/10. Tổng92.404s,trung vị2.4765s so98.467/2.7965củapatch7;cache/warmup không cân bằng, không tuyên bố tăng tốc.24reserved chưa hỏi,121validationcũ đã mở;không điểm nghĩa toàn600.

Fullsuite lần đầu186PASS/1FAIL ở test xóa tài liệu: delete dùng ngày thực22/10nhưng retrieval as_of21/10nên tombstone nằm sau ngày đọc. Đã xác định lỗi đồng hồ fixture, không quy cho prompt hay sửa logic sản phẩm. Sau khi batch kết thúc, test được khóa knowledge.local_today=TODAYcùng ngàyas_of,giữ nguyênassertionxóa. Fullsuite kiểm lại tại AI/runtime/tests-context-r3-p8-final.log. Bản trước của test được giữ trongsnapshot.

Lỗi quy trình lần này: batch model đã được khởi chạy sau suite chưa xanh, trước khi chốt nguyên nhân test. Không nghiệm thu dựa vào lượt đó; kết quả raw vẫn giữ và không đổi mã bot khi batch chạy. Cần kiểm tra exit code của pytest trước mọi lệnh start batch lần sau. Fixture được sửa và kiểm lại riêng sau khi batch dừng; không sửa nguồn/gold để nâng điểm.

Quyết định: giữpatch8candidate để hồi quy100, chưa production-accepted.187test không chứng minh prompt hiểu ngôn ngữ đúng; cần hồi quy model thật, đặc biệtA20(đọc lead time/MOQ)vàA44(vừa xin hành động vừa đối chiếu quy định).87/100đã đo thuộcpatch7,không gán chopatch8. Chưa chạy lại479trênpatch8/chưa mở24reserved. Lượt này1sửa prompt+1batch24; không chạy batch thứ hai.

Cập nhật18:01UTC: bảnpatch8đãbịloạisauhồiquy100.88PASSso87nhưnglàmhỏngA36,mấtchủđềA35vàmâuthuẫnhơnởA34. Đãphụchồibotđúnghashpatch7,giữtestclockfixture,187testqua.18/24thuộcbảnthửđãloại;active17/24và87/100. Xem../../quality_loop_20261021/old100_patch8/REPORT.md vàdecision.json.
