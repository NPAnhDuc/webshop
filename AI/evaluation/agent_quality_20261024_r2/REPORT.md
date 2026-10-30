# Ranh giới ý định — candidate r2 chưa nghiệm thu

Một thay đổi prompt có kiểm định: yêu cầu planner chọn hành động trước chủ đề; phân biệt kiểm nguồn với nhập/clean/ghi dữ liệu, giữ yêu cầu biểu đồ và route giải thích công nghệ sang documents. Không thêm quyền ghi, đổi model/config/frontend hoặc bật mặc định.

Đã đóng băng revision mới trước đúng một batch local80lượt:74câu r1 giữ nguyên câu/thứ tự tương đối,6control mới về phủ định, chart đúng metric, thuật ngữ, số lượng RAM và Excel không ghi đè. Gold Q12 được sửa từ deferred sang documents chỉ trong r2, có parent hash/reason tại gold_corrections.json; gold r1 giữ nguyên. Không sử dụng đáp án/gold trong prompt.

Checks16/20mới+control,58/60hồi quy. Review ngữ nghĩa riêng74/80; trên đúng74câu cũ đạt70/74 so với69/74r1. Sửa được Q11 (ghi đè Excel được từ chối), Q12 (route thuật ngữ đúng) và A04 (có chart giá vốn). Đổi lại Q14/A22 xếp hạng SKU bị nhầm thành data_quality; vì vậy lợi ích chưa ổn định, **accepted_for_application=false**. Không tuyên bố đã cải thiện tổng quát hoặc đã trả lời nội dung DDR5: nhánh documents vẫn chưa nối vào chế độ agent_tools.

6FAIL còn lại:

- Q10,A20: yêu cầu xóa/clean vẫn bị đổi thành đọc nguồn cũ.
- Q14,A22: xếp hạng bán chạy bị đổi thành kiểm/đếm SKU của dataset.
- Q19: “3 thanh RAM” bị lấy limit5 và trả4; đúng giá/danh mục nhưng sai số lượng.
- Q20: đọc/chuẩn hóa Excel mới dù không ghi đè vẫn bị thay bằng đọc nguồn cũ.

Các control phủ định “không xóa, chỉ kiểm nguồn” và “đừng clean” đi đúng quality; chart Q17 đúng quý3/2026, metric lãi gộp502.202.000VND và ảnh; thuật ngữ DDR5 route documents. Tất cả69câu cũ có answer không đổi sau chuẩn hóa đường dẫn artifact được đối chiếu với review r1; các câu đổi và6control được đọc riêng. Checks không thay đánh giá ngữ nghĩa.

Q04 slot time_mode vẫn lệch last_month dù câu có tháng9/2026; calendar code ưu tiên kỳ literal nên tool args/số thực thi đúng. Cần control đổi ngày server ở revision tiếp theo, không lấy kết quả đúng nhờ lịch hiện tại làm chứng minh slot đúng.

Batch80/80hoàn tất, integrity unchanged=true. Không sửa code/data/config lúc chạy, không batchmodel thứ hai. Median0,953s/max3,172s; không suy nhanh hơn r1 vì cold/warm khác nhau.33test hội thoại/toolPASS8,38s cho thay đổi prompt; không chạy lại full327test vốn đã qua ở r1 vì không đổi logic thực thi. Code/runtime/bank/gold/config/source hashes được khóa và giữ lại.

Bước tiếp: ưu tiên phân loại operation thành bước ngữ nghĩa nhỏ trước khi điền metric/time, thay vì tiếp tục kéo dài prompt chung; giữ ACL và lịch/SQL kiểm bằng code. Thêm phân biệt ranking vs dataset count, import/clean vs inspect, và danh từ đơn vị số lượng. So lại cùng câu và hồi quy trong revision mới; giữ candidate r1/r2 đã loại và không dùng validation RAG cũ để sửa. Chưa triển khai Excel/DS/fine-tune/HyDE hoặc kích hoạt curated mặc định. Không có runner model còn chạy cuối lượt.
