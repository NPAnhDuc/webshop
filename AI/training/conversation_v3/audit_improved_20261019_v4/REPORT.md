# Kiểm tra mở rộng chatbot local

Hoàn tất 62/106 câu: **PASS 61 · FAIL 1**.

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
| Q032 | PASS | Tháng 6 năm 2026, mã nào đóng góp lợi nhuận gộp nhiều nhất? |  |
| Q033 | PASS | Xếp hạng 5 sản phẩm theo doanh thu tháng 5 năm 2026. |  |
| Q034 | PASS | Mặt hàng nào có số lượng bán ròng cao nhất tháng 4 năm 2026? |  |
| Q035 | PASS | Chỉ tính laptop: top 3 bán chạy tháng 9 năm 2026? |  |
| Q036 | PASS | Trong nhóm chuột, món nào bán được nhiều nhất tháng 9 năm 2026? |  |
| Q037 | PASS | Top 3 laptop theo doanh thu tháng 8 năm 2026. |  |
| Q038 | PASS | Tháng 7 năm 2026, GPU nào mang lại lợi nhuận gộp lớn nhất? |  |
| Q039 | PASS | Doanh thu tháng 2 năm 2026 bao nhiêu? |  |
| Q040 | PASS | Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất? |  |
| Q041 | PASS | Đổi tiêu chí qua doanh thu nhé. |  |
| Q042 | PASS | Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy. |  |
| Q043 | PASS | Doanh thu tháng 6 năm 2026 bao nhiêu? |  |
| Q044 | PASS | Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất? |  |
| Q045 | PASS | Đổi tiêu chí qua doanh thu nhé. |  |
| Q046 | PASS | Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy. |  |
| Q047 | PASS | Doanh thu tháng 9 năm 2026 bao nhiêu? |  |
| Q048 | PASS | Trong khoảng thời gian vừa xem, khách mua món gì nhiều nhất? |  |
| Q049 | PASS | Đổi tiêu chí qua doanh thu nhé. |  |
| Q050 | PASS | Lùi một tháng so với kỳ vừa xem, vẫn giữ tiêu chí ấy. |  |
| Q051 | PASS | Mặt hàng bán chạy nhất tháng đó? |  |
| Q052 | PASS | Tháng chín năm 2026 nhé. |  |
| Q053 | PASS | Cho tôi xem theo lãi gộp thay vì số lượng. |  |
| Q054 | PASS | Giờ chuyển sang doanh thu của tháng tám cùng năm. |  |
| Q055 | PASS | So sánh doanh thu tháng 9 năm 2026. |  |
| Q056 | FAIL | Với tháng 8 năm 2026. | Sai tiêu chí so sánh. |
| Q057 | PASS | Còn nếu đối chiếu theo lợi nhuận gộp? |  |
| Q058 | PASS | Thôi, chỉ lấy doanh thu tháng 7 năm 2026. |  |
| Q059 | PASS | Tiền bán hàng tháng 9 năm 2026? |  |
| Q060 | PASS | Mua hàng rồi có đổi trả được không? |  |
| Q061 | PASS | Quay lại số liệu: bán chạy nhất tháng 8 năm 2026 là món nào? |  |
| Q062 | PASS | Vẽ sơ đồ lời lỗ cho tháng vừa hỏi. |  |

## Chi tiết các câu FAIL

### Q056 — compare-continuation

**Hỏi:** Với tháng 8 năm 2026.

**Bot trả lời:**

So sánh **2026-09** (1.189.908.000 đ) với **2026-08** (1.427.320.000 đ), theo doanh thu: chênh lệch **-237.412.000 đ**, **-16.63%**. Dữ liệu mô phỏng; chưa xác lập nguyên nhân.

**Lý do:** Sai tiêu chí so sánh.
