@echo off
chcp 65001 >nul
title Khởi động Chatbot Shop - Local Dev Mode
echo ==============================================================
echo       KHỞI ĐỘNG CHATBOT SHOP (CHẠY TRỰC TIẾP NODE.JS)
echo ==============================================================
echo.
echo [1/3] Đang mở terminal Backend (Port 5000)...
start "ChatbotShop Backend API" cmd /k "cd /d d:\Chatbot\chatbotshop\backend && npm run dev"

echo [2/3] Backend đang khởi tạo...
timeout /t 2 >nul

echo [3/3] Đang mở trình duyệt & chạy Frontend (Port 5173)...
start http://localhost:5173

cd /d d:\Chatbot\chatbotshop\frontend
npm run dev
