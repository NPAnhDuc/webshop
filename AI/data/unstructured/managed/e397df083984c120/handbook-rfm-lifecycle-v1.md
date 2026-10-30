# Phân khúc RFM và hành động theo vòng đời khách hàng

> Tài liệu phương pháp nội bộ (handbook phân tích kinh doanh), chỉ dành cho quản lý. Mọi con số trong ví dụ là minh họa, KHÔNG phải số liệu của shop. Số liệu shop (doanh thu, giá vốn, đơn, tồn kho) chỉ lấy từ công cụ SQL/báo cáo trên database data/business_sql/scenario_v1/shop.sqlite (dữ liệu mô phỏng 01/10/2025–30/09/2026).

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