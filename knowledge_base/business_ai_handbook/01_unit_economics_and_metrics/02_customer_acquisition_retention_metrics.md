# MODULE 1.2: CHỈ SỐ THU HÚT, GIỮ CHÂN KHÁCH HÀNG & PHÂN TÍCH COHORT (CAC, LTV, RETENTION)

---

## 1. CHI PHÍ THU HÚT KHÁCH HÀNG (CUSTOMER ACQUISITION COST - CAC)

### 1.1. Phân biệt Paid CAC vs. Blended CAC
Trong thực tế phân tích dữ liệu, việc sử dụng sai khái niệm CAC dẫn đến việc đốt ngân sách tiếp thị sai lầm nghiêm trọng.

1. **Paid CAC (Chi phí thu hút trực tiếp từ quảng cáo trả phí)**:
   Chỉ đo lường chi phí bỏ ra để mang về một khách hàng mới thông qua các kênh trả tiền trực tiếp (Meta Ads, Google Ads, TikTok Ads, Shopee Ads):
   $$\text{Paid CAC} = \frac{\text{Tổng chi phí quảng cáo trả phí (Ad Spend)}}{\text{Số lượng khách hàng MỚI phát sinh từ kênh trả phí}}$$

2. **Blended CAC (Chi phí thu hút tổng hòa)**:
   Tính toán bình quân toàn bộ chi phí bán hàng và tiếp thị trên tổng số lượng khách hàng mới từ mọi nguồn (bao gồm cả Organic, Truyền miệng, Tự nhiên, SEO, Khách vãng lai):
   $$\text{Blended CAC} = \frac{\text{Tổng Ad Spend} + \text{Phí Agency} + \text{Lương Marketing} + \text{Chi phí sáng tạo nội dung}}{\text{Tổng số khách hàng MỚI toàn hệ thống}}$$

> [!WARNING]
> **Cảnh báo bẫy dữ liệu (Data Trap)**: Nếu chỉ nhìn vào Blended CAC, chủ shop sẽ bị ảo tưởng rằng chi phí thu hút khách đang rẻ (do bị pha loãng bởi lượng khách tự nhiên Organic). Khi scale ngân sách quảng cáo lên gấp 3 lần, Paid CAC sẽ tăng vọt theo quy luật hiệu suất giảm dần (Diminishing Returns), làm sụp đổ dòng tiền nếu AI không cảnh báo trước.

---

## 2. GIÁ TRỊ VÒNG ĐỜI KHÁCH HÀNG (CUSTOMER LIFETIME VALUE - CLV / LTV)

### 2.1. Công thức LTV Chuẩn Hiệu Chỉnh Theo Biên Lợi Nhuận Gộp (Margin-Adjusted LTV)
Nhiều tài liệu tính LTV đơn thuần bằng $LTV = \text{Doanh thu} \times \text{Số lần mua}$. Đây là công thức sai lầm vì doanh thu không mang lại tiền mặt sau khi trừ giá vốn hàng bán và chi phí vận hành.

Công thức chuẩn tài chính:
$$\text{LTV} = \text{AOV} \times \text{Tần suất mua hàng (F)} \times \text{Vòng đời khách hàng (T)} \times \text{Biên Lãi Gộp (Gross Margin \%)}$$

Trong đó:
- **AOV (Average Order Value)**: Giá trị trung bình trên một đơn hàng thành công.
  $$\text{AOV} = \frac{\text{Tổng Doanh thu thuần (Net Revenue)}}{\text{Tổng số đơn hàng hoàn thành}}$$
- **Tần suất mua hàng trung bình hàng năm ($F$)**:
  $$F = \frac{\text{Tổng số đơn hàng}}{\text{Tổng số khách hàng riêng biệt (Unique Customers)}}$$
- **Vòng đời khách hàng trung bình ($T$)**: Thời gian khách hàng tiếp tục tương tác và mua sắm trước khi rời bỏ (Churn).
  $$T = \frac{1}{\text{Tỷ lệ rời bỏ hàng năm (Annual Churn Rate)}}$$

