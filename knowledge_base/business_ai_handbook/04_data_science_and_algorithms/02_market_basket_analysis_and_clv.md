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

### 1.2. Mã Nguồn Python Khai Phá Giỏ Hàng với Thư Viện MLxtend

```python
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

def run_market_basket_analysis(df_order_items: pd.DataFrame, min_support: float = 0.01, min_lift: float = 1.2) -> pd.DataFrame:
    """
    df_order_items bao gồm:
    - order_id: Mã đơn hàng
    - product_name: Tên sản phẩm
    """
    # 1. Tạo ma trận giỏ hàng One-Hot (Basket Matrix)
    basket = (df_order_items.groupby(['order_id', 'product_name'])['product_name']
              .count().unstack().reset_index().fillna(0)
              .set_index('order_id'))
    
    # 2. Chuyển đổi số lượng thành dạng Boolean (True/False)
    basket_bool = basket.map(lambda x: True if x > 0 else False)
    
    # 3. Chạy thuật toán Apriori tìm tập phổ biến
    frequent_itemsets = apriori(basket_bool, min_support=min_support, use_colnames=True)
    
    if frequent_itemsets.empty:
        return pd.DataFrame()
        
    # 4. Tạo các luật kết hợp
    rules = association_rules(frequent_itemsets, metric="lift", min_threshold=min_lift)
    
    # Sắp xếp theo Lift và Confidence giảm dần
    rules = rules.sort_values(by=['lift', 'confidence'], ascending=[False, False])
    
    # Làm sạch định dạng kết quả
    rules['antecedents'] = rules['antecedents'].apply(lambda x: ', '.join(list(x)))
    rules['consequents'] = rules['consequents'].apply(lambda x: ', '.join(list(x)))
    
    return rules[['antecedents', 'consequents', 'support', 'confidence', 'lift']]
```

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

### 2.3. Triển Khai Python Hoàn Chỉnh Dự Báo 12 Tháng Tiếp Theo

```python
import pandas as pd
from lifetimes import BetaGeoFitter, GammaGammaFitter
from lifetimes.utils import summary_data_from_transaction_data

def train_predict_clv(df_transactions: pd.DataFrame, time_horizon_days: int = 365, discount_rate: float = 0.01) -> pd.DataFrame:
    """
    df_transactions cần:
    - customer_id: ID khách
    - order_date: Ngày đặt
    - order_value: Doanh thu thuần
    """
    # 1. Chuyển đổi về bảng Summary RFM-T chuẩn của Lifetimes
    summary = summary_data_from_transaction_data(
        df_transactions,
        customer_id_col='customer_id',
        datetime_col='order_date',
        monetary_value_col='order_value',
        observation_period_end=df_transactions['order_date'].max(),
        freq='D' # Chu kỳ ngày
    )
    
    # 2. Huấn luyện mô hình BG/NBD
    bgf = BetaGeoFitter(penalizer_coef=0.01)
    bgf.fit(summary['frequency'], summary['recency'], summary['T'])
    
    # Dự báo số lượng đơn mua trong 365 ngày tới
    summary['predicted_orders_next_1y'] = bgf.predict(
        time_horizon_days, summary['frequency'], summary['recency'], summary['T']
    )
    # Tính xác suất khách hàng còn active
    summary['prob_alive'] = bgf.conditional_probability_alive(
        summary['frequency'], summary['recency'], summary['T']
    )
    
    # 3. Huấn luyện mô hình Gamma-Gamma cho khách có ít nhất 1 lần mua lại (frequency > 0)
    returning_customers = summary[summary['frequency'] > 0]
    
    ggf = GammaGammaFitter(penalizer_coef=0.01)
    ggf.fit(returning_customers['frequency'], returning_customers['monetary_value'])
    
    # Dự báo giá trị đơn hàng trung bình trong tương lai
    summary['expected_avg_spend'] = ggf.conditional_expected_average_profit(
        summary['frequency'], summary['monetary_value']
    )
    
    # 4. Tính toán CLV 1 năm tới (Chiết khấu dòng tiền 1% mỗi tháng)
    summary['predicted_clv_1y'] = ggf.customer_lifetime_value(
        bgf,
        summary['frequency'],
        summary['recency'],
        summary['T'],
        summary['monetary_value'],
        time=12, # 12 tháng
        freq='D',
        discount_rate=discount_rate
    )
    
    return summary.sort_values(by='predicted_clv_1y', ascending=False)
```
