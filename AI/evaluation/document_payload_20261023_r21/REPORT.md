# R21: đã xác định vị trí lỗi đọc bài viết

Một batch quan sát patch9 nguyên trạng:12 câu development đã mở (6FAIL/6PASS),24 lời gọi router/selector. Hoàn thành12/12, integritytrue. Đọc toàn bộ đáp án, search results, payload và lựa chọn fragment; cả12 đáp án giống baseline từng ký tự. Giữ nhãn6PASS/6FAIL có dẫn xuất từ review cũ, không gọi đây là điểm đánh giá độc lập hay cải thiện.

11/12 trường hợp có đúng tên bài trong search và selector, không mất bài giữa hai bước. Q0239 IdeaPad có đủ ba câu về RAM hàn/khe DDR4, đối chiếu tên thương mại và mãSKU trong payload; selector chọn Wi-Fi/OLED thay thế. Q0302 Photoshop có yêu cầu8GB/16GB cùng giới hạn phiên bản/cấu hình trong payload; selector chọn ba cảnh báo OLED/SSD. Q0017 có tốc độ KC3000 phân biệt dung lượng và giới hạn mức tối đa nhưng bỏ cả hai. Q0156 có câu không đánh giá CPU chỉ từ GHz nhưng bỏ câu này.

Q0351 là trường hợp khác: đúng bài081SG không có trong cả hai kết quả search. Đã đối chiếu predicate ở retrieval.py với manifest: câu nhắc B12M-081SG cũng khớp tên catalog MSI Modern15B12M. `product_codes` của sản phẩm là `b12m`, của đúng bài là `b12m-081sg`, giao rỗng; bộ lọc liên kết sản phẩm loại bài người dùng nêu đích danh. Đây là kiểm tra predicate offline kết hợp trace, không phải suy đoán thiếu dữ liệu. Bài081SG đã tồn tại trong manifest.

Selector prompt1690–3007tokens, num_ctx6144; tất cả24completion finish`stop`. Không thấy dấu hiệu hết cửa sổ hoặc output bị cắt trong mẫu này. Điều đó không chứng minh runtime luôn đúng cho mọi câu. Nguồn đúng và câu cần thiết có mặt nhưng quyết định chọn sai cho thấy không nên giải quyết bằng việc cào thêm chung chung hoặc chỉ tăngcontext.

Lưu ý thiếu nội dung thật: bài CPU hiện tại không giải thích riêng khái niệm luồng; bài IPS/TN/VA không mô tả chi tiết khác biệt TN vàVA. Không được chế thêm kiến thức để biến các câu đó thànhPASS. Sai chọn đoạn và thiếu kiến thức có thể cùng tồn tại; cần bài từ hãng có nguồn nếu muốn đáp ứng sâu hơn.

Tổng120.154s,median5.867s; không dùng thời gian này so tốc độ với batch khác vì cache/load khác. Không đổi production/model/prompt/KB/config, không thử lại r19 hoặc unload model. Patch9 vẫn450/479development,87/100hồi quy,193unit đã qua. Chưa có cải thiện mới để thông báo.

## Bước sửa tiếp theo

Thử **ràng buộc tài liệu được gọi đích danh cho tác vụ tóm tắt** ở bước search, trước lọc SKU phụ: so tên đầy đủ trong dấu ngoặc kép với tài liệu đã qua lọc quyền, trạng thái và ngày hiệu lực. Chỉ bật khi router xác định đọc/tóm tắt một tài liệu, không áp cho yêu cầu nhiều việc hoặc câu so sánh sản phẩm. Không dùng tên bài/IDbenchmark hoặc gold trong logic; không biến nội dung tài liệu thành chỉ thị. Giữ ràng buộc quyền/ngày và định tuyến giá hiện tại.

Đây là một sửa khác parserpatch15 đã bị loại. Giữ parser/prompt/model/schema/budget nguyên trạng để kiểm nguyên nhân. Test định danh tài liệu với phân quyền, phiên bản, tên gần giốngSKU, không tìm được tên, dấu ngoặc kép chứa nội dung không phải tên bài, và yêu cầu hỗn hợp. Sau unit, một batch28quoted development cảPASScontrols. Chấm đủ ý và sai chủ đề riêng; không nghiệm thu chỉ vì hết nguồn ngoài bài. Nếu còn suy giảm rollback, nếu gainkhôngregress mới hồi quy100lượt sau, rồi479. Reserved24/validation chưa dùng.
