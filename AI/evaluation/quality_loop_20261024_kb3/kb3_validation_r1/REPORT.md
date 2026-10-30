# Validation 121 — lần mở thứ hai (26/10/2026)

Chạy `scripts/run_quality_loop_kb3_20261024.py --split validation --round kb3_validation_r1` trên cấu hình hiện tại (KB3: gói kỹ thuật + handbook, ngày 24/10/2026, `RAG_EVIDENCE_RERANK=1`, toàn bộ sửa đổi RAG 24–25/10 và automation 25/10). Dịch vụ bật lại bằng `start-local.ps1 -SkipMonthly` sau khi máy khởi động lại. 121/121 hoàn tất, 0 lỗi hạ tầng; kiểm tra tự động 105 PASS_CHECKS / 15 NEEDS_REVIEW / 1 FAIL_CHECKS.

Bộ này được mở lần đầu với patch5 (`quality_loop_20261021/validation_v1`, đọc tay 112/121). Từ đó các lần sửa chỉ dựa trên bộ development; chín câu FAIL của lần đầu đã được ghi trong báo cáo cũ nên đây là "gần độc lập", không phải holdout mới hoàn toàn.

## Kết quả đọc tay

| | patch5 (21/10) | hiện tại |
|---|---:|---:|
| Tổng | 112/121 | **117/121** |
| Khách hàng | 49/52 | 51/52 |
| Admin | 63/69 | 66/69 |

Phương pháp: 90 câu trả lời giống hệt `validation_v1` giữ nhãn cũ (88 PASS, 2 FAIL); 31 câu đổi được đọc đầy đủ với trích dẫn chuẩn, rubric và lý do chấm cũ. Không câu nào từng PASS chuyển thành FAIL.

Sửa được 5: Q0037 (dự báo/nhập hàng → nói rõ cần công cụ ngoài RAG thay vì hỏi lại), Q0078 ("máy vừa nói" khi chưa có máy → hỏi lại thay vì trả chính sách chung), Q0158 (định vị đủ quy mô/phân khúc/kênh, không còn báo thiếu mâu thuẫn; có thêm 2 dòng tên cột từ từ điển dữ liệu), Q0232 ("Không" + ngân sách marketing thường xuyên), Q0328 (đủ "loại" và "thể tích ngoài").

Câu sản phẩm đổi (16) chủ yếu bỏ dòng nhiễu không được hỏi (màn hình/HDMI khi hỏi CPU, cảnh báo flash khi hỏi dung lượng).

Còn sai 4: Q0124 (khách hỏi doanh thu shop — phản hồi phân quyền chưa đúng yêu cầu rubric), Q0274 (câu kế toán "cộng tiền mua hàng chưa bán vào giá vốn" bị định tuyến sai), Q0223 (C-BTS hết hạn 31/8 — nay trích nhầm chiến dịch C-TET, không kết luận), Q0266 (so bản quy định tháng 3 và tháng 4 — vẫn thiếu bản cũ).

Chấm do Claude đọc, chưa có người duyệt độc lập. Không train, không nạp câu trả lời vào tri thức. Chi tiết nhãn: `semantic_review.json`, phân nhóm: `partition.json`.
