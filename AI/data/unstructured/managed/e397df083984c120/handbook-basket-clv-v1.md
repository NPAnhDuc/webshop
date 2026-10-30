# Phân tích giỏ hàng (support, confidence, lift) và CLV xác suất

> Tài liệu phương pháp nội bộ (handbook phân tích kinh doanh), chỉ dành cho quản lý. Mọi con số trong ví dụ là minh họa, KHÔNG phải số liệu của shop. Số liệu shop (doanh thu, giá vốn, đơn, tồn kho) chỉ lấy từ công cụ SQL/báo cáo trên database data/business_sql/scenario_v1/shop.sqlite (dữ liệu mô phỏng 01/10/2025–30/09/2026).

# MODULE 4.2: KHAI PHÁ GIỎ HÀNG (MARKET BASKET) & DỰ BÁO GIÁ TRỊ VÒNG ĐỜI (CLV)

---

## 1. KHAI PHÁ LUẬT KẾT HỢP GIỎ HÀNG (MARKET BASKET ANALYSIS - APRIORI & LIFT)

### 1.1. Khái niệm và Công thức Toán học
Mục tiêu là tìm ra các quy tắc dạng: **"Nếu khách hàng mua sản phẩm A (Antecedent), xác suất rất cao họ sẽ mua thêm sản phẩm B (Consequent)"**.

Có 3 chỉ số toán học quyết định:
1. **Độ hỗ trợ (Support)**: Tỷ lệ phần trăm đơn hàng chứa cả sản phẩm A và B trên tổng số đơn:
   $$\text{Support}(A \rightarrow B) = \frac{\text{Số đơn hàng chứa cả A và B}}{\text{Tổng số đơn hàng toàn shop}}$$

2. **Độ tin cậy (Confidence)**: Xác suất có điều kiện khách sẽ mua B khi đã có A trong giỏ:
   $$\text{Confidence}(A \rightarrow B) = \frac{\text{Support}(A \cup B)}{\text{Support}(A)} = \frac{\text{Số đơn chứa cả A và B}}{\text{Số đơn chứa A}}$$

3. **Độ nâng (Lift - Chỉ số quan trọng nhất)**: Đo lường mức độ ảnh hưởng thực sự của việc mua A đến khả năng mua B, so với việc B được mua một cách ngẫu nhiên độc lập:
   $$\text{Lift}(A \rightarrow B) = \frac{\text{Confidence}(A \rightarrow B)}{\text{Support}(B)} = \frac{P(A \cap B)}{P(A) \times P(B)}$$

| Giá trị Lift | Bản chất Quan hệ | Ứng dụng Bán lẻ của AI |
| :---: | :--- | :--- |
| **$\text{Lift} > 1.0$** | **Quan hệ Bổ trợ Mạnh (Complementary)** | Khách mua A làm tăng vọt khả năng mua B. **Hành động:** Tạo Combo giảm giá nhẹ, đặt B ở mục "Sản phẩm thường được mua cùng nhau" (Frequently Bought Together) hoặc Pop-up đề xuất khi khách thêm A vào giỏ. |
| **$\text{Lift} = 1.0$** | **Độc lập ngẫu nhiên** | Việc mua A không ảnh hưởng gì tới B. Không cần can thiệp. |
| **$\text{Lift} < 1.0$** | **Triệt tiêu / Thay thế (Substitutes)** | Khách đã mua A thì ít có khả năng mua B (ví dụ: Đã mua CPU Core i5 thì không mua thêm CPU Core i7). Không bao giờ gợi ý mua kèm hai sản phẩm này cùng lúc. |

---

## 2. DỰ BÁO GIÁ TRỊ VÒNG ĐỜI KHÁCH HÀNG XÁC SUẤT (PROBABILISTIC CLV - BG/NBD & GAMMA-GAMMA)

### 2.1. Mô hình BG/NBD (Beta-Geometric / Negative Binomial Distribution)
Trong bán lẻ không có hợp đồng (Non-contractual setting như shop máy tính, thương mại điện tử), khách hàng có thể rời bỏ bất cứ lúc nào mà không thông báo.
Mô hình BG/NBD giải quyết bài toán:
1. Khi khách hàng còn "sống" (Active), số lượng giao dịch của họ tuân theo **Phân phối Poisson** với tham số $\lambda$.
2. Tham số giao dịch $\lambda$ giữa các khách hàng biến thiên theo **Phân phối Gamma**.
3. Sau mỗi giao dịch, khách hàng có xác suất rời bỏ (Churn) là $p$, tuân theo **Phân phối Beta-Geometric**.

**Đầu ra của mô hình BG/NBD:**
- $P(\text{Alive})$: Xác suất khách hàng vẫn còn đang hoạt động tại thời điểm hiện tại.
- $\mathbb{E}[X(t)]$: Kỳ vọng số lượng đơn hàng khách hàng sẽ mua trong $t$ ngày tới.

### 2.2. Mô hình Gamma-Gamma (Dự Báo Giá Trị Đơn Hàng Tương Lai)
Ước tính giá trị chi tiêu trung bình trên mỗi đơn hàng trong tương lai của khách hàng, dựa trên giả định giá trị giao dịch của từng cá nhân dao động quanh mức trung bình của họ theo phân phối Gamma.

---