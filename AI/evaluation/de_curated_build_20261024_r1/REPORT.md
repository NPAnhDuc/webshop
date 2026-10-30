# Dựng curated mô phỏng — revision 1

Đã tạo `AI/data/de_pipeline/retail_sim_v1/curated_20261024_r1/curated.sqlite` từ raw đã đóng băng, sau khi xác minh lại hợp đồng và chuỗi audit/đối soát. Status `built_verified_not_activated`: bản dữ liệu phân tích nội bộ đã dựng và kiểm, chưa publish hoặc thay nguồn phục vụ chatbot.

Projection có 67 SKU, 1748 dòng sổ tài chính, 99 khoản chi phí, 24455 snapshot tồn ngày/SKU. Chỉ lấy cột cho phép, có khóa chính và khóa ngoại SKU; không copy thông tin khách hàng, đơn hàng, toàn bộ catalog hoặc bảng khác. Vì không có bảng orders, bộ này chưa cung cấp số đơn hoặc là DB thay thế trực tiếp cho finance tool hiện tại. Không gộp 35 đơn backend vào nguồn 1427 đơn scenario; export 37 SKU cũ không được dùng.

8/8 gate parity đạt: từng dòng của bốn projection khớp raw; tổng tài chính và tổng theo tháng khớp; integrity/FK đạt; tổng tài chính vẫn khớp sau đóng/mở lại DB. Không join bảng chi phí vào từng dòng bán. Tổng mô phỏng trong kỳ 01/10/2025–30/09/2026: doanh thu thuần 13.495.418.000 VND, giá vốn thuần 11.615.510.000, lãi gộp 1.879.908.000, chi phí hoạt động 1.392.049.598, lãi hoạt động trước lãi vay/thuế 487.858.402. Đây không phải lãi ròng hoặc hoạt động thật của shop.

Đơn vị VND nguyên, giá chưa VAT và FIFO theo hợp đồng mô phỏng có hash. Sales completeness vẫn unverified; không sinh ngày/tháng giao dịch trống thành 0. Trạng thái admin_only có trong manifest/metadata để consumer kiểm tra, chưa phải lớp xác thực HTTP hoặc quyền filesystem. Không cung cấp file này cho người mua.

Hash DB mới `2518f490d7a0c8a8b26d9ec7d5d22fecd3f2891b12207abbcbe80f48168515e4`. Raw, staging, reconciliation và eligibility giữ nguyên hash; source SQLite vẫn `f544a0a0255d78a06f01833275170a6f2eda89f2c9053a923433e420ca365028`. Manifest hoàn tất ghi cuối; lỗi để lại build.failed.json và không có completion manifest, không tự xóa/tái sử dụng thư mục dở dang. Code snapshot và hợp đồng được kiểm lại lưu cùng revision.

8 test mới PASS10,95s: projection bỏ PII, không nhân chi phí, grain và coverage, không ghi đè, raw bị sửa, eligibility sai nguồn/nhãn/trạng thái, contract bị đổi metric dù rehash, nguồn đổi trong lúc dựng và lỗi tổng sau ghi đĩa. Toàn bộ suite **304 test PASS116,95s**, log `AI/runtime/tests-de-curated-r1.log`. Không chạy model/GPU, embedding, fine-tune/Colab hoặc thay frontend/config/mode/auth.

Bước tiếp: reader chỉ đọc kiểm manifest/hash/lineage và phân quyền server trước khi nối công cụ DE/admin; nếu cần order count phải bổ sung projection theo hợp đồng mới, không suy số đơn từ số dòng sổ. CSV/Excel mapping và DS/backtest chưa triển khai. Chưa có đo cải thiện độ đúng/tốc độ câu trả lời hội thoại trong lượt này; PASS parity/unit không thay đánh giá ngữ nghĩa hoặc validation độc lập.
