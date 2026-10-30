# Công cụ ảnh báo cáo trong chatbot

Đăng nhập vai trò Chủ shop trong Streamlit và hỏi:

- `Vẽ biểu đồ doanh thu quý 3 năm 2026 và phân tích`
- `Vẽ sơ đồ lợi nhuận quý 3 năm 2026 và phân tích`
- `Xuất ảnh báo cáo kinh doanh tháng 9 năm 2026`

Engine gọi công cụ phân tích SQL; UI dùng `shopbot/reporting.py` tạo ảnh PNG từ
cùng report, trình bày nhận xét quan sát và cung cấp nút tải. Có hai loại ảnh:
báo cáo tổng quan (diễn biến tháng, nhóm hàng, cấu phần lời/lỗ, kênh bán) và sơ
đồ doanh thu → giá vốn → lợi nhuận gộp → chi phí → lợi nhuận hoạt động.

Ảnh có kỳ, đơn vị, nhãn nguồn, số dòng và fingerprint; dữ liệu mô phỏng ghi rõ.
Không suy đoán số từ ảnh và không dùng LLM tự bịa dữ liệu vẽ. Chưa có chi phí thì
chỉ thể hiện lợi nhuận gộp; kỳ không có dữ liệu không vẽ số 0 giả định.
Không hỗ trợ tùy ý mọi loại sơ đồ bằng một câu lệnh; các mẫu hiện có được kiểm thử.

Ví dụ đã xuất nằm trong `examples/`: hai PNG, JSON số liệu và Markdown phân tích.
Tái tạo bằng `AI/.venv/Scripts/python.exe AI/scripts/export_report_images.py`
từ thư mục gốc dự án. Ảnh của ứng dụng được tạo trong bộ nhớ của phiên admin;
không lưu báo cáo thật vào thư mục công khai.

## Vì sao train trước đó nhanh

- Qwen chưa được huấn luyện lại toàn bộ.
- Kev v1 là LoRA: 147 record train × 2 epoch = 294 lượt, 38 optimizer steps,
  wall time trong báo cáo Colab 211,3 giây, khoảng 3 phút 31 giây.
- E5 v2 có 569 câu supported nhưng trainer lấy ngẫu nhiên 1 câu/nhóm/epoch,
  53 nhóm × 3 epoch = 159 lượt lấy mẫu, khoảng 21 optimizer steps. Không phải
  cả 824 câu của pack được học hết ở mỗi epoch. Cần nói rõ đây là pilot nhỏ.
- Dự báo là gradient boosting trên vài trăm ngày; không phải train deep learning
  từ đầu. Các số doanh thu mới được tính bằng SQL, không phải model học thuộc.
- Tạo biểu đồ là thực thi công cụ, không cần train model để vẽ từng báo cáo.

Pilot này xác minh đường đi kỹ thuật. E5 không cải thiện validation nên giữ
baseline; câu hỏi theo khuôn chưa chứng minh hiểu tình huống thực tế. Bước tiếp
theo là bộ câu hỏi đa bước độc lập, lỗi dữ liệu/quyền/phiên bản và truy xuất thật,
rồi sửa tầng lỗi, mới huấn luyện thêm khi có bằng chứng cần thiết. Train lâu hơn
một mình không bảo đảm chatbot tốt hơn.