### 2.2. Công thức LTV cho Mô hình Khách hàng Liên tục (Continuous Retention Model)
Áp dụng tỷ lệ chiết khấu dòng tiền ($d$) và tỷ lệ duy trì khách hàng định kỳ ($r$):
$$\text{LTV} = \sum_{t=0}^{\infty} \frac{\text{Lợi nhuận gộp từ khách hàng tại kỳ } t \times r^t}{(1 + d)^t} = \frac{\text{Lợi nhuận gộp kỳ } 0 \times r}{1 + d - r}$$

---

## 3. CÁC TỶ LỆ VÀNG ĐO LƯỜNG SỨC KHỎE DOANH NGHIỆP

### 3.1. Tỷ số LTV : CAC (The Golden Ratio)
Tỷ số này cho biết cứ mỗi 1 đồng bỏ ra để tìm kiếm khách hàng mới thì mang về bao nhiêu đồng lợi nhuận trong toàn bộ vòng đời của họ.

$$\text{Tỷ số LTV:CAC} = \frac{\text{LTV}}{\text{Paid CAC}}$$

| Tỷ số LTV : CAC | Đánh giá Sức khỏe Doanh nghiệp | Chỉ dẫn Hành động cho AI Business Analyst |
| :---: | :--- | :--- |
| **< 1.0 : 1** | **BÁO ĐỘNG ĐỎ (Chết dần)** | Shop đang đốt tiền mua khách hàng với giá cao hơn lợi nhuận họ mang lại. Ngay lập tức rà soát tắt các nhóm quảng cáo kém hiệu quả, tăng giá bán hoặc cắt giảm chi phí khuyến mãi. |
| **1.0 : 1 - 2.0 : 1** | **Nguy hiểm (Biên quá mỏng)** | Sau khi trừ chi phí cố định (mặt bằng, lương văn phòng), shop sẽ bị lỗ ròng. Cần tập trung tăng AOV (bán chéo cross-sell) và tăng tỷ lệ khách quay lại. |
| **3.0 : 1 - 4.0 : 1** | **TỶ LỆ VÀNG (Lý tưởng)** | Mô hình kinh doanh cực kỳ khỏe mạnh và bền vững. Có thể duy trì quy mô quảng cáo hiện tại và tối ưu hóa chuyển đổi. |
| **> 5.0 : 1** | **Tăng trưởng chậm / Thận trọng quá mức** | Shop đang chi tiêu quá ít cho việc thâu tóm thị phần (Underinvesting). Đối thủ có thể nhảy vào chiếm khách hàng. Khuyến nghị mở rộng ngân sách quảng cáo để scale quy mô. |

---

### 3.2. Thời Gian Hoàn Vốn CAC (CAC Payback Period)
Đo lường số tháng cần thiết để lợi nhuận gộp từ một khách hàng bù đắp hoàn toàn chi phí ban đầu đã bỏ ra để có được khách hàng đó.

$$\text{CAC Payback Period (Tháng)} = \frac{\text{Paid CAC}}{\text{Lợi nhuận gộp trung bình mang lại từ khách hàng mỗi tháng}}$$

- **Benchmark Bán lẻ / E-Commerce Công nghệ**:
  - Tốt nhất: **< 1 - 3 tháng** (Lý tưởng nhất là hòa vốn hoặc có lãi ngay tại đơn hàng đầu tiên - First Purchase Profitability).
  - Tối đa chấp nhận được: **6 - 12 tháng**. Nếu thời gian hoàn vốn vượt quá 12 tháng, doanh nghiệp sẽ đối mặt với khủng hoảng thanh khoản (Liquidity Crunch) vì tiền vốn bị chôn trong chi phí quảng cáo quá lâu.

---

## 4. PHÂN TÍCH COHORT (COHORT RETENTION ANALYSIS)

### 4.1. Bản chất của Phân tích Nhóm thuần tập (Cohort)
Phân tích Cohort chia khách hàng thành các nhóm dựa trên tháng đầu tiên họ phát sinh giao dịch mua hàng (Acquisition Cohort). Việc theo dõi hành vi mua lại của từng cohort qua các tháng giúp loại bỏ sự "nhiễu" của lượng khách hàng mới để nhìn rõ chất lượng thực sự của sản phẩm và dịch vụ.

### 4.2. Ma trận Tam Giác Duy Trì Khách Hàng (Retention Triangle Table)
Bảng số liệu chuẩn hóa tỷ lệ giữ chân khách hàng qua thời gian:

