# Kế hoạch đã điều chỉnh theo yêu cầu người dùng

Mốc bắt đầu: candidate agent r3 chưa đạt, 9 lỗi ngữ nghĩa/84lượt. Cấu hình web vẫn basic_rag, model local Qwen3 hiện có. Không coi dữ liệu mô phỏng là shop thật, không gộp35đơn backend với1427đơn scenario.

## 1. Đóng băng, hồi quy, trace trước sửa

- Snapshot code trước sửa, parent hashes,9ca lỗi cũ và oracle số lượng được lưu tại evaluation/regression_contract_20261024_r1.
- Cùng bank chạy trước/sau, không ghi đè results/gold cũ. Có kế hoạch và kết quả mong đợi, phân biệt modelplan với toolargs thực thi.
- Trace mỗi lượt: question/role/ngày server, plans, calls với args/output/status, state trước/sau, lỗi và thời gian. Trace không tự là tri thức/nhãn train. Chỉ server chọn thư mục; phân quyền HTTP/filesystem vẫn cần tích hợp.

## 2. Sửa xác định và kiểm hợp đồng

- Literal số lượng/giá phải xác minh bằng mã; thiếu hàng thì công bố số thiếu, không bịa cho đủ. Kiểm số trả về và ID trùng trước render.
- Chuẩn hóa trạng thái kỳ/chỉ tiêu/đối tượng/thao tác; giữ kỳ khi đổi metric, xóa/chuyển context khi đổi đối tượng không tương thích, phân quyền từ server. Đổi nhóm hàng không nhất thiết xóa mọi kỳ: giữ kỳ lịch khi phù hợp, reset lựa chọn/SKU/filter không còn hợp lệ, hỏi lại nếu mơ hồ.
- Registry capability phân biệt supported/deferred/disabled, roles, args, sources. Đăng ký documents từ đầu kể cả chưa wire retrieval; không báo đã xử lý khi chỉ có stub. Ca documents-only và mixed phải có kỳ vọng tách nguồn catalog/knowledge và hạn chế hiện tại.
- Runtime kiểm schema/role/args/nguồn/kết quả. Không viết luật khớp từng câu test để thay hiểu ngôn ngữ; classifier không được làm unsupported action thành tool khác.

## 3. Tài liệu, logs và nhãn

- Nối nhánh kiến thức có nguồn với lọc phiên bản/hiệu lực/quyền, rồi phân loại thiếu kiến thức/truy xuất/tổng hợp/routing từ trace.
- Bổ sung data đúng loại lỗi, không cào ồ ạt hoặc đưa gold/trace/câu sai của bot vào RAG.
- Gán nhãn routing ngay từ kế hoạch đã được người kiểm xác nhận; lưu parent trace/hash, capability và args kỳ vọng, ngày/ngữ cảnh/nhóm paraphrase. Lưu baseline luật/LLM, tách nhóm hội thoại thành train/dev/holdout, không dùng development đã lộ làm independent validation. Chưa fine-tune Kev trước khi đủ nhãn và tiêu chuẩn đánh giá.
- Số liệu gold được tính bằng SQL độc lập, không gọi analyze_business/renderer của bot làm oracle. Kiểm riêng kết quả, kế hoạch và ngữ nghĩa; unitPASS không là accuracyAI.

## 4. Tái lập và phần mở rộng

- Docker Compose môi trường phát triển làm sớm, pin dependencies, mount dữ liệu/revisions chỉ đọc, trace riêng, healthcheck; dùng Ollama local hiện có, không tự khởi động worker8011/r19 đã bị chặn. Docker dev không đồng nghĩa deploy công khai.
- Excel: xem trước sheet/mapping; định dạng ngày dd/mm được khai báo rõ, không đoán ngày mơ hồ; đơn vị VND/nghìn VND phải xác nhận, chuẩn hóa có lineage; quarantine, đối soát, phiên bản/rollback bằng đổi pointer có kiểm, không xóa raw cũ.
- DA: KPI/so sánh/biểu đồ từ curated có nguồn và grain đúng. DS: baseline đơn giản gồm seasonal naive, time-based backtest, so cùng horizons/metrics/độ phủ; chỉ giữ mô hình phức tạp nếu thắng rõ, không hứa causal insight từ tương quan.
- Kev/HyDE/deploy sau khi đủ nhãn/holdout và kiểm định thích hợp. Không tải model lớn/API trả phí để né lỗi logic.

## Điều kiện qua bước

Ca lỗi đã biết phải được sửa, không làm hỏng hồi quy liên quan; có raw trace và kiểm ngữ nghĩa riêng. Các chức năng chưa nối phải nói đúng trạng thái; không promote candidate chỉ vì tăng điểm trên development. Phát hành revision mới cho mọi thay đổi bank/gold/data.


## Cập nhật yêu cầu mở rộng sản phẩm

Giữ106lượt làm hồi quy; mở rộng300developmentturn ở evaluation/buyer_expansion_20261024_r2. Không đánh đồng số turn với unique questions hoặc independent validation; câu thiếu nguồn cần review trước chấm groundedness. Hiểu lỗi chính tả/teencode/viết dính được người dùng hoãn đến khi nền ổn: chưa triển khai feature đó. Khi thực hiện, dùng bank riêng, giữ câu gốc và xác minh ngân sách/số lượng/SKU/phủ định, hỏi lại khi mơ hồ thay vì tự sửa operand. Giai đoạn sau nối tài liệu RAG và đánh giá theo nhóm, rồi Excel/DA/DS/Kev theo gate; devCompose có thể làm sớm.
