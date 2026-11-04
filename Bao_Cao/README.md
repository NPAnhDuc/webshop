# Báo cáo môn Kho dữ liệu và Khai phá dữ liệu

Đề tài: **Xây dựng chatbot tư vấn bán hàng TechStore ứng dụng truy xuất thông tin lai và phân lớp ý định.**

| File | Nội dung |
|---|---|
| `BaoCao.md` | Bản gốc của báo cáo (Markdown), đọc được ngay trên GitHub |
| `BaoCao.docx` | Bản Word: có trang bìa, mục lục tự động, đánh số trang |
| `BaoCao.pdf` | Bản PDF xuất từ Word |
| `hinh/` | 19 sơ đồ và biểu đồ dùng trong báo cáo |
| `cong_cu/ve_hinh.py` | Script vẽ lại các hình (matplotlib) |
| `cong_cu/md_sang_docx.py` | Script dựng lại file Word từ `BaoCao.md` (python-docx) |

Trước khi nộp, điền tên trường, khoa, giảng viên, sinh viên và lớp ở trang bìa, rồi mở file Word và nhấn F9 (hoặc References → Update Table) để cập nhật mục lục.

Dựng lại từ thư mục `AI` (cần `matplotlib`, `python-docx`, `Pillow` trong môi trường ảo của dự án):

```powershell
.\.venv\Scripts\python.exe ..\Bao_Cao\cong_cu\ve_hinh.py
.\.venv\Scripts\python.exe ..\Bao_Cao\cong_cu\md_sang_docx.py
```

Nguồn dữ liệu, ảnh và mô hình ghi ở mục 3.2 và Phụ lục A của báo cáo. Dữ liệu kinh doanh trong đề tài là dữ liệu mô phỏng.
