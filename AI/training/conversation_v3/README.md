# Model tiếng Việt local và hiểu hội thoại v3

- Hội thoại: Qwen3-4B-Instruct-2507 Q4_K_M qua Ollama, endpoint 127.0.0.1:11435.
- Tìm tài liệu: dangvantuan/vietnamese-embedding (PhoBERT, 768 chiều), PyVi tách từ + mean pooling, worker CPU 127.0.0.1:8011. Inference offline sau tải.
- Qwen3 là model đa ngôn ngữ hỗ trợ tiếng Việt; PhoBERT là encoder chuyên tiếng Việt, không phải model tự viết câu trả lời.
- Từ khóa + embedding kết hợp RRF, lọc quyền/phiên bản/hiệu lực trước khi tìm kiếm. Khi worker chưa sẵn sàng, nguồn ghi rõ TF-IDF fallback.
- Model quyết định ý định, tham chiếu thời gian và tiêu chí; code kiểm tra schema, quyền, lịch và SQL. Không chạy SQL hoặc Python do model viết.
- Bộ nhớ trong phiên, tách vai trò; 6 lượt gần nhất + kỳ/ý định/tiêu chí đang xem. Nút cuộc trò chuyện mới xóa bộ nhớ. Chưa phải trí nhớ người dùng xuyên thiết bị.

## Train trên Colab

`data/manifest.json` ghi số mẫu và giới hạn. Train/validation/test tách nhóm cách diễn đạt trước khi mở rộng kỳ/ngữ cảnh; không có text trùng giữa các split. Đây là dữ liệu tổng hợp, cần thêm hội thoại thật đã được duyệt.

`train_colab.py` train 4 lớp cuối PhoBERT + 4 đầu phân loại (ý định, thời gian, tiêu chí, đơn vị kỳ), 4 epochs. Chọn checkpoint bằng validation; test chỉ dùng sau chọn. `outputs/tutor-failures.jsonl` là hàng đợi gia sư: kiểm tra ngữ cảnh, sửa nhãn có căn cứ rồi tạo phiên bản dataset mới; không tự biến câu trả lời sai thành sự thật và không đưa test cũ vào train rồi báo lại test đó.

Adapter đã tải về và được thử làm gợi ý cho planner Qwen qua worker local sau pilot 15/15. Nó không thay planner hay tự quyết quyền công cụ; xem `results/activation-review.json`. Không nhét doanh thu vào trọng số. Số bán/doanh thu/lợi nhuận lấy từ SQL cùng 67 SKU, dữ liệu mô phỏng 10/2025–09/2026.

## Kiểm tra local

`python scripts/evaluate_conversation_local.py --model qwen3:4b-instruct-2507-q4_K_M --output training/conversation_v3/results/qwen3-pilot.json`

Đây là pilot nhỏ có chuỗi câu như ảnh người dùng, câu thiếu kỳ, thay tiêu chí, đổi kỳ, so sánh và kế hoạch; kết quả không chứng minh độ chính xác ngoài thực tế. Unit test có mock chỉ kiểm tra hợp đồng công cụ/bộ nhớ; pilot trên gọi model thật mới đo khả năng hiểu.

## Kết quả đã xác nhận 19/10/2026

- Dataset revision 2: 2.676 mẫu; train 1.748, validation 464, test 464. Các biến thể cùng câu với ngữ cảnh khác không được coi là hội thoại khách độc lập.
- Tesla T4: 4 epochs, 440 optimizer steps, 135,9 giây, chọn epoch 3. Validation joint accuracy 93,53%; frozen synthetic test joint accuracy 100%. Không phải con số production.
- Gói Colab đã tải và khớp SHA256 hiển thị trong notebook: `c296249f0d5b5ff4aa0768de76bafc475b80a794a2c41038755f782a0c7eb6fe`.
- Pilot thực thi local: model cũ 10/15, Qwen3 lần đầu 12/15, sau sửa hướng dẫn 13/15, kết hợp gợi ý PhoBERT + Qwen3 15/15. Đây là pilot được dùng để cải thiện, không phải test mù; validation/test Colab tách riêng.
- Kiểm tra truy xuất 4 câu: tìm đúng tài liệu mong đợi trong top 3, nguồn ghi dense tiếng Việt + TF-IDF, không bị cắt token ở các kết quả này.
- 69 unit/integration tests qua. Bộ nhớ chỉ trong phiên; dữ liệu số vẫn là mô phỏng.

## Sau đánh giá mở rộng

Adapter phân loại tổng hợp chưa bao phủ đủ tác vụ; giữ checkpoint để đối chiếu, mặc định không gọi. `VI_CLASSIFIER_SHADOW=1` mới chạy kiểm tra; kết quả không đưa vào prompt planner. Embedding PhoBERT gốc vẫn dùng tìm tài liệu. Cải thiện sau audit là sửa planner/bộ nhớ/SQL, không có lượt finetune mới. Xem [IMPROVEMENT_REPORT.md](IMPROVEMENT_REPORT.md) để biết số câu PASS/FAIL, hồi quy và giới hạn còn lại.
