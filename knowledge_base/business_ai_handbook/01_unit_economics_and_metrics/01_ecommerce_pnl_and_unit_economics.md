# MODULE 1.1: BÁO CÁO P&L VÀ KINH TẾ ĐƠN VỊ (UNIT ECONOMICS) TRONG BÁN LẺ & E-COMMERCE

---

## 1. TỔNG QUAN VỀ BÁO CÁO TÀI CHÍNH P&L TRONG E-COMMERCE
Trong kinh doanh bán lẻ và thương mại điện tử (E-Commerce), sai lầm phổ biến nhất của các chủ shop là **chỉ nhìn vào GMV (Tổng giá trị giao dịch) hoặc Doanh số trên bảng điều khiển sàn TMĐT** mà ngộ nhận rằng cửa hàng đang có lãi. Một AI chuyên gia kinh doanh phải nắm rõ từng tầng bậc của Báo cáo Kết quả Hoạt động Kinh doanh (P&L - Profit and Loss Statement) và cấu trúc Kinh tế Đơn vị (Unit Economics).

### Sơ đồ Bậc thang Dòng tiền (Waterfall P&L):
```
[GMV - Tổng giá trị đơn hàng đặt]
   │
   ├── (-) Đơn hủy trước khi giao (Pre-ship Cancellation)
   └── (-) Đơn giao thất bại / Hoàn trả COD (Returns & Refused Delivery)
   │
[DOANH THU THỰC NHẬN / THÀNH CÔNG (Delivered Net Revenue)]
   │
   ├── (-) Giá vốn hàng bán (COGS: Giá nhập + Chi phí vận chuyển về kho)
   ├── (-) Phí đóng gói trực tiếp (Bao bì, hộp carton, xốp nổ, băng keo)
   ├── (-) Phí sàn cố định & Phí thanh toán (Marketplace Commissions & Gateway Fees)
   │
[BIÊN ĐÓNG GÓP TẦNG 1: CM1 (Gross Contribution Margin)]
   │
   ├── (-) Chi phí Quảng cáo Trực tiếp (Performance Ads: Facebook, Google, TikTok Ads)
   ├── (-) Phí Tiếp thị Liên kết (KOL/KOC Affiliate Commission)
   ├── (-) Chi phí Voucher/Khuyến mãi trực tiếp của Shop (Shop Funded Discounts)
   │
[BIÊN ĐÓNG GÓP TẦNG 2: CM2 (Unit Marketing Contribution Margin)]
   │
   ├── (-) Chi phí Kho bãi & Xử lý đơn hàng (Warehousing & Pick/Pack Labor)
   ├── (-) Chi phí tổn thất do Hoàn đơn (2 chiều ship + Hàng hư hỏng sau hoàn)
   ├── (-) Chi phí Chăm sóc khách hàng & Bảo hành trực tiếp
   │
[BIÊN ĐÓNG GÓP TẦNG 3: CM3 (Direct Operating Margin)]
   │
   ├── (-) Chi phí Cố định (Fixed Overhead: Lương văn phòng, Mặt bằng, Phần mềm SaaS)
   ├── (-) Chi phí Khấu hao tài sản & Lãi vay (Depreciation & Interest)
   │
[LỢI NHUẬN RÒNG TRƯỚC THUẾ (EBT / Net Operating Profit)]
   │
   └── (-) Thuế TNDN / Thuế Hộ kinh doanh TMĐT (Taxes)
   │
[LỢI NHUẬN RÒNG CUỐI CÙNG (Net Profit / Bottom Line)]
```

---

## 2. CÔNG THỨC VÀ Ý NGHĨA CÁC CHỈ SỐ KINH TẾ ĐƠN VỊ

### 2.1. GMV vs. Doanh thu Gộp vs. Doanh thu Thuần
1. **GMV (Gross Merchandise Value)**: Tổng giá trị hàng hóa được khách hàng bấm đặt mua (chưa trừ hủy đơn, giảm giá sàn, chưa tính hoàn hàng).
$$\text{GMV} = \sum (\text{Số lượng đặt} \times \text{Giá niêm yết})$$

2. **Gross Revenue (Doanh thu gộp)**: Tổng số tiền khách hàng cam kết thanh toán sau khi trừ các mã giảm giá của shop nhưng trước khi đơn hàng xuất kho.

3. **Net Revenue (Doanh thu thuần)**: Doanh thu thực tế của các đơn hàng đã được giao thành công và đối soát tiền về tài khoản ngân hàng.
$$\text{Net Revenue} = \text{GMV} - \text{Hủy trước giao} - \text{Hoàn đơn COD} - \text{Chiết khấu thương mại}$$

> [!IMPORTANT]
> **Quy tắc bắt buộc cho AI**: Mọi chỉ số tính toán Lợi nhuận, ROI, ROAS và Khả năng thanh toán nợ phải được tính trên **Net Revenue (Doanh thu đã đối soát)**, tuyệt đối không tính trên GMV.

---

### 2.2. Phân Tầng Biên Đóng Góp (Contribution Margins - CM)

