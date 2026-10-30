# catalog.product_facts — bộ 300 người mua (r3) và hồi quy r13

## Thay đổi

- Công cụ mới `catalog.product_facts(product_id, fields)` (`agent_tools.py`, đăng ký enabled cho customer/admin trong `capabilities.py`): đọc trường thông số của đúng một sản phẩm active từ catalog snapshot; trường không có trong bản ghi trả `missing=true`, không suy đoán. Trường cho phép = `SPEC_FIELDS` + `connection`, `recommended_psu_w` (chưa thu thập → luôn báo thiếu).
- Gắn yêu cầu bằng luật cố định sau route (`product_fact_request` trong `catalog_planner.py`): đúng một tên model khớp nguyên văn (chuẩn hóa dấu; tên ngắn nằm trong tên dài hơn tính là một), một dấu hiệu thông số theo thứ tự ưu tiên (VRAM trước RAM, loại RAM trước dung lượng RAM, pin trước dung lượng...). Không kích hoạt nếu có hai sản phẩm, so sánh, ngân sách/số lượng mua, hoặc route là admin/handoff. Không gọi thêm model; router prompt không đổi.
- `agent_conversation.py`: action `facts`, kiểm plan (một ref, field thuộc danh sách), render giá trị nguyên văn + đơn vị, dòng "chưa có thông tin trong bản ghi; tôi không suy đoán" cho trường thiếu, nhãn dữ liệu mô phỏng.

## Kết quả

| Nhóm | Lượt | r2 | **r3** |
|---|---:|---:|---:|
| Thông số một sản phẩm | 134 | 0 | **134** (103 có giá trị, 31 báo thiếu đúng) |
| Tìm kiếm | 40 | 40 | 40 |
| So sánh nêu tên | 20 | 20 | 20 |
| Nhiều lượt | 56 | 55 | 55 (còn BUY-287) |
| Kiến thức/chính sách | 30 | 0 | 0 — nhánh tài liệu tắt |
| Tư vấn | 20 | 0 | 0 — chưa có chức năng |

Checker thông số kiểm: đúng tool + args (product_id, field), giá trị catalog có trong câu trả lời (danh sách: mọi phần tử), trường có giá trị không bị nói là thiếu, trường thiếu phải nói rõ. Đã sửa checker cho giá trị dạng danh sách; không sửa gold.

Hồi quy r13 (cùng 118 lượt): 106 không đổi answer/toolargs so r8 (103/106), mixed 11/12 (Q58). integrity unchanged=true cả hai lượt; r3 median 0,31s, max 1,75s. Toàn bộ **520 test PASS** (`runtime/tests-facts-full.log`), thêm `tests/test_product_facts.py`.

**Lưu ý độ tin cậy:** luật nhận dạng thông số được viết khi đã thấy bộ câu này (134/134 offline trước khi chạy model). Đây là điểm development, không chứng minh hiểu các cách hỏi mới; test có thêm vài cách diễn đạt khác nhưng cần bank thông số mới, giữ riêng để đo thật.

## Vấn đề dữ liệu catalog phát hiện (chưa sửa, cần chủ shop/nguồn xác nhận)

- MSI GeForce RTX 3060 Ventus 2X **12G**: bản ghi `vram_gb=8` — mâu thuẫn với tên model. Bot trả đúng bản ghi (8 GB) nên đang đưa thông tin có thể sai cho khách.
- Deepcool CH160: bản ghi `supported_form_factors=[ATX, mATX, ITX]`; mẫu này thường là vỏ mini-ITX. Cần kiểm lại.
- Gold bank cũng lấy từ cùng catalog nên không bắt được lỗi dữ liệu; cần đối chiếu nguồn nhà sản xuất riêng.

## Còn lại

BUY-287 (route search thay compare), BUY-213 VAT bị chặn nhầm, BUY-220/222 hủy đơn/chi nhánh → handoff, câu hỏi lại mặc định sai ngữ cảnh, tư vấn chưa có, nhánh tài liệu cần worker 8011. Không train, không đổi model/config/default `basic_rag`, không frontend/deploy.
