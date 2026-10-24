# MODULE 2.2: CHIẾN LƯỢC ĐỊNH GIÁ & ĐỘ CO GIÃN CỦA CẦU (PRICING STRATEGIES & ELASTICITY)

---

## 1. ĐỘ CO GIÃN CỦA CẦU THEO GIÁ (PRICE ELASTICITY OF DEMAND - PED)

### 1.1. Công thức và Bản chất Kinh tế
Độ co giãn của cầu theo giá ($E_d$) đo lường mức độ phản ứng của số lượng hàng bán ra khi giá bán của sản phẩm thay đổi:

$$E_d = \frac{\% \text{ Biến động lượng cầu } (\Delta Q)}{\% \text{ Biến động giá bán } (\Delta P)}$$

Khi sử dụng dữ liệu thực tế tại hai thời điểm $(P_1, Q_1)$ và $(P_2, Q_2)$, AI phải sử dụng **Công thức Co giãn Điểm giữa (Midpoint Arc Elasticity)** để kết quả không bị phụ thuộc vào chiều tăng hay giảm:

$$E_d = \frac{(Q_2 - Q_1) / (Q_2 + Q_1)}{(P_2 - P_1) / (P_2 + P_1)}$$

### 1.2. Phân loại và Ý nghĩa Hành động trong Bán lẻ

| Giá trị $|E_d|$ | Phân loại | Hành vi Khách hàng | Hành động Chiến lược cho AI |
| :---: | :---: | :--- | :--- |
| **$|E_d| > 1$** | **Co giãn (Elastic)** | Khách hàng cực kỳ nhạy cảm về giá (ví dụ: Linh kiện phổ thông như Core i3, Chuột văn phòng). | **Không được tự ý tăng giá**. Nếu giảm giá nhẹ, sản lượng sẽ tăng mạnh đủ để bù đắp và làm tăng tổng doanh thu. |
| **$|E_d| < 1$** | **Kém co giãn (Inelastic)** | Khách hàng ít quan tâm đến giá (Hàng độc quyền, Card đồ họa cao cấp RTX 4090, Dịch vụ sửa chữa cấp tốc). | **Có thể tăng giá**. Mức giảm sản lượng sẽ rất nhỏ, làm tăng cả Tổng Doanh Thu và Biên Lợi Nhuận Ròng. |
| **$|E_d| = 1$** | **Co giãn đơn vị (Unitary)** | Tỷ lệ thay đổi lượng cầu đúng bằng tỷ lệ thay đổi giá. | Doanh thu đạt cực đại. Muốn tăng lợi nhuận phải tìm cách giảm giá vốn COGS. |

---

## 2. CÔNG THỨC ĐIỀU KIỆN HÒA VỐN KHI THAY ĐỔI GIÁ BÁN (BREAKEVEN VOLUME UNDER PRICE CHANGE)

Đây là công thức toán học tối quan trọng mà AI bắt buộc phải chạy mỗi khi chủ shop có ý định giảm giá hoặc khuyến mãi:

> **Bài toán:** Nếu shop đang có Biên Lợi Nhuận Gộp hiện tại là $M = \frac{P - C}{P}$, khi quyết định **giảm giá $x\%$**, thì sản lượng bán ra phải tăng thêm ít nhất bao nhiêu $\%$ ($\%\Delta Q$) để **Tổng Lợi Nhuận Gộp không bị sụt giảm**?

$$\%\Delta Q_{\text{breakeven}} = \frac{x\%}{M - x\%}$$

### Bảng Ma Trận Hòa Vốn Sản Lượng (Breakeven Sales Multiplier Matrix):

| Biên Lợi Nhuận Gộp Hiện Tại ($M$) | Giảm giá 5% | Giảm giá 10% | Giảm giá 15% | Giảm giá 20% |
| :---: | :---: | :---: | :---: | :---: |
| **15%** (Ngành Laptop / PC lắp ráp) | **+ 50.0%** | **+ 200.0%** | $\infty$ (Phá sản) | Âm vốn |
| **25%** (Ngành Màn hình, Ghế Gaming) | **+ 25.0%** | **+ 66.7%** | **+ 150.0%** | **+ 400.0%** |
| **40%** (Phụ kiện Phím, Chuột, Tai nghe)| **+ 14.3%** | **+ 33.3%** | **+ 60.0%** | **+ 100.0%** |

> [!CAUTION]
> **Cảnh báo cực độ cho AI CCO:**
> Nhìn vào bảng trên, nếu một chiếc PC ráp sẵn có biên lãi gộp là **$15\%$**, nếu chủ shop "hứng lên" tung voucher giảm giá **$10\%$**, thì lượng đơn hàng bán ra **phải tăng gấp 3 lần (+200%)** chỉ để thu về số tiền lãi bằng với lúc chưa giảm giá! Nếu không đạt mức tăng gấp 3, shop đang làm việc không công cho đơn vị vận chuyển và khách hàng.

