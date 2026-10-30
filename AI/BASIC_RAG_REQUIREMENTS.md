# Phạm vi nghiệm thu RAG cơ bản

Theo yêu cầu người dùng ngày 20/10/2026. Luồng mặc định là `CHATBOT_MODE=basic_rag`. Luồng công cụ cũ giữ để đối chiếu bằng cấu hình `tools`, không nằm trong nghiệm thu này. Không huấn luyện lại trọng số hoặc chạy thêm Colab trong thay đổi này.

## Người mua

| Yêu cầu | Cách triển khai và giới hạn |
|---|---|
| Thông số sản phẩm | 67 bản thông số tham khảo đã lập chỉ mục, gồm trường thực sự có trong nguồn. Không tự suy cổng, pin, hệ điều hành hoặc khả năng nâng cấp còn thiếu. Thông tin bảo hành của nhà bán lẻ nước ngoài không phải cam kết của shop. |
| Giải thích thuật ngữ | 34 tài liệu kỹ thuật đã duyệt, gồm OLED/IPS, Hz/FPS, RAM, SSD, CPU/GPU, USB-C/Thunderbolt, Wi-Fi và giới hạn theo biến thể; tham khảo nguồn kỹ thuật chính thức. Không coi kiến thức kỹ thuật hãng là chính sách shop. |
| Chính sách | Đọc điều khoản đã duyệt; chưa có điều khoản thật thì từ chối. Bộ chính sách hiện tại chỉ là mô phỏng, thiếu thời hạn và điều kiện thực tế. |
| Khuyến mãi | Đọc nội dung, điều kiện và thời hạn trong tài liệu được duyệt. Bắt buộc ngày kết thúc khi duyệt chương trình mới; loại tài liệu hết hiệu lực theo ngày. Chưa có chương trình thật của shop. |
| Hướng dẫn chọn máy | Đọc bài buying_guide đã duyệt; chưa có bài của shop thì báo thiếu. Không thay bài của shop bằng ý kiến tự sinh. |
| Thông tin cửa hàng | Đọc store_info được duyệt. Địa chỉ, giờ mở cửa, liên hệ và URL thật chưa được xác nhận. |
| Hướng dẫn mua | Đọc shopping_guide được duyệt, không tạo đơn/tra đơn thật. Hiện thiếu hướng dẫn của shop. |
| So sánh nhẹ | Truy xuất thông số hai máy, trích các khác biệt có nguồn; chưa tính điểm hoặc khẳng định benchmark. |
| Từ chối | Thiếu bằng chứng thì báo thiếu; câu mơ hồ cần làm rõ; ngoài phạm vi đưa về chủ đề cửa hàng. Model định tuyến vẫn cần đánh giá thêm với câu khách thật. |
| Gặp nhân viên | Nhận yêu cầu và báo rõ chưa gửi vì chưa có kênh chuyển nhân viên được kết nối. Chưa gọi là chuyển người thật thành công. |

Giá và tồn kho không được lập chỉ mục trong bản thông số mới. Câu hỏi giá/tồn tức thời và lọc chính xác theo ngân sách được chuyển về trang sản phẩm; vì chưa có URL shop được xác minh nên bot không tự dựng đường dẫn. RAG cơ bản không dùng danh sách giá/tồn hay bộ xếp hạng SKU từ luồng sales/tools.

## Admin

| Yêu cầu | Cách triển khai và giới hạn |
|---|---|
| Chiến lược, mục tiêu, marketing, biên giá | Đọc tài liệu đã duyệt và hiện hành; các tài liệu hiện có là mô phỏng. |
| Tóm tắt, việc cần làm | Chọn các câu/đoạn nguồn, giữ nhiệm vụ và người phụ trách nếu được ghi; không tự giao việc. |
| Báo cáo số liệu đã lập sẵn | Đọc 12 báo cáo tháng từ 10/2025 đến 09/2026; không tính lại SQL trong lượt hỏi. |
| Quy trình, nhà cung cấp | Đọc quy trình đã lập, phân biệt tham số mô phỏng với quy định thật. |
| Đối chiếu, mâu thuẫn | Truy xuất nhiều tài liệu và dẫn từng nguồn. Kiểm tra dấu hiệu mâu thuẫn bằng model; đây là bước có thể sai, không phải bộ chứng minh logic. Khác mục tiêu ở hai quý không mặc nhiên là mâu thuẫn. |
| Gợi ý theo khuôn | Trích các điều kiện/quy trình cần cân nhắc; không sinh ngân sách, số nhập hay dự báo mới. |
| Phiên bản | Chọn bản đã duyệt có hiệu lực mới nhất của cùng mã; không phục hồi bản cũ khi bản mới hết hạn hoặc bị gỡ. |
| Dẫn nguồn, từ chối | Tên tài liệu/file, mục, đoạn và phiên bản; thiếu điều khoản không tự điền. |

