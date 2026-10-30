# Nối nhánh tài liệu RAG vào chế độ agent — r15/r16, bộ 300 r5/r6

## Worker 8011

Không có lỗi code: log 21/10 đã `ready`; worker chỉ không chạy (agent trước bị chặn lệnh khởi động). Đã khởi động lại `scripts/vietnamese_embedding_service.py` bằng `.venv-kev` (loopback 127.0.0.1:8011, `HF_HUB_OFFLINE=1`). Health: `dangvantuan/vietnamese-embedding` revision `4ab46e46…`, 768 chiều, max 256 token, adapter hiểu hội thoại có nạp. `start-local.ps1` vẫn tự khởi động worker khi chạy app. Worker hiện chạy như tiến trình nền của phiên làm việc; khởi động lại máy cần chạy lại `start-local.ps1`.

## Thay đổi

- `GroundedDocuments` (`agent_tools.py`): adapter gọi grounded RAG hiện có (lọc vai trò, trạng thái duyệt, phiên bản, ngày hiệu lực; cùng pipeline với `basic_rag` trên web). Không truyền bộ nhớ catalog vào truy xuất. Trạng thái: `answered` (đủ/một phần nguồn), `no_source`, hoặc hành động RAG (clarify/denied/deferred/handoff); worker/index lỗi → `unavailable`, `executed=false`, không trả lời từ trí nhớ.
- `AgentTools(documents=...)`: registry vẫn để `documents.answer` disabled theo mặc định; chỉ bật khi server cấu hình bộ trả lời. Kiểm tra quyền/tham số vẫn chạy trước.
- `agent_conversation.py`: nhánh documents dùng câu trả lời và nguồn thật; câu kết hợp ghép nguồn hai phần, `partial` chỉ khi phần tài liệu không đủ nguồn. Câu tham chiếu trơn ("Chỉ giải thích thuật ngữ thôi") lấy mệnh đề kiến thức từ câu hỏi trước của **người dùng** (không lấy văn bản bot); không có thì hỏi lại.
- Runner r15/r16, buyer r5/r6 ghi model/revision worker vào metadata và kiểm lại trước khi chạy.

## Kết quả

**Hồi quy 118 (r16):** 106 lượt chỉ đổi đúng 7 câu trước đây trả "nhánh tài liệu chưa kết nối" (Q12, Q18, Q40, Q42, B-S09, B-N17, B-N21); còn lại giống r8. Review 7 câu:
- Q18, Q40 (DDR5), Q42 (nối tiếp → DDR5, r15 trả nhầm OLED trước khi sửa): đúng, có nguồn.
- Q12 "Thông số RAM laptop là gì?": trả SO-DIMM/DDR — chấp nhận được cho câu mơ hồ.
- B-S09 đổi trả, B-N17 trả góp, B-N21 giao hàng: không bịa, nhưng chỉ nêu "chính sách demo/cần chủ shop duyệt"; B-N21 trích mục đổi trả/bảo hành cho câu giao hàng — thiếu tài liệu chính sách thật.

**Câu kết hợp (checker mới, docs phải chạy thật):** 11/12; phần tài liệu `answered` cả 11. Q56 "giải thích RAM là gì" trả đoạn DDR5 — đúng chủ đề rộng nhưng chưa định nghĩa RAM. Q58 vẫn sai route admin.

**Bộ 300 (r6):** thông số 134, tìm kiếm 40, so sánh 20, nhiều lượt 56 — không đổi. 37 lượt gọi tài liệu: answered 27, no_source 7, clarify/deferred/handoff 3; câu trả lời giống hệt r5. Review tay 30 câu kiến thức/chính sách:

| Kết quả | Câu |
|---|---:|
| Trả lời hữu ích, đúng chủ đề, có nguồn | 9 (+1 một phần: OLED/IPS chỉ nói OLED) |
| Trung thực: chưa có nguồn / chỉ có chính sách demo | 11 |
| **Trích sai chủ đề nhưng gắn "full"** (GPU tích hợp, hai CPU i5, VRAM vs RAM, nguồn 80 Plus → USB PD, SSD gần đầy, ưu tiên tài liệu bảo hành) | 6 |
| RAG tự hỏi lại/deferred/handoff không cần thiết (BUY-210, 220, 223) | 3 |

Tư vấn: 7 câu route documents nhận đoạn tài liệu liên quan một phần; chưa phải tư vấn, cần review riêng. Thời gian: median 0,34s, câu tài liệu 3–13s (max 12,8s, lần đầu tạo embedding cache).

Toàn bộ **553 test PASS** (`runtime/tests-docs2-full.log`), thêm `tests/test_documents_tool.py`.

## Hạn chế / việc tiếp

- RAG đánh dấu `full` cả khi đoạn trích lệch chủ đề (6/30) — cần kiểm tra liên quan câu hỏi–bằng chứng hoặc bổ sung tài liệu (VRAM, 80 Plus, dual-channel, GPU tích hợp). Không sửa pipeline RAG trong lượt này vì nó cũng là `basic_rag` của web với bộ hồi quy 479 riêng.
- Chính sách shop là mô phỏng, thiếu giao hàng/hủy đơn/VAT/chi nhánh — cần tài liệu chủ shop duyệt.
- Phát lại offline không dùng được cho câu RAG (model chọn bằng chứng theo ID nên lời gọi đã ghi không khớp lại); phải chạy model thật.
- Default web vẫn `basic_rag`; chế độ agent vẫn opt-in. Không train, không đổi model/config, không frontend/deploy.