---

## 3. CÁC CHIẾN LƯỢC ĐỊNH GIÁ KINH ĐIỂN TRONG BÁN LẺ THỰC CHIẾN

### 3.1. Chiến Lược Sản Phẩm Mồi (Loss-Leader Pricing)
- **Cơ chế**: Cố tình bán một mã hàng cực kỳ nổi tiếng, có nhu cầu cao ở mức **giá siêu rẻ (sát giá vốn, biên lợi nhuận 0% - 2%)** để kéo toàn bộ lượt tìm kiếm và khách hàng từ đối thủ về website/gian hàng của mình.
- **Cách thu lại lợi nhuận**: Thiết lập quy tắc trên hệ thống buộc hoặc gợi ý khách hàng mua kèm phụ kiện (Phím chuột, Pad lót, Nguồn, Tản nhiệt, Dây cáp, Gói bảo hành vàng) có biên lợi nhuận gộp từ $35\% - 50\%$.
- **Điều kiện bảo toàn dòng tiền**:
  $$\text{Doanh thu Combo} \times \text{Biên Lãi Gộp Combo} > \text{Lợi nhuận mục tiêu mong muốn}$$

---

### 3.2. Chiến Lược Chim Mồi & 3 Bậc Giá (Decoy Pricing & Good-Better-Best)
Tâm lý học hành vi người tiêu dùng thường tránh sản phẩm rẻ nhất (sợ chất lượng kém) và ngần ngại sản phẩm đắt nhất (sợ tốn tiền), từ đó sẽ chọn sản phẩm ở giữa.

**Cấu trúc thiết lập 3 gói của AI:**
1. **Gói Cơ bản (Good - Chim mồi cấp thấp)**: Cấu hình đủ chạy, giá rẻ nhưng tính năng bị cắt giảm rõ rệt (ví dụ: RAM 8GB, SSD 256GB - 10.000.000đ).
2. **Gói Mục Tiêu (Better - Nơi shop dồn margin)**: Cấu hình nâng cấp vượt trội hoàn toàn so với gói cơ bản nhưng giá chỉ chênh lệch nhẹ (ví dụ: RAM 16GB, SSD 512GB, Tản khí RGB - 12.500.000đ). Biên lãi gộp tối ưu $18\%$.
3. **Gói Cao Cấp (Best - Mồi neo giá cao)**: Cấu hình cao cấp với giá rất đắt để làm cho gói "Better" trông cực kỳ rẻ và hợp lý (ví dụ: 19.000.000đ).

---

### 3.3. Chiến Lược Bán Gói Kết Hợp (Bundle Pricing)
Bán các sản phẩm bổ trợ lẫn nhau với mức chiết khấu nhẹ so với mua lẻ từng món, giúp tăng Giá trị Trung bình Đơn hàng (AOV) và giảm chi phí đóng gói/vận chuyển trên mỗi đơn vị hàng hóa.

**Công thức xác định giá Combo tối ưu:**
$$\text{Giá Combo} = (\text{Giá bán lẻ A} + \text{Giá bán lẻ B}) \times (1 - d)$$

Trong đó tỷ lệ giảm giá combo $d$ phải thỏa mãn điều kiện:
$$d < \frac{\text{Lợi ích tiết kiệm chi phí đóng gói \& ship} + \text{Tăng biên lợi nhuận gộp nhờ số lượng}}{\text{Tổng doanh thu bán lẻ A + B}}$$

---

### 3.4. Lộ Trình Hạ Giá Thanh Lý Kho (Markdown Optimization Schedule)
Đối với các mặt hàng thuộc nhóm **Slow-moving** hoặc **Non-moving** theo phân tích tồn kho, AI sẽ tự động kích hoạt lộ trình giảm giá theo từng bậc thời gian thay vì để tồn đọng:

```
[Sản phẩm tồn kho > 45 ngày]
         │
         ├── Tuần 1: Giảm 5% (Gắn nhãn: Deal chớp nhoáng tuần này)
         │
         ├── Tuần 2: Giảm 10% (Tạo combo mua 1 tặng 1 phụ kiện tồn)
         │
         ├── Tuần 3: Giảm về Giá vốn (At Cost - Thu hồi 100% dòng tiền mặt)
         │
         └── Tuần 4: Giảm dưới giá vốn 10% (Chấp nhận cắt lỗ để giải phóng mặt bằng kho
                     và đưa tiền vào các mã hàng Nhóm A sinh lời cao)
```
