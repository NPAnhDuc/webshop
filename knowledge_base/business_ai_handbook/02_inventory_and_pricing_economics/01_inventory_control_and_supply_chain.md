# MODULE 2.1: QUẢN TRỊ TỒN KHO & CHUỖI CUNG ỨNG BÁN LẺ (INVENTORY CONTROL & SUPPLY CHAIN)

---

## 1. TẦM QUAN TRỌNG CỦA TỒN KHO TRONG BÁN LẺ CÔNG NGHỆ
Trong ngành bán lẻ thiết bị điện tử và linh kiện vi tính, **tồn kho chính là "tiền mặt bị đóng băng"**. Đặc thù của ngành công nghệ là tốc độ giảm giá và lỗi thời sản phẩm cực kỳ nhanh:
- Khi Intel hoặc AMD ra mắt thế hệ vi xử lý (CPU) mới, các dòng cũ có thể mất giá từ $15\% - 30\%$ chỉ sau một đêm.
- Nếu giữ lượng tồn quá lớn (Overstocking), shop sẽ bị thâm hụt dòng tiền và chịu chi phí lưu kho khổng lồ.
- Nếu giữ lượng tồn quá ít (Understocking), shop sẽ bị đứt hàng (Stockout), mất khách vào tay đối thủ và rớt thứ hạng hiển thị trên các thuật toán sàn TMĐT.

---

## 2. CÁC CHỈ SỐ ĐO LƯỜNG TỐC ĐỘ XOAY VÒNG TỒN KHO

### 2.1. Vòng Quay Tồn Kho (Inventory Turnover Ratio - ITR)
Đo lường số lần mà lượng hàng tồn kho bình quân được bán hết và thay thế trong một khoảng thời gian nhất định (thường tính theo năm hoặc quý).

$$\text{ITR} = \frac{\text{Giá vốn hàng bán trong kỳ (COGS)}}{\text{Giá trị tồn kho bình quân (Average Inventory)}}$$

Trong đó:
$$\text{Average Inventory} = \frac{\text{Giá trị tồn kho đầu kỳ} + \text{Giá trị tồn kho cuối kỳ}}{2}$$

- **Ý nghĩa chỉ số:**
  - ITR cao chứng tỏ hàng bán nhanh, vốn quay vòng tốt, ít bị ứ đọng vốn.
  - Tuy nhiên, nếu ITR quá cao (ví dụ $> 20$ vòng/năm), có thể shop đang nhập số lượng quá nhỏ giọt, dẫn đến chi phí vận chuyển mỗi lần nhập hàng tăng cao và nguy cơ đứt hàng liên tục.

### 2.2. Số Ngày Tồn Kho Bình Quân (Days of Inventory Outstanding - DIO)
Đo lường số ngày trung bình cần thiết để một sản phẩm từ lúc nhập về kho cho đến khi được bán thành công cho khách hàng.

$$\text{DIO} = \frac{\text{Average Inventory}}{\text{COGS}} \times 365 = \frac{365}{\text{ITR}}$$

- **Benchmark chuẩn cho ngành Bán lẻ Máy tính & Đồ Công nghệ:**
  - Nhóm linh kiện chính (CPU, VGA, RAM, SSD): **15 - 30 ngày** (Vòng quay 12 - 24 lần/năm).
  - Nhóm phụ kiện (Vỏ case, Nguồn, Tản nhiệt, Phím, Chuột): **30 - 45 ngày**.
  - Hàng cồng kềnh / Ghế gaming / Bàn nâng hạ: **20 - 35 ngày**.
  - **BÁO ĐỘNG ĐỎ:** Bất kỳ mã SKU nào có $\text{DIO} > 60 \text{ ngày}$ được coi là **Hàng quay chậm (Slow-moving)**; $\text{DIO} > 90 \text{ ngày}$ là **Hàng ứ đọng / Hàng chết (Deadstock)** cần thanh lý khẩn cấp.

### 2.3. Tỷ Lệ Bán Hết (Sell-Through Rate - STR)
Đo lường tỷ lệ phần trăm số lượng hàng bán ra so với tổng số lượng hàng sẵn có trong kho trong một tháng hoặc một chiến dịch:

$$\text{STR} = \frac{\text{Số lượng sản phẩm bán ra}}{\text{Số lượng tồn đầu kỳ} + \text{Số lượng nhập thêm trong kỳ}} \times 100\%$$

