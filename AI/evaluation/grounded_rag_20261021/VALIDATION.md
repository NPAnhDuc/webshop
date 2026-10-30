# Kiểm tra mã — 21/10/2026

- Pipeline mới, RAG trước và trích nguồn: **39 passed**. Bao gồm phạm vi thời gian, câu nhiều phần, ID bằng chứng giả, quyền người mua, lịch sử phiên bản/gỡ tài liệu, cache khác corpus/revision và ranh giới miền tri thức.
- Toàn bộ kiểm tra lõi, bỏ riêng AppTest: **155 passed in60.98s**, exit0.
- Streamlit AppTest: **4 passed in10.62s**, exit0. Kiểm tra chat demo, mật khẩu admin, báo cáo demo và cách ly/đăng xuất; đây là kiểm tra giao diện luồng công cụ cũ, không thay thế100 câu RAG mới.
- Tổng155+4=159 kiểm tra tự động đã qua;39 kiểm tra tập trung là tập con, không cộng thêm vào159.

Lệnh chạy từ D:\Chatbot\chatbotshop, PythonAI/.venv/Scripts/python.exe:

```powershell
$env:LLM_PROVIDER='demo'
$env:KEV_BASE_URL=''
$env:OLLAMA_BASE_URL='http://127.0.0.1:1'
AI/.venv/Scripts/python.exe -X utf8 -m pytest AI/tests --ignore=AI/tests/test_app.py -q --tb=short --basetemp=D:/Chatbot/chatbotshop/AI/runtime/test-core-20261021-g -o cache_dir=D:/Chatbot/chatbotshop/AI/runtime/pytest-cache-grounded-20261021
AI/.venv/Scripts/python.exe -X utf8 -m pytest AI/tests/test_app.py -v -s --tb=short --basetemp=D:/Chatbot/chatbotshop/AI/runtime/test-app-20261021-h -o cache_dir=D:/Chatbot/chatbotshop/AI/runtime/pytest-cache-grounded-20261021
```

Các biến môi trường trên chỉ ở subprocess chạy kiểm tra để không gọi nhầm model đang benchmark, không sửa.env của ứng dụng. Test có thể mock requests và tự ghi đè provider riêng. Basetemp là thư mục mới trong workspace; khi chạy lại chọn tên mới.

Log cục bộ: AI/runtime/tests-core-20261021-g.log và AI/runtime/tests-app-20261021-h.log. Lần chạy cả bộ ban đầu không hoàn tất; lượt lõi đang chạy tiếp cũng được dừng chủ động trước khi chạy lại cách ly như trên. Không coi hai lượt đó là kết quả đạt.

Model thật được đo riêng trên100 câu frozen bằngrun_grounded_comparison.py, không dùng provider demo. Bộ này được dùng trong phát triển, chưa phải bộ kiểm tra mù độc lập.
