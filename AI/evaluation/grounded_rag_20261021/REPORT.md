# Cải thiện RAG cơ bản — 21/10/2026

Đã chạy lại đủ 100 câu với cùng câu hỏi, tiêu chí, vai trò, lịch sử theo nhóm và mốc 20/10/2026. Tổng **67/100 → 85/100**.

| Chỉ tiêu | Trước | Sau |
|---|---:|---:|
| Người mua | 42/50 | 45/50 |
| Admin | 25/50 | 40/50 |
| Trả nội dung/phần đã biết | 43/67 | 55/67 |
| Hỏi lại/thiếu/giới hạn/quyền | 24/33 | 30/33 |
| Trung vị thời gian | 7.88s | 5.38s |
| Tổng thời gian 100 câu | 705.25s | 555.95s |
| Chậm nhất | 36.99s | 12.28s |

## Những gì đã thay đổi

- Giữ phạm vi thời gian có cấu trúc qua các lượt; xác định tháng/quý tương đối bằng lịch. Lọc đúng kỳ trước khi đưa nguồn vào model; kỳ không có thì không lấy năm khác thay.

- Giữ chủ đề hội thoại và tách câu nhiều ý để yêu cầu model chọn bằng chứng cho từng phần. Đưa thuộc tính nguồn vào ID để giảm nhầm RAM/CPU, mục tiêu/thực hiện; đây là hỗ trợ model, không phải bộ chứng minh đã trả đủ.

- Ưu tiên SKU được gọi tên, chia ngân sách ngữ cảnh giữa nhiều sản phẩm. Loại tài liệu do model đoán được mở rộng trong miền tương thích; thiếu chính sách shop không lấy bài kỹ thuật để lấp.

- Đã mở đọc archive khi admin yêu cầu rõ, chỉ với mã tài liệu đã duyệt còn tồn tại; không phục hồi tài liệu đã gỡ hoặc mở nguồn nội bộ cho người mua. Tuy nhiên hai câu đối chiếu lịch sử vẫn FAIL, nên chưa nghiệm thu chức năng này.

- Cache vector theo hash nội dung và model/revision, dùng lại giữa các tập nguồn và sau khởi động lại. Thay tài liệu/model tạo khóa mới; quyền đọc, phiên bản và ngày hiệu lực vẫn được lọc ở mỗi câu hỏi. Cache không lưu câu trả lời hoặc quyền truy cập.

- Giữ hai bước model local: hiểu yêu cầu rồi chọn nguồn. Phương án gộp một lần gọi bị loại vì làm sai các câu thuật ngữ vốn đúng. Không fine-tune, không train Colab, không thêm dữ liệu thật/giả để làm đẹp điểm; SQL và manifest tri thức giữ nguyên hash.

## Lỗi được sửa và lỗi còn lại

Chuyển FAIL→PASS: C04, C09, C26, C31, C34, C45, A03, A04, A05, A06, A08, A12, A14, A16, A17, A18, A21, A33, A34, A41, A42, A43. Chuyển PASS→FAIL: C03, C06, C44, A39.

Còn 15 câu FAIL: C03, C06, C29, C35, C44, A15, A20, A23, A29, A30, A35, A39, A40, A44, A50. Có 10 câu FAIL nhưng bot tự gắn full; nhãn đó chưa đủ đáng tin để nghiệm thu tự động.

Các lỗi và câu trả lời nguyên văn được giữ trong báo cáo từng câu bên dưới. Những câu thiếu ý, sai kỳ hoặc sai trọng tâm vẫn bị đánh FAIL dù trích đúng văn bản.

## Kiểm chứng và giới hạn

Đã kiểm tra 195 trích đoạn: 0 lỗi đoạn không có trong nguồn; 0 ca nguồn admin lọt sang người mua; 0 kết quả rỗng do ngoại lệ. Hash dữ liệu và mã trong lượt chạy không đổi. Chỉ kiểm tra đúng nguyên văn không chứng minh đã chọn đúng ý.

159 kiểm tra tự động đã qua (155 lõi và 4 Streamlit; 39 kiểm tra tập trung nằm trong 155). [Lệnh chạy và phạm vi kiểm tra](VALIDATION.md). React/Express chưa được kết nối trong thay đổi này; Streamlit dùng pipeline mới theo mặc định, RAG_PIPELINE=legacy cho đối chiếu.

Bộ 100 này được dùng để tìm và sửa lỗi, nên là bộ hồi quy phát triển, chưa phải bộ nghiệm thu mù. Codex soạn và chấm thủ công theo tiêu chí/nguồn, không phải đánh giá độc lập của người thật hoặc tỷ lệ đúng ngoài thực tế.

Hai lượt chạy khác ngày, trạng thái cache và áp lực RAM khác nhau. Mốc thời gian nghiệp vụ vẫn cố định để so đáp án. Các số thời gian là quan sát cả lượt chạy, không phải chứng minh tăng tốc trong môi trường kiểm soát hay SLA nhiều người dùng.

Dữ liệu kinh doanh vẫn là mô phỏng 67 SKU và 12 tháng. Các chính sách thật còn thiếu phải được shop xác nhận. RAG này đọc báo cáo có sẵn; chưa tính KPI từ giao dịch, dự báo hay thực hiện hành động.

Cần ưu tiên sửa bốn câu thoái lui C03, C06, C44, A39 và kiểm tra trên bộ câu hỏi mới độc lập; không coi 85/100 là đã hoàn thiện RAG.

## Tệp đối chiếu

- [Chấm đủ 100 câu](final_v7/REPORT.md) và [đáp án nguyên văn](final_v7/ANSWERS.md).

- [Kết quả thô và thời gian](final_v7/results.json), [chấm thủ công](final_v7/review.json), [hash/kiểm tra](final_v7/integrity.json).

- [Baseline 67/100](../adversarial_100_20261020/REPORT.md). Các thư mục pilot/full_v1…full_v6 là bản thử bị bỏ hoặc dừng, không cộng thành điểm lượt cuối.
