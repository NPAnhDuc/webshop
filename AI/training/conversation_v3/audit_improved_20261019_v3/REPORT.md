# Kiểm tra mở rộng chatbot local

Hoàn tất 57/106 câu: **PASS 45 · FAIL 12**.

Chấm cả ý định, kỳ, câu trả lời và số liệu SQL; không chỉ chấm chọn đúng công cụ. Câu thiếu thông tin hỏi lại đúng được PASS. Yêu cầu không làm được/thiếu dữ liệu vẫn FAIL, phân loại riêng với trả lời sai.

Bộ câu hỏi đã đóng băng trước chạy. Không sửa prompt/model, không đổi nhãn, không train trong lượt đánh giá. Đây là kiểm thử chức năng có đáp án viết trước, không phải ước lượng độ chính xác production.

| Mã | Kết quả | Câu hỏi | Lý do FAIL |
|---|---|---|---|
| Q001 | PASS | Tiền bán hàng tháng 10 năm 2025 được bao nhiêu? |  |
| Q002 | PASS | Cho tau tổng doanh thu T11/2025. |  |
| Q003 | PASS | Doanh số tháng 12/2025 tính ra tiền là mấy? |  |
| Q004 | PASS | Tính doanh thu bán hàng của tháng 1 năm 2026 giúp tôi. |  |
| Q005 | PASS | Tiền bán hàng tháng 2 năm 2026 được bao nhiêu? |  |
| Q006 | PASS | Cho tau tổng doanh thu T3/2026. |  |
| Q007 | PASS | Doanh số tháng 4/2026 tính ra tiền là mấy? |  |
| Q008 | PASS | Tính doanh thu bán hàng của tháng 5 năm 2026 giúp tôi. |  |
| Q009 | PASS | Tiền bán hàng tháng 6 năm 2026 được bao nhiêu? |  |
| Q010 | PASS | Cho tau tổng doanh thu T7/2026. |  |
| Q011 | PASS | Doanh số tháng 8/2026 tính ra tiền là mấy? |  |
| Q012 | PASS | Tính doanh thu bán hàng của tháng 9 năm 2026 giúp tôi. |  |
| Q013 | PASS | Tổng doanh thu quý 4 năm 2025 là bao nhiêu? |  |
| Q014 | PASS | Cho tôi số doanh thu Q4/2025. |  |
| Q015 | PASS | Tổng doanh thu quý 1 năm 2026 là bao nhiêu? |  |
| Q016 | PASS | Cho tôi số doanh thu Q1/2026. |  |
| Q017 | PASS | Tổng doanh thu quý 2 năm 2026 là bao nhiêu? |  |
| Q018 | PASS | Cho tôi số doanh thu Q2/2026. |  |
| Q019 | PASS | Tổng doanh thu quý 3 năm 2026 là bao nhiêu? |  |
| Q020 | PASS | Cho tôi số doanh thu Q3/2026. |  |
| Q021 | PASS | Giá vốn tháng 8 năm 2026 hết bao nhiêu? |  |
| Q022 | PASS | Lợi nhuận gộp tháng 7 năm 2026 là bao nhiêu? |  |
| Q023 | PASS | Tháng 9 năm 2026 lời bao nhiêu sau chi phí vận hành nhưng trước lãi vay và thuế? |  |
| Q024 | PASS | Chi phí vận hành tháng 6 năm 2026 là mấy đồng? |  |
| Q025 | PASS | Tháng 9 năm 2026 đã hoàn lại cho khách bao nhiêu tiền? |  |
| Q026 | PASS | Giá trị hàng nhận từ nhà cung cấp tháng 8 năm 2026 bao nhiêu? |  |
| Q027 | PASS | Có bao nhiêu đơn hàng trong tháng 5 năm 2026? |  |
| Q028 | PASS | Doanh thu tháng 4 năm 2026 chia theo từng kênh bán thế nào? |  |
| Q029 | PASS | Món bán chạy nhất tháng 9/2026 là gì? |  |
| Q030 | PASS | Top 3 mặt hàng được mua nhiều nhất tháng 8 năm 2026. |  |
| Q031 | PASS | Ba sản phẩm mang về nhiều doanh thu nhất tháng 7 năm 2026? |  |
| Q032 | FAIL | Tháng 6 năm 2026, mã nào đóng góp lợi nhuận gộp nhiều nhất? | Cần top_products; nhận business_analysis.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q033 | PASS | Xếp hạng 5 sản phẩm theo doanh thu tháng 5 năm 2026. |  |
| Q034 | PASS | Mặt hàng nào có số lượng bán ròng cao nhất tháng 4 năm 2026? |  |
| Q035 | PASS | Chỉ tính laptop: top 3 bán chạy tháng 9 năm 2026? |  |
| Q036 | PASS | Trong nhóm chuột, món nào bán được nhiều nhất tháng 9 năm 2026? |  |
| Q037 | PASS | Top 3 laptop theo doanh thu tháng 8 năm 2026. |  |
| Q038 | PASS | Tháng 7 năm 2026, GPU nào mang lại lợi nhuận gộp lớn nhất? |  |
| Q039 | PASS | Doanh thu tháng 2 năm 2026 bao nhiêu? |  |
| Q040 | FAIL | Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất? | KeyError: 'sku' |
| Q041 | FAIL | Đổi tiêu chí qua doanh thu nhé. | KeyError: 'sku' |
| Q042 | FAIL | Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy. | Cần top_products; nhận revenue.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q043 | PASS | Doanh thu tháng 6 năm 2026 bao nhiêu? |  |
| Q044 | FAIL | Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất? | KeyError: 'sku' |
| Q045 | FAIL | Đổi tiêu chí qua doanh thu nhé. | KeyError: 'sku' |
| Q046 | FAIL | Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy. | Cần top_products; nhận revenue.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q047 | PASS | Doanh thu tháng 9 năm 2026 bao nhiêu? |  |
| Q048 | FAIL | Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất? | KeyError: 'sku' |
| Q049 | FAIL | Đổi tiêu chí qua doanh thu nhé. | KeyError: 'sku' |
| Q050 | FAIL | Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy. | Cần top_products; nhận revenue.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả. |
| Q051 | PASS | Mặt hàng bán chạy nhất tháng đó? |  |
| Q052 | PASS | Tháng chín năm 2026 nhé. |  |
| Q053 | PASS | Cho tôi xem theo lãi gộp thay vì số lượng. |  |
| Q054 | FAIL | Giờ chuyển sang doanh thu của tháng tám cùng năm. | Cần revenue; nhận top_products.; Không thấy số đúng 1.427.320.000 cho revenue trong câu trả lời. |
| Q055 | PASS | So sánh doanh thu tháng 9 năm 2026. |  |
| Q056 | FAIL | Với tháng 8 năm 2026. | Sai tiêu chí so sánh. |
| Q057 | PASS | Còn nếu đối chiếu theo lợi nhuận gộp? |  |

