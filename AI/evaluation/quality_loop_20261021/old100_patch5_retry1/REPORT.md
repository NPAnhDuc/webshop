# Hồi quy100 trên patch5

100/100 câu cũ hoàn tất, integrity unchanged=true. Bank/gold cùng byte với bản v7. Chấm ngữ nghĩa theo cùng rubric: **87 PASS/13 FAIL**, khách47/50, admin40/50; so v7 85/100, sửa C06 và C44, không có PASS→FAIL.87 câu trả lời kèm trích dẫn giống hệt v7 nên kế thừa đánh giá có ghi rõ;13 câu thay đổi được đọc lại. Đây là bộ kiểm thử đã dùng để phát triển, không phải điểm validation hoặc độ chính xác thực tế.

13 FAIL còn lại: C29, C35, A15, A20, A23, A35, A39, A44, C03, A29, A30, A40, A50. C03 có cảnh báo nâng cấp nhưng chưa nêu rõ giới hạn RAM tối đa SKU chưa xác nhận; không nâng điểm vì có nguồn chung. A29/A30 chưa xử lý phiên bản/hiệu lực; A40 chưa phân biệt mục tiêu và thực tế bằng số cụ thể. Vẫn có nhiều câu thừa/lặp dù được PASS phần nội dung chính.

213 quote checks,0 integrity issues được runner ghi nhận. Kiểm tra nguồn tách khỏi chấm nghĩa. Median 4.930s, tổng 541.550s; v7 median5.38s,tổng555.95s. Warmup/cache không cân bằng, không quy chênh lệch tốc độ thành tác dụng riêng patch5.

Đồng hồ giữ20/10/2026 để so cùng điều kiện với bộ cũ. Mã hiện tại đã có full479 development riêng;121 validation chưa mở. Dữ liệu shop vẫn mô phỏng. Lần preflight ban đầu lỗi chuẩn hóa newline đã dừng trước câu đầu và giữ riêng artifact, không tính là lượt hỏi model.
