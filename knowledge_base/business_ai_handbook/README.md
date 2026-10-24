# BỘ TÀI LIỆU CHUYÊN GIA DỮ LIỆU & PHÂN TÍCH KINH DOANH CHO AI LOCAL
## (Autonomous AI Chief Commercial Officer & Business Intelligence Handbook)

---

## 1. MỤC TIÊU VÀ SỨ MỆNH HỆ THỐNG
Tập tài liệu này được thiết kế theo chuẩn công nghiệp quốc tế và thực tiễn thương mại tại Việt Nam, nhằm mục đích **huấn luyện (training), nạp tri thức (RAG - Retrieval-Augmented Generation) và làm chỉ dẫn hành động (Agent System Instructions)** cho một mô hình AI Local (Llama 3, Qwen 2.5, DeepSeek, Mistral, v.v.).

Sau khi nạp tri thức này, AI không chỉ là một chatbot trả lời câu hỏi thông thường, mà sẽ đóng vai trò như một **Bộ phận Kinh doanh chuyên nghiệp / Giám đốc Thương mại (Chief Commercial Officer - CCO) / Chuyên gia Phân tích Dữ liệu Kinh doanh Cấp cao (Lead Business Analyst)** cho cửa hàng (Shop bán lẻ & Thương mại điện tử):
1. **Đọc và Phân tích Dữ liệu Thực tế**: Tự động truy vấn SQL, kết nối cơ sở dữ liệu bán hàng, kho vận, chi phí quảng cáo, tồn kho và khách hàng.
2. **Chẩn đoán Sức khỏe Doanh nghiệp**: Xác định chính xác "điểm nghẽn" (bottlenecks) về dòng tiền, tỷ lệ hoàn hàng COD, biên lợi nhuận ròng, hao hụt kho, chi phí cơ hội.
3. **Đưa ra Hướng đi Chiến lược (Prescriptive Analytics)**: Không dừng lại ở việc báo cáo "Doanh thu giảm bao nhiêu %", mà chỉ ra chính xác *Vì sao giảm (Root Cause)*, *Cần làm gì ngay trong 48 giờ tới (Action Plan)*, và *Tác động tài chính dự kiến là bao nhiêu tiền ($ & % Profit Margin)*.

---

## 2. CẤU TRÚC TỔ CHỨC CỦA BỘ TÀI LIỆU (KNOWLEDGE BASE STRUCTURE)

```
knowledge_base/business_ai_handbook/
├── README.md                                            # Tổng quan, Kiến trúc RAG và Hướng dẫn nạp tri thức
│
├── 01_unit_economics_and_metrics/                      # MODULE 1: KINH TẾ ĐƠN VỊ & BÁO CÁO P&L BÁN LẺ
│   ├── 01_ecommerce_pnl_and_unit_economics.md          # P&L E-commerce, Biên đóng góp CM1/CM2/CM3, Chi phí sàn TMĐT, Hoàn đơn COD
│   └── 02_customer_acquisition_retention_metrics.md    # CAC, LTV, LTV:CAC, CAC Payback, Cohort Retention, Phễu chuyển đổi AOV/CVR
│
├── 02_inventory_and_pricing_economics/                 # MODULE 2: QUẢN TRỊ TỒN KHO & ĐỊNH GIÁ CHIẾN LƯỢC
│   ├── 01_inventory_control_and_supply_chain.md        # Vòng quay tồn kho (ITR), DIO, EOQ, Điểm đặt hàng lại (ROP), Tồn an toàn (SS)
│   └── 02_pricing_strategies_and_elasticity.md         # Co giãn giá (PED), Định giá mồi (Loss-leader), Bán chéo combo, Xả hàng cận date
│
├── 03_data_engineering_and_sql/                        # MODULE 3: KỸ THUẬT DỮ LIỆU & TRUY VẤN SQL BÁN LẺ THỰC CHIẾN
│   ├── 01_dimensional_modeling_and_schema_design.md    # Mô hình dữ liệu Kim Cương (Kimball Star Schema): Facts & Dimensions bán lẻ
│   └── 02_production_retail_sql_queries.md             # Bộ truy vấn SQL chuẩn: Cohort Analysis, RFM, Stock Runway, Giỏ hàng kết hợp
│
├── 04_data_science_and_algorithms/                     # MODULE 4: KHOA HỌC DỮ LIỆU & THUẬT TOÁN BÁN LẺ
│   ├── 01_rfm_segmentation_and_customer_lifecycle.md   # Phân khúc khách hàng RFM (Recency, Frequency, Monetary) & Chiến dịch hành động
│   ├── 02_market_basket_analysis_and_clv.md            # Khai phá giỏ hàng (Apriori/FP-Growth, Lift) & Mô hình xác suất CLV (BG/NBD)
│   └── 03_demand_forecasting_and_time_series.md        # Dự báo nhu cầu bán hàng: Seasonality, Lễ Tết, Double-day, LightGBM/Prophet
│
└── 05_ai_agent_and_system_prompts/                     # MODULE 5: KIẾN TRÚC AGENT AI & PROMPT HỆ THỐNG CCO
    ├── 01_chief_commercial_officer_persona_and_prompts.md # System Prompt CCO, Tư duy MECE, Pyramid Principle, Báo cáo SCQA
    └── 02_text_to_sql_and_data_agent_architecture.md    # Kiến trúc Text-to-SQL an toàn, Sandbox thực thi và Vòng lặp tự sửa lỗi SQL
```

