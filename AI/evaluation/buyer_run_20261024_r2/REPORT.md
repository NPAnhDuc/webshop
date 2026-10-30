# Bộ 300 lượt người mua — lần chạy đầu (r1) và sau sửa (r2)

Bank: `buyer_expansion_20261024_r2/bank.jsonl` (hash trong metadata), vai customer, `CHATBOT_MODE=agent_tools`, Qwen3-4B local, ngày server 23/10/2026. Development do người viết tự soạn từ template, không phải independent validation. Gold catalog lọc độc lập từ catalog JSON. Chấm cơ học bằng `check_buyer.py`; prose chưa human review.

## Kết quả

| Nhóm | Lượt | r1 (code r11) | r2 (code r12) |
|---|---:|---:|---:|
| Tìm kiếm catalog | 40 | 23 | **40** |
| So sánh hai máy (nêu tên) | 20 | 20 | 20 |
| Hội thoại nhiều lượt | 56 | 9 | **55** |
| Hỏi thông số một sản phẩm | 134 | 0 | 0 — chưa có công cụ |
| Kiến thức/chính sách | 30 | 0 | 0 — `documents.answer` còn tắt |
| Tư vấn nhu cầu | 20 | 0 | 0 — chưa có chức năng, cần review ngữ nghĩa |

Cả hai lượt integrity unchanged=true; r2 median 0,28s, max 1,69s. Checker ban đầu chấm sai 3 ca "lượt trước chỉ có 1 món" (gold `clarify_if_fewer_than_two`); đã sửa checker và chấm lại cả r1/r2, không sửa gold.

## Lỗi đã sửa ở r12 (`catalog_planner.py`, router prompt không đổi)

1. Đếm số lượng thiếu danh từ: mainboard, case, bộ nguồn, card đồ họa, phụ kiện, "món", "lựa chọn" → "lấy 3 mainboard" bị thành 5.
2. Thiếu danh mục `accessories` ("phụ kiện").
3. "hạ trần xuống N đồng" không được hiểu là ngân sách.
4. Model chép lại giá/số lượng/tên loại vào `extra_requirements` ("lấy 2", "số lượng 2", "thanh RAM") → bị coi là bộ lọc chưa hỗ trợ hoặc ungrounded. Nay chỉ bỏ khi giá trị khớp đúng toán hạng đã parse (`restates_operands`); yêu cầu kỹ thuật thật (DDR5, RAM 16GB) vẫn deferred.
5. Cách gọi thứ tự: "món đầu", "hai sản phẩm/món/lựa chọn (đứng) đầu", "số một… số hai", "lựa chọn thứ nhất", "món kế tiếp". Không match đủ hai vị trí thì rơi về so tên chính xác thay vì trả rỗng.

Hồi quy cùng 118 lượt (`agent_quality_20261024_r12`): 106 không đổi answer/toolargs so r8 (103/106), mixed 11/12 như r11. Toàn bộ **492 test PASS** (`runtime/tests-buyer-r2-full.log`), thêm `tests/test_buyer_operands.py`.

## Lỗi còn lại / khoảng trống chức năng

- **134 câu thông số** ("máy X RAM bao nhiêu GB/pin bao nhiêu Wh") đều route sang documents. Cần công cụ `catalog.product_facts`: gắn đúng tên model, đọc field từ catalog, field null phải nói "chưa có thông tin". 31 câu field thiếu: không thấy bot bịa số (bot chưa trả số nào).
- **BUY-287** "Xin bảng thông số của hai sản phẩm đầu ở kết quả mới" → router chọn search (thêm bộ lọc giả) thay vì compare.
- **BUY-213** hỏi hóa đơn VAT bị từ chối như câu admin (chặn nhầm khách).
- **BUY-220/222/223** hủy đơn, chi nhánh/giờ mở cửa, liên hệ nhân viên → handoff "chưa kết nối"; hai câu đầu nên là documents/chính sách.
- **Tư vấn** (20): không có chức năng; câu chưa rõ nhận câu mặc định "Bạn muốn chọn hoặc so sánh những model nào?" — sai ngữ cảnh khi khách không hỏi so sánh.
- Kiến thức/chính sách: route documents 26/30 nhưng nhánh tài liệu tắt (cần worker 8011) — route đúng không phải trả lời đúng.

Không train, không đổi model/config/default `basic_rag`, không frontend/deploy. Bank/gold giữ nguyên.
