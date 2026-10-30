# Hợp đồng và gate trước curated — revision 1

Đã kiểm tra chuỗi raw → staging audit → reconciliation và tạo hợp đồng nguồn có hash tại `contract.json`. Trạng thái `eligible_for_simulation_curated_build`: đủ điều kiện cho bước dựng curated mô phỏng, **chưa tạo bảng curated, publish hoặc thay nguồn chatbot**.

Hợp đồng khóa source_id, hash ledger/catalog qua raw manifest, staging và reconciliation; kiểm từng check và quarantine thay vì chỉ đọc cờ passed tổng. Sai nguồn, kỳ, giả định kế toán hoặc artifact bị sửa thì từ chối trước khi ghi output. Thư mục output đã tồn tại không được ghi đè.

Đơn vị VND nguyên, giá chưa VAT, FIFO và lãi hoạt động trước lãi vay/thuế được khai báo theo assumptions của simulator. Bản assumptions được chụp riêng với hash trong revision này; không thêm ngược vào raw manifest đã chốt. Đây là khai báo mô phỏng có bằng chứng local, không phải xác nhận kế toán, tỷ giá hoặc doanh thu thật. Không có chỉ tiêu lãi ròng. Grain riêng cho dòng sổ, chi phí, SKU và tồn ngày/SKU; không join chi phí vào từng dòng bán gây nhân tổng. Sales completeness vẫn unverified; ngày không có giao dịch không tự trở thành ngày doanh thu 0.

Nguồn vẫn retail_sim_v1, 67 SKU/1427 đơn; không ghép 35 đơn backend hay export cũ 37 SKU. SHA ledger vẫn `f544a0a0255d78a06f01833275170a6f2eda89f2c9053a923433e420ca365028`.

12 test mới PASS13,71s: nguồn/hash không đổi, output không ghi đè, snapshot assumptions, sai nguồn/kỳ/thuế/phương pháp giá vốn/thiếu đơn vị, sửa raw/staging, reconciliation nguồn khác và check FAIL bị che bởi passed tổng. Lượt đầu pytest lỗi môi trường temp/cache; chạy lại bằng basetemp mới trong runtime và tắt cache đã qua. Không đổi test/gold cũ để làm kết quả qua.

Toàn bộ suite hoàn tất **296 test PASS99,15s**, log `AI/runtime/tests-de-contract-r1.log`. Không chạy model/GPU, train/Colab hoặc embedding. Không thay mode/config/frontend/backend auth. Các điểm development hội thoại trước đó không thay đổi và không được coi là validation độc lập.

Bước tiếp: materialize curated revision từ đúng raw đã khóa, giữ grain riêng, kiểm tổng và lineage trước manifest hoàn tất. Chưa kích hoạt nguồn mới. CSV/Excel mapping, tool DE hội thoại và DS/backtest còn ở các bước sau. Adapter hiện chỉ nhận giả định mô phỏng đã hỗ trợ; dữ liệu thật cần hợp đồng/mapping riêng. Hash/no-overwrite không phải chữ ký hoặc WORM; gate không tự cấp giấy phép sử dụng dữ liệu.
