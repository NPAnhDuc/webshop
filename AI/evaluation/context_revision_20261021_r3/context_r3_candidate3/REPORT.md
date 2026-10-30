# Patch9: hỏi rõ sản phẩm khi tham chiếu chưa có đối tượng

Sau truy xuất, bot kiểm tra câu nhắc sản phẩm “vừa/đã nói, nhắc, chọn, tư vấn” có đối tượng xác nhận hay chưa. Nếu không có lịch sử, bộ nhớ sản phẩm hoặc sản phẩm được nêu rõ ngay trong câu và khớp nguồn, bot hỏi lại trước bước chọn bằng chứng. Bài giải thích thuật ngữ không xác định được một model máy. Đây là kiểm tra ràng buộc đối tượng, không thêm đáp án hay ID kiểm thử vào mã.

Kiểm tra nằm sau truy xuất để câu tự nêu model vẫn được giải đáp. Không thay prompt/router, không áp dụng lại patch8 đã loại; không đổi SQL, nguồn, gold, model hoặc trọng số. Snapshot trước sửa tại `../patch9_before_code/`.

Cùng 24 development với patch7 (`context_r3_candidate1`): **17→18 PASS nghĩa, 6 FAIL**. Chỉ R2D10 thay đổi: câu “máy vừa nói” chưa có đối tượng được hỏi lại thay vì trả bài CPU/USB-C. Không có PASS→FAIL trong 24; khách 8/8, admin 10/16. Đã đọc đủ 24 theo cùng rubric, tách khỏi checks; đây là đánh giá của Codex, không phải người duyệt độc lập. 23 answer/action/source còn lại giống patch7.

Checks riêng: 17 PASS_CHECKS, 2 FAIL_CHECKS, 5 NEEDS_REVIEW. Sáu lỗi D15–D20 vẫn còn: yêu cầu đổi giá/cộng dòng đơn bị chọn bằng chứng sai, bốn câu nguyên tắc/phạm vi chưa giải đáp. Không tính việc có trích dẫn là đáp đúng. Không có thao tác ghi hay tính tổng được thực hiện.

Batch 24 hoàn tất, integrity unchanged=true. 12 trích đoạn có trong đúng nguồn/phiên bản đã chốt, không có quote issue hoặc lộ nguồn nội bộ cho khách. Tổng 93.217 giây, trung vị 2.2495 giây so 98.467/2.7965 của patch7. Không tuyên bố cải thiện tốc độ vì cache/warmup không được kiểm soát.

**193 test qua trong 46.00 giây**, log `AI/runtime/tests-context-r3-p9.log`; đã kiểm exit code 0 trước khi chạy batch. Thêm 6 ca: ba cách nhắc sản phẩm chưa có đối tượng, câu tự nêu model, câu nối có bộ nhớ sản phẩm và câu đổi sang model khác. Test dùng router giả lập để kiểm luồng; độ hiểu của model được kiểm riêng bằng batch thật. Giữ fixture cùng đồng hồ từ lượt trước.

Giữ patch9 candidate để hồi quy, chưa nghiệm thu. Lượt này một sửa và một batch 24, không mở 24 reserved. 87/100 cũ thuộc patch7, chưa đo trên patch9; 112/121 validation thuộc patch5 đã mở. Chưa chạy lại toàn 479 hoặc có điểm nghĩa toàn 600.

Bước tiếp theo: kiểm ba runner, preflight rồi chạy duy nhất `run_quality_regression.py --round old100_patch9`, so cùng 100 với `old100_patch7`. Đọc câu đổi và các ca nối sản phẩm, đặc biệt C02/C03/C06/C44. Giữ nguyên kết quả thử nếu phải loại; không sửa tiếp trước hồi quy. 18/24 của patch8 đã loại cũng là 18 nhưng sửa D15; patch9 hiện tại sửa D10, hai bản khác nhau.

Cập nhật21:10UTC: old100_patch9 đã hoàn tất87PASS/13FAIL,0PASS→FAILso patch7;98answer/action/sourceskhớp,A16/A17đọclạivẫnđúng. Giữcandidateđể đánhgiárộng. Hiện đangchạy candidate_v9_development --splitdevelopment479lượt,khôngsửa mã/nguồn/model/config hoặcmởbatchkhác. Đọcquality_loop_20261021/CURRENT.md vàcandidate_v9_development/REVIEW_PLAN.mdtrướchànhđộngtiếp.24reservedchưahỏi,chưanghiệmthu.
