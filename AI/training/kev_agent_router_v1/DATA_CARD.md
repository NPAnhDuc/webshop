# Nhãn khởi đầu cho router Kev

Revision v1, ngày 23/10/2026. Chưa huấn luyện, chưa xuất checkpoint.

`seed_labels.jsonl` chứa 36 câu do người phát triển soạn và nhãn ý định đã đọc kiểm tra. Đây là dữ liệu đã lộ trong quá trình sửa hệ thống, chỉ được dùng làm hạt giống development/train; không được báo cáo điểm trên nó như validation/test độc lập. Không có câu trả lời bot hoặc số tiền/doanh thu dùng làm target huấn luyện.

Nhãn là bước định tuyến: search, compare, documents, admin, handoff, outside. Câu so sánh thiếu tên vẫn mang nhãn compare; bước giải đối tượng sẽ hỏi lại. Khách tự xưng quản lý vẫn mang ý định admin; server phải từ chối quyền, model không được cấp quyền. Chưa có ví dụ đạt yêu cầu cho lớp clarify độc lập.

36 mẫu chưa đủ để train và đánh giá router cho shop: handoff/outside chỉ có một ví dụ mỗi lớp, thiếu hội thoại khó, lỗi chính tả và các cách diễn đạt mới. Cần mở rộng dữ liệu có nhãn được kiểm tra, cân bằng mức cần thiết, gom paraphrase và hội thoại vào cùng nhóm, rồi tạo holdout độc lập trước khi train. Không chia ngẫu nhiên các lượt trong cùng hội thoại. Không dùng 479/121 bank RAG lịch sử hoặc kết quả bot sai làm nhãn tự học.

`server_role` chỉ là ngữ cảnh để học cách phân luồng, không phải quyền do model quyết định. `prior_user_questions` giữ câu hỏi trước trong cùng nhóm; chưa phải dataset hoàn chỉnh của stateful router. Khi dựng bộ train chính thức cần cung cấp schema bộ nhớ server và kiểm tra nhãn trên schema đó.

Luồng tiếp theo: nhãn đủ và kiểm tra → baseline Kev chưa train → fine-tune Colab → đánh giá holdout/calibration/chi phí lỗi → tải checkpoint về local → chạy kiểm thử công cụ và phân quyền trước khi thay router. Lưu checkpoint và manifest; không dựa vào việc phiên Colab tồn tại lâu dài. Bản này chưa có notebook train sẵn sàng và chưa khởi chạy Colab.
