# MODULE 5.2: KIẾN TRÚC AGENT TEXT-TO-SQL & TỰ ĐỘNG HÓA PHÂN TÍCH DỮ LIỆU (DATA AGENT PIPELINE)

---

## 1. TỔNG QUAN KIẾN TRÚC AGENT DỮ LIỆU KINH DOANH
Để biến một LLM Local (chạy trên máy chủ riêng hoặc máy tính shop qua Ollama / vLLM) thành một nhà phân tích kinh doanh độc lập, hệ thống phải tuân theo kiến trúc **Khép Kín 5 Bước (Autonomous Data Agent Loop)**:

```
[1. CÂU HỎI KINH DOANH TỪ CHỦ SHOP]
   (Ví dụ: "Mặt hàng nào đang tồn kho trên 45 ngày và làm cách nào để xả vốn?")
            │
            ▼
[2. ÁNH XẠ NGỮ NGHĨA & SINH TRUY VẤN SQL (Text-to-SQL)]
   • Nạp DDL lược đồ bảng & Từ điển thuật ngữ kinh doanh
   • Sinh câu lệnh SQL chuẩn xác
            │
            ▼
[3. THỰC THI TRONG MÔI TRƯỜNG CÁCH LY AN TOÀN (Sandbox Execution)]
   • Bật cơ chế READ-ONLY (Chặn tuyệt đối DROP, DELETE, UPDATE)
   • Giới hạn thời gian chạy (Timeout: 10s) & Giới hạn số dòng (LIMIT 100)
            │
            ├──► [NẾU LỖI CÚ PHÁP / LỖI BẢNG]
            │          │
            │          ▼
            │     [VÒNG LẶP TỰ SỬA LỖI (Self-Correction Loop - Max 3 tries)]
            │     Gửi lại mã lỗi SQL cho LLM để viết lại câu lệnh đúng
            ▼
[4. XỬ LÝ KẾT QUẢ DỮ LIỆU THÔ (Result Dataframe)]
   • Tính toán các tỷ lệ phần trăm, đối soát số liệu
            │
            ▼
[5. TỔNG HỢP & XUẤT BÁO CÁO ĐIỀU HÀNH CHO CHỦ SHOP]
   • Viết báo cáo theo cấu trúc SCQA, đề xuất chiến lược xử lý
```

---

## 2. TỪ ĐIỂN ÁNH XẠ THUẬT NGỮ KINH DOANH SANG CỘT DỮ LIỆU (BUSINESS SEMANTIC LAYER)
Khi đưa vào prompt của LLM, bảng ánh xạ này giúp mô hình không bao giờ hiểu sai ý của người dùng:

| Câu hỏi của Chủ Shop | Khái niệm Kinh tế | Biểu thức SQL tương ứng |
| :--- | :--- | :--- |
| "Doanh thu thực tế / Doanh thu đã trừ phí" | Net Delivered Revenue | `SUM(net_revenue) WHERE order_status = 'DELIVERED'` |
| "Hàng bán ế / Hàng đọng vốn" | Deadstock Inventory | `WHERE days_without_sales > 45 AND units_available > 0` |
| "Khách hàng ruột / Khách sỉ" | Champions / High LTV | `WHERE frequency >= 3 AND monetary_total > 20000000` |
| "Đơn boom / Hoàn hàng" | Failed Delivery Losses | `WHERE order_status = 'RETURNED' OR is_cod_returned = TRUE` |
| "Lãi gộp sản phẩm" | Product Gross Profit (CM1) | `SUM(unit_selling_price - unit_cost_price)` |

---

## 3. MÃ NGUỒN PYTHON TRIỂN KHAI HOÀN CHỈNH AGENT TEXT-TO-SQL TỰ SỬA LỖI

Đoạn mã dưới đây sử dụng Python thuần với `sqlite3` và kết nối API của mô hình Local (Ollama hoặc OpenAI-compatible API):

