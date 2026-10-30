# Giữ thao tác và kỳ khi câu nối chỉ đổi chỉ tiêu

Đã đóng băng code trước sửa và3ca có trạng thái đã xác nhận, lấy từ trace A03/Q27/Q36. Bài kiểm tra trước/sau cố ý inject advisory plan sai=clarify:0/3→3/3. Đây là kiểm hợp đồng ràng buộc trạng thái, không phải số lỗi model thực trước đó. SQL kỳ vọng truy vấn trực tiếp raw ledger, không dùng analyze_business làm oracle.

shopbot/admin_state.py nhận diện tham chiếu literal chỉ tiêu đã biết trong câu chỉ đổi metric, giữ operation finance/chart/compare và kỳ đã xác nhận. Không điền kỳ khi thiếu; từ chối bind khi pending, entity khác shop, kỳ sai, comparison không đủ hoặc câu đổi hành động/đối tượng/kỳ rõ. Scope nhỏ này không thay bộ định tuyến ngữ nghĩa tổng quát. Alias metric là operand allowlist, không danh sách đáp án hay câu hỏi test.

AdminConversation dùng reference plan trước advisory planner; trace ghi state_resolution để biết nguồn quyết định. Không đổi prompt/model/nguồn hoặc mặc định app.44targetedPASS11,51s; full384PASS114,23s. Tests có câu phủ định, nhiều metric, scope/SKU, kỳ mới/mâu thuẫn, pending/invalid state và đổi role.

Một modelbatch cùng106câu/gold r5 tại agent_quality_20261024_r6 hoàn tất và integritytrue. Ngữ nghĩa91→93/106: A03/Q27 nay giữ compare tháng8–9/2026, giá vốn1.240.171.000 và1.010.759.000VND mô phỏng, chênh-229.412.000/-18,50%; khớp SQL độc lập.104answer khác không đổi. Q36 vốn đúng vẫn đúng, giờ không phụ thuộc planner. Không chạy batch thứ hai sau khi người dùng ngắt/hỏi và yêu cầu tiếp tục; chỉ kiểm tra hoàn tất và chấm batch đã chạy.

Phần state này chưa hoàn thiện quy tắc reset khi đổi đối tượng/nhóm hàng hoặc xử lý unsupported→inspect. Candidate vẫn chưa nghiệm thu. Bước tiếp dựa trên các13FAIL còn lại, không mở validation RAG hoặc cào data để chữa lỗi state.
