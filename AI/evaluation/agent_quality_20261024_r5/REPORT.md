# Registry/documents + baseline hội thoại22turn — r5 chưa nghiệm thu

Một batch model106lượt: cùng84câu r4 +22turn/6hội thoại từ conversation_cases_r2 đã đóng băng trước sửa. Nhánh documents gọi documents.answer đã đăng ký, hiện disabled/executed=false, không có nguồn/tri thức được sinh. Gold Q12/Q18 chỉ cập nhật tool kỳ vọng tương ứng, có parenthash/gold_changes; không sửa action/answer hoặc artifact cũ.

84câu cũ: checks19/24+57/60, ngữ nghĩa76/84, nội dung84answer không đổi so r4 sau chuẩn hóa đường dẫn artifact.22turn mới: checks15/22, review riêng15/22; chỉ2/6hội thoại hoàn tất đúng. Tổng91/106ngữ nghĩa, không so trực tiếp tỷ lệ91/106với76/84vì tập mở rộng. accepted_for_application=false.

7FAIL mới: Q27 mất thao tác so sánh khi đổi sang giá vốn; Q28 doanh thu từng mẫu→inspect; Q29/Q30 câu viết dính RAM/SSD chưa nhận nhóm/số lượng; Q37clean bản saoExcel→inspect; Q39ranking→inspect; Q41 chưa xử lý cảcatalog+tài liệu hoặc công bố đủ giới hạn. Q31 hỏi lại đúng khi không có2kết quả trước, chỉ đạt an toàn cục bộ, không coi workflow catalog đã thành công. Quality không biến kỳ dataset thành kỳ finance, giữ kỳ sau quality và role-change reset ở các control tương ứng đã đạt.

8FAIL cũ còn nguyên. Registry kiểm hành động được gọi đúng theo capability; không tự sửa classifier gọi sai capability. Không có ghi dữ liệu sai, không khởi động embedding/R19, không fine-tune hoặc đổi model/config/frontend/default app.

106trace identity/role/parentlinks verified; đổi role bắt đầu chain mới. Oracle số tài chính lấy từ SQL độc lập đã chốt, không dùng hàm tính bot. Checker mới cho phép public documents.answer nhưng vẫn cấm private tools với customer; xác minh docdisabled/khôngsource, không bỏ kiểm quyền để tăng điểm. Registry contract3/8→8/8, targeted50PASS17,90s/full362PASS121,95s.

Integrity input/runtime source/model config=true. Ghi nhận một sai sót thao tác: file helper check_results.py được copy vào output khi runner chưa đóng hẳn; helper không được runner đọc hoặc nằm trong input, chưa thực thi khi model chạy. Không có input/runtime code thay; chỉ chỉnh/chạy helper sau runner exit0 và integritytrue. Không chạy batch thứ hai để thay kết quả.

Median106turn0,8515s/max26,734s không suy SLA. Metadata/trace/raw/checks và human_review giữ riêng. Bước tiếp theo state/guard deterministic, chưa cào dataRAG hoặc làm DS để né hồi quy. Documents hiện mới đăng ký, chưa nối truy xuất thật. DevCompose/Excel/DA/DS/Kev vẫn theo PLAN và gate đã ghi.
