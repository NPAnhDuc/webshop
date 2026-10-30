# Nâng cấp tư vấn người mua — 20/10/2026

Phạm vi: chatbot Python/Streamlit hiện có. Không sửa frontend React, không thêm micro hoặc nối nút PC Builder. Endpoint chat demo ở backend Express vẫn là luồng riêng, chưa nối với Engine Python trong thay đổi này.

## Cách hoạt động

1. Planner local xác định ý định, tham chiếu câu trước, quyền truy cập.
2. Bộ trích xuất nhu cầu trả JSON: loại hàng, ngân sách, hãng, RAM tối thiểu, giới hạn cân nặng, công nghệ màn hình, nhu cầu sử dụng; hỗ trợ sửa/bỏ điều kiện hoặc bắt đầu nhu cầu mới.
3. Server giữ hồ sơ theo phiên, kiểm tra kiểu/giới hạn dữ liệu và con số có đơn vị. Ngân sách có từ “dưới” được giữ nghiêm ngặt; không tự nới khi không có hàng. Giới hạn RAM/cân nặng không được tự thêm khi câu hiện tại không có số đo tương ứng.
4. Công cụ chỉ đọc danh mục công khai, lọc giá/tồn/thông số trước. Thông số bắt buộc bị thiếu không được coi là đáp ứng.
5. Khi có nhu cầu sử dụng, model chọn tối đa ba SKU từ các ứng viên đã lọc. Server kiểm tra ID; model không sinh thêm sản phẩm, giá, tồn hay khẳng định hiệu năng. Nếu chọn ID sai/lỗi model, giữ danh sách theo giá và đánh dấu semantic_shortlist=false.
6. Câu trả lời dựng từ thông số nguồn; so sánh giá/RAM/cân nặng/dung lượng pin và chỉ rõ tiêu chí giá khi khuyên lựa chọn tiết kiệm. Số Wh không đổi thành số giờ pin.
7. Ghi nhớ danh sách đang xem để hiểu “con đầu”, “con thứ hai”; xóa tham chiếu cũ khi bắt đầu nhu cầu mới hoặc không có kết quả. Không có đối tượng rõ thì hỏi lại.

Đặt SALES_ADVISOR=0 để đối chiếu luồng cũ. Mặc định bật khi LLM_PROVIDER=ollama. Chưa huấn luyện lại trọng số, chưa chạy thêm Colab; đây là thay đổi luồng hiểu nhu cầu, truy vấn và kiểm chứng.

## Kết quả và bằng chứng

- Bộ tests đầy đủ: **129 passed**. Sau sửa cuối về xóa tham chiếu và trình bày so sánh: **18/18 sales tests passed**.
- `live_v4/`: **12/12** tình huống phát triển chạy qua Engine và model local thật. Bao gồm chuỗi ngân sách → hãng → bỏ hãng/đổi ngân sách → so sánh → chọn; điều kiện không có mẫu đáp ứng; hỏi game/FPS; câu mơ hồ; chuột; phân quyền; chính sách chưa có.
- Kết quả thô các lần trước được giữ trong `live_v1/`, `live_v2/`, `live_v3/`. Đáp án no_match được sửa sau khi đối chiếu SQL, có ghi ở `ERRATA.md`. Vì đã xem và sửa theo tập này, **không phải kết quả kiểm tra mù hoặc độ chính xác thực tế**.
- `live_v4` chạy trước hai sửa cuối về xóa tham chiếu cũ và thêm dòng đối chiếu số đo; không coi kết quả đó là chạy lại sau hai sửa này. Sales tests đã kiểm tra sau sửa.
- Streamlit `/_stcore/health` trả HTTP 200. Không thực hiện kiểm tra giao diện trình duyệt cho thay đổi này.
- SQLite mô phỏng không thay đổi: SHA256 `f544a0a0255d78a06f01833275170a6f2eda89f2c9053a923433e420ca365028`.

## Giới hạn còn lại

- Danh mục hiện là **67 SKU mô phỏng**, chưa có dữ liệu bán thật/giá bán cập nhật thị trường. Ví dụ ASUS dưới 20 triệu, RAM 16 GB không có mẫu phù hợp; RAM 16 GB, tối đa 1,5 kg, dưới 25 triệu cũng không có. Không giả định có thể nâng RAM khi chưa có bằng chứng từng SKU.
- Xếp gợi ý theo model chưa được người bán chuyên môn đánh giá độc lập; kết quả 12 câu chỉ kiểm tra hợp đồng lọc/ngữ cảnh/phân quyền và cách thừa nhận thiếu benchmark.
- Trích nhu cầu bằng model vẫn có thể sai hãng/nhu cầu sử dụng hoặc bỏ sót diễn đạt hiếm. Bộ kiểm tra đơn vị chỉ hỗ trợ các cách biểu diễn trong mã; chưa bao phủ mọi phủ định, khoảng hoặc tiền viết bằng chữ.
- Chưa xác nhận tương thích PC hoàn chỉnh, FPS, thời gian pin thực nghiệm, năng lực tản nhiệt hoặc khả năng nâng cấp.
- Chưa có đặt đơn, giữ hàng, chuyển nhân viên thật hoặc tự cấp giảm giá/chính sách trả góp. Không dùng lợi nhuận nội bộ để xếp gợi ý cho khách.
- Bộ nhớ giới hạn phiên và sáu lượt gần nhất; chưa có hồ sơ khách bền vững xuyên thiết bị. Chưa tự học từ câu khách hỏi và chưa fine-tune model.

Mã chính: `shopbot/sales.py`, `shopbot/engine.py`, `shopbot/conversation.py`, `shopbot/store.py`. Kiểm tra: `tests/test_sales.py`, `scripts/evaluate_sales.py`.
