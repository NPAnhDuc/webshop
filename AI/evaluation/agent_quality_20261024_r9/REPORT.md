# Mixed catalog candidate — rejected and rolled back

Một thử nghiệm xử lý tìm/so sánh sản phẩm kèm câu hỏi kiến thức: router chọn nhánh kết hợp, tách hai source span, giữ giá/số lượng/phủ định, chạy catalog và registered-disabled documents, báo partial thay bỏ phần tài liệu. Không nối retrieval hoặc thực thi code/SQL từ tài liệu.

Trước sửa snapshot/harness8ca tại ../mixed_catalog_20261024_r1; injected planner + real tools trước0/8 sau8/8, oracle catalog JSON độc lập.64targeted tests đạt8,87s. Đây không phải bằng chứng model định tuyến tốt.

Một modelbatch118=106cũ nguyên +12mới. Runner exit1 do3unavailable liên tiếp Q56-Q58, dù đã ghi đủ118results; không chạy lại, không tạo integrity.json/regression-results giả hoàn tất. post_stop_integrity.json xác minh mọi inputhash vẫn nguyên sau exit và TRƯỚC rollback. Code snapshot/results/modelcalls/traces giữ nguyên candidate.

Chấm riêng: cùng106 giảm103→100;102answer không đổi,4đổi Q02/Q15/Q19/Q41.3hồi quy mới Q02/Q15/Q19: router admin chọn nhầm search_documents cho câu nguồn hoặc RAM đơn thuần; splitter tạo knowledge_question không có trong câu, guard chặn. Q41 vẫnfail, lần này overlap cả câu thay vì tách đúng.

12mới7/12 theo checks và review riêng:6mixedsearch laptop/RAM/SSD trả đúng SKU và nói rõ docsdisabled;1searchcontrolcustomer đúng.2monitorsearch trả4/5 thay2 vì parser literal chưa nhận danh từ monitor;2mixedcomparison tách bỏ từ “So” nên coverageguard từchối;1adminsearchđơn thuần bịnhầmmixed. Các vấn đề này chưa sửa trong lượt này, không sửa gold đểpass.

Candidate bị loại; khôi phục catalog_planner.py vàagent_conversation.py BYTE-EXACT baseline r8, giữ code mới trongcode_snapshot và test_mixed_catalog_candidate.py ởfolder evaluation.55targeted checks sau rollback đạt5,62s, logtests-mixed-rollback-r1.log. Defaultbasic_rag/config/model/nguồn khôngđổi; khôngpromote/deploy. R8 vẫn là checkpoint hồi quy103/106, không coi testcode64pass thay nghiệmthuAI.

118trace role/question/parentlinks verified. Không APIpaid/train/Colab/worker8011-r19/download/frontend/agents. Bước sau nếu quay lại mixed: phân tách decision schema không ưu tiên nhánh mới, kiểm nghĩa có hai yêu cầu trước thựcthi, lập regression các ca vừa sai; giữ coverageguard thay bỏ đểche lỗi. Tách lỗi countmonitor khỏi lỗi decomposition/routing. Không batchthứhai trong heartbeat.
