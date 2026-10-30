# Dự báo nhu cầu: mùa vụ, thước đo sai số, baseline trước mô hình phức tạp

> Tài liệu phương pháp nội bộ (handbook phân tích kinh doanh), chỉ dành cho quản lý. Mọi con số trong ví dụ là minh họa, KHÔNG phải số liệu của shop. Số liệu shop (doanh thu, giá vốn, đơn, tồn kho) chỉ lấy từ công cụ SQL/báo cáo trên database data/business_sql/scenario_v1/shop.sqlite (dữ liệu mô phỏng 01/10/2025–30/09/2026).

# MODULE 4.3: DỰ BÁO NHU CẦU BÁN HÀNG & CHUỖI THỜI GIAN (DEMAND FORECASTING & TIME SERIES)

---

## 1. ĐẶC ĐIỂM CHUỖI THỜI GIAN TRONG BÁN LẺ & TMĐT VIỆT NAM
Chuỗi thời gian bán lẻ hàng công nghệ và thương mại điện tử không bao giờ là một đường thẳng mà luôn chịu tác động mạnh mẽ của 4 thành phần:

$$\text{Demand}(t) = \text{Trend}(t) \times \text{Seasonality}(t) \times \text{Event/Campaign}(t) + \epsilon(t)$$

1. **Chu kỳ tuần (Day-of-Week Seasonality)**: Khách hàng thường nghiên cứu cấu hình máy tính vào đầu tuần và bùng nổ đặt hàng/lắp máy vào thứ Sáu, thứ Bảy và Chủ Nhật.
2. **Hiệu ứng ngày nhận lương (Payday Effect)**: Tại Việt Nam, các ngày 15 và ngày cuối tháng (30/31) lượng chuyển đổi đơn hàng tăng vọt từ $40\% - 80\%$ so với ngày thường.
3. **Hiệu ứng Ngày Hội Mua Sắm Siêu Sale (Mega Double-Day & Lễ Tết)**:
   - Các ngày sale đôi: 9.9, 10.10, 11.11, 12.12. Doanh số có thể gấp 3 - 5 lần ngày thường nhưng biên lợi nhuận thấp hơn do trợ giá.
   - Mùa Black Friday (tháng 11) và Mùa Lễ Tết Nguyên Đán (tháng 12 Âm lịch): Đỉnh cao mua sắm thiết bị mới. Sau Tết (tháng Giêng) thị trường thường rơi vào giai đoạn "ngủ đông".

---

## 2. CÁC THƯỚC ĐO ĐÁNH GIÁ ĐỘ CHÍNH XÁC DỰ BÁO TRONG BÁN LẺ

1. **WAPE (Weighted Absolute Percentage Error - Chuẩn mực bán lẻ)**:
   Không bị lỗi chia cho 0 như MAPE khi một số ngày sản phẩm không có lượt mua nào:
   $$\text{WAPE} = \frac{\sum_{t=1}^n |y_t - \hat{y}_t|}{\sum_{t=1}^n y_t} \times 100\%$$
   - $\text{WAPE} < 15\%$: Dự báo xuất sắc.
   - $\text{WAPE} \in [15\%, 25\%]$: Khá tốt, áp dụng an toàn cho việc lên đơn nhập hàng.
   - $\text{WAPE} > 35\%$: Kém, cần thu thập thêm đặc trưng hoặc điều chỉnh tồn kho an toàn (Safety Stock) cao hơn.

2. **RMSE (Root Mean Squared Error)**:
   Phạt rất nặng các lỗi dự báo lệch lớn (giúp tránh việc đánh giá thấp nhu cầu dẫn đến đứt hàng đột ngột).
   $$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{t=1}^n (y_t - \hat{y}_t)^2}$$

---