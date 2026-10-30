# Patch7 — sửa chặn nhầm kỳ hiện tại

Bot phân giải lịch trước khi kiểm tra tham chiếu mơ hồ. Tháng/quý đã xác định được chuyển tới router và tra nguồn đúng kỳ. Máy/bộ/tài liệu chưa xác định vẫn phải hỏi, kể cả có tháng hiện tại. Không mặc định “kỳ này” là tháng. Không thêm câu trả lời, SKU hoặc ID kiểm thử vào quy tắc; không đổi model, dữ liệu hay gold.

Cùng24development với baseline_regraded: **12→17PASS nghĩa,7FAIL**, sửa R2D01/02/03/13/14, không có PASS→FAIL trong24. Khách7/8,admin10/16. Đã đọc/chấm đủ24, bởiCodex, không phải đánh giá người độc lập. Checks tách riêng:11/8/5→16PASS_CHECKS/3FAIL_CHECKS/5NEEDS_REVIEW. Gain này từ thay đổi bot, không phải4cờ giả do fixture r2 đã sửa trước lượt này.

Ba câu báo thiếu nguồn đúng tháng/quý, hai câu dự đoán/vẽ biểu đồ được trả giới hạn công cụ đúng. Câu “Trong tháng này, bộ đó có vừa case không?” vẫn hỏi lại đúng. D15(cập nhật giá) vàD16(cộng dòng đơn) nay tới router nhưng bị chọn sai bằng chứng thay vì deferred. Không thực hiện thay giá hoặc tính tổng; hai câu vẫn FAIL, không tính cải thiện dù câu trả lời thay đổi. Bốn lỗi nguyên tắc/phạm vi kinh doanh và một lỗi máy chưa xác định vẫn còn. Không sửa nguyên nhân thứ hai trong cùng lượt.

Integrity24unchanged=true,15trích đoạn có trong đúng nguồn/phiên bản đã chốt,0lộ nguồn nội bộ cho khách. Trích đúng không đồng nghĩa trả đúng; ví dụ câu FIFO không đáp ứng phép cộng doanh thu. Không có số liệu/shop policy tự sinh được nạp vào tri thức.

Thời gian tổng91.044→98.467giây, trung vị1.5075→2.7965giây. Không tuyên bố nhanh hơn: baseline có7câu bị trả sớm trước model, lượt mới phải thực sự định tuyến/truy xuất; hai lượt cũng khác trạng thái cache. Chưa có phép đo tốc độ đại diện.

Quyết định: giữ candidate để hồi quy, **chưa nghiệm thu/chưa xác nhận độ đúng toàn hệ thống**. Chưa chạy lại100cũ hoặc479development trênpatch7. Điểm87/100 và112/121 cũ thuộcpatch5; không chuyển sangpatch7.24reserved vẫn chưa hỏi. Lượt này chỉ1sửa và1batch24; bước tiếp theo hồi quy100 cùng mã trước sửa tiếp hoặc mởreserved. Raw outputs, baseline và600cũ giữ nguyên.

Snapshot trước sửa: ../patch7_before_code/. Bản sửa chỉgrounded_rag.py, tests thêm6ca (2ca và4đối chứng tham số). Fullsuite lần đầu186PASS/1FAIL do mock test mới chưa giả lập lượt chọn bằng chứng khi không có nguồn; đã sửa mock,31testgrounded qua. Fullsuite kiểm lại **187PASS trong45.90s**, ghi tại AI/runtime/tests-context-r3-p7-final.log. Các kết quả model vàreview nằm trong thư mục này; record_review.py chỉ ghi quyết định sau đọc, không làm judge tự động.

Cập nhật16:00UTC: hồi quy100 đã hoàn tất tại ../../quality_loop_20261021/old100_patch7/.87PASS/13FAIL giữ nguyên,0PASS→FAIL;99answer/action/sourceobjects giống hệt,A17chỉđổi thứ tự nguồn đượcđọclại. Giữcandidate cho development,chưa production-accepted/chưa rerun479/chưa mởreserved. Các đoạn chưa hồi quy ở trên ghi trạng thái thời điểm chạy24, đã được cập nhật bởi kết quả này.