| Cohort Mua Lần Đầu | Số Khách Hàng | Tháng 0 (M0) | Tháng 1 (M1) | Tháng 2 (M2) | Tháng 3 (M3) | Tháng 6 (M6) | Tháng 12 (M12) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Tháng 01/2026** | 1,200 | 100% | 18.5% | 12.0% | 9.8% | 7.5% | 5.2% |
| **Tháng 02/2026** | 1,450 | 100% | 16.2% | 11.4% | 8.9% | 6.8% | - |
| **Tháng 03/2026** | 1,800 | 100% | 21.0% | 14.5% | 10.2% | - | - |
| **Tháng 04/2026** | 2,100 | 100% | 23.4% | 15.8% | - | - | - |

### 4.3. Các Chỉ Số Giữ Chân Cốt Lõi:
1. **Repeat Purchase Rate (RPR - Tỷ lệ khách mua lại)**:
   $$\text{RPR} = \frac{\text{Số lượng khách hàng mua từ 2 lần trở lên}}{\text{Tổng số khách hàng duy nhất trong kỳ}} \times 100\%$$
   - Ngành linh kiện máy tính / PC: RPR trung bình từ $15\% - 25\%$ trong vòng 12 tháng (do chu kỳ nâng cấp linh kiện dài).
   - Ngành phụ kiện (Chuột, phím, tai nghe, lót chuột, dây cáp): RPR kỳ vọng $\ge 35\%$.

2. **Repurchase Interval (Chu kỳ mua lặp lại trung bình)**:
   Số ngày trung bình giữa đơn hàng thứ 1 và đơn hàng thứ 2 của cùng một khách hàng.
   - Giúp AI xác định chính xác thời điểm "vàng" để gửi tin nhắn chăm sóc tự động (Zalo ZNS, SMS, Email Marketing) nhắc nhở khách hàng quay lại mua sắm.

---

## 5. PHỄU CHUYỂN ĐỔI BÁN LẺ VÀ TỶ LỆ RƠI RỤNG (CONVERSION FUNNEL)

```
[1. LƯỢT TIẾP CẬN / XEM QUẢNG CÁO (Impressions)]
   │ 
   ├── CTR (Click-Through Rate): Tỷ lệ bấm vào link (Chuẩn: 1.5% - 3.5%)
   ▼
[2. TRUY CẬP WEBSITE / GIAN HÀNG (Store Visits / Traffic)]
   │
   ├── Bounce Rate (Tỷ lệ thoát trang): Khách rời đi ngay mà không tương tác (< 40%)
   ├── Product View Rate: Xem chi tiết sản phẩm (> 60%)
   ▼
[3. THÊM SẢN PHẨM VÀO GIỎ HÀNG (Add to Cart - ATC)]
   │
   ├── ATC Rate: Tỷ lệ thêm vào giỏ / Tổng lượt xem (Chuẩn: 8% - 15%)
   ▼
[4. BẤM TIẾN HÀNH THANH TOÁN (Initiate Checkout)]
   │
   ├── Cart Abandonment Rate (Tỷ lệ bỏ quên giỏ hàng): (Thực tế TMĐT: 65% - 75%)
   ▼
[5. ĐẶT HÀNG THÀNH CÔNG (Order Completed)]
   │
   └── Overall CVR: Tỷ lệ chuyển đổi tổng thể (Đơn mua / Lượt truy cập: 1.5% - 3.0%)
```

### Công thức Chẩn đoán Bệnh từ Phễu của AI:
- **Nếu Impressions cao nhưng CTR thấp**: Hình ảnh sản phẩm xấu, tiêu đề không hấp dẫn, giá niêm yết ngoài bìa không cạnh tranh.
- **Nếu CTR cao nhưng ATC (Thêm giỏ) thấp**: Khách vào nhưng nội dung trang chi tiết sản phẩm sơ sài, thiếu review đánh giá uy tín, hoặc thông số kỹ thuật không rõ ràng.
- **Nếu ATC cao nhưng Checkout thấp (Bỏ giỏ hàng > 80%)**: Phí ship quá đắt, không có phương thức thanh toán phù hợp (thiếu COD hoặc thiếu Trả góp 0%), hoặc quy trình điền thông tin quá rườm rà.
