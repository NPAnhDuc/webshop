# Patch10: kiểm sửa phần dẫn nguồn trên cùng479development

Baseline patch9 đã chấm đủ479:450PASS/29FAIL,112review kế thừa theo exact outputs và367đọc mới. Khóa hash mã/results/review/metadata/bank/gold trước sửa trong `../patch10_before_code/BASELINE_PATCH9.json`.24reservedchưahỏi,121validationcũđãmở.

Một sửa tại question_parts: phần dẫn nguồn dạng câu trần thuật đứng trước dấu phẩy chỉ cung cấp ngữ cảnh, không trở thành một yêu cầu riêng phải có bằng chứng. Nhận diện cấu trúc nguồn tổng quát và giữ mệnh đề có câu hỏi thật. Toàn bộ question ban đầu vẫn trong payload, scope giải lịch từ câu gốc vẫn nguyên. Không đổi model/data/gold, không dùng ID/SKU/đáp án, không áp lại promptpatch8 hoặc tăng ứng viênpatch6.

Test cần xanh trước batch: ngữ cảnh tài liệu/báo cáo/chính sách/danh mục có/không dấu, câu hỏi thật ở mệnh đề đầu không bị bỏ, hai ý ngăn dấu phẩy giữ đủ, câu “theo bạn…” giữ câu hỏi, kỳ trong phần dẫn vẫn đến selector và cả hai ý trả đủ.

Chạy mộtbatch `run_quality_loop.py --round candidate_v10_development --split development`,479cùngIDs vàđồnghồ21/10/2026. Không sửa mã/data/model/config hoặc mở batch khác khi runner đang chạy. Ba lỗi hạ tầng liên tiếp thì dừng đúng nguyên nhân; không coi thiếu model là thiếu knowledge. Resume chỉ cùnghash/config/IDs/source.

Khi xong đủ479/integritytrue, so `candidate_v9_development`: kế thừa review chỉ khi answer/action/source objects giống hệt, đọc lại mọi case thay đổi (với đầy đủ câu trước trong hội thoại). Kiểm riêng ba lỗi claim phụ Q0154/Q0193/Q0228: đã có đáp án chính nên checks không đo được việc loại sai phạm vi. Đánh giá sửa được lỗi, noise giảm và có thiếu ý/hồi quy không; không chỉ báo tăngPASS_CHECKS.

Mọi kết quả cũ và gold giữ nguyên. Đây là bộ phát triển đã mở, không gọi là kiểm tra mù. Sau batch này vẫn cần hồi quy100cùngrubric trước chốt candidate. Chưa mở24reserved hoặc rerunvalidationđể sửa. Không fine-tune/deploy/APIphí/subagents/nhắn ai khác. Không dùng điểm450/479patch9cho patch10trước đọc/chấm.