- **STR < 40% trong tháng đầu tiên nhập về**: Cảnh báo sản phẩm kém hấp dẫn hoặc định giá sai, cần kích hoạt chương trình khuyến mãi sớm.
- **STR > 85% trong 2 tuần đầu**: Sản phẩm "cháy hàng", cần đặt hàng bổ sung khẩn cấp để tránh mất doanh thu.

---

## 3. CÁC MÔ HÌNH ĐỊNH LƯỢNG TỐI ƯU HÓA ĐẶT HÀNG

### 3.1. Lượng Đặt Hàng Kinh Tế (Economic Order Quantity - EOQ)
Mô hình EOQ tìm điểm cân bằng hoàn hảo giữa **Chi phí đặt hàng (Ordering Cost)** và **Chi phí lưu kho (Holding Cost)** nhằm giảm thiểu tổng chi phí quản lý hàng tồn kho.

$$\text{EOQ} = \sqrt{\frac{2 \cdot D \cdot S}{H}}$$

Trong đó:
- $D$ = Nhu cầu hàng năm của sản phẩm (Annual Demand - đơn vị: sản phẩm).
- $S$ = Chi phí cố định cho mỗi lần thực hiện một đơn đặt hàng nhập kho (Ordering Cost - bao gồm phí giấy tờ, công kiểm đếm, cước vận chuyển lô hàng).
- $H$ = Chi phí lưu trữ và giữ 1 đơn vị sản phẩm trong kho trong 1 năm (Annual Holding Cost per unit).
  $$H = \text{Tỷ lệ chi phí lưu kho hàng năm } (I) \times \text{Giá vốn đơn vị } (C)$$

```
Chi phí
  ▲
  │ \                         / Tổng chi phí (Total Cost)
  │  \                       /
  │   \                     /  Chi phí lưu kho (Holding Cost)
  │    \       EOQ         /
  │     \       │         /
  │      \______│________/
  │       \     │       /
  │        \    │      /       Chi phí đặt hàng (Ordering Cost)
  │         \___│_____/
  └─────────────┴──────────────────► Số lượng đặt hàng (Q)
```

---

### 3.2. Mức Tồn Kho An Toàn (Safety Stock - SS)
Tồn kho an toàn là lớp đệm bảo vệ shop trước 2 rủi ro không lường trước:
1. Nhu cầu thị trường tăng đột biến (Demand Fluctuation).
2. Nhà cung cấp giao hàng trễ hẹn (Lead Time Delay).

Khi cả Nhu cầu hàng ngày ($D$) và Thời gian giao hàng của NCC ($L$) đều biến thiên ngẫu nhiên theo phân phối chuẩn:
$$\text{SS} = Z \times \sqrt{\bar{L} \cdot \sigma_D^2 + \bar{D}^2 \cdot \sigma_L^2}$$

Trong đó:
- $Z$: Hệ số mức độ phục vụ (Service Level Factor).
  - Service Level $95\%$ (cho phép hết hàng $5\%$ số lần): $Z = 1.65$.
  - Service Level $98\%$: $Z = 2.05$.
  - Service Level $99\%$ (cho các mặt hàng cốt lõi tạo doanh số): $Z = 2.33$.
- $\bar{L}$: Thời gian giao hàng trung bình của nhà phân phối (ngày).
- $\sigma_L$: Độ lệch chuẩn của thời gian giao hàng (đo lường mức độ trễ hẹn).
- $\bar{D}$: Số lượng bán trung bình mỗi ngày (Daily Demand).
- $\sigma_D$: Độ lệch chuẩn của số lượng bán hàng ngày.

*Nếu thời gian giao hàng cố định ($L = \text{const}$, tức $\sigma_L = 0$), công thức rút gọn thành:*
$$\text{SS} = Z \times \sigma_D \times \sqrt{L}$$

---

### 3.3. Điểm Đặt Hàng Lại (Reorder Point - ROP)
Mức tồn kho báo động mà khi lượng hàng trong kho giảm xuống tới con số này, hệ thống AI phải lập tức gửi cảnh báo tạo đơn nhập hàng mới:

$$\text{ROP} = (\bar{D} \times \bar{L}) + \text{SS}$$

