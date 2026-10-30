# Admin SQL và biểu đồ — kết quả ngày 23/10/2026

## Kết quả

24/24 lượt admin và 36/36 lượt hồi quy buyer đạt sau chấm ngữ nghĩa riêng với checks cơ học. Bank này do người phát triển soạn và đã dùng để sửa lỗi, không phải kiểm định độc lập. Các ca từ chối tính năng chưa hỗ trợ chỉ chứng minh xử lý đúng giới hạn, không chứng minh đã có tính năng đó.

Checker kiểm tool, tham số, kỳ, SKU, quyền, số tiền, chênh lệch, phần trăm và tổng biểu đồ. Đáp án số admin được tạo từ truy vấn trực tiếp sổ `financial_ledger`, chi phí, đơn và hoàn trả; không gọi lại hàm báo cáo của bot làm đáp án và không đưa gold vào prompt. `human_review.json` ghi việc đọc ý nghĩa câu trả lời và hội thoại; `checks.json` không thay review này.

Toàn bộ 248 test PASS trong 63,22 giây, log `AI/runtime/tests-admin-agent-r4.log`. Bank60/gold r4 giữ nguyên byte từ admin r1. Hash code, SQL, catalog, bank/gold và cấu hình không đổi trong batch; `integrity.json` xác nhận 60 lượt. Code được chụp trong `code_snapshot/`. Không còn batch model đang chạy.

Trung vị 0,9135 giây/lượt, p95 nearest-rank 1,281 giây, tổng70,533 giây. Lượt đầu23,297 giây có chi phí nạp model; trung vị bỏ lượt đầu0,906 giây. Đây là batch local, không phải SLA, chưa đo tải đồng thời hoặc trải nghiệm web production.

## Đã nối trong chế độ agent thử nghiệm

- `CatalogConversation` chuyển yêu cầu quản trị đến `AdminConversation`; quyền do caller server cấp, không do người dùng tự xưng hay model quyết định.
- Báo cáo doanh thu thuần, giá vốn hàng đã bán, lãi gộp, biên gộp, chi phí vận hành, lãi hoạt động trước lãi vay/thuế, số đơn và tiền hoàn khách.
- Kỳ tháng/quý/năm, mốc tương đối theo đồng hồ phiên, so hai kỳ, giữ chỉ tiêu và kỳ qua câu nối. Thiếu kỳ thì hỏi lại. Chuẩn hóa khoảng trắng như tháng9/năm2025 trước khi giải lịch.
- Model chỉ chọn slot. Code kiểm toán tử lịch và bộ nhớ trước SQL: time_mode do model tự chọn không phải bằng chứng có kỳ. Model vẫn có lúc chọn time_mode sai trong raw plan; lớp kiểm tra chặn thực thi sai.
- So sánh dùng delta và phần trăm từ Python; biên gộp dùng điểm phần trăm. Mốc0/âm không tạo phần trăm tăng trưởng giả. Kỳ dài khác nhau được ghi rõ là so tổng, chưa chuẩn hóa theo ngày.
- Biểu đồ PNG theo đúng metric được hỏi, kèm bảng số và artifact có cấu trúc. Đường dẫn đầu ra do server cấp, không nhận từ model. Số biểu đồ lấy từ cùng SQL và được đối chiếu tổng.
- Không có bản ghi là no_data, không tự kết luận doanh thu0. Nguồn có kỳ yêu cầu, số dòng và khoảng ngày thực sự có bản ghi; completeness=unverified. Ví dụ năm2025 chỉ có10–12/2025 được ghi rõ, không khẳng định đủ cả năm.
- Không thay yêu cầu lãi ròng sau thuế bằng lãi gộp/lãi hoạt động; không thay topSKU bằng tổng số đơn. Không chạy SQL/Python tùy ý hoặc ghi dữ liệu.

## Ví dụ đã kiểm trên dữ liệu mô phỏng

Với đồng hồ phiên 23/10/2026:

1. “Doanh thu tháng trước?” →09/2026: 1.189.908.000đ.
2. “So với tháng trước thì sao?” →09 so08, giảm237.412.000đ, tương ứng16,63%.
3. “Còn giá vốn thì sao?” →giữ08/09, đổi chỉ tiêu sang giá vốn; không chuyển sang tư vấn sản phẩm.
4. “Lãi gộp bao nhiêu?” ở hội thoại mới →hỏi kỳ. “Tháng8 năm2026 nhé” →187.149.000đ.
5. “Vẽ biểu đồ chi phí vận hành quý3/2026” →ảnh theo tháng, tổng361.456.588đ, có nhãn mô phỏng.

Các con số này thuộc scenario, không phải số liệu kinh doanh thật của shop. Không ghép35đơn backend với1427đơn scenario.

## Quá trình và giới hạn

r1 review ban đầu50/60, r2 review ban đầu58/60. r3 checks60/60 nhưng audit độ phủ ngữ nghĩa59/60: số năm2025 đúng SQL, song chưa nói cụ thể dữ liệu chỉ có10–12/2025. r4 sửa trình bày độ phủ và qua60/60. Raw, bank, gold, code snapshot và review mỗi vòng giữ riêng; không đổi gold để nâng điểm.

Chế độ mặc định vẫn không đổi. Chưa nối agent vào phiên xác thực backend/web; frontend không sửa. Caller tích hợp phải giữ role và profile trong phiên server, cấu hình catalog/SQL/report_directory ở server, rồi truyền `CatalogConversation(tools)` cho `Engine(..., tool_agent=...)` khi bật chế độ `agent_tools`. Artifact admin cần được phục vụ qua kênh có kiểm quyền, không công khai đường dẫn thành URL.

Chưa nối nhánh tài liệu trong prototype này, lọc/xếp hạng SKU, nhập Excel/DE đầy đủ, dự báo/DS, review thật, HyDE hoặc fine-tune Kev/Colab. Chưa accepted_for_application; cần bộ kiểm định độc lập và kiểm thử điều kiện hỗn hợp/phủ định/đổi vai/mốc lịch trước production.

## Bước tiếp

Ưu tiên DE: raw bất biến và manifest nguồn → mapping schema/ngày/tiền/SKU → profile và quarantine lỗi → đối soát bán/hoàn/giá vốn/chi phí → phát hành curated revision. Không tự xóa outlier, gộp nguồn hoặc lấp ngày thiếu bằng0. Sau đó mở rộng semantic metrics và mới backtest dự báo. Kiểm thử admin thêm ca chưa lộ, đặc biệt grain, độ phủ, nhiều kỳ và câu phủ định; giữ validation RAG lịch sử nguyên vẹn.

Không train/Colab, tải model mới, dùng API trả phí, deploy hoặc khởi động lại/bypass worker embedding8011/r19 trong công việc này. Automation hiện có đã lưu yêu cầu tiếp tục từ checkpoint khi lượt chạy sau khả dụng sau hạn mức; không hứa chạy đúng thời điểm reset và không tự mua credits.