---

## 3. HƯỚNG DẪN NẠP TRI THỨC VÀO AI LOCAL (RAG & CONTEXT INJECTION GUIDE)

### 3.1. Phân mảnh văn bản (Chunking Strategy)
Để mô hình Vector Database (Milvus, Chroma, Qdrant, LanceDB) và mô hình Embedding (như `BAAI/bge-m3`, `nomic-embed-text`, `text-embedding-3-small`) đạt hiệu quả tối ưu:
- **Chunk Size**: 800 - 1200 tokens (tương đương 1 mục con hoàn chỉnh gồm công thức + giải thích + code SQL/Python).
- **Chunk Overlap**: 150 - 200 tokens để giữ nguyên ngữ cảnh chuyển tiếp giữa các phần.
- **Metadata Tagging**: Mỗi chunk cần được gắn các thẻ:
  - `category`: `[unit_economics, inventory, pricing, sql, data_science, agent_strategy]`
  - `business_level`: `[operational, tactical, strategic]`
  - `market`: `[global_standard, vietnam_ecommerce]`

### 3.2. Embedding & Vector Search
- **Embedding Model khuyên dùng**:
  - Tiếng Việt & Đa ngôn ngữ: `BAAI/bge-m3` (Hỗ trợ độ dài ngữ cảnh lên tới 8192 tokens, xuất sắc cho cả từ khóa sparse và ngữ nghĩa dense).
  - Tối ưu tài nguyên nhẹ trên Local: `all-MiniLM-L6-v2` hoặc `bkai-foundation-models/vietnamese-bi-encoder`.
- **Hybrid Search**: Khuyến nghị kết hợp Vector Search (Cosine Similarity) với BM25 Search để tìm kiếm chính xác các thuật ngữ kinh tế viết tắt như `AOV`, `CAC`, `LTV`, `EOQ`, `ROP`, `CM1`, `CM2`.

### 3.3. Reranking (Tái xếp hạng)
Sử dụng Cross-Encoder (như `BAAI/bge-reranker-large` hoặc `BAAI/bge-reranker-v2-m3`) để xếp hạng lại top 10 kết quả trước khi đưa top 3 - 5 context phù hợp nhất vào System Prompt của LLM.

### 3.4. Mô hình Ngôn ngữ Local khuyên dùng
- **Khuyến nghị hàng đầu (16GB - 32GB RAM / VRAM)**:
  - `Qwen/Qwen2.5-14B-Instruct` hoặc `Qwen2.5-7B-Instruct` (Khả năng suy luận toán học, viết SQL và hiểu tiếng Việt cực kỳ xuất sắc).
  - `DeepSeek-Coder-V2-Lite-Instruct` hoặc `DeepSeek-R1-Distill-Qwen-14B` (Tư duy chuỗi suy luận logic / Chain-of-Thought phân tích tài chính sâu).
- **Hệ thống cấu hình thấp (8GB - 12GB VRAM / RAM)**:
  - `Qwen2.5-7B-Instruct` định dạng 4-bit (GGUF / Ollama / vLLM).
  - `Meta-Llama-3.1-8B-Instruct`.

---

## 4. QUY TRÌNH RA QUYẾT ĐỊNH CỦA AI BUSINESS ANALYST
Khi nhận dữ liệu từ chủ shop, AI sẽ tuân thủ nghiêm ngặt quy trình 5 bước:

```
[DỮ LIỆU ĐẦU VÀO] (SQL/CSV/Doanh số/Tồn kho/Chi phí ads)
        │
        ▼
[BƯỚC 1: KIỂM TOÁN DỮ LIỆU & TÍNH TOÁN METRICS]
   • Tính GMV, Doanh thu thuần, Giá vốn COGS, Tỷ lệ hoàn đơn COD
   • Tính CM1, CM2, LTV, CAC, Tốc độ xoay vòng kho (DIO)
        │
        ▼
[BƯỚC 2: CHẨN ĐOÁN NGUYÊN NHÂN GỐC RỄ (ROOT CAUSE)]
   • Dùng Cây Vấn Đề MECE & Kỹ thuật 5 Whys
   • Phân tách: Do thị trường? Do giá? Do quảng cáo kém hiệu quả? Hay do đọng vốn tồn kho?
        │
        ▼
[BƯỚC 3: MÔ PHỎNG & SO SÁNH PHƯƠNG ÁN (WHAT-IF SCENARIOS)]
   • Kịch bản A: Giảm giá 10% -> Volume tăng bao nhiêu để bù biên lợi nhuận?
   • Kịch bản B: Cắt bỏ chiến dịch quảng cáo ROAS < 1.5 -> Lợi nhuận ròng tăng bao nhiêu?
        │
        ▼
[BƯỚC 4: HÀNH ĐỘNG CHIẾN LƯỢC (ACTION PLAN)]
   • Việc cần làm trong 24h - 48h (Giá bán, Tồn kho, Đặt hàng NCC, Tắt/Bật Ads)
   • Việc cần làm trong 30 ngày (Đàm phán nhà cung cấp, Tối ưu phễu, CSKH)
        │
        ▼
[BƯỚC 5: ĐO LƯỜNG TÁC ĐỘNG TÀI CHÍNH DỰ KIẾN (IMPACT $ & %)]
   • Ước tính số tiền thu về, giải phóng dòng tiền và tăng biên LN ròng.
```
