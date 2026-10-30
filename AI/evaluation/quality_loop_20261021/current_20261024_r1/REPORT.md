# Hồi quy 479 basic_rag trên code 24/10 — giống hệt patch9

Chạy `scripts/run_quality_loop.py --round current_20261024_r1 --split development` (CHATBOT_MODE=basic_rag, RAG_PIPELINE=grounded, worker 8011 đang chạy), dữ liệu/bank/gold kiểm hash như các vòng trước. Code gồm mọi thay đổi chế độ agent ngày 24/10 (mixed split, product_facts, định tuyến người mua, GroundedDocuments) và `engine.py` đã khác bản nghiệm thu patch9 (trace agent).

**Kết quả:** 479/479 câu có câu trả lời, basic_action và tập chunk nguồn **giống hệt** `candidate_v9_development` (so bằng `compare_479.py`, chuẩn hóa khoảng trắng). Kế thừa review patch9: **450 PASS / 29 FAIL**, không câu nào cần review lại. Checks tự động: 422 PASS_CHECKS, 53 NEEDS_REVIEW, 4 FAIL_CHECKS — cùng phân bố do cùng đầu ra.

## Về 6 câu trích lệch chủ đề (bộ 300 người mua)

Không cài cổng kiểm tra liên quan câu hỏi–bằng chứng. Đo offline trên kết quả patch9 đã review (không gọi model):

| Cổng | Bắt câu lệch (6) | Ý patch9 PASS bị rơi |
|---|---:|---:|
| Tỷ lệ từ nội dung của ý có trong bằng chứng < 0,2 | 5 | 79 |
| Thuật ngữ viết tắt/có số phải có mặt (bất kỳ) | 3 | 35 |
| Thuật ngữ viết tắt/có số phải có mặt (tất cả) | 4 | 52 |

Ý bị rơi chủ yếu là câu CPU ("Còn số nhân CPU…", "… có CPU như thế nào") vì nguồn ghi "Core i5…/bộ xử lý"; thêm từ đồng nghĩa là vá theo câu, cùng kiểu đã làm patch10–17 bị loại. Vì vậy không chạy 479 cho một cổng đã biết gây hồi quy.

Hướng đúng là bổ sung tài liệu nguồn chính thức cho đúng khoảng trống (GPU tích hợp/rời, VRAM vs RAM, 80 PLUS, SSD gần đầy, CPU cùng tên khác thế hệ, thứ tự ưu tiên tài liệu bảo hành), theo `KNOWLEDGE_GAPS.md`: chỉ thêm khi có nguồn chính thức, không tạo cặp hỏi đáp từ câu trả lời sai của bot. Chưa thực hiện.
