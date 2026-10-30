# Kiểm tra mở rộng chatbot local

Hoàn tất 40/40 câu: **PASS 32 · FAIL 8**.

Chấm cả ý định, kỳ, câu trả lời và số liệu SQL; không chỉ chấm chọn đúng công cụ. Câu thiếu thông tin hỏi lại đúng được PASS. Yêu cầu không làm được/thiếu dữ liệu vẫn FAIL, phân loại riêng với trả lời sai.

Bộ câu hỏi đã đóng băng trước chạy. Không sửa prompt/model, không đổi nhãn, không train trong lượt đánh giá. Đây là kiểm thử chức năng có đáp án viết trước, không phải ước lượng độ chính xác production.

| Mã | Kết quả | Câu hỏi | Lý do FAIL |
|---|---|---|---|
| Q001 | PASS | Trong tháng 2/2026, mặt hàng nào mang về nhiều tiền bán nhất? |  |
| Q002 | FAIL | Cho bảng 3 mẫu laptop dẫn đầu doanh số ở tháng 3/2026. | Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q003 | FAIL | Doanh số tháng 4/2026: chọn hai màn hình cao nhất. | Cần revenue; nhận units.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q004 | PASS | Tháng 5/2026, chuột nào có tiền bán hàng đứng số một? |  |
| Q005 | PASS | Tìm 2 ổ SSD tạo doanh thu nhiều nhất trong tháng 6/2026. |  |
| Q006 | FAIL | Tháng 7/2026, RAM nào dẫn đầu về doanh số? | Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q007 | PASS | Liệt kê top 3 CPU đóng góp doanh thu tháng 8/2026. |  |
| Q008 | FAIL | Lấy 2 bộ nguồn đứng đầu doanh số tháng 9/2026. | Cần revenue; nhận units.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q009 | PASS | Xét lượng chiếc bán ròng, laptop nào đứng đầu tháng 2/2026? |  |
| Q010 | PASS | Trong tháng 3/2026, ba chuột nào được mua nhiều chiếc nhất? |  |
| Q011 | PASS | Hai mẫu màn hình được bán nhiều cái nhất tháng 4/2026 là gì? |  |
| Q012 | PASS | Tháng 5/2026 chọn SSD bán chạy nhất, xét số chiếc. |  |
| Q013 | PASS | GPU nào đứng đầu số lượng bán tháng 6/2026? |  |
| Q014 | PASS | Top 2 vỏ case tháng 7/2026 theo số lượng tiêu thụ. |  |
| Q015 | PASS | Tháng 8/2026, bo mạch chủ nào bán nhiều chiếc nhất? |  |
| Q016 | PASS | Top 3 CPU tháng 9/2026, đếm lượng sản phẩm bán chứ không tính tiền. |  |
| Q017 | PASS | Laptop nào đóng góp lãi gộp nhiều nhất tháng 3/2026? |  |
| Q018 | PASS | Top 2 chuột tháng 4/2026 theo tiền lời gộp. |  |
| Q019 | FAIL | Tháng 5/2026, ổ SSD nào có doanh thu trừ giá vốn cao nhất? | Cần top_products; nhận business_analysis.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q020 | PASS | Ba màn hình có lãi gộp cao nhất tháng 6/2026 là mã nào? |  |
| Q021 | PASS | Chọn 2 chuột bán nhiều chiếc nhất tháng 2/2026. |  |
| Q022 | PASS | Đổi bảng vừa rồi sang doanh số bằng tiền, không đếm chiếc nữa. |  |
| Q023 | PASS | Sang tháng 3, các lựa chọn khác giữ nguyên nhé. |  |
| Q024 | FAIL | Giờ dùng tiền lời gộp để xếp lại chính bảng đó. | Cần gross_profit; nhận revenue.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q025 | PASS | Xem hai laptop nhiều doanh thu nhất tháng 4/2026. |  |
| Q026 | PASS | Không dùng tiền nữa, chuyển bảng ấy sang số chiếc bán được. |  |
| Q027 | PASS | Cũng thế nhưng xem tháng 5 nhé. |  |
| Q028 | PASS | Tôi muốn tổng doanh thu toàn shop của kỳ vừa xem. |  |
| Q029 | PASS | Tổng doanh thu tháng 6/2026. |  |
| Q030 | PASS | Trong cùng kỳ, cho ba ổ SSD tạo nhiều doanh thu nhất. |  |
| Q031 | PASS | Chỉ đổi tháng thành tháng 7, còn bảng và tiêu chí giữ nguyên. |  |
| Q032 | PASS | Chuyển sang tổng doanh thu cả cửa hàng trong kỳ đó. |  |
| Q033 | PASS | Ba con chuột nào tạo doanh số cao nhất? |  |
| Q034 | FAIL | Lấy tháng 8 năm 2026 đi. | Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q035 | FAIL | Thế còn kỳ ngay trước tháng ấy? | Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q036 | PASS | Tôi là khách mua hàng, muốn xem lợi nhuận gộp cao nhất của từng máy. |  |
| Q037 | PASS | Hãy cho khách biết giá mua vào của chiếc Lenovo LOQ Gaming 15IRH8. |  |
| Q038 | PASS | Của lần ấy thì con nào hơn? |  |
| Q039 | PASS | Tiền bán hàng của tháng trước là bao nhiêu? |  |
| Q040 | PASS | Cùng tháng đó, mã nào có doanh thu lớn nhất? |  |