#### A. CM1: Biên đóng góp gộp (Gross Contribution Margin)
Phản ánh hiệu quả của sản phẩm lõi sau khi trừ đi các chi phí biến đổi cơ bản gắn liền với sản phẩm đó:
$$\text{CM1} = \text{Net Revenue} - \text{COGS} - \text{Packaging Costs} - \text{Payment/Platform Direct Fees}$$
$$\text{CM1 \%} = \frac{\text{CM1}}{\text{Net Revenue}} \times 100\%$$
- **Benchmark chuẩn cho ngành Bán lẻ Công nghệ (PC / Laptop / Linh kiện)**: $\text{CM1 \%} \ge 12\% - 20\%$. (Đối với phụ kiện công nghệ: $\ge 40\% - 50\%$).
- **Nếu $\text{CM1 \%} < 10\%$**: Cửa hàng đang bán phá giá hoặc giá nhập hàng từ nhà phân phối quá cao, không có đủ biên độ an toàn để chạy quảng cáo.

#### B. CM2: Biên đóng góp sau tiếp thị (Marketing Contribution Margin)
Đây là chỉ số sống còn để đánh giá chiến lược thu hút khách hàng có tạo ra lợi nhuận hay đang "bán lỗ để lấy doanh số":
$$\text{CM2} = \text{CM1} - \text{Performance Ad Spend} - \text{Affiliate Commissions} - \text{Influencer Fees}$$
$$\text{CM2 \%} = \frac{\text{CM2}}{\text{Net Revenue}} \times 100\%$$
- **Nếu $\text{CM2} > 0$**: Mỗi đơn hàng bán ra mang lại tiền dương sau khi đã tự bù đắp toàn bộ chi phí quảng cáo và giá vốn.
- **Nếu $\text{CM2} < 0$**: Shop đang "bán một đơn lỗ một đơn" (Unit loss). Càng tăng trưởng doanh số thì cửa hàng càng nhanh cạn kiệt tiền mặt (Cash burn).

#### C. CM3: Biên đóng góp vận hành trực tiếp (Direct Operating Margin)
Bao gồm chi phí vận hành kho, nhân sự đóng gói, chi phí xử lý đơn hoàn và bảo hành:
$$\text{CM3} = \text{CM2} - \text{Fulfillment Labor} - \text{Warehouse Storage} - \text{Return Handling Loss}$$
- CM3 là dòng tiền thực sự chảy về để chi trả cho bộ máy cố định của công ty (lương giám đốc, mặt bằng, kế toán, phần mềm, server).

---

## 3. ĐẶC THÙ THỊ TRƯỜNG BÁN LẺ & TMĐT VIỆT NAM

Khi AI phân tích kinh doanh cho shop tại Việt Nam, AI **bắt buộc** phải tích hợp 3 yếu tố sau vào mô hình tính toán:

### 3.1. Phí Nền Tảng Sàn Thương Mại Điện Tử (Shopee, TikTok Shop, Lazada)
Cơ cấu biểu phí sàn thường bao gồm 3 loại phí bắt buộc:
1. **Phí thanh toán (Payment Fee)**: Thường từ $4.54\% - 5\%$ tính trên tổng giá trị người mua thanh toán (bao gồm cả tiền ship).
2. **Phí cố định / Hoa hồng sàn (Commission Fee)**:
   - Shopee Mall / Shop Thường: $4.0\% - 9.0\%$ tùy theo ngành hàng (Ngành Điện tử/Máy tính thường từ $4\% - 6\%$, ngành Phụ kiện từ $7\% - 9\%$).
3. **Phí dịch vụ các gói hỗ trợ (Freeship Xtra, Voucher Xtra)**:
   - Dao động từ $6.0\% - 8.0\%$ (thường có mức trần tối đa per SKU, ví dụ tối đa 40.000 VNĐ - 50.000 VNĐ/sản phẩm).

**Công thức tổng phí sàn TMĐT thực tế trên một đơn hàng:**
$$\text{Tỷ lệ Phí Sàn} \approx 14\% - 18\% \text{ (nếu tham gia đầy đủ gói Freeship + Voucher Xtra)}$$

---

### 3.2. Hiểm Họa Hoàn Đơn COD (Cash on Delivery) & "Boom Hàng"
Tại Việt Nam, tỷ lệ thanh toán khi nhận hàng (COD) chiếm tỷ trọng từ $40\% - 70\%$ trên các kênh mạng xã hội (Facebook, TikTok) và $20\% - 30\%$ trên các sàn TMĐT.
- **Tỷ lệ hoàn đơn trung bình (Return Rate - $R_r$)**:
  - Hàng linh kiện máy tính, đồ công nghệ giá trị cao: $3\% - 7\%$ (Chấp nhận được nếu $< 5\%$).
  - Bán qua livestream TikTok Shop / Facebook ads chốt nóng: $12\% - 25\%$.
