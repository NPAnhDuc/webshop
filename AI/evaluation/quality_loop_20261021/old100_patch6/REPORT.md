# Patch6 — đã loại sau hồi quy100

Bản thử admission BM25 tìm thêm được pricing-policy v1/v2, nhưng chất lượng trả lời giảm. Cùng100 câu/nguồn/rubric/clock với patch5: **76/100 so87/100**, khách39/50 so47/50, admin37/50 so40/50. Không có FAIL→PASS;11 PASS→FAIL: C19, C21, C23, C24, C27, C28, C30, C33, A11, A34, A37.

Chấm72 câu/trích dẫn nguyên vẹn bằng kế thừa review có ghi rõ;28 câu thay đổi đã đọc lại rubric/nguồn. Thiếu thông tin RAM Photoshop, dung lượng SSD, công suất PSU; trả chuột khác thayG305; lấy lịch2025/2026 thay báo cáo2027. Có nguồn không có nghĩa đúng câu hỏi. C15 vẫn được PASS vì nêuHz cao không bắt buộc, không tự tăng độ khó tiêu chí để làm xấu bản thử.

Integrity=true,0integrityissues về quote/quyền theo runner; những kiểm tra đó không bắt được các lỗi nghĩa trên. Median5.585s,tổng538.940s; không cân bằng warmup/cache, không dùng tốc độ để bù độ đúng.

**Đã loại patch6, phục hồi toàn bộ hash mã khớp candidate_v5_development.** Bản thử retrieval.py và test riêng được lưu old100_patch6/source_snapshot/; test riêng bị loại khỏi bộ active.182 test qua là của bản thử, patch5 active có181 test qua. Không xóa raw/đổi gold/nguồn/model. Quyết định tại old100_patch6/decision.json.

Thử nghiệm cho thấy mở rộng recall mà thiếu kiểm soát độ liên quan có thể làm xấu lựa chọn bằng chứng. Không tiếp tục thử biến thể trong cùng lần thức. Chốt patch5 cho lần đo validation đầu tiên (không nghiệm thu sản phẩm): DEVELOPMENT_FREEZE_PATCH5.json. Vẫn biết13 lỗi bộ100 và26 lỗi trong112 review development có chủ đích. Đang chạy validation_v1 với121 câu chưa dùng để chỉnh mã; sau mở phải ghi rõ bộ đó đã dùng, không gọi lại làm kiểm tra mù sau các sửa tiếp theo.
