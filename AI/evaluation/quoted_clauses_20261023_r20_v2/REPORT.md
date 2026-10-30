# R20: kiểm tra offline cách tách câu có tên bài viết

Đã đọc lại 479 kết quả development của patch9; không gọi model, dịch vụ embedding, không đổi mã chạy, dữ liệu hay cấu hình. Không thử lại lệnh r19 bị automatic review chặn.

Trong 28 câu có trích dẫn bằng dấu ngoặc kép, parser hiện tại tách 13 tên bài ở dấu phẩy hoặc chữ “và”. Ví dụ tên “Nhân CPU, luồng và xung GHz dùng để làm gì?” bị biến thành ba yêu cầu; model lấy thêm Wi-Fi 6 GHz và tốc độ SSD cho các phần rời. Đây là lỗi cấu trúc đầu vào có căn cứ, chưa chứng minh là nguyên nhân duy nhất của đáp án sai.

Đối chiếu `available_fields` với document_id của manifest: 27/28 câu có tài liệu đúng tên trong các bằng chứng đã đưa tới selector; chỉ 24/28 có tài liệu đó trong nguồn cuối cùng được chọn. Q0239 và Q0302 có đúng tài liệu trong available_fields nhưng đáp án chọn tài liệu khác. Q0351 không có tài liệu đúng tên trong available_fields; chưa phân biệt mất ở bước retrieval hay giới hạn fragment. Không được kết luận cả bốn trường hợp đều là retrieval miss.

17/28 đáp án dẫn ít nhất một nguồn khác tên bài được hỏi. Đây là tín hiệu nhiễu, không tự động là 17 FAIL: một số nguồn khác bổ sung hợp lệ. Điểm nghĩa đã chấm trước của nhóm này là 19 PASS/9 FAIL. 13 câu thay đổi parser gồm 10 PASS/3 FAIL; phải giữ các đối chứng PASS để tránh chỉ kiểm lại lỗi.

Đã lưu **candidate riêng**, chỉ tách mệnh đề ngoài cặp `“…”`, `"…"`, `«…»` hoàn chỉnh; không có tên sản phẩm, ID benchmark hay đáp án trong logic. So offline toàn479: 451 câu không có ngoặc kép giữ nguyên; 13 câu thay đổi; 15 câu có ngoặc kép khác giữ nguyên. Năm kiểm tra biên qua: dấu phân cách ngoài ngoặc vẫn tách, hai trích dẫn, dấu ngoặc không đóng và số thập phân. Đây là kiểm tra cấu trúc, không phải cải thiện điểm trả lời.

`../quoted_clauses_20261023_r20` là kết quả lần ghi đầu được giữ nguyên. Trường `exact_title_in_retrieved_sources` ở bản đó đặt tên sai: `result.sources` chỉ chứa nguồn được chọn, không phải toàn bộ retrieval. Bản v2 sửa cách diễn giải và thêm đối chiếu available_fields, không sửa kết quả chatbot hay nhãn lịch sử.

## Bước tiếp theo đã chốt

Một thử nghiệm production candidate riêng: chỉ thay parser bằng candidate này, giữ model/prompt/retrieval/KB/config. Snapshot patch9 trước khi thay, chạy các unit phù hợp, rồi một batch toàn 28 câu quoted development (đủ nhóm hội thoại), đối chiếu nguyên câu/nguồn/thiếu ý với patch9. Không lấy 5 kiểm tra parser làm bằng chứng nghiệm thu chatbot. Chấm nghĩa tách PASS_CHECKS; đọc đủ cả 19 đối chứng PASS và 9 FAIL, báo nguồn thừa riêng. Nếu có suy giảm, phục hồi patch9; nếu có cải thiện không suy giảm, kiểm hồi quy100 ở lượt kế tiếp trước khi nghiệm thu, rồi mới toàn479. Không mở reserved24 hay validation để sửa.

Rủi ro: một phần câu hỏi sau khi gộp vẫn chịu giới hạn tối đa3 fragment; có thể mất ý thay vì tốt hơn. Parser này cũng không sửa 6 FAIL quoted vốn đã là một phần, không giải quyết chắc Q0351. Không kết hợp thêm title filtering hoặc prompt mới cùng lượt thử để còn xác định nguyên nhân.

Production vẫn patch9, lần đo được chấp nhận gần nhất 450/479 development và87/100 hồi quy; 193 unit lần cuối đã qua. Không có cải thiện độ đúng/tốc độ mới để thông báo người dùng.
