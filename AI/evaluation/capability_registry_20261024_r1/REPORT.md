# Registry capability và nhánh tài liệu đăng ký sớm

Một bước triển khai: shopbot/capabilities.py làm danh sách hợp đồng tập trung cho8capabilities. Có role, required/optional args, nguồn, enabled/disabled/unsupported và thông báo rõ. AgentTools thực thi ACL/args trước availability; discovery trả bản copy theo role và readiness cấu hình server, không chạm DB/model. Thiếu importer/SQL ranking không được tự chạy công cụ khác khi gọi đúng tên capability đó.

documents.answer đã được đăng ký cho customer/admin và nhánh documents gọi nó thật, nhưng status=disabled/executed=false/sources=[]. Không sinh câu trả lời tri thức, không gọi RAG/embedding hoặc khởi động worker. file.transform và sales.rank đăng ký unsupported, chỉ admin; không ghi hoặc đọc file tùy ý. Không chứng nhận classifier đã biết chọn đúng capability: lỗi transform/ranking→inspect cũ vẫn còn.

8ca hợp đồng được viết và chạy trước sửa:3/8PASS. Sau sửa cùng bank8/8PASS.50test targetedPASS17,90s, full362testPASS121,95s, log runtime/tests-capability-registry-r1.log. Tests kiểm ACL trước status, args SQL/path/role, dữ liệu discovery không sửa registry, disabled không gọi retrieval, trace không ghi giả success. Baseline_code/manifest và before/after/cases giữ nguyên.

Một batch local106turn tại agent_quality_20261024_r5:84câu cũ và22turn trong6hội thoại đã đóng băng. Integrity các input/runtime code/config=true.84answer cũ nguyên nội dung,76/84đúng như r4, không tăng accuracy.22turn mới15đúng, nhưng chỉ2/6hội thoại đạt toàn bộ. Đây là baseline quan trọng cho bước state/guard, không coi15/22turn thành6workflow thành công. Không promote/default change.

Không sửa state hoặc semantic router trong lượt này. Bước tiếp: kỳ/metric/object/operation có keep/reset được kiểm bằng mã, xử lý missing comparison context và câu cả catalog+documents. Câu viết dính catalog cũng cần normalization literal có contract riêng. Không sửa prompt/cào RAG để che lỗi. Chưa nối retrieval hoặc devCompose trong lượt này.