**Ví dụ thực tế**:
- Một shop bán CPU Core i5-14400F trung bình $\bar{D} = 5$ chiếc/ngày, độ lệch chuẩn $\sigma_D = 2$ chiếc/ngày.
- Nhà phân phối mất trung bình $\bar{L} = 4$ ngày để giao hàng tới kho shop.
- Chọn Service Level $95\%$ ($Z = 1.65$).
- Tồn kho an toàn: $\text{SS} = 1.65 \times 2 \times \sqrt{4} = 6.6 \approx 7 \text{ chiếc}$.
- Điểm đặt hàng lại: $\text{ROP} = (5 \times 4) + 7 = 27 \text{ chiếc}$.
- **Chỉ dẫn cho AI**: "Khi số lượng tồn kho khả dụng của i5-14400F chạm mốc 27 chiếc, hệ thống phải tự động đề xuất tạo PO (Purchase Order) nhập lô hàng tiếp theo với số lượng đúng bằng EOQ."

---

## 4. CHI PHÍ LƯU KHO THỰC TẾ (HOLDING COST BREAKDOWN)
Rất nhiều chủ shop chỉ tính tiền thuê kho khi nói về chi phí tồn kho. Đây là thiếu sót chí tử. Tổng chi phí lưu kho hàng năm ($I$) thường chiếm từ **$25\% - 35\%$ tổng giá trị tồn kho**:

1. **Chi phí vốn (Capital Opportunity Cost)**: $10\% - 15\%$ (Lãi suất vay ngân hàng hoặc lợi nhuận nếu đem số tiền đọng trong kho đi đầu tư việc khác).
2. **Chi phí mất giá công nghệ & Lỗi thời (Obsolescence / Depreciation)**: $8\% - 14\%$ (Linh kiện điện tử giảm giá liên tục khi dòng mới ra mắt).
3. **Chi phí kho bãi vật lý & Tiện ích**: $3\% - 5\%$ (Tiền thuê mặt bằng, điều hòa hút ẩm bảo quản đồ điện tử, camera giám sát).
4. **Chi phí hao hụt & Hư hại (Shrinkage & Damage)**: $2\% - 3\%$ (Rơi vỡ, móp méo vỏ hộp, tráo đồ, chuột bọ cắn dây cáp).

---

## 5. PHÂN LOẠI DANH MỤC HÀNG HÓA THEO MA TRẬN ABC - FSN

### 5.1. Phân loại ABC (Dựa trên Nguyên lý Pareto 80/20 về Doanh thu/Lợi nhuận)
- **Nhóm A (Sản phẩm sống còn)**: Chiếm $15\% - 20\%$ tổng số mã SKU nhưng mang lại **$70\% - 80\%$ Doanh thu/Lợi nhuận gộp** (Ví dụ: CPU, VGA phân khúc phổ thông bán chạy).
  - *Chính sách AI*: Theo dõi tồn kho hàng ngày (Daily cycle count), đặt Service Level cao $98\% - 99\%$, tuyệt đối không được để đứt hàng.
- **Nhóm B (Sản phẩm bổ trợ)**: Chiếm $30\%$ số mã SKU, mang lại $15\% - 20\%$ Doanh thu (RAM, SSD, Nguồn PSU, Màn hình văn phòng).
  - *Chính sách AI*: Theo dõi hàng tuần, đặt hàng theo mô hình EOQ chuẩn, Service level $90\% - 95\%$.
- **Nhóm C (Sản phẩm đuôi dài - Long tail)**: Chiếm $50\%$ số mã SKU nhưng chỉ mang lại **$5\% - 10\%$ Doanh thu** (Các loại cáp chuyển đổi chuyên biệt, ốc vít độ case, tản nhiệt custom kén người dùng).
  - *Chính sách AI*: Giảm thiểu nhập số lượng lớn, chỉ nhập khi có đơn hàng (Just-In-Time) hoặc duy trì tồn kho tối thiểu 1 - 2 đơn vị.

### 5.2. Ma trận FSN (Fast, Slow, Non-moving)
- **Fast-moving (F)**: Sản phẩm có tốc độ bán $< 15$ ngày/lô.
- **Slow-moving (S)**: Sản phẩm bán từ $16 - 60$ ngày.
- **Non-moving (N)**: Không có bất kỳ đơn hàng nào phát sinh trong $> 60$ ngày.
  - *Quy tắc AI*: Tự động kích hoạt cơ chế "Cảnh báo xả hàng": Đề xuất hạ giá bán về giá hòa vốn hoặc tạo combo quà tặng kèm với Nhóm A để thu hồi dòng tiền trước khi sản phẩm mất giá hoàn toàn.