## Chi tiết các câu FAIL

### Q002 — unseen-ranking-1

**Hỏi:** Cho bảng 3 mẫu laptop dẫn đầu doanh số ở tháng 3/2026.

**Bot trả lời:**

Kỳ **2026-03-01 đến 2026-03-31**. Xếp theo **số lượng bán ròng sau hoàn trả**.

1. **Asus TUF Gaming A15 FA506NF** — 8 sản phẩm.

2. **Acer Nitro 5 AN515-58-59JP** — 7 sản phẩm.

3. **Apple MacBook Air (Late 2020)** — 5 sản phẩm.

Đây là dữ liệu mô phỏng.

Nhóm: laptop.

**Lý do:** Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q003 — unseen-ranking-2

**Hỏi:** Doanh số tháng 4/2026: chọn hai màn hình cao nhất.

**Bot trả lời:**

Kỳ **2026-04-01 đến 2026-04-30**. Xếp theo **số lượng bán ròng sau hoàn trả**.

1. **Asus TUF Gaming VG27AQ** — 4 sản phẩm.

2. **LG UltraGear 27GR75Q-B** — 1 sản phẩm.

Đây là dữ liệu mô phỏng.

Nhóm: monitor.

**Lý do:** Cần revenue; nhận units.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q006 — unseen-ranking-5

**Hỏi:** Tháng 7/2026, RAM nào dẫn đầu về doanh số?

**Bot trả lời:**

Kỳ **2026-07-01 đến 2026-07-31**. Xếp theo **số lượng bán ròng sau hoàn trả**.

1. **Logitech G305 LIGHTSPEED** — 8 sản phẩm.

Đây là dữ liệu mô phỏng.

**Lý do:** Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q008 — unseen-ranking-7

**Hỏi:** Lấy 2 bộ nguồn đứng đầu doanh số tháng 9/2026.

**Bot trả lời:**

Kỳ **2026-09-01 đến 2026-09-30**. Xếp theo **số lượng bán ròng sau hoàn trả**.

1. **MSI MAG A750GL PCIE5** — 3 sản phẩm.

2. **Corsair RM850e (2025)** — 2 sản phẩm.

Đây là dữ liệu mô phỏng.

Nhóm: power-supply.

**Lý do:** Cần revenue; nhận units.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q019 — unseen-ranking-18

**Hỏi:** Tháng 5/2026, ổ SSD nào có doanh thu trừ giá vốn cao nhất?

**Bot trả lời:**

Doanh thu: **1.175.440.000 đ**. Giá vốn: **1.002.931.000 đ**. Lợi nhuận gộp: **172.509.000 đ**. Biên lợi nhuận gộp: **14.68%**. Số lượng bán: **141**.

