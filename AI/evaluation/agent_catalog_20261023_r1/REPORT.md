# Structured catalog conversation r1: chưa đạt với model thật

Một batch12lượt/9hội thoại hoàn thành,integritytrue. Toàn214unit tests PASS51.41s gồm21tests công cụ/hội thoại với planner kiểm soát. Nhưng chấm tay action thật chỉ1/12đúng(S09),11FAIL. Đây là bank development mới do Codex soạn, không độc lập và không phải479RAGcũ.

Model đặt unsupported_filters=true ở cả12câu, kể cả lọc ngân sách đơn giản. S01/S02/S04/S12bịdefer; có lỗi continuation, số tiền mặc định vô căn cứ và routing handoff/outside. Không cótool_evidenceđược thực thi; guard ngăn trả danh sách không đáp ứng. S08không lộ tài chính nhưng handoff không thay cho từ chối đúng. Không coi thiếu câu trả lời là thiếu dữ liệu.

Không nghiệm thu lớp LLMplanner. Giữ code ở trạng thái opt-in prototype, không đổi mode/config hiện tại hoặc đấu vào frontend/backendauth. Default RAG và các công cụ đã kiểm tra giữ nguyên. Chưa train model; đây là inference/evaluation local. Không có batch thứ hai/sửa prompt sau khi xem kết quả trong lượt này.

Bước tiếp: chẩn đoán kích thước/payload và tách quyết định routing khỏi giải biến thể; cần giảm context dư bằng pipeline hai bước hoặc candidate retrieval, rồi test cùng câu và hồi quy. Không kết luận nguyên nhân là context truncation khi chưa capture token/finish metadata. Không bỏ guard để nâng tỷ lệ trả lời. Admin flow, RAG và permalink vẫn chưa nối.
