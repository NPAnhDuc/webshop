# Kiểm tra capability trước advisory planner

Snapshot admin_conversation.py/capabilities.py ở baseline_code và harness check_guard.py được tạo, chạy trước khi sửa runtime. Cùng 20 câu, intentionally incorrect planner luôn chọn data_quality: trước 9/20, sau 20/20. Không có model call trong harness; đây là kiểm logic, không phải độ chính xác tiếng Việt tổng quát.

capability_guard.py nhận một số hành động rõ ràng: xử lý file/dòng dữ liệu, xếp hạng hoặc tách doanh số theo SKU. AdminConversation kiểm quyền trước guard; guard trả capability registered unsupported, deferred/executed=false, không gọi tool thay thế, không thay kỳ tài chính đã xác nhận. Có dấu vết state_resolution/admin_plan/capability_status. Không triển khai importer hoặc ranking thật.

Phủ định được kiểm qua các câu “không xóa hay sửa, chỉ kiểm tra”, “đừng clean hay thay đổi”, “không ghi đè nhưng làm sạch bản sao”. Đây là baseline lexical có phạm vi hẹp, chưa phải bộ hiểu phủ định/ý định tổng quát. Câu không khớp vẫn qua semantic planner; cần đánh giá thêm câu diễn đạt mới trước khi dùng rộng.

409 kiểm thử mã đạt trong 153,87 giây; log AI/runtime/tests-capability-guard-r1.log. Lượt targeted đầu: 56 đạt, 3 lỗi setup do quyền thư mục pytest tạm cũ; chạy toàn bộ bằng basetemp mới trong workspace và tắt cache đã đạt. Không thay quyền hệ thống.

Một model batch duy nhất cùng106 câu/gold r6 tại ../agent_quality_20261024_r7. Review ngữ nghĩa riêng103/106 so93/106; 10fail cũ sửa, 95answer không đổi, Q11 vốn đúng chỉ đổi lời deferred. Còn Q29/Q30/Q41; không promote app mặc định. Xem REPORT.md của r7 cho phân biệt checks/ngữ nghĩa và giới hạn.
