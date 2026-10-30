# Hai luồng dữ liệu và phạm vi huấn luyện

## Trạng thái

Pilot Colab đã xác minh chỉ huấn luyện retriever E5 trên 37 bản ghi sản phẩm,
không phải huấn luyện mô hình tài chính hay toàn bộ kho tài liệu chiến lược.
Chưa xác minh hoàn tất huấn luyện Kev. Không dùng kết quả pilot để chứng minh
khả năng phân tích kinh doanh thực tế.

## Skill phân tích đang chạy trong ứng dụng

`shopbot/business_analysis.py`, được Engine gọi với quyền admin khi hỏi
"Phân tích kinh doanh quý 3 năm 2026" hoặc "Lãi lỗ tháng 9 năm 2026".
SQL chỉ đọc có tham số; không chạy mã hoặc SQL do LLM tự sinh.

Đầu vào hiện tại là sổ bán hàng đã nhập qua quy trình kiểm tra và chống trùng:
`day, sku, quantity, revenue, cost`. Tiền là số nguyên VND; revenue và cost là
tổng của dòng giao dịch, không phải đơn giá. Dữ liệu benchmark nước ngoài không
được tự đổi thành doanh thu thực của shop hoặc ghép theo mã sản phẩm không khớp.

Kết quả: doanh thu, giá vốn, lợi nhuận gộp, biên gộp có trọng số theo doanh thu,
số lượng bán, tỷ trọng doanh thu theo SKU, SKU có lợi nhuận gộp âm, bảng và
hai biểu đồ (SKU và diễn biến tháng). Giữ kỳ lọc, số dòng, nguồn dữ liệu và
các giới hạn cùng kết quả. Thiếu giá vốn sẽ từ chối tính; kỳ rỗng không được
diễn giải là doanh thu bằng 0. Chưa đối soát hoàn trả và định nghĩa doanh thu
thuần nên không gắn nhãn doanh thu thuần. Không coi ngày có bản ghi đầu/cuối
là bằng chứng đầy đủ dữ liệu.

Chưa tính lợi nhuận ròng vì chưa có sổ chi phí vận hành/thuế/phí. Chưa quy kết
nguyên nhân, tính ROAS, dự báo, hay khuyến nghị ngân sách tối ưu.

## Phần cần nối tiếp

1. Dữ liệu tài chính: bổ sung transaction_id, order_id, thời gian/múi giờ,
   currency, chiết khấu, hoàn trả, giá vốn xác nhận; bảng chi phí, marketing,
   tồn kho theo ngày, và trạng thái chốt kỳ. Mỗi nguồn có khóa chống trùng,
   quy tắc đối soát và báo cáo lỗi riêng. Không tự điền giá vốn chưa biết.
2. Tài liệu: chia theo mục, câu và bảng; giữ trang, phiên bản, thời gian hiệu lực,
   quyền truy cập và phân biệt chính sách shop với báo cáo tham khảo bên ngoài.
   Dùng embedding/retrieval, không nhét toàn bộ giao dịch vào vector store.
3. Ghép chứng cứ: công cụ tính trả số; RAG trả điều khoản/mục tiêu đúng kỳ;
   câu trả lời tách số đã quan sát, giả thuyết, và hành động đề xuất. Chưa có
   tài liệu được duyệt thì không bịa ngân sách hay mục tiêu.
4. Dự báo: đánh giá bằng chia tập theo thời gian, so baseline đơn giản trước;
   chỉ chọn mô hình phức tạp hơn nếu cải thiện trên kỳ giữ riêng. Không hứa
   deep learning chính xác hơn khi chưa có kiểm thử. Lượng dữ liệu đủ phải xét
   theo độ phủ chu kỳ mùa vụ, SKU, khuyến mãi và độ đầy đủ, không chỉ số dòng.
5. Gia sư: lưu câu hỏi thất bại, nguồn, phép tính chuẩn và loại lỗi; sửa ingest,
   công cụ hoặc retrieval trước; chỉ đưa ví dụ đã kiểm tra vào train. Giữ riêng
   test theo thời gian/nguồn/chủ đề. Model tự hỏi đáp không tạo ra sự thật mới.

Hai luồng có thể dùng chung mô hình hội thoại và bộ định tuyến. Chỉ huấn luyện
embedding/reranker khi có lỗi tìm kiếm đo được; mô hình dự báo được huấn luyện
riêng. Tính toán kế toán và làm sạch dữ liệu là pipeline kiểm chứng được,
không phải thao tác "train RAG".
