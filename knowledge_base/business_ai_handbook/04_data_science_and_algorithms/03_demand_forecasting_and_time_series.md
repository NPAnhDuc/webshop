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

## 3. MÃ NGUỒN PYTHON TRIỂN KHAI DỰ BÁO NHU CẦU BẰNG LIGHTGBM

Phương pháp Gradient Boosting (LightGBM) hiện là tiêu chuẩn vàng trong các cuộc thi Data Science quốc tế (như Kaggle M5 Forecasting) để dự báo nhu cầu bán lẻ nhờ tốc độ siêu nhanh và khả năng học các mối quan hệ phi tuyến phức tạp:

```python
import pandas as pd
import numpy as np
import lightgbm as lgb
from datetime import datetime, timedelta

def build_forecasting_features(df_daily_sales: pd.DataFrame) -> pd.DataFrame:
    """
    df_daily_sales yêu cầu:
    - date: Cột ngày (datetime)
    - sku: Mã sản phẩm
    - units_sold: Số lượng bán trong ngày
    """
    df = df_daily_sales.sort_values(by=['sku', 'date']).copy()
    
    # 1. Đặc trưng lịch (Calendar & Vietnamese Market Features)
    df['day_of_week'] = df['date'].dt.dayofweek
    df['day_of_month'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    
    # Ngày nhận lương ở VN: 14-16 và 29-31 hàng tháng
    df['is_payday'] = df['day_of_month'].isin([14, 15, 16, 29, 30, 31]).astype(int)
    
    # Ngày hội Siêu Sale đôi (9/9, 10/10, 11/11, 12/12)
    df['is_double_day'] = (
        (df['day_of_month'] == df['month']) & (df['month'].isin([9, 10, 11, 12]))
    ).astype(int)
    
    # 2. Đặc trưng độ trễ (Lag Features) - Học xu hướng quá khứ
    for lag in [1, 2, 7, 14, 21, 28]:
        df[f'lag_{lag}'] = df.groupby('sku')['units_sold'].shift(lag)
        
    # 3. Đặc trưng thống kê trượt (Rolling Window Statistics)
    # Lưu ý: shift(1) để tránh rò rỉ dữ liệu (Data Leakage) ngày hiện tại
    grouped = df.groupby('sku')['units_sold']
    
    df['rolling_mean_7'] = grouped.shift(1).rolling(window=7).mean()
    df['rolling_std_7'] = grouped.shift(1).rolling(window=7).std()
    df['rolling_mean_14'] = grouped.shift(1).rolling(window=14).mean()
    df['rolling_mean_28'] = grouped.shift(1).rolling(window=28).mean()
    
    # Loại bỏ các dòng đầu tiên bị NaN do độ trễ
    return df.dropna().reset_index(drop=True)

def train_demand_forecaster(feature_df: pd.DataFrame, target_col: str = 'units_sold'):
    feature_cols = [
        'day_of_week', 'day_of_month', 'month', 'is_weekend', 'is_payday', 'is_double_day',
        'lag_1', 'lag_2', 'lag_7', 'lag_14', 'lag_21', 'lag_28',
        'rolling_mean_7', 'rolling_std_7', 'rolling_mean_14', 'rolling_mean_28'
    ]
    
    # Tách tập Train (dữ liệu cũ) và Validation (14 ngày gần nhất)
    split_date = feature_df['date'].max() - timedelta(days=14)
    train_data = feature_df[feature_df['date'] <= split_date]
    val_data = feature_df[feature_df['date'] > split_date]
    
    lgb_train = lgb.Dataset(train_data[feature_cols], label=train_data[target_col])
    lgb_val = lgb.Dataset(val_data[feature_cols], label=val_data[target_col], reference=lgb_train)
    
    params = {
        'objective': 'regression_l1', # Tối ưu hóa MAE/WAPE
        'metric': 'mae',
        'boosting_type': 'gbdt',
        'learning_rate': 0.05,
        'num_leaves': 31,
        'feature_fraction': 0.8,
        'verbose': -1,
        'random_state': 42
    }
    
    model = lgb.train(
        params,
        lgb_train,
        num_boost_round=1000,
        valid_sets=[lgb_train, lgb_val],
        callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
    )
    
    # Tính WAPE trên tập Validation
    val_preds = model.predict(val_data[feature_cols], num_iteration=model.best_iteration)
    actuals = val_data[target_col].values
    wape = np.sum(np.abs(actuals - val_preds)) / np.sum(actuals) * 100.0
    print(f"Validation WAPE: {wape:.2f}%")
    
    return model, feature_cols
```
