# Cải thiện hội thoại — 19/10/2026

Bộ cũ cùng 106 câu: **69 PASS / 37 FAIL → 93 PASS / 13 FAIL**.
12 câu diễn đạt bổ sung: **10 PASS / 2 FAIL**.

Cùng database mô phỏng, cùng câu hỏi và đáp án SQL. Không sửa nhãn để nâng điểm. Mốc trước là bản đã rà soát thủ công: hai từ chối quyền đúng được PASS. Các lượt thử dừng giữa chừng giữ riêng, không dùng làm điểm cuối. Đây là bộ kiểm thử phát triển, không phải ước lượng chất lượng trên khách thật.

## Đã thay đổi

- Sửa phân tích Q4/2025 và ký hiệu tháng/quý; lịch vẫn do code kiểm tra.
- Model chọn thay đổi của lượt nối; server giữ kỳ, tiêu chí, số kết quả và nhóm khi không đổi. Công cụ mới không bị ép về ý định cũ.
- SQL lọc laptop/chuột/GPU/các nhóm linh kiện trước xếp hạng, giữ đồng hạng cao nhất.
- Trả CPU/GPU từ product_facts bằng danh sách trường công khai; không đưa bản ghi thô vào câu trả lời.
- Phân biệt tiền hoàn, tiền nhập, số đơn, doanh thu theo kênh; số tính từ sổ SQL.
- Tìm tài liệu theo ngày của phiên hỏi, quyền và hiệu lực; không khẳng định có OLED khi không có.
- Đồng nhất cửa sổ ngữ cảnh 6144 ở hai bước gọi Ollama để tránh nạp lại model.
- Encoder phân loại tổng hợp giữ để đối chiếu, mặc định không gọi; embedding tiếng Việt tìm tài liệu vẫn hoạt động.

12 câu bổ sung lần đầu đạt 9/12, bản được chọn đạt 10/12. Thử thêm ví dụ JSON đạt 12/12 câu này nhưng bộ chính giảm từ 93 xuống 92/106, hồi quy Q054 (đổi chủ đề). Đã lưu thử nghiệm và khôi phục nguyên source bản 93/106, xác nhận bằng SHA256. Không coi các bộ đã dùng để sửa là test mù.

Đợt này sửa planner, bộ nhớ và công cụ; không có lượt finetune trọng số mới. Dữ liệu doanh thu vẫn là mô phỏng, không trở thành dữ liệu shop thật sau sửa.

## Kiểm chứng

91 unit/integration tests qua. `verification.json` xác nhận cùng ngân hàng câu hỏi, cùng SHA256 database, source lúc chạy khớp source hiện tại; kiểm tra thêm 12 câu bằng cùng đáp án SQL độc lập.

Lỗi thực thi: 0. Ca hồi quy so với bản trước: không có.

## Câu vẫn FAIL

| Mã | Hỏi | Lý do |
|---|---|---|
| Q063 | Đổi trả được trong mấy ngày? | Tài liệu demo chưa có thời hạn/điều kiện hoặc quy định thanh toán cụ thể để giải đáp; chỉ tìm thấy nguồn không đủ tính PASS. |
| Q064 | Mua laptop có được trả góp không? | Tài liệu demo chưa có thời hạn/điều kiện hoặc quy định thanh toán cụ thể để giải đáp; chỉ tìm thấy nguồn không đủ tính PASS. |
| Q065 | Điều kiện bảo hành của shop như thế nào? | Tài liệu demo chưa có thời hạn/điều kiện hoặc quy định thanh toán cụ thể để giải đáp; chỉ tìm thấy nguồn không đủ tính PASS. |
| Q073 | Cho tôi ba laptop tầm 18 đến 22 triệu, ưu tiên OLED. | Chưa giữ điều kiện màn hình OLED. |
| Q078 | Laptop dưới 1 triệu có hàng không? | Không có sản phẩm đáp ứng; ghi FAIL về khả năng hoàn thành yêu cầu, dù từ chối đúng. |
| Q093 | Dự báo doanh thu tháng 11 năm 2026 kèm khoảng dự báo 95%. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu forecast. Không tính câu trả lời chung chung là PASS. |
| Q094 | Xuất file Excel chi tiết doanh thu tháng 9 năm 2026 cho tôi tải. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu excel. Không tính câu trả lời chung chung là PASS. |
| Q095 | Build PC 25 triệu tương thích đầy đủ CPU, main, RAM, GPU và nguồn. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu pc_compatibility. Không tính câu trả lời chung chung là PASS. |
| Q096 | Chứng minh quảng cáo tháng 8 năm 2026 gây ra bao nhiêu doanh thu tăng thêm. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu causal_analysis. Không tính câu trả lời chung chung là PASS. |
| Q097 | Tính lợi nhuận ròng sau thuế thu nhập tháng 9 năm 2026. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu net_profit. Không tính câu trả lời chung chung là PASS. |
| Q098 | Lấy doanh thu tháng 12 năm 2026. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu future_data. Không tính câu trả lời chung chung là PASS. |
| Q099 | So sánh doanh thu năm 2026 với đủ 12 tháng năm 2025. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu complete_years. Không tính câu trả lời chung chung là PASS. |
| Q100 | Phân nhóm khách hàng RFM và cho danh sách từng nhóm trong năm 2026. | Chưa có kết quả/đáp án kiểm chứng được cho yêu cầu rfm. Không tính câu trả lời chung chung là PASS. |

## Các câu bổ sung còn FAIL

- Q006: Top 2 chuột về doanh số tháng 7/2026. — Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.
- Q007: Giữ nguyên bảng đó, chuyển sang tháng sáu. — Cần revenue; nhận units.; Sai SKU/thứ tự/số kết quả hoặc chưa áp dụng bộ lọc ngành hàng.; Câu trả lời thiếu tên hoặc giá trị của sản phẩm cần trả.

Chuỗi doanh số từng chọn nhầm đơn vị ở câu đầu rồi kế thừa sai sang câu sau. Đây là một lỗi gốc ảnh hưởng hai lượt. Hàng đợi `tutor-review-queue.jsonl` giữ lỗi trước sửa, trạng thái chạy lại và đáp án SQL; chưa tự cho vào train. Cần rà nghĩa từ/đơn vị và dựng lại ngữ cảnh chuẩn cho câu nối trước khi gán nhãn huấn luyện.

Các yêu cầu thiếu dữ liệu/chức năng vẫn FAIL dù trả lời giới hạn đúng. Không tự tạo thuế/chính sách, dự báo có độ tin cậy, bằng chứng nhân quả hoặc tương thích linh kiện để biến thành PASS.

- Chi tiết 106 câu được chọn: `audit_improved_20261019_verified_v2/REPORT.md`.
- Chi tiết 12 câu bổ sung được chọn: `audit_new_wording_20261019_v2/REPORT.md`.
- Thử nghiệm không kích hoạt: `audit_improved_20261019_verified_v3/REPORT.md` và `audit_new_wording_20261019_v4/REPORT.md`.
- Bản trước giữ nguyên: `audit_extended_20261019_v1/reviewed/REPORT.md`.