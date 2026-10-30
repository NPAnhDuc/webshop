# Context revision3 — baseline đã có, bot chưa sửa

24development có12PASS/12FAIL ngữ nghĩa trên mã patch5, cùng24outputs được hỏi ởr2. Kết quả tự động theo fixture đã sửa:11PASS_CHECKS/8FAIL_CHECKS/5NEEDS_REVIEW. Đây là bộ chẩn đoán tập trung, không so tỷ lệ với validation121 hay coi là chất lượng bot giảm.

R2 có4 cờFAIL giả vì extractor lấy cả đoạn thay vì chỉ giá trị được hỏi. Giữ nguyên toàn bộ bank/gold/results r2. Revision3 sửa tất cả8span numeric từ nguồn gốc, gồm các span reserved, theo cùng quy tắc độc lập với output. Không đổi câu hỏi/split/source/model/mã bot. Regrade lại24outputs đã có, không gọi thêm model, mọi thời gian vẫn của lượt chạy cũ. Provenance và correction manifest được giữ.12PASS/12FAIL ngữ nghĩa không thay đổi.

7lỗi liên quan guard kỳ hiện tại chặn trước phân giải lịch/giới hạn công cụ,1lỗi máy chưa có tham chiếu bị trả thuật ngữ chung,4lỗi nguyên tắc/phạm vi kinh doanh. Dữ liệu thêm không sửa được các lỗi này; không nạp đáp án bot vào knowledge.

24reserved chưa được hỏi model, không dùng kết quả để sửa ban đầu. Cùng nguồn/ý liên quan vàCodex soạn, không độc lập. Bước sau: một sửa tổng quát có unit phản chứng và một batch so cùng24development; hồi quy trước khi chốt/mởreserved. Bot active vẫnpatch5, không có cải thiện mới được tuyên bố.

Cập nhật sau baseline: patch7 sửa guard thời gian,24development12→17PASS vàhồi quy100giữ87PASS. Patch8 thay promptđịnh tuyến,17→18PASS trêncùng24,6FAIL còn lại,0PASS→FAILtrong24.187testqua. Chưa hồi quy100chopatch8/chưa nghiệmthu/chưa mở24reserved. Xem context_r3_candidate2/REPORT.md vàCURRENT.md đểtiếp tục;điểm/chúthíchbotchưađổiởtrênlàmốcbaseline.

Cập nhật18:01UTC: patch8bịloạisauhồiquy100doA36hồiquyvàA35mấtchủđềchiếndịch,dùtổng87→88PASS. Mãactivephụchồiđúnghashpatch7:17/24developmentvà87/100hồiquy,187testqua.18/24và88/100thuộcbảnđãloại.24reservedvẫnchưahỏi. Xemquality_loop_20261021/old100_patch8/REPORT.md vàCURRENT.md trước hànhđộngtiếp.

Cập nhật19:02UTC: patch9 candidate dựa trênpatch7 kiểm ràng buộc tham chiếu sản phẩm trước chọn bằng chứng. Cùng24development:17→18PASS nghĩa,6FAIL,sửaD10,0PASS→FAIL;khách8/8,admin10/16.193testqua. Không áp dụngpatch8đãloại. Chưa hồi quy100 trênpatch9/chưa nghiệmthu/chưa mở24reserved. Xemcontext_r3_candidate3/REPORT.md vàCURRENT.md.
