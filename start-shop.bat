@echo off
title TechStore Launcher
echo ==========================================================
echo  Khoi dong TechStore - Website & Chatbot Shop Dien Tu
echo ==========================================================

start "TechStore Backend (Port 5000)" cmd /k "cd /d %~dp0backend && npm start"
start "TechStore Customer Frontend (Port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev"
start "TechStore Admin Portal 2FA (Port 5174)" cmd /k "cd /d %~dp0admin && npm run dev"

echo.
echo He thong dang duoc khoi dong:
echo - Frontend Khach Hang: http://localhost:5173
echo - Admin Portal (OTP 2FA): http://localhost:5174
echo - Backend API:          http://localhost:5000
echo.
pause
