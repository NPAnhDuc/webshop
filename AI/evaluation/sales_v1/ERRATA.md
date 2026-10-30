# Sửa đáp án kiểm tra phát triển

Các kết quả live_v1, live_v2, live_v3 được giữ nguyên, không ghi đè. Đây là tập phát triển đã được xem để sửa lỗi, không phải kiểm tra mù.

- live_v1 chưa có đáp án no_match cho ASUS dưới 20 triệu, RAM tối thiểu 16 GB. SQL danh mục mô phỏng cho thấy không có máy đủ cả giá, RAM và tồn. live_v3 sửa kỳ vọng này.
- live_v3 đánh fail trường hợp RAM 16 GB, tối đa 1,5 kg, dưới 25 triệu vì đòi phải có sản phẩm. Đối chiếu trực tiếp SQL cho thấy không có mẫu đủ tất cả điều kiện; từ live_v4 kỳ vọng no_match. Không thêm hay sửa sản phẩm để làm kiểm tra đạt.
- live_v4 kiểm tra cả điều kiện lưu trong hồ sơ, không chỉ sản phẩm trả về, để phát hiện việc làm yếu ngân sách khi chưa xuất hiện mẫu vượt giá.

Các mẫu nhẹ dưới 1,5 kg trong danh mục hiện chỉ có RAM 8 GB; chưa có bằng chứng nâng cấp RAM cho từng SKU. Không giả định có thể nâng lên 16 GB để lấp chỗ thiếu.
