# TechStore PC Studio - Superstore & Enterprise Admin System

Hệ sinh thái thương mại điện tử chuyên nghiệp cho chuỗi siêu thị máy tính, linh kiện PC và Laptop cao cấp. Tích hợp công cụ tự ráp máy **PC Builder**, **AI Chatbot trợ lý kỹ thuật**, và **11 phân hệ quản trị Admin Portal**.

---

## 🌳 Cấu trúc các nhánh trên Repository

Dự án được phân nhánh độc lập theo từng phần để dễ dàng clone và triển khai:

* **Nhánh `frontend`**: Toàn bộ ứng dụng giao diện người dùng và cổng quản trị Admin (Vite + React 18 + TailwindCSS + Lucide Icons).
* **Nhánh `backend`**: Toàn bộ máy chủ API và cơ sở dữ liệu thời gian thực (Node.js + Express + TypeScript + SQLite/JSON Store).
* **Nhánh `main`**: Toàn bộ monorepo đầy đủ cả Frontend, Backend và cấu hình Docker.

---

## 🚀 Hướng dẫn Clone & Khởi chạy

### Cách 1: Chạy độc lập theo từng nhánh

#### 🔹 1. Khởi chạy Backend (Port 5000):
```bash
git clone -b backend https://github.com/NPAnhDuc/webshop.git techstore-backend
cd techstore-backend
npm install
npm run dev
```

#### 🔹 2. Khởi chạy Frontend (Port 5173):
```bash
git clone -b frontend https://github.com/NPAnhDuc/webshop.git techstore-frontend
cd techstore-frontend
npm install
npm run dev
```

---

### Cách 2: Khởi chạy toàn bộ từ nhánh `main`:
```bash
git clone https://github.com/NPAnhDuc/webshop.git
cd webshop

# Cài đặt và chạy song song
start-shop.bat
# hoặc chạy thủ công trong 2 terminal:
# Terminal 1: cd backend && npm install && npm run dev
# Terminal 2: cd frontend && npm install && npm run dev
```

Mở trình duyệt:
* **Khách hàng (Storefront)**: [http://localhost:5173](http://localhost:5173)
* **Quản trị (Admin Portal)**: [http://localhost:5173](http://localhost:5173) ➜ Bấm *"Tài khoản"* (Tài khoản: `admin` / Mật khẩu: `admin123`)
* **Backend API**: [http://localhost:5000](http://localhost:5000)
