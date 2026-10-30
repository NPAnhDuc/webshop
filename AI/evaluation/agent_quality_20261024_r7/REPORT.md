# Capability preflight — r7

Giữ nguyên106 câu/gold r6, không đổi prompt/model/nguồn/config. Một bước code: chặn yêu cầu xử lý file hoặc doanh số theo SKU rõ ràng bị đổi thành kiểm nguồn cũ. Đây là baseline lexical trước advisory planner, chưa phải hiểu tiếng Việt tổng quát. Kiểm quyền trước guard; unsupported không chạy công cụ, không ghi dữ liệu và không tự tạo số liệu.

Một batch local Qwen hoàn tất106/106, integrity unchanged=true. Helpers checks được chuẩn bị trước batch; không sửa runtime/input/model/config trong khi chạy. Mọi kết quả/candidate cũ nguyên vẹn.

- Checks cơ học:24/24 mới +60/60 hồi quy +19/22 hội thoại.
- Review ngữ nghĩa riêng:103/106, trước93/106. Cùng84 câu cũ84/84;22 lượt hội thoại19/22. Toàn bộ hội thoại đạt4/6, trước2/6.
- Sửa10fail: Q10,Q14,Q20,Q22,Q24,Q28,Q37,Q39,A20,A22. Yêu cầu Excel/ranking/per-SKU nay báo chưa hỗ trợ đúng, không kiểm nguồn thay thế. Đây là tăng độ đúng trong từ chối/chọn capability, chưa thêm chức năng clean hay xếp hạng thật.
- 11answer thay đổi đã đọc riêng:10fail sửa vàQ11 vốn deferred đúng.95answer khác giữ nguyên sau chuẩn hóa đường dẫn revision; tool/args cũng không đổi. Không tìm thấy hồi quy mới trong bộ đã lộ này.
- Còn3fail: Q29/Q30 viết dính RAM/SSD; Q41 tìm sản phẩm kèm giải thích DDR5 chưa xử lý đủ. Chưa nối documents retrieval trong agent_tools; registry disabled không phải RAG đã hoạt động.

106trace kiểm role/question/parent links;11turn guard không gọi bất kỳ tool. training_allowed=false. Bộ này development đã lộ, không phải validation độc lập hoặc chứng minh accuracy ngoài thực tế. Không đưa đáp án kiểm thử/log vào RAG/training.

409unit/integration tests đạt153,87s; riêng20ca guard offline9/20→20/20 cùng harness. Lượt targeted đầu có3setup errors do quyền pytest temp cũ, fullsuite dùng basetemp mới trong workspace đã đạt. Không thay quyền ứng dụng. Log AI/runtime/tests-capability-guard-r1.log.

Median modelbatch0,7495s, max31,64s; cold/warm khác nhau và có ít model call hơn khi guard bind được, chưa suy ra SLA hoặc tốc độ production. Nguồn SQL/catalog/curated được kiểm hash giữ nguyên, số demo vẫn mô phỏng, không ghép backend35đơn vàscenario1427đơn.

accepted_for_application=false; default basic_rag không đổi. Chưa deploy/frontend/auth/server principal integration/fine-tune/Colab/embedding startup/model download. Bộ300buyer mới chưa chạy. Bước tiếp kiểm mixed catalog+documents, rồi review/freeze bộ mở rộng theo nhóm; typo normalization sau nền ổn theo yêu cầu. Nhánh tài liệu cần được nối với phân quyền/provenance; không retry worker8011/r19 bị chặn. Excel/DA/DS/Kev/devCompose tiếp theo reliability PLAN.