## Chi tiết các câu FAIL

### Q032 — rank-3

**Hỏi:** Tháng 6 năm 2026, mã nào đóng góp lợi nhuận gộp nhiều nhất?

**Bot trả lời:**

Doanh thu: **838.580.000 đ**. Giá vốn: **717.998.000 đ**. Lợi nhuận gộp: **120.582.000 đ**. Biên lợi nhuận gộp: **14.38%**. Số lượng bán: **108**.

Nguồn: 116 dòng bán hàng mô phỏng; 2026-06-01 ≤ ngày < 2026-07-01. Lợi nhuận gộp = doanh thu − giá vốn; biên gộp = lợi nhuận gộp / doanh thu.

SKU có doanh thu cao nhất: **2243d61cc7fbfde1c3d93d38a133c97a6edb6b1d950fca079a016c91c049a5f1**, 87.000.000 đ (10.37%). 

Doanh thu trên đã trừ hoàn trả **27.630.000 đ**. Chi phí vận hành: **107.024.380 đ**. Lợi nhuận hoạt động trước lãi vay và thuế: **13.557.620 đ**. Có **96 đơn**, **4 sản phẩm hoàn trả**. Giá trị hàng đã nhận từ nhà cung cấp: **597.084.000 đ** (không trừ lần nữa vào lợi nhuận vì giá vốn đã tính theo FIFO). Mục tiêu mô phỏng: **1.269.000.000 đ**; đạt **66.08%**. Còn thiếu **430.420.000 đ** so với kế hoạch. Kiểm tra đóng góp từng SKU và lịch hết hàng trước khi đề xuất tăng chi quảng cáo. SKU đóng góp lợi nhuận gộp lớn nhất: **2243d61cc7fbfde1c3d93d38a133c97a6edb6b1d950fca079a016c91c049a5f1**, **10.966.000 đ**; đây là kết quả quan sát, chưa chứng minh ngân sách tăng thêm sẽ có hiệu quả. Giá vốn tồn kho tại 2026-06-30: **1.460.715.000 đ**. 

