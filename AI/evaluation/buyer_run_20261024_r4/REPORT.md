# Sửa định tuyến người mua — bộ 300 (r4) và hồi quy r14

## Thay đổi (luật cố định sau route; router prompt không đổi)

1. **Câu hỏi quy trình công khai của khách → documents** (`public_policy_question`): hóa đơn/VAT, bảo hành, đổi trả, hủy đơn, giao hàng, trả góp, thanh toán, chi nhánh, giờ mở cửa, địa chỉ, liên hệ — khi là câu hỏi thông tin và **không** có từ dữ liệu nội bộ (doanh thu, giá vốn, lợi nhuận, tồn kho, nguồn dữ liệu, chủ shop, admin, phân quyền...) và **không** là yêu cầu nối máy ("cho tôi gặp nhân viên", "chuyển sang nhân viên"). Chỉ áp dụng vai customer và chỉ đổi route admin/handoff. Khách tự xưng chủ shop vẫn đi admin để server từ chối.
2. **Cặp thứ tự của danh sách trước → compare**: "hai sản phẩm đầu", "số một và số hai"... khi đã có danh sách server, không có ngân sách/số lượng mới và không phải câu kết hợp; chỉ dùng thứ tự, không đoán theo tên.
3. **Câu hỏi lại theo ngữ cảnh** (`clarify_message`): giữ câu cũ khi khách đang hỏi so sánh; câu mang dấu hiệu tư vấn (ngân sách, nên, cân nhắc, nhu cầu...) nói rõ chưa có chức năng tư vấn và gợi ý việc làm được; còn lại hỏi trung tính (tìm theo ngân sách / thông số / so sánh).

Trước khi chạy model đã phát lại offline r13 và buyer r3 với câu trả lời model đã ghi: 118 lượt không đổi (chỉ khác đường dẫn ảnh biểu đồ), 300 lượt đổi đúng 12 ca mục tiêu, không ca nào cần thêm lời gọi model.

## Kết quả model thật

| Nhóm | Lượt | r3 | **r4** |
|---|---:|---:|---:|
| Thông số | 134 | 134 | 134 |
| Tìm kiếm | 40 | 40 | 40 |
| So sánh nêu tên | 20 | 20 | 20 |
| Nhiều lượt | 56 | 55 | **56** (BUY-287 so đúng 2 máy) |
| Kiến thức/chính sách: route documents | 30 | 26 | **30** (VAT, hủy đơn, chi nhánh, liên hệ) — vẫn chưa trả lời vì nhánh tài liệu tắt |
| Tư vấn | 20 | 0 | 0 — câu hỏi lại nay đúng ngữ cảnh, chức năng tư vấn chưa có |

Hồi quy r14 (118 lượt): 106 không đổi answer/toolargs so r8 (103/106), mixed 11/12 (Q58). integrity unchanged=true cả hai lượt; r4 median 0,28s, max 1,58s. Toàn bộ **539 test PASS** (`runtime/tests-routing-full.log`), thêm `tests/test_buyer_routing_fixes.py`.

## Giới hạn

- Luật lexical viết sau khi thấy các câu lỗi; điểm là development đã lộ. Từ khóa chính sách có thể bỏ sót cách nói khác hoặc bắt nhầm câu có từ "liên hệ"/"địa chỉ" trong ngữ cảnh khác; cần bank chính sách mới giữ riêng.
- Route documents đúng ≠ trả lời đúng: nhánh tài liệu cần worker 8011.
- 20 câu tư vấn cần chức năng tư vấn có nguồn và review người; câu hỏi lại chưa được human review.
- Còn Q58 (admin hiểu "so máy" thành so kỳ), Q29/Q30/Q41 (viết dính, đang hoãn), hai bản ghi catalog nghi sai (RTX 3060 12G ghi 8 GB, Deepcool CH160).

Không train, không đổi model/config/default `basic_rag`, không frontend/deploy.
