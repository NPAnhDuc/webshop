# Tiếp tục — 21/10/2026, baseline600 đã chạy và validation121 đã chấm

## Trước mọi thao tác

Đọc LOOP_PLAN.md. Kiểm CẢ run_quality_loop.py VÀ run_quality_regression.py của workspace. Nếu bất kỳ batch còn chạy: không sửa code/data/model/config, không mở batch khác và giữ im lặng khi không đổi. Lúc kết thúc audit13:02UTC không có runner đang chạy.

Mã active là patch5 đã đóng băng tại DEVELOPMENT_FREEZE_PATCH5.json; khớp từng hash. Chưa nghiệm thu hệ thống. Không có sửa bot hoặc batch model mới trong lần audit này; chỉ chấm121 và cập nhật báo cáo.

## Kết quả đã có

- Bank600 lượt (300khách/300admin),545 lời văn/454nhóm. Cả479development và121validation hoàn tất, integrity=true, mã/source/gold không thay trong batch. Nguồn shop mô phỏng; không fine-tune/thêm chính sách thật hoặc tự học đáp án bot.
- Patch5 development479:422PASS_CHECKS/4FAIL_CHECKS/53NEEDS_REVIEW. So v1 cùng479:413/13/53,11lỗi sửa,2hồi quy Q0191/Q0396. Riêng89so patch2:77/5/7→79/3/7; sửa2lỗi thiếu chỉ tiêu Q0267/Q0352, không suy giảm kiểm tra trong89.27câu đổi tách liệt kê qua kiểm tra hẹp.181test mã active đã qua.
- Review development112ca chọn:86PASS/26FAIL;100kế thừa câu/trích dẫn nguyên vẹn,12đọc lại.367ca chưa chấm nghĩa đầy đủ. Không dùng112ca chọn hoặc PASS_CHECKS suy điểm toàn479.
- Validation121 được Codex đọc/chấm từng câu mới:112PASS/9FAIL; khách49/52,admin63/69;96nhóm hội thoại/87nhóm đạt mọi lượt. Checks tự động102/4/15, không đổi thành điểm nghĩa. 227quotechecks,0absentquotes,0private-source leaks. Median4.547s,tổng604.565s. Chưa có người duyệt độc lập.
- Nhóm business_reasoning chỉ2/7PASS, trong khi61câu validation là mẫu báo cáo/mục tiêu tài chính và33lượt thuộc tính sản phẩm. Không lấy tổng112/121 làm độ chính xác tư vấn thực tế. Nhiều câuPASS vẫn lặp/thừa. Chưa đo recall@k cấpđoạn độc lập.
-9FAIL validation:Q0037(deferred bị hỏi lại),Q0078(chưa rõ máy nhưng trả chính sách),Q0124(khách hỏi doanh thu báo thiếu thay vì từ chối quyền, không rò dữ liệu),Q0158(có phân khúc lại báo thiếu),Q0223(không kết luận khuyến mãi hết hạn),Q0232(ngân sách chiến dịch/cả năm),Q0266(thiếu đối chiếu phiên bản),Q0274(hỏi nguyên tắc kế toán lại hỏi kỳ/model),Q0328(thiếu loại case). human_review.json ghi từng quyết định, không dùng source checks làm PASS nghĩa.
- Tổng600:524PASS_CHECKS/8FAIL_CHECKS/68NEEDS_REVIEW. Không có điểm nghĩa toàn600. BASELINE_600_REPORT.md/BASELINE_600_SUMMARY.json là báo cáo tổng đúng phạm vi; validation_v1/REPORT.md/summary.json là kết quả bộ121. accepted=false.
- Bộ100 cũ patch5:87/100(khách47/admin40), so v7=85 sửaC06/C44, không hồi quy từPASS.87review kế thừa câu/trích dẫn nguyên vẹn,13đọc lại.213quotechecks0integrityissues. Đây là bộ phát triển đã thấy, không trộn vào validation.
- Patch3/4/6 đều đã loại, snapshot/decision/raw giữ nguyên. Patch6 tăng recall nguồn nhưng làm100giảm87→76 với11hồi quy. Đã phục hồi patch5; test mới của bản6 lưu trong source_snapshot rồi gỡ khỏi bộ active. Không thử lại nhãn đơn thuần/xóa rộng context/mở gateBM25 blanket.

## Validation đã mở — quy tắc sửa tiếp

Patch5 đóng băng TRƯỚC khi chạy validation, không dùng121để chọn/sửa patch5. Nay121đã mở/đã chấm. Mọi sửa tiếp phải thừa nhận bộ này đã dùng; tạo holdout MỚI để xác minh mới, không gọi121cũ là kiểm tra mù. Giữ nguyên bank/gold/results của revision này. Cùng kho nguồn nên không coi đánh giá là độc lập.

## Việc tiếp theo có căn cứ

1. Đọc NEXT_REVISION_PLAN.md và BASELINE_600_REPORT.md. Có thể hoàn tất chấm367development còn lại, nhất là phần giải thích/đối chiếu, không gắnPASS tự động. Không cần chạy model lại chỉ để chấm câu đã có.
2. Chuẩn bị revision câu hỏi/nhóm holdout mới trước sửa tiếp; đa dạng câu nối/đối chiếu/thời gian và giới hạn, không tăng số bằng các tổ hợp báo cáo giống nhau. Gold lấy nguồn đã duyệt, không từ đáp án bot, không sửa gold sau khi thấy kết quả. Giữ ngân hàng600 cũ nguyên vẹn.
3. Chọn một nguyên nhân chung cho một bước sửa: guard tham chiếu mơ hồ đang chạy trước resolve_scope nên dễ chặn kỳ hiện tại hoặc nguyên tắc kế toán; phải phân biệt thiếu đối tượng với kỳ xác định được/yêu cầu cần công cụ. Đây mới là giả thuyết; cần unit phản chứng khác lời văn/kỳ/SKU, không ID/đáp án benchmark trong code. Không sửa nhiều hướng cùng lần.
4. Sau sửa chạy test phù hợp rồi một batch cần thiết và so cùng câu/hồi quy; nguồn thiếu thực mới bổ sung bằng nguồn chính thức/revision mới. Chưa deploy/Colab/finetune/API trả phí/subagents/nhắn người khác. Giữ tác vụ mỗi giờ; chỉ báo cải thiện đo được/lỗi chặn hoặc cần xác nhận dữ liệu thật.

## Tệp và hạ tầng

report_quality_status.py đã hỗ trợ v5, old100patch5, patch6 đã loại và assessment600/validation; có thể tạo lại REPORT/STATUS khi không có batch. Hai runner dùng cùng runner.lock/GPU. Mã active181test đã qua; không cần lặp pytest khi chỉ sửa báo cáo. Runtime logs không là nguồn tri thức, interactive/evaluation/unattributed phải tách; unknown không coi khách thật. KNOWLEDGE_GAPS.md vẫn cần điều khoản thật từ chủ shop, không bịa.
