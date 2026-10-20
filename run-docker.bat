@echo off
chcp 65001 >nul
title Khởi động Chatbot Shop - Docker Mode
echo ==============================================================
echo       KHỞI ĐỘNG CHATBOT SHOP (BACKEND DOCKER + FRONTEND)
echo ==============================================================
echo.
echo [1/3] Đang kiểm tra Docker & khởi động Backend container...
docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo [CHÚ Ý] Docker Desktop chưa được bật trên máy!
    echo Vui lòng mở ứng dụng "Docker Desktop", đợi icon cá voi xanh hiện lên rồi chạy lại file này.
    echo Hoặc bạn có thể click đúp file "run-local.bat" để chạy trực tiếp không cần Docker.
    echo.
    pause
    exit /b
)

echo.
echo [2/3] Backend Docker đã chạy thành công trên http://localhost:5000
echo [3/3] Đang khởi động Frontend và tự động mở trình duyệt...
timeout /t 2 >nul
start http://localhost:5173

cd frontend
npm run dev
