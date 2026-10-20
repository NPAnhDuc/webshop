@echo off
title TechStore Launcher
echo ==========================================================
echo  Khoi dong TechStore - Website & Chatbot Shop Dien Tu
echo ==========================================================

start "TechStore Backend (Port 5000)" cmd /k "cd /d %~dp0backend && npm start"
start "TechStore Frontend (Port 5173)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo He thong dang duoc khoi dong:
echo - Frontend: http://localhost:5173
echo - Backend:  http://localhost:5000
echo.
pause