## Quản lý và cập nhật

Admin Streamlit có tải MD/TXT/PDF có chữ/DOCX, chỉnh nội dung thành phiên bản mới, quyền đọc, nhóm hàng, ngày hiệu lực và gỡ khỏi truy xuất. PDF scan cần OCR riêng, không giả vờ đã đọc được ảnh.

Kho quản lý tách theo database tại `data/unstructured/managed/<namespace>/`. Nội dung chuẩn hóa được lưu thành MD và manifest có SHA256. Có thể cập nhật tài liệu nền bằng phiên bản quản lý mới, không sửa file nền hoặc database tài chính. Gỡ là ngừng truy xuất và giữ lịch sử kiểm toán.

Manifest được đọc lại ở lượt hỏi tiếp theo, không đợi lịch tháng. Cache embedding phụ thuộc đúng nội dung và model revision; lượt đầu sau thay đổi có thể cần tính vector. Chưa đo SLA trên tài liệu lớn hoặc nhiều người dùng đồng thời.

Lịch sử hội thoại giới hạn sáu lượt, tách vai trò; câu nối dùng chủ đề trước và phạm vi tháng/quý đã xác nhận. Pipelinegrounded mặc định hiểu yêu cầu rồi chọn bằng chứng từng phần, lọc đúng kỳ trước khi gọi model. Không có kỳ thì không lấy kỳ khác thay. Mở rộng loại tài liệu trong cùng miền phù hợp, không lấy bài kỹ thuật để thay điều khoản shop còn thiếu. Chưa phải bộ nhớ xuyên thiết bị. Truy xuất kết hợp embedding tiếng Việt, TF-IDF và BM25; có hỗ trợ một số viết tắt và lỗi gõ nhẹ. Bộ lọc quyền/hiệu lực/phiên bản luôn bắt buộc; loại/nhóm do model dự đoán là ưu tiên mềm, chỉ lọc cứng khi người dùng yêu cầu rõ.

Log nằm tại `runtime/rag-basic/<namespace>/turns.jsonl`, có câu hỏi, câu trả lời, loại yêu cầu, trạng thái, nguồn/phiên bản. Có che một số email/điện thoại/khóa theo mẫu, không bảo đảm che mọi dữ liệu nhạy cảm. Log xoay vòng theo dung lượng; admin xem các câu none/partial/unverified để biết tài liệu còn thiếu. Câu hỏi benchmark được gắn nguồn development_evaluation trong các lượt mới; log cũ chưa có nhãn này không nên coi là phản hồi khách thật.

## Nghiệm thu

Xem kết quả chạy và các lỗi tại `evaluation/basic_rag_v1/REPORT.md`. Bộ phát triển gồm câu trên kho hiện tại và bộ chính sách giả lập cách ly để kiểm tra chức năng khi có tài liệu. Không nhập chính sách/địa chỉ kiểm thử vào kho phục vụ người dùng.

Đo riêng recall@8 theo tài liệu và đoạn chuẩn, đáp án kỳ vọng, trích đoạn nguyên văn, nguồn/quyền, từ chối khi thiếu dữ liệu và việc không trả giá/tồn tức thời. Trích đúng đoạn không tự chứng minh đoạn có liên quan hoặc câu trả lời đã đầy đủ; vẫn cần người kiểm tra và bộ câu hỏi độc lập của shop.

Không nghiệm thu tính KPI từ giao dịch, so sánh kỳ bằng phép tính, biểu đồ, dự báo, phân khúc, nhập hàng định lượng, tính trả góp, trạng thái đơn hoặc Build PC trong luồng này. Không thay đổi React/Express để kết nối chatbot trong đợt này.

## Mốc đo21/10/2026

[Bộ hồi quy100 câu](evaluation/grounded_rag_20261021/REPORT.md):85đạt/15chưađạt, từ baseline67đạt. Khách45/50,admin40/50. Có4câu thoái lui(C03,C06,C44,A39) và các lỗi khác: thiếu ý, trả máy khác cho model không có, lịch sử chính sách, chưa kết luận hết hạn, định tuyến sai. Chức năng đọc archive đã mở có kiểm soát cho admin, nhưng hai câu lịch sử vẫn FAIL; chưa coi là nghiệm thu thành công đối chiếuv1/v2.

195 trích đoạn khớp nguồn, không thấy nguồn admin lọt sang khách trong bộ thử, nhưng đúng trích đoạn không đồng nghĩa đúng câu trả lời.10câu FAIL vẫn tự gắnfull; không dùng nhãn đó để tự chấm hoặc tự nạp câu trả lời thành dữ liệu học. Các câu hỏi này đã dùng trong phát triển, cần bộ hỏi thật độc lập trước nghiệm thu sản phẩm.
