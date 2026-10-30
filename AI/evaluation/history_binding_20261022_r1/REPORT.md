# Chẩn đoán: cùng model, khác lịch sử và cách nhắc sản phẩm

Sau khi loạipatch10, dùng đúng mãpatch9đã phục hồi. Sáu kịch bản có kiểm soát trên hai câu đã mở ởdevelopment; chỉ bốn văn bản câu hỏi khác nhau. Giữcùng nguồn,gold,clock21/10/2026,model/config,subjectđượcxácminh. Không phải sáu câu hỏi độc lập hoặc kiểm tra mù.

| Biến thể cho mỗi câu | Đạt nội dung chính |
|---|---:|
| Đại từ + lịch sử nguyên bảnpatch9 | 2/2 |
| Đại từ + lịch sử ngắn ghi lại từpatch10 | 0/2 |
| Nêu rõ tên sản phẩm hiện tại + cùng lịch sử ngắn | 2/2 |

Đã đọc cả sáu output, không suy nghĩa từchecks. VớiDeepcoolCH160, lịch sử ngắn làm hỏi lại dùsubjectđúng; nêu tên trong câu hiện tại trảTemperedGlass. VớiG.Skill64GB, lịch sử ngắn làm trảDDR5/Photoshopthaybốtrí; nêu tên trongcâu hiện tại trảđủ2thanh×32GBmỗithanh. CâuG.Skillvẫn thừaPhotoshop, nên không gọi là đáp án hoàn hảo.

Inputs lấy **profile ở lượt trước** từ hai round đã ghi, một lượt history mỗi profile; không sửa lời đáp ghi lại. Lời đáp model chỉ là dữ liệu hội thoại không đáng tin cậy, không xuất bản làmknowledge/gold hoặc train. Gold của hai câu lấy nguyên từ bankdevelopmentđã chốt, không truyền choEngine. Biến thể nêu tên chỉ thay đại từ bằng `rag_product_subject`đã xác nhận, không thêm đáp án vật liệu hoặc bố trí RAM vào câu hỏi.

Runner `run_history_binding_probe.py` dùng chung `runner.lock`, chốt hashbank/gold/DB/manifest/code/config, kiểm mỗi lượt, không chạytrùngGPU. Đủ6/integritytrue,không stderr. Bản script đã thực thi lưu riêng tại `run_history_binding_probe.executed.py`; bank/results/metadata/reviewgiữ nguyên. Khi sửa bot hoặc runner sau này phải round/revision mới, không chạy đèr1.

Kết quả ủng hộ giả thuyết phụ thuộc câu trả lời trước, và cách diễn đạt câu hiện tại với đối tượng rõ là hướng đáng kiểm. **Chưa có resolver tự động trong bot, chưa có cải thiện sản phẩm được chốt.** Hai câu đã biết lỗi không đủ chứng minh tổng quát. Không loại bỏ history toàn bộ nhưpatch4đãthửvàthấtbại.

Bước tiếp theo nên tạo một baseline chẩn đoán rộng hơn từ các nhóm product_contextđã mở, cùng ba biến thể profile, trước sửa resolver. Không đụng24reserved. Nếu thử vật chất hóa tham chiếu thành câu độc lập, chỉ dùng một sản phẩm đã xác minh, giữ câu gốc/lịch sử, bảo vệ đổi chủ đề/modelmới/sohai máy/multiple subjects/đối tượng chưa rõ; không tự ghi đèclarify hoặc cấp giá/đápán. Dùng revision/output mới với hash mới, rồi so cùng câu và hồi quy, không sửa r1.
