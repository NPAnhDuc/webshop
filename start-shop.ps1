# Script khởi động đồng thời cả Backend (Node.js) và Frontend (React)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Khởi động TechStore - Website & Chatbot Shop Điện Tử" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Start Backend on Port 5000 in background or new window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; Write-Host '--- KHỞI ĐỘNG BACKEND (PORT 5000) ---' -ForegroundColor Green; npm start"

# Start Frontend on Port 5173
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; Write-Host '--- KHỞI ĐỘNG FRONTEND (PORT 5173) ---' -ForegroundColor Yellow; npm run dev"

Write-Host "`nĐang mở hệ thống:" -ForegroundColor Green
Write-Host "• Storefront (Khách hàng): http://localhost:5173" -ForegroundColor White
Write-Host "• Cổng Admin: http://localhost:5173 (Bấm nút 'Cổng Quản Trị' góc trên phải, đăng nhập admin / admin123)" -ForegroundColor White
Write-Host "• Backend API: http://localhost:5000" -ForegroundColor White
