# Đánh giá rộng patch9 trước khi sửa tiếp

Sau khi patch9 qua hồi quy100 (87PASS,0PASS→FAIL so patch7), giữ nguyên mã/source/model/gold và chạy đúng479development của bank600 đã chốt. Đồng hồ vẫn21/10/2026, dùng `run_quality_loop.py --round candidate_v9_development --split development`, khóa chung với các runner khác. Không dùng `--split all` hoặc validation. Đây là lượt phát triển đã mở, không kiểm tra mù.

Trong lúc runner chạy: không sửa code/data/model/config, không mở batch cạnh tranh GPU. Ba lỗi hạ tầng liên tiếp sẽ dừng; chỉ xử lý đúng dịch vụ gây lỗi khi có căn cứ. Giữ kết quả cũ nguyên vẹn. Resume chỉ cùng code/config/source/IDs và cùng round; nếu mã khác phải round mới.

Sau khi đủ479/integritytrue:

1. So cùng479 với `candidate_v5_development`: checks theo vai trò/chủ đề/nhóm, danh sách check fixed/regressed. Checks không phải độ đúng nghĩa.
2. Đối chiếu112review cũ. Chỉ kế thừa khi answer/action/source objects giống hệt, ghi provenance. Đọc lại mọi thay đổi đã có review và mọi lỗi mới.
3.367development cũ chưa được chấm nghĩa phải được đọc theo câu hỏi, đủ lịch sử hội thoại và đúng nguồn/rubric. Chia thành các cohort theo ID/nhóm hội thoại để mỗi lượt xử lý vừa sức; lưu coverage và trạng thái chưa đọc. Không tự chấm PASS chỉ vì check đạt hoặc quote đúng.
4. Trước khi sửa tiếp, phân loại lỗi chung: thiếu nguồn thật, sai truy xuất, mất chủ đề/kỳ/SKU, chọn sai trường, thiếu ý/mâu thuẫn, quyền và định tuyến. Không lấy đáp án bot thành knowledge; dữ liệu mới chỉ nguồn chính thức và revision riêng.

24reserved revision3 chưa hỏi.121validation cũ đã mở; không gọi lại bộ đó là kiểm tra mù. Patch8/patch6 bị loại vẫn giữ bằng chứng; không áp dụng lại chỉ vì một bộ target có điểm cao hơn. Cần giữ các ca nguyên tắc/công cụ đangFAIL như lỗi thật, không loại khỏi mẫu.

193unit đã qua trên đúng mã patch9; không chạy lại vô cớ nếu không đổi mã. Không fine-tune/Colab/APIphí/subagents/deploy/nhắn ai khác. Không có điểm nghĩa toàn479hoặc600trước khi hoàn tất coverage; lượt này chưa nghiệm thu sản phẩm.
