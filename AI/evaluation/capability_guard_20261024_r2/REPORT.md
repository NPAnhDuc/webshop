# Phạm vi đề cập hành động — r2

Trước khi mở rộng bộ buyer, kiểm thêm nguy cơ guard r7 chặn nhầm câu hỏi kiến thức/trạng thái. Chụp baseline_code, đóng băng20 câu tại check_scope.py và chạy before.json trước sửa:9/20. Sau một bước sửa cùng20 câu20/20; không có model call trong phép đo này.

Phân biệt câu định nghĩa (“chuẩn hóa dữ liệu là gì?”), hướng dẫn và trạng thái đã hoàn tất (“đã làm sạch chưa?”) với lệnh thực hiện. Scope được giới hạn theo mệnh đề: “giải thích ... rồi xóa dữ liệu” vẫn phải báo unsupported cho phần xóa; giải thích không làm mất lệnh thật ở phía sau.20ca cũ r1 vẫn20/20 (artifact after_scope_r2.json bổ sung riêng trong folder r1, không sửa file before/after cũ).

Đây vẫn là guard lexical có phạm vi hẹp, không phải giải pháp NLU tổng quát. Guard trảNone chỉ nghĩa là không can thiệp advisory planner; không chứng minh model sau đó trả lời đúng câu định nghĩa/audit.20scopeprobes mới chưa được model-evaluate end-to-end. Không tính chúng vào accuracy106 hoặc dữ liệu RAG/train.

131targeted tests đạt13,36s, gồm admin, catalog, state, capability, planner và scope; logtests-capability-scope-r2b.log. Lần chọn test ban đầu sai tên file trace nên khôngcollecttest, đã sửa selection rồi chạy thành công. Không rerun full409DEtests vì không đụng DE/source/reader; r7full409 vẫn là kết quả riêng cũ.

Một modelbatch cùng106bank/goldr7 ở ../agent_quality_20261024_r8: integritytrue,103/106semantic không đổi,106answer/toolargs nguyên. Check24/24+60/60+19/22, fullsessions4/6. Chưa cải thiện3fail Q29/Q30/Q41, chưa triển khai mixed hoặc typo. Không promote/defaultconfig/frontend/model/training/worker thay đổi.
