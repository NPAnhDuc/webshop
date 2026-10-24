# MODULE 4.1: PHÂN KHÚC KHÁCH HÀNG RFM & QUẢN TRỊ VÒNG ĐỜI (CUSTOMER LIFECYCLE MANAGEMENT)

---

## 1. PHƯƠNG PHÁP LUẬN PHÂN TÍCH RFM
Mô hình RFM là phương pháp kinh điển trong Khoa học Dữ liệu Bán lẻ dựa trên 3 trục hành vi chính:
1. **Recency ($R$)**: Khách hàng mua đơn hàng gần nhất cách đây bao nhiêu ngày? (Khách mua càng gần đây càng có xác suất phản hồi cao với các thông điệp tiếp thị).
2. **Frequency ($F$)**: Khách hàng đã thực hiện bao nhiêu đơn hàng thành công trong suốt thời gian qua? (Phản ánh mức độ trung thành và sự tin tưởng).
3. **Monetary ($M$)**: Tổng số tiền khách hàng đã mang lại cho cửa hàng là bao nhiêu? (Đo lường giá trị tài chính thực tế).

---

## 2. KỊCH BẢN HÀNH ĐỘNG CHIẾN LƯỢC THEO TỪNG PHÂN KHÚC (ACTIONABLE RETAIL PLAYS)

| Phân khúc RFM | Đặc điểm Hành vi | Tỷ lệ doanh thu | Kịch bản Hành động của Bộ phận Kinh doanh & AI |
| :--- | :--- | :---: | :--- |
| **Champions (Khách VIP Cốt Lõi)** | $R \in [4, 5], F \in [4, 5], M \in [4, 5]$<br>Mua mới, mua rất nhiều lần, chi tiêu khủng. | 40% - 60% | • Không giảm giá đại trà.<br>• Đặc quyền: Đặt hàng trước linh kiện hiếm (Pre-order RTX 5090/Ryzen 9000), bảo hành 1 đổi 1 tận nhà.<br>• Gửi quà sinh nhật tri ân từ đích danh Chủ shop. |
| **Loyal Customers (Khách Trung Thành)** | $R \in [3, 5], F \in [3, 5], M \in [3, 4]$<br>Mua đều đặn, phản hồi tốt với khuyến mãi. | 20% - 30% | • Chương trình tích điểm thành viên (Loyalty Club).<br>• Bán chéo (Cross-sell) phụ kiện cao cấp, nâng cấp tản nhiệt, bàn phím cơ. |
| **Potential Loyalists (Khách Mới Tiềm Năng)** | $R \in [4, 5], F \in [1, 2], M \in [3, 5]$<br>Mới mua 1-2 đơn gần đây nhưng giá trị lớn. | 10% - 15% | • **Kích hoạt Vòng lặp Mua lại (Repurchase Loop)**: Gửi voucher giảm 5% cho đơn thứ hai có hạn dùng 14 ngày.<br>• Khảo sát mức độ hài lòng về trải nghiệm giao hàng. |
| **At Risk (Khách VIP Sắp Rời Bỏ)** | $R \in [1, 2], F \in [3, 5], M \in [4, 5]$<br>Từng chi rất nhiều tiền nhưng đã > 60-90 ngày chưa mua. | Cực kỳ nguy hiểm | • **Chiến dịch Cứu vãn (Win-back Campaign)**: AI tự động gửi tin nhắn Zalo/SMS riêng từ Quản lý CSKH kèm voucher độc quyền 10% - 12%.<br>• Tìm hiểu xem khách có gặp lỗi bảo hành hay chuyển sang mua của đối thủ không. |
| **Hibernating / About to Sleep** | $R \in [1, 2], F \in [1, 2], M \in [1, 2]$<br>Mua ít, đã lâu không quay lại. | < 5% | • Tuyệt đối không chi tiền quảng cáo trả phí (Paid Ads) nhắm vào nhóm này.<br>• Chỉ dùng các kênh tiếp thị tự động 0 đồng (Email marketing, Thông báo app tự động). |

---

## 3. MÃ NGUỒN PYTHON THỰC THI PHÂN CỤM RFM (MACHINE LEARNING K-MEANS & QUINTILES)

Đoạn mã Python dưới đây thực hiện xử lý dữ liệu giao dịch thực tế, loại bỏ ngoại lai, áp dụng chuẩn hóa Log-transform và thuật toán phân cụm K-Means:

```python
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

def compute_rfm_segments(df_orders: pd.DataFrame, reference_date: datetime = None) -> pd.DataFrame:
    """
    df_orders yêu cầu các cột:
    - customer_id: ID khách hàng
    - order_id: Mã đơn hàng
    - order_date: Ngày tạo đơn (datetime)
    - order_status: Trạng thái đơn ('DELIVERED')
    - net_amount: Giá trị đơn hàng (float)
    """
    # 1. Lọc đơn hàng thành công
    valid_orders = df_orders[df_orders['order_status'] == 'DELIVERED'].copy()
    
    if reference_date is None:
        reference_date = valid_orders['order_date'].max() + pd.Timedelta(days=1)
        
    # 2. Tính toán R, F, M
    rfm = valid_orders.groupby('customer_id').agg({
        'order_date': lambda d: (reference_date - d.max()).days, # Recency
        'order_id': 'nunique',                                   # Frequency
        'net_amount': 'sum'                                      # Monetary
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # 3. Chia phân vị Quintiles (1 đến 5 điểm)
    # Recency: Số ngày càng nhỏ thì điểm càng cao (dùng pct_rank đảo)
    rfm['r_score'] = pd.qcut(rfm['recency'].rank(method='first', ascending=False), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Frequency: Mua nhiều đơn thì điểm cao (xử lý trùng lặp với rank first)
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first', ascending=True), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Monetary: Chi tiêu nhiều thì điểm cao
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first', ascending=True), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    
    # 4. Phân loại phân khúc chiến lược
    def assign_segment(row):
        r, f, m = row['r_score'], row['f_score'], row['m_score']
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'Potential Loyalists'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At Risk'
        elif r <= 2 and f <= 2:
            return 'Hibernating'
        else:
            return 'General Customers'
            
    rfm['segment'] = rfm.apply(assign_segment, axis=1)
    
    # 5. Phân cụm bổ trợ bằng K-Means Unsupervised Learning
    # Dùng Log-transform vì dữ liệu tiền tệ và số đơn thường phân phối lệch phải (skewed)
    rfm_log = np.log1p(rfm[['recency', 'frequency', 'monetary']])
    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_log)
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm['cluster_kmeans'] = kmeans.fit_predict(rfm_scaled)
    
    return rfm

# Ví dụ tóm tắt báo cáo kinh doanh cho AI:
def generate_rfm_executive_summary(rfm_df: pd.DataFrame) -> dict:
    summary = rfm_df.groupby('segment').agg(
        customer_count=('customer_id', 'count'),
        avg_recency=('recency', 'mean'),
        avg_frequency=('frequency', 'mean'),
        total_revenue=('monetary', 'sum'),
        avg_spend=('monetary', 'mean')
    ).reset_index()
    
    total_rev = summary['total_revenue'].sum()
    summary['revenue_contribution_pct'] = (summary['total_revenue'] / total_rev) * 100.0
    return summary.to_dict(orient='records')
```
