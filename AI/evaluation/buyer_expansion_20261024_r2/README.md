# Mở rộng kiểm thử người mua — r2

Đã tạo300lượt hỏi,296nội dung câu khác nhau;4câu lặp nằm ở các trạng thái hội thoại khác nhau, không dùng số lượng lượt để giả thành300câu độc lập.14hội thoại4lượt tạo56turn: đổi ngân sách/số lượng, so thứ tự và đổi nhóm sản phẩm.134câu thông số phủ67sản phẩm;40search phủ10danh mục;20so sánh laptop;30kiến thức/chính sách;20tư vấn nhu cầu.

QUESTIONS.md đọc trực tiếp câu hỏi; bank.jsonl có nhóm, câu, kỳ vọng/nguồn/goldstatus. Manifest/review có hash và thống kê. Không sửa bộ106cũ, không đưa gold hoặc cả ngân hàng vào prompt/RAG/train.

Oracle search/compare lấy trực tiếp catalogJSON, không gọi hàm tìm/so của bot. Đây là snapshot mô phỏng, không giá/tồn thương mại trực tiếp hoặc xác minh nhà sản xuất.134câu fact có31field chưa có thông tin, cố ý kiểm không bịa; không coi null là thông số sản phẩm không hỗ trợ tính năng.50câu kiến thức/tư vấn cần nguồn chính thức/chính sách shop và review ngữ nghĩa, chưa có đáp án chuẩn hoàn chỉnh. Không sinh chính sách hoặc FPS làm gold.

R1 là bản nháp được giữ nguyên. R2 sửa fieldnames theo schema thực và dùng spacing bình thường ở bank chính, tránh trộn feature đoán lỗi chính tả đang hoãn. errata có parenthash. Cần thêm tình huống thực từ logs, case đối kháng và review ngoài người viết;300template-derived development turns chưa đại diện toàn bộ khách hàng và không phải independent validation.

Chưa chạy model300turn, chưa thêm dataRAG, chưatrain hoặc sửa model/runtime/config. Sau khi sửa lỗi core: review/freeze từng round, chạy50–100turn theo nhóm và hồi quy106, đo tool/args/nguồn/đúngsố/trạngthái/trảlờingữnghĩa/abstention/latency, không gộp routeđúng với tri thứcđãtrảlờiđúng. Các câu chỉ documents cần nhánh retrieval thật; registered-disabled khôngđược tínhlàđãđápứng.

Hiểu tiếng Việt sai chính tả là giai đoạn sau khi core ổn theo yêu cầu người dùng. Khi làm: giữ question gốc, chuẩn hóa/candidate rewrite có confidence và xác minh thực thể; giữ nguyên ngân sách, số lượng, mã máy và phủ định. Không chắc “20/2triệu”, SKU gần nhau hoặc “không quá/dưới” thì hỏi lại. Không biến đoán câu thành quyền đọc admin/ghi dữ liệu. Chưa triển khai hoặc tự bật sửa lỗi chính tả trong revision này.

Thứ tự tiếp: fix lỗi capability/state còn lại + dùng bank này để đánh giá độ phủ → nốiRAGtài liệu có nguồn → kiểm định language normalization riêng khi nền ổn → Excel/DA/DS/Kev theo gate và labels/holdout. DevCompose làm sớm để tái lập, deploy công khai sau. Không mở validation RAG cũ để sửa.
