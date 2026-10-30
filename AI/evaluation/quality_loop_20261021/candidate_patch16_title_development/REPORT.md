# Patch16 rejected: đúng bài nhưng tóm tắt vẫn thiếu ý

208unit PASS57.54s, một batch28quoted development hoàn thành/integritytrue. Đọc toàn28đápán và nguồn, chấm nghĩa riêng: **19→17PASS,4fix/6regressions**. Không nghiệm thu dù source focus tốt hơn và thời gian quan sát ngắn hơn.

Fix: KC3000 đủ tốc độ theo dung lượng/DRAM/điều kiện; IdeaPad đúng RAM và đối chiếuSKU; Photoshop đúng8GB/16GBvà yêu cầu khác;081SGđúng màn hình/pin/giới hạn vùng. Nguồn sai chủ đề của bốn ca này đã được xử lý.

Regress: Q0142 chỉ còn câu điều kiện chung, bỏ kết luận không đồng nhấtWiFi/Internet; Q0230 mất giới hạnFPS/điều kiện khi giải thích bài mua laptop; Q0257 mất giới hạnOLED; Q0309 bỏ đối chiếuSKU/giới hạnRAM; Q0323 thiếu thông tin hãngWirelessđể giải thích xung đột dữ liệu; Q0337 thiếu cơ chếECCtrongchipvà giới hạn ngoài chip. Q0316giữPASS: vẫn có SO-DIMM/RAMhànkhôngthayđược, dù checklistngắn hơn. Không gán FAIL chỉ vì câu ngắn.

Một phần lỗi cũ cải thiện nhưng chưa đủPASS: CPUcó giới hạnGHznhưng nguồn thiếu giải thích luồng; IPS/TN/VAthiếu mô tả sâu; CPU/GPUchưa đủ điều kiện tăng tốc; MSI408AUvàLegionchỉ chọn giới hạn, bỏ thông số chính. Không sửa goldđể nâng điểm.

Đã phục hồi26app/shopbot đúng hashpatch9; lưu candidate source/test trước khi xóa file test mới khỏi tests. Rollback unit suite ở AI/runtime/tests-quality-patch16-rollback.log. Dữ liệu/model/config/prompt/schema/parser giữ nguyên. Không chạy old100/full479trên candidate bị loại; không có batch thứ hai trong heartbeat.

Tổng118.268s,median3.0155s là thời gian của mẫu này; chưa có thử đối chứng cold/warmđồng nhất để nghiệm thu tăng tốc. Không lấy tốc độ đánh đổi thiếu ý. Production vẫn450/479và87/100được chấp nhận trước đó. Không mở reserved/validation hay thử lại r19.

Bước tiếp: trước khi viết candidate nữa, kiểm tra offline đơn vị bằng chứng cho bài ngắn. Các bài có cùng một đoạn nội dung bị tách thành nhiều câu, model chỉ chọn điều kiện hoặc lặp ý. Có thể thử giữ đoạn nghĩa nguyên vẹn cho yêu cầu tóm tắt một bài được định danh, thay vì chỉ nâng cap hoặc thêm judge. Cần kiểm tra ranh giới chunk/đoạn, ngân sách, citation/ACL và câu hỏi hỗn hợp; không tự sinh thêm kiến thức thiếu trong bài. Đây là đề xuất chưa triển khai, title-filter đơn lẻ vẫn bị loại.

Rollback verified:193unitPASS43.73s;26production hashes matchpatch9, no model runner. Other-title source rows0/28but semantic decline still rejects candidate.