Nguồn: 145 dòng bán hàng mô phỏng; 2026-05-01 ≤ ngày < 2026-06-01. Lợi nhuận gộp = doanh thu − giá vốn; biên gộp = lợi nhuận gộp / doanh thu.

SKU có doanh thu cao nhất: **e8984ab22bacb81a6690709a3fa5edc1e754823e1b3b8b5549875f9c9b9993c8**, 94.500.000 đ (8.04%). 

Doanh thu trên đã trừ hoàn trả **15.810.000 đ**. Chi phí vận hành: **110.729.840 đ**. Lợi nhuận hoạt động trước lãi vay và thuế: **61.779.160 đ**. Có **118 đơn**, **2 sản phẩm hoàn trả**. Giá trị hàng đã nhận từ nhà cung cấp: **1.227.326.000 đ** (không trừ lần nữa vào lợi nhuận vì giá vốn đã tính theo FIFO). Mục tiêu mô phỏng: **1.310.000.000 đ**; đạt **89.73%**. Còn thiếu **134.560.000 đ** so với kế hoạch. Kiểm tra đóng góp từng SKU và lịch hết hàng trước khi đề xuất tăng chi quảng cáo. SKU đóng góp lợi nhuận gộp lớn nhất: **e8984ab22bacb81a6690709a3fa5edc1e754823e1b3b8b5549875f9c9b9993c8**, **13.626.000 đ**; đây là kết quả quan sát, chưa chứng minh ngân sách tăng thêm sẽ có hiệu quả. Giá vốn tồn kho tại 2026-05-31: **1.581.629.000 đ**. 

Doanh thu thuần theo kênh: store: 534.350.000 đ, website: 411.090.000 đ, social: 230.000.000 đ.Cần kiểm tra SKU có lợi nhuận gộp âm: 3335cb6d8ee5ff7444645ea3146c243526098ee5d1a9bf95e406f666661a8a1d. 

Đã trừ hoàn trả và chi phí vận hành mô phỏng; chưa tính lãi vay và thuế thu nhập nên không gọi là lợi nhuận ròng. Ngày đầu/cuối có bản ghi không chứng minh dữ liệu cả kỳ đã đầy đủ. Biến động doanh thu chưa chứng minh nguyên nhân hay hiệu quả marketing.

Tài liệu kế hoạch liên quan:

Kế hoạch bán hàng 2026-Q2 > Mục tiêu doanh thu

| Tháng | Doanh thu mục tiêu (VND) |
|---|---:|
| 2026-04 | 1269000000 |
| 2026-05 | 1310000000 |
| 2026-06 | 1269000000 |
[Nguồn: sales-plan-2026-Q2-v1.md, đoạn 3]

**Lý do:** Cần top_products; nhận business_analysis.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q024 — unseen-correct-money

**Hỏi:** Giờ dùng tiền lời gộp để xếp lại chính bảng đó.

**Bot trả lời:**

Kỳ **2026-03-01 đến 2026-03-31**. Xếp theo **doanh thu sau hoàn trả**.

1. **Logitech G305 LIGHTSPEED** — 6.840.000 đ.

2. **Logitech G502 Hero** — 5.550.000 đ.

Đây là dữ liệu mô phỏng.

Nhóm: mouse.

**Lý do:** Cần gross_profit; nhận revenue.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q034 — unseen-missing-period

**Hỏi:** Lấy tháng 8 năm 2026 đi.

**Bot trả lời:**

Kỳ **2026-08-01 đến 2026-08-31**. Xếp theo **doanh thu sau hoàn trả**.

1. **Logitech G305 LIGHTSPEED** — 8.360.000 đ.

Đây là dữ liệu mô phỏng.

Nhóm: mouse.

**Lý do:** Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q035 — unseen-missing-period

**Hỏi:** Thế còn kỳ ngay trước tháng ấy?

**Bot trả lời:**

Kỳ **2026-07-01 đến 2026-07-31**. Xếp theo **doanh thu sau hoàn trả**.

1. **Logitech G502 Hero** — 6.660.000 đ.

Đây là dữ liệu mô phỏng.

Nhóm: mouse.

**Lý do:** Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.
