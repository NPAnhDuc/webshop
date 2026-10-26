# Script khởi động đồng thời cả Backend (Node.js), Frontend (React) và Admin Portal (2FA OTP)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Khởi động TechStore - Website & Chatbot Shop Điện Tử" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Start Backend on Port 5000
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; Write-Host '--- KHỞI ĐỘNG BACKEND (PORT 5000) ---' -ForegroundColor Green; npm start"

# Start Customer Frontend on Port 5173
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; Write-Host '--- KHỞI ĐỘNG FRONTEND KHÁCH HÀNG (PORT 5173) ---' -ForegroundColor Yellow; npm run dev"

# Start Dedicated Admin Portal on Port 5174
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\admin'; Write-Host '--- KHỞI ĐỘNG CỔNG ADMIN PORTAL 2FA (PORT 5174) ---' -ForegroundColor Magenta; npm run dev"

Write-Host "`nĐang mở hệ thống:" -ForegroundColor Green
Write-Host "• Storefront Khách hàng: http://localhost:5173" -ForegroundColor White
Write-Host "• Cổng Admin 2FA (Riêng biệt): http://localhost:5174 (Login: admin / admin123 + OTP: 888999 hoặc Authenticator)" -ForegroundColor White
Write-Host "• Backend API: http://localhost:5000" -ForegroundColor White