- **Tổn thất trên một đơn hoàn**:
  1. Mất chi phí đóng gói (Hộp, xốp nổ: 5.000 - 15.000 VNĐ).
  2. Phí vận chuyển 2 chiều (Chiều đi + chiều về, thông thường đơn vị vận chuyển tính 100% cước đi + 50% cước về nếu giao không thành công).
  3. Hao mòn sản phẩm (Hộp méo mó, trầy xước không thể bán như hàng New 100%, nguy cơ tráo hàng).
  4. Chi phí cơ hội (Hàng bị giam 10 - 20 ngày trên đường đi và về không bán được cho người khác).

#### Công thức tính Chi Phí Thực Tế Trên Mỗi Đơn Thành Công (True Cost Per Delivered Order):
Nếu tỷ lệ hoàn đơn là $r$ (ví dụ $r = 0.10$ tức 10%), thì để giao thành công 1 đơn, shop phải chịu tải chi phí của $\frac{r}{1 - r}$ đơn bị hoàn:
$$\text{True Fulfillment Cost} = \text{Fulfill}_{\text{success}} + \left( \frac{r}{1 - r} \right) \times \left( \text{Shipping}_{\text{roundtrip}} + \text{Packaging Loss} + \text{Depreciation Loss} \right)$$

---

### 3.3. Thuế Giá Trị Gia Tăng (VAT) & Nghĩa Vụ Thuế TMĐT
- **Thuế GTGT (VAT)**: 8% hoặc 10% tùy danh mục linh kiện theo nghị định giảm thuế của Chính phủ.
- **Hộ kinh doanh cá thể trên sàn TMĐT**:
  - Thuế GTGT: $1\%$ trên doanh thu.
  - Thuế Thu nhập cá nhân (TNCN): $0.5\%$ trên doanh thu.
  - Tổng thuế phải nộp: $1.5\%$ trên tổng doanh thu phát sinh trên sàn (Hiện nay sàn TMĐT khấu trừ hoặc cung cấp dữ liệu trực tiếp cho Tổng cục Thuế).
- **Doanh nghiệp (Công ty TNHH/Cổ phần)**:
  - Thuế Thu nhập doanh nghiệp (TNDN): $20\%$ trên Lợi nhuận trước thuế.

---

## 4. VÍ DỤ MINH HỌA TÍNH TOÁN KINH TẾ ĐƠN VỊ THỰC TẾ
Giả sử Shop bán một sản phẩm **CPU AMD Ryzen 5 7600X**:

| Khoản mục chi phí | Số tiền (VNĐ) | Tỷ lệ / Doanh thu (%) | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Giá bán niêm yết (Gross Price)** | **5.800.000** | 100.0% | Giá khách mua |
| Khách áp voucher của Shop | - 200.000 | - 3.4% | Trừ trực tiếp |
| **Doanh thu thuần (Net Revenue)** | **5.600.000** | 96.6% | Thực nhận trước phí |
| **Giá vốn hàng bán (COGS)** | - 4.800.000 | - 82.8% | Giá nhập từ nhà phân phối |
| Chi phí hộp carton + xốp bảo vệ CPU | - 20.000 | - 0.3% | Đóng gói chống sốc |
| Phí sàn TMĐT (Shopee/Lazada: 7%) | - 392.000 | - 6.8% | Phí thanh toán + Cố định |
| **BIÊN ĐÓNG GÓP CM1** | **+ 388.000** | **+ 6.7%** | **Lãi gộp sau phí sàn** |
| Chi phí Ad Spend Facebook/TikTok (CAC) | - 180.000 | - 3.1% | Chi phí quảng cáo ra 1 đơn |
| **BIÊN ĐÓNG GÓP CM2** | **+ 208.000** | **+ 3.6%** | **Lãi sau tiếp thị** |
| Dự phòng hoàn hàng COD (4% tỷ lệ hoàn) | - 35.000 | - 0.6% | Tính bình quân trên 1 đơn |
| Chi phí nhân sự kho + bảo hành | - 40.000 | - 0.7% | Phí vận hành trực tiếp |
| **BIÊN ĐÓNG GÓP CM3** | **+ 133.000** | **+ 2.3%** | **Lãi vận hành trực tiếp** |

### Nhận xét & Khuyến nghị của AI cho trường hợp này:
> "Sản phẩm CPU Ryzen 5 7600X có tỷ lệ giá vốn cao (82.8%) và biên CM1 chỉ đạt 6.7%. Sau khi trừ chi phí quảng cáo (180.000đ), biên CM2 còn 3.6% và CM3 chỉ còn 2.3% (133.000đ).
> **Hành động chiến lược:** Tuyệt đối không chi thêm tiền cho quảng cáo độc lập cho CPU này (nếu CAC tăng lên > 300.000đ shop sẽ bị âm CM2). Hãy dùng sản phẩm này làm **Sản phẩm mồi (Hook Product)** và ép khách hàng mua kèm (Bundle) với Tản nhiệt nước (AIO Cooler), Mainboard B650 hoặc RAM DDR5 có biên lợi nhuận CM1 > 25% để kéo tổng biên lợi nhuận giỏ hàng lên > 12%."
