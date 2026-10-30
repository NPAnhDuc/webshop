# Nâng cấp RAG, tri thức và fine-tune reranker — 24–25/10/2026

Mọi số đều là development đã lộ (người viết sửa lỗi khi đã thấy bộ câu), không phải independent validation. Database giữ nguyên: `data/business_sql/scenario_v1/shop.sqlite`; mọi số liệu shop trong câu trả lời phải khớp database này.

## Kết quả

| Bộ | Trước | Sau | Ghi chú |
|---|---:|---:|---|
| 479 quality loop (`quality_loop_20261024_kb3/kb3_final_r5`) | 450 (patch9) | **462** | 287 giống patch9, 58 câu số liệu đối chiếu từng số với SQL, 96 đổi có đủ trích dẫn chuẩn, 38 đọc tay (27 đúng) |
| Câu hỏi theo kỳ, đáp án SQL độc lập (`period_20261024_*`) | 3/14 | **14/14** | quý, tháng; trước đây đọc "quý 3/2026" thành tháng 3, quý chỉ lấy 1 tháng |
| Handbook admin (`handbook_20261024_*`) | 3/20 | **17/20** (đọc tay) | còn H10 hỏi lại thừa, H13, H15 chưa đưa SQL |
| 300 người mua (agent) | catalog 250/250 | 250/250 | kiến thức 5/6 khoảng trống được trả lời đúng nguồn; chính sách vẫn trung thực "chưa có nguồn" |

Còn sai trong 479 (17): Q0020, Q0102, Q0116, Q0130 (handbook làm mất ý "chưa mô hình hóa thuế"), Q0137, Q0168, Q0196, Q0203, Q0214, Q0241, Q0351 và 6 câu sai từ patch9 không đổi.

## Thay đổi chính (`shopbot/`)

1. **Số liệu admin theo kỳ trả bằng SQL** (`rag_metrics.py`): doanh thu thuần, lãi gộp, giá vốn, số đơn, chi phí vận hành, tiền hoàn, lợi nhuận hoạt động theo tháng/quý dùng `analyze_business` (cùng SQL công cụ tài chính). Quý có tổng và từng tháng; kỳ không có dữ liệu nói rõ. Câu về mục tiêu/kế hoạch/nguyên nhân/nhóm/kênh/SKU hoặc có sẵn con số vẫn đi tài liệu.
2. **Sửa đọc kỳ** (`rag_scope.py`): "quý 3/2026" không còn bị hiểu là tháng 3.
3. **Cách ly bằng chứng theo đối tượng đã xác định** (`grounded_rag.py`): câu thuộc tính của sản phẩm đã gắn chỉ chọn trong hồ sơ sản phẩm đó; tên tài liệu trích nguyên văn “…” gắn đúng tài liệu (tìm cả khi router lọc nhầm loại); "Giải thích nội dung “X”" trình bày các câu của X theo thứ tự thay vì để model chọn 1–2 câu; nhãn trường gõ nguyên văn ("thể tích ngoài", "loại") luôn được trả; câu nối "…sản phẩm vừa nói" không bị hỏi lại khi server đã gắn sản phẩm.
4. **Reranker đã fine-tune** (bật bằng `RAG_EVIDENCE_RERANK=1`, đã bật trong `.env`): sắp xếp ứng viên trước khi model 4B chọn; khi bật, tài liệu phương pháp (handbook) bị bộ lọc loại che có thể được xét nhưng chỉ giữ nếu điểm cao hơn mọi ứng viên đúng loại. Lỗi worker → giữ thứ tự cũ.
5. **Agent**: `documents.answer` nối RAG thật; `catalog.product_facts`; câu kết hợp; định tuyến chính sách/so sánh thứ tự (xem các REPORT trong `buyer_run_*`).

## Tri thức đã nạp (KnowledgeStore, có phiên bản)

- `data/unstructured/technology_20261024_gaps/`: 5 tài liệu từ nguồn chính thức (Intel, NVIDIA, CLEAResult 80 PLUS, Samsung Semiconductor), URL + ngày tải + hash; Intel đọc qua web vì script bị 403 (ghi `web_reviewed`), Kingston bị chặn nên không dùng. Câu "ưu tiên tài liệu bảo hành nào" là chính sách nội bộ — chưa có nguồn, không tự tạo.
- `data/unstructured/handbook_20261024/`: 9 tài liệu admin từ `knowledge_base/business_ai_handbook` (commit 4cc4b89). Module 3.1 (lược đồ Kimball không tồn tại) thay bằng từ điển dữ liệu sinh từ `shop.sqlite`; module 3.2 viết lại cho SQLite, mọi truy vấn lãi lỗ/đơn/kênh đã chạy và **bằng đúng** công cụ tài chính cho 09/2026, Q3/2026 và cả năm; RFM đối soát tổng doanh thu với sổ cái. Module 05 (system prompt) không nạp. Số minh họa được ghi rõ không phải số shop.

## Fine-tune

- **Reranker cross-encoder** (`models/evidence_reranker_20261024/`, train CPU 2 epoch, ~40 phút/epoch): nền PhoBERT `vietnamese-embedding` rev `4ab46e46…`, đóng băng 8 lớp, train 4 lớp trên + đầu điểm. Dữ liệu `data/finetune_20261024/` (1.247 train / 261 dev, chia theo sản phẩm/tài liệu): nhãn lấy từ hồ sơ catalog/tài liệu (khớp DB), câu hỏi từ mẫu khác mẫu bộ đánh giá + câu do Qwen local viết từ đoạn nguồn; loại mọi câu trùng bộ đánh giá. Dev top-1 **93,5%** (MRR 0,959) so với cosine 73,6%, BM25 68,2%.
- **Không fine-tune Qwen3-4B tại máy**: RTX 2060 6 GB (Ollama dùng 4,2 GB), RAM 8 GB, torch CPU — QLoRA 4B cần ~10–12 GB VRAM. Muốn làm cần Colab/GPU thuê, và cần bộ nhãn mới.
- **HyDE không áp dụng**: đo cho thấy truy xuất đã đưa tài liệu đúng lên hạng 1–2; lỗi nằm ở khâu chọn đoạn. HyDE thêm một lần gọi 4B và rủi ro thuật ngữ bịa.

## Ổn định hệ thống

- Worker embedding rò bộ nhớ (mỗi request một luồng mới, torch/oneDNN giữ bộ đệm theo luồng; +750 MB/60 request) gây Ollama `bad_alloc` và runner `MemoryError`. Sửa: server một luồng + đệm theo kích thước cố định; đo lại ổn định ~1,37 GB sau 120 request. Lỗi này có từ trước, ảnh hưởng cả web khi chạy lâu.
- `VI_UNDERSTANDING_ADAPTER=0` cho phép không nạp adapter hội thoại cũ (không dùng ở `basic_rag`), mặc định vẫn nạp.

## Kiểm thử

586 unit test PASS (`runtime/tests-rag9-full.log`). Chưa chạy lại bộ old100 và split validation 121.

## Việc tiếp theo đề xuất

Chính sách shop thật (giao hàng, đổi trả, VAT, trả góp, chi nhánh) từ chủ shop; bộ câu hỏi mới giữ riêng (holdout) để đo thật; Q0130/Q0196/Q0203; câu viết dính (đang hoãn); fine-tune model sinh nếu có GPU.