```python
import sqlite3
import re
import json
import requests
from typing import Dict, Any, List

class RetailBusinessDataAgent:
    def __init__(self, db_path: str, llm_api_url: str = "http://localhost:11434/api/generate", model_name: str = "qwen2.5:14b"):
        self.db_path = db_path
        self.llm_api_url = llm_api_url
        self.model_name = model_name
        self.schema_context = self._extract_database_schema()

    def _extract_database_schema(self) -> str:
        """Trích xuất tự động cấu trúc bảng và kiểu dữ liệu từ SQLite để làm context cho AI."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = cursor.fetchall()
        conn.close()
        return "\n\n".join([t[0] for t in tables if t[0] is not None])

    def _call_local_llm(self, prompt: str, system_prompt: str = "") -> str:
        """Gửi prompt tới máy chủ LLM Local."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": 0.1} # Nhiệt độ thấp để sinh SQL chính xác
        }
        resp = requests.post(self.llm_api_url, json=payload, timeout=60)
        return resp.json().get("response", "")

    def _clean_sql_query(self, raw_response: str) -> str:
        """Lọc bỏ các ký tự markdown thừa để chỉ lấy câu lệnh SQL thuần túy."""
        sql_match = re.search(r"```sql\s*(.*?)\s*```", raw_response, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        sql_match_plain = re.search(r"```\s*(.*?)\s*```", raw_response, re.DOTALL)
        if sql_match_plain:
            return sql_match_plain.group(1).strip()
        return raw_response.strip()

    def _execute_safe_sql(self, sql_query: str) -> tuple[List[Dict[str, Any]], str]:
        """Thực thi SQL an toàn ở chế độ Read-Only."""
        # 1. Kiểm tra an ninh: Chặn các lệnh phá hoại dữ liệu
        forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'REPLACE']
        for kw in forbidden_keywords:
            if re.search(rf"\b{kw}\b", sql_query, re.IGNORECASE):
                return [], f"SECURITY_ERROR: Lệnh cấm {kw} không được phép thực thi!"

        # 2. Đảm bảo có LIMIT để tránh tràn bộ nhớ
        if not re.search(r"\bLIMIT\b", sql_query, re.IGNORECASE):
            sql_query += " LIMIT 50"

        try:
            conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True) # Mở DB ở chế độ READ-ONLY tuyệt đối
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            results = [dict(row) for row in rows]
            conn.close()
            return results, ""
        except sqlite3.Error as e:
            return [], str(e)

    def analyze_business_question(self, user_question: str) -> str:
        """Quy trình khép kín: Sinh SQL -> Chạy DB -> Tự sửa lỗi nếu có -> Viết báo cáo phân tích."""
        system_sql_prompt = f"""
Bạn là chuyên gia chuyển đổi câu hỏi kinh doanh sang truy vấn SQLite (Text-to-SQL).
Chỉ trả về DUY NHẤT một khối mã SQL trong thẻ ```sql ... ```. Không giải thích thêm.

CƠ SỞ DỮ LIỆU CỦA SHOP CÓ CẤU TRÚC SAU:
{self.schema_context}

QUY TẮC BẮT BUỘC:
- Dùng đúng tên cột và tên bảng.
- Chỉ đọc dữ liệu (SELECT), tính toán aggregate chuẩn (SUM, COUNT, AVG, ROUND).
- Khi tính doanh thu hoặc sản lượng bán, luôn lọc đơn giao thành công (order_status = 'DELIVERED').
"""
        # Bước 1: Sinh SQL lần đầu
        current_prompt = f"Câu hỏi của chủ shop: {user_question}\nHãy viết truy vấn SQL để lấy dữ liệu trả lời:"
        generated_sql_resp = self._call_local_llm(current_prompt, system_sql_prompt)
        sql_query = self._clean_sql_query(generated_sql_resp)

        # Bước 2 & 3: Thực thi và Vòng lặp Tự sửa lỗi (Self-Correction Loop tối đa 3 lần)
        max_attempts = 3
        results = []
        error = ""
        
        for attempt in range(max_attempts):
            results, error = self._execute_safe_sql(sql_query)
            if not error:
                break
            # Nếu có lỗi, đưa mã lỗi cho AI để viết lại
            fix_prompt = f"""
Câu lệnh SQL sau đây bị lỗi khi chạy trên SQLite:
{sql_query}

Thông báo lỗi từ hệ thống:
{error}

Hãy sửa lại câu lệnh SQL cho đúng cấu trúc bảng và trả về mã mới trong ```sql ... ```:
"""
            generated_sql_resp = self._call_local_llm(fix_prompt, system_sql_prompt)
            sql_query = self._clean_sql_query(generated_sql_resp)

        if error:
            return f"❌ Không thể truy vấn dữ liệu sau 3 lần thử. Lỗi kỹ thuật: {error}"

        # Bước 4 & 5: Đưa dữ liệu thô vào LLM để viết Báo cáo Điều hành CCO
        system_analyst_prompt = """
Bạn là Giám đốc Thương mại & Trưởng bộ phận Phân tích Kinh doanh (CCO).
Dựa trên kết quả số liệu thực tế được cung cấp, hãy viết Báo cáo Phân tích Chiến lược cho Chủ shop.
Tuân thủ nghiêm ngặt định dạng:
1. [HÀNH ĐỘNG KHẨN CẤP 24H]: Việc cần làm ngay lập tức.
2. [BẰNG CHỨNG DỮ LIỆU]: Bảng tóm tắt số liệu cốt lõi trích xuất được.
3. [NGUYÊN NHÂN GỐC RỄ]: Vì sao lại có tình trạng này (MECE / 5 Whys).
4. [CHIẾN LƯỢC TRUNG HẠN]: Kế hoạch 30 ngày tới.
5. [DỰ BÁO TÁC ĐỘNG TÀI CHÍNH]: Ước tính số tiền thu về hoặc tiết kiệm (VNĐ).
"""
        final_prompt = f"""
CÂU HỎI CỦA CHỦ SHOP: {user_question}
CÂU LỆNH SQL ĐÃ CHẠY: {sql_query}
KẾT QUẢ DỮ LIỆU TRÍCH XUẤT TỪ HỆ THỐNG:
{json.dumps(results[:30], ensure_ascii=False, indent=2)}

Hãy viết báo cáo phân tích và hướng đi hành động cụ thể cho chủ shop:
"""
        executive_report = self._call_local_llm(final_prompt, system_analyst_prompt)
        return executive_report
```
