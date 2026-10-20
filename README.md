# TechZone - Hệ Thống E-Commerce & AI Chatbot Shop Điện Tử

Hệ thống bán hàng công nghệ cao cấp kết hợp PC Builder tương tác và 2 AI Chatbot (Tư vấn bán hàng + Trợ lý dữ liệu kinh doanh).

---

## 🚀 Cách Khởi Động Nhanh Nhất (1-Click)

Bạn có thể chạy dự án theo 1 trong 2 cách sau:

### Cách 1: Chạy bằng Docker (Khuyên Dùng)
1. Mở ứng dụng **Docker Desktop** trên Windows (chờ biểu tượng cá voi chuyển màu xanh).
2. Click đúp vào file `run-docker.bat` ở thư mục gốc `d:\Chatbot\chatbotshop`.
   - Script sẽ tự động bật container backend trong Docker (`http://localhost:5000`).
   - Tự động bật frontend và mở trình duyệt tại `http://localhost:5173`.

### Cách 2: Chạy trực tiếp bằng Node.js (Không cần Docker)
- Chỉ cần click đúp vào file `run-local.bat`.
- Hệ thống sẽ tự động bật 2 cửa sổ chạy Backend (`port 5000`) và Frontend (`port 5173`), đồng thời mở trình duyệt ngay.

---

## 💻 Cách Khởi Động Bằng Dòng Lệnh (Terminal)

### 1. Khởi động Backend
- **Chạy bằng Docker**:
  ```bash
  docker compose up -d
  ```
- **Hoặc chạy trực tiếp bằng npm**:
  ```bash
  cd d:\Chatbot\chatbotshop\backend
  npm run dev
  ```
  *(Backend chạy tại: http://localhost:5000)*

### 2. Khởi động Frontend
Mở một cửa sổ Terminal mới:
```bash
cd d:\Chatbot\chatbotshop\frontend
npm run dev
```
*(Frontend chạy tại: http://localhost:5173)*

---

## 🔑 Tài Khoản Quản Trị (Admin Portal)

Truy cập: [http://localhost:5173/admin](http://localhost:5173/admin)

- **Tài khoản Quản trị viên (Admin)**:
  - Tên đăng nhập: `admin`
  - Mật khẩu: `admin123`
  - *Quyền hạn: Xem Dashboard KPI, biểu đồ doanh thu, điều khiển Chatbot phân tích dữ liệu, duyệt chiến dịch xả hàng tồn kho, quản lý tài liệu RAG.*

- **Tài khoản Thủ kho (Inventory Manager)**:
  - Tên đăng nhập: `kho`
  - Mật khẩu: `kho123`
  - *Quyền hạn: Nhập kho (Tạo phiếu nhập hàng), kiểm kê tồn kho theo thời gian thực.*

---

## 🎯 Các Tính Năng Nổi Bật

1. **Storefront Hiện Đại**:
   - Slider tự động chuyển cảnh phong cách công nghệ cao.
   - Thanh ticker cập nhật tin khuyến mãi chạy trực tiếp.
   - Lọc sản phẩm đa chiều theo thương hiệu, tầm giá, loại tấm nền (OLED/IPS), dung lượng RAM, nhu cầu sử dụng.

2. **So Sánh Sản Phẩm Đa Chiều (Comparison Drawer)**:
   - Cho phép chọn tối đa 4 sản phẩm cùng lúc.
   - Bảng ma trận đối chiếu cấu hình chi tiết.
   - Nút **"Chỉ hiện điểm khác biệt"** làm nổi bật hàng thông số khác nhau.
   - Nút **"Hỏi AI tóm tắt khác biệt"** gọi chatbot tự động so sánh điểm mạnh yếu.

3. **Xây Dựng Cấu Hình PC Tương Tác (PC Builder Blueprint)**:
   - Sơ đồ bo mạch chủ trực quan: linh kiện được chọn sẽ phát sáng socket tương ứng.
   - Đồng hồ đo công suất nguồn (Wattage Power Gauge) tính toán TDP thực tế + 25% an toàn.
   - Bộ quy tắc kiểm tra tương thích phần cứng: Socket CPU - Mainboard, loại RAM DDR4/DDR5, kích thước Case - VGA - Tản nhiệt, công suất nguồn.
   - Nút "Sao chép cấu hình" chia sẻ và "Thêm tất cả vào giỏ hàng" 1 chạm.

4. **Chatbot Tư Vấn Bán Hàng (Customer Chatbot)**:
   - Nút chat nổi ở góc dưới bên phải màn hình cửa hàng.
   - Hiểu nhu cầu ("tìm laptop màn OLED tầm 20 triệu", "tư vấn máy chơi game mỏng nhẹ").
   - Trả lời kèm thẻ sản phẩm bấm xem chi tiết hoặc thêm giỏ hàng ngay trong khung chat.

5. **Trợ Lý Phân Tích Dữ Liệu Kinh Doanh (Admin Data Assistant)**:
   - Hỗ trợ các câu hỏi quản trị kinh doanh:
     - *"Báo cáo doanh thu tháng này so với kế hoạch (Target vs Actual)"*
     - *"Đề xuất phương án xử lý hàng tồn kho lâu ngày (Dead stock discount)"*
     - *"Phân tích sản phẩm bán chạy nhất theo danh mục"*
   - Trả về thẻ hành động có nút phê duyệt trực tiếp cho Admin.