Doanh thu thuần theo kênh: store: 447.290.000 đ, website: 337.780.000 đ, social: 53.510.000 đ.Cần kiểm tra SKU có lợi nhuận gộp âm: cdc875d18109ca5c457ea2feee66cd5cb9f055700d6d0c0cffeacb398a8ea0bd, 15311338f518072cfa659390b765f41584c33a22b249885c4d1591dc9aa7af81. 

Đã trừ hoàn trả và chi phí vận hành mô phỏng; chưa tính lãi vay và thuế thu nhập nên không gọi là lợi nhuận ròng. Ngày đầu/cuối có bản ghi không chứng minh dữ liệu cả kỳ đã đầy đủ. Biến động doanh thu chưa chứng minh nguyên nhân hay hiệu quả marketing.

Tài liệu kế hoạch liên quan:

Kế hoạch bán hàng 2026-Q2 > Mục tiêu doanh thu

Kỳ: 2026-Q2. Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT: 3848000000 VND. Biên lợi nhuận gộp mục tiêu: 14,5%. Đây là kế hoạch định trước, không điều chỉnh theo kết quả.
[Nguồn: sales-plan-2026-Q2-v1.md, đoạn 2]

**Lý do:** Cần top_products; nhận business_analysis.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q040 — context-rank-2

**Hỏi:** Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất?

**Bot trả lời:**



**Lý do:** KeyError: 'sku'

### Q041 — context-rank-2

**Hỏi:** Đổi tiêu chí qua doanh thu nhé.

**Bot trả lời:**



**Lý do:** KeyError: 'sku'

### Q042 — context-rank-2

**Hỏi:** Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy.

**Bot trả lời:**

Cần hai kỳ có dữ liệu. Ví dụ: doanh thu quý 3 so với quý 2 năm 2026.

**Lý do:** Cần top_products; nhận revenue.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q044 — context-rank-6

**Hỏi:** Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất?

**Bot trả lời:**



**Lý do:** KeyError: 'sku'

### Q045 — context-rank-6

**Hỏi:** Đổi tiêu chí qua doanh thu nhé.

**Bot trả lời:**



**Lý do:** KeyError: 'sku'

### Q046 — context-rank-6

**Hỏi:** Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy.

**Bot trả lời:**

Cần hai kỳ có dữ liệu. Ví dụ: doanh thu quý 3 so với quý 2 năm 2026.

**Lý do:** Cần top_products; nhận revenue.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q048 — context-rank-9

**Hỏi:** Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất?

**Bot trả lời:**



**Lý do:** KeyError: 'sku'

### Q049 — context-rank-9

**Hỏi:** Đổi tiêu chí qua doanh thu nhé.

**Bot trả lời:**



**Lý do:** KeyError: 'sku'

### Q050 — context-rank-9

**Hỏi:** Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy.

**Bot trả lời:**

Cần hai kỳ có dữ liệu. Ví dụ: doanh thu quý 3 so với quý 2 năm 2026.

**Lý do:** Cần top_products; nhận revenue.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

### Q054 — clarification-continuation

**Hỏi:** Giờ chuyển sang doanh thu của tháng tám cùng năm.

**Bot trả lời:**

Kỳ **2026-08-01 đến 2026-08-31**. Xếp theo **lợi nhuận gộp**.

1. **Apple MacBook Air (Late 2020)** — 16.024.000 đ.

Đây là dữ liệu mô phỏng.

**Lý do:** Cần revenue; nhận top_products.; Không thấy số đúng 1.427.320.000 cho revenue trong câu trả lời.

### Q056 — compare-continuation

**Hỏi:** Với tháng 8 năm 2026.

**Bot trả lời:**

So sánh **2026-09** (1.189.908.000 đ) với **2026-08** (1.427.320.000 đ), theo doanh thu: chênh lệch **-237.412.000 đ**, **-16.63%**. Dữ liệu mô phỏng; chưa xác lập nguyên nhân.

**Lý do:** Sai tiêu chí so sánh.
