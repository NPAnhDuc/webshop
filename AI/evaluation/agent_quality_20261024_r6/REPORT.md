# Confirmed metric-reference state — r6

Giữ nguyên106câu/gold r5 và prompt/model. Một bước sửa code: câu nối chỉ thay chỉ tiêu được bind vào operation/kỳ đã xác nhận, thay vì để advisory planner làm mất so sánh. Trường hợp khác vẫn đi planner/guard hiện có. Nguồn/quyền/lịch/SQL/default config/frontend không thay.

Batch106/106hoàn tất trước khi người dùng hỏi dừng tạm; sau yêu cầu tiếp tục đã kiểm process/integrity và chấm chính batch đó, không chạy lại model. Integrity unchanged=true. Helpers được copy trước batch; không sửa runtime/input/config hoặc tạo helper trong lúc model chạy.

Checks19/24+58/60 và16/22contract. Review ngữ nghĩa riêng93/106so91/106r5;84câu cũ77/84,22turnmới16/22, vẫn chỉ2/6hội thoại mới đạt toàn bộ. Không đổi mẫu/gold để tính tăng điểm.

A03/Q27 được sửa: “còn giá vốn?” sau so sánh doanh thu giữ2kỳ tháng8 và9/2026 và đổi metric sang cost. SQL độc lập xác nhận1.240.171.000/1.010.759.000VND, delta-229.412.000/-18,50%. Đây là dữ liệu mô phỏng chưa VAT, không phải số thật của shop.104answer còn lại giữ nguyên nội dung sau chuẩn hóa đường dẫn artifact; review tiếp nối r5. Không có hồi quy mới trong tập này.

Còn13FAIL: Q10,Q14,Q20,Q22,Q24,A20,A22 (transform/ranking→inspect); Q28(perSKU→inspect),Q29/Q30(viết dính catalog),Q37(clean→inspect),Q39(rank→inspect),Q41(mixedcatalog+documents). accepted_for_application=false; chưa bật mặc định. Documents vẫn registered-disabled, chưa truy xuất RAG thật trong mode agent_tools. State reset theo đối tượng còn thiếu, không coi helper literal là hiểu hội thoại toàn diện.

106trace role/question/parent links verified, có state_resolution. A03 giảm model call2→1, Q27 3→1 do không hỏi lại planner cho operand đã biết; đây là giảm số call có đo, không suy SLA từ thời gian. Median toàn batch0,8275s/max26,359s có cold/warm.44targetedPASS11,51s/full384PASS114,23s. Log tests-admin-state-r1.log và quality-data-quality-r6.log.

2reviewed seed labels mới ở training/state_reference_labels_20261024_r1, cùnggroup_id để không rò paraphrase qua split; development đã lộ, chưa đủtrain/holdout, không đưaRAG. Giữ mọi raw/source/curated/candidate/gold cũ. Bước tiếp kiểm capability/đối tượng và state keep/reset dựa trên trace, không kéo dài prompt hoặc train model để che lỗi logic. Không còn runner model/test ở cuối bước.
