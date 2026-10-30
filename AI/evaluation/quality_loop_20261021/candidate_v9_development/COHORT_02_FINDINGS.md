# Cohort02: ba lỗi ngữ nghĩa mà PASS_CHECKS không phát hiện

Đã chọn90ID từ pending_ids trước khi đọc, chia thành ba panel30câu. Đọc câu hỏi, đáp án, lịch sử cùng hội thoại, các dữ kiện/nguồn đã duyệt; ba câu nghi ngờ được đối chiếu thêm toàn văn nguồn. Kết quả87PASS/3FAIL theo đánh giá của Codex, tách khỏi checks. Không có người duyệt độc lập.

Các câu FAIL đều có thuộc tính chính đúng, nhưng kèm một claim không ràng buộc được cho sản phẩm:

- Q0154: hỏi GPU của MSI RTX5060Ti, bot thêm “Mã trong danh mục là B12M-041BD…” và giới hạn408AU/041BD từ tài liệu laptop MSI Modern15. Đây là nhầm đối tượng, không chỉ dài dòng.
- Q0193: hỏi đường chéo màn AsusVG27AQ, bot thêm cảnh báo trường kết nối bị xung đột từ tài liệu chuột LogitechG305. Không được áp cảnh báo riêng chuột cho màn hình.
- Q0228: hỏi loại nguồn MSIMAGA750GL, bot thêm “Hai loại bổ sung cho nhau” từ bài CPU/GPU; quan hệ giữa hai chủ thể trong nguồn bị tách ra mà câu hỏi không có hai chủ thể đó.

Cả ba được PASS_CHECKS vì trường chính đúng và có nguồn. Answer/action/source objects giống hệt patch5; đây là lỗi có sẵn vừa được đọc ra, **không phải ba hồi quy mới của patch9**. Giữ kết quả/gold/review cũ nguyên vẹn. Không thay rubric hoặc đáp án chuẩn để làm đẹp điểm.

16câu khác có thông số cùng sản phẩm hoặc nền liên quan thừa, ghi secondary issue; không coi chúng là hoàn hảo. Ví dụ giải thích dung lượng flash khi hỏi dung lượng SSD không gán mã riêng của thiết bị khác. Q0306nêu rõ mã408AU khi thêm thông tin biến thể, không tự đổi mã sản phẩm đang hỏi; vẫn ghi thừa. Q0298đảo thứ tự hai kỳ nhưng citation riêng khớp từng số, câu không yêu cầu “lần lượt”, nên không gán sai kỳ.

## Nguyên nhân chung có bằng chứng từ trace

Cả ba có `plan.parts` gồm P1=`Theo danh mục tham khảo` và P2=câu hỏi thuộc tính thực. `part_evidence.P1` chọn mảnh từ tech-msi-variant, tech-g305-source-conflict hoặc tech-cpu-gpu. P2chọn đúng thuộc tính từ hồ sơ sản phẩm. Q0140cũng có P1ảo và chọn ba trường màn hình/GPU/RAM không hỏi, P2mới chọn CPU.

Vì vậy ưu tiên giả thuyết **tách phần dẫn nguồn thành câu hỏi riêng**, trước khi mở rộng truy xuất hoặc thêm dữ liệu. Tài liệu đang đủ cho thuộc tính chính; thêm data không sửa việc P1ảo nhận bằng chứng. Patch5từng sửa chỉ dẫn liệt kê nhưng chưa xử lý mọi phần dẫn nguồn. Không cần nạp đáp án bot vào knowledge.

Sau khi hoàn thành202ca còn lại, có thể thử một sửa tổng quát ở cách tách ý: giữ toàn bộ câu gốc/kỳ/chủ đề trong payload nhưng không bắt phần dẫn nguồn độc lập phải có đáp án. Không hardcode ID/SKU/giá trị hoặc đúng một mẫu benchmark. Cần phản chứng: hai câu hỏi thật ngăn bằng dấu phẩy vẫn đủ ý, kỳ trong phần dẫn vẫn được giữ, liệt kê chỉ tiêu vẫn đúng, câu “theo bạn…” vẫn hỏi nhu cầu chứ không mất câu hỏi. Chạy cùng câu và hồi quy; không áp lại promptpatch8 hoặc tăng ứng viên patch6đãloại.

Lượt này chỉ audit:0sửa bot/data/model/config,0model batch. Coverage277/479,tập đã chấm248PASS/29FAIL,202chưa đọc. Không có điểm nghĩa toàn479/600;24reserved vẫn chưa hỏi. Đọc hết coverage và xác định lỗi chung trước sửa tiếp như kế hoạch.
