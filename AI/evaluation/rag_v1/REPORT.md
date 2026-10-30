# Cải thiện RAG cơ bản — 20/10/2026

Phạm vi: RAG tài liệu và luồng admin SQL + tài liệu. Không fine-tune mới, không chuyển sang agentic RAG.

## Kết quả

| Kiểm tra | Trước | Sau |
|---|---:|---:|
| Trả lời đúng phần được hỏi, dev | 29/32 | 32/32 |
| Tìm được đoạn chuẩn, dev | 87.9% | 97.0% |
| Độ dài trung bình câu trả lời, dev | 139 từ | 57 từ |
| 16 ca giữ riêng | Chưa đo baseline | 14/16 |
| Hội thoại nhiều lượt / quyền / đối chiếu kế hoạch | — | 7/7 |

Bộ nhỏ được viết từ tài liệu shop mô phỏng: 48 ca, có các biến thể cùng họ câu. Không phải độ chính xác production. 16 ca giữ riêng không được dùng để sửa. Bộ chấm kiểm tra con số/từ khóa cần thiết và thừa nhận phần thiếu; kiểm tra thủ công vẫn cần cho câu trả lời tự do.

## Đã sửa

- BM25 giữ mã chiến dịch kết hợp TF-IDF và embedding tiếng Việt bằng RRF; nhận Q3/2026, tăng số bằng chứng để ghép nhiều nguồn.
- Chunk theo heading kể cả thiếu dòng trống, giữ tiêu đề bảng/đơn vị; bỏ nhãn mô phỏng lặp khỏi văn bản nhúng nhưng giữ nguyên trong nguồn và metadata.
- Model chọn câu/dòng bảng có sẵn và phần câu hỏi chưa được giải đáp; renderer ghép bằng chứng ngắn, dẫn mục/phiên bản. Không ghép nguyên các chunk dài như trước.
- Cung cấp ngày hiệu lực cho bộ chọn bằng chứng. Các bước lọc quyền, bản nháp và phiên bản vẫn thực hiện trước tìm kiếm.
- Viết lại câu nối bằng câu hỏi tài liệu trước và kỳ server đã xác nhận; giữ bộ nhớ theo vai trò. Tăng giới hạn đầu ra riêng bước viết lại để tránh JSON bị cắt.
- Làm rõ SUP-LAP/SUP-PC từ bảng suppliers, lưu procurement v2 và provenance; giữ v1, không thay số kinh doanh.
- Admin có đối chiếu mục tiêu/thực hiện, bảng nhóm hàng, SKU ưu tiên kiểm tra và tồn lịch sử. Tháng 9 thiếu 349.092.000 đồng; không quy hụt kế hoạch cho ngành hàng khi thiếu mục tiêu ngành hàng.

## Kiểm chứng và các bản không chọn

- Kiểm tra độc lập 64 trích đoạn đã hiển thị: 0 không khớp nguồn. Đây chỉ là kiểm tra nguồn, không bảo đảm hiểu đúng toàn bộ câu hỏi.
- 111 unit/integration tests qua; kiểm tra mục tiêu sau sửa cuối cũng qua. Tính tiền lấy từ SQL, không dùng model viết SQL/Python.
- Reranker bằng model từng làm rơi nguồn đúng; không bật mặc định. Các thử nghiệm diễn giải tự do trả lời thiếu/lặp nên không triển khai. Giữ raw logs của các bản dừng hoặc bị loại.
- Hiệu chỉnh bộ chấm: quy tắc không cộng dồn có thể nằm ở cả chính sách giá và lịch marketing; một câu về quyền thay ngân sách chỉ có bằng chứng một phần. Lưu errata riêng, không ghi đè bank/raw run.
- Hồi quy ngoài tài liệu: 84/94 PASS; 0 câu vốn đúng bị sai. Các tác vụ thiếu dữ liệu/chưa hỗ trợ vẫn được ghi FAIL.

## Còn hạn chế

- Hai ca giữ riêng chưa đạt: cách nói “quá ba tháng” chưa nối đúng ngưỡng 90 ngày; câu vừa hỏi xả kho vừa hỏi quyền thay ngân sách chưa nói rõ phần ngân sách còn thiếu.
- Bản chọn dùng tổng hợp trích xuất nhiều nguồn, chưa có diễn giải tự do đủ tin cậy. Không gọi nó là RAG hoàn hảo.
- Chưa có reranker được chứng minh tốt hơn, chưa đánh giá production, chưa tăng chất lượng tư vấn mua hàng sâu ở lượt này.
- Dữ liệu vẫn mô phỏng. Điều khoản shop chưa có vẫn phải thiếu; không tự chế chính sách/thuế/dự báo hoặc kết luận nhân quả.

## Tệp bằng chứng

- `bank.json`, `manifest.json`, `errata.json`: câu hỏi và nguồn chuẩn.
- `baseline_dev/`, `baseline_reviewed/`, `extractive_dev_v6/`, `final_holdout_v6/`: raw results và số đo.
- `conversation_v7/`: kiểm thử model thật nối câu và luồng admin.
- `core_regressions_v7/`: hồi quy số liệu/sản phẩm/quyền; không trộn bộ chấm tài liệu cũ yêu cầu chép nguyên chunk vào điểm RAG mới.
- `verification.json`, `corpus-correction.json`: hash và đối soát nguồn/dữ liệu.
