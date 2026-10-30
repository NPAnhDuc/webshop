# Công cụ kiểm tra nguồn curated cho admin — revision 1

Đã nối `admin.data_quality` vào dispatcher AgentTools, với reader chỉ đọc và nguồn do server truyền vào. Tool trả nguồn/revision/hash, kỳ khai báo, số dòng theo bảng, ngày giao dịch đầu/cuối, kết quả parity và giới hạn độ phủ. Nguồn hiện vẫn là mô phỏng, không chứng minh shop thật hoặc dữ liệu đủ cả kỳ. Không trả nội dung khách hàng hay cho phép người dùng chọn đường dẫn/SQL.

Reader yêu cầu SHA256 manifest được pin từ cấu hình server đáng tin cậy, kiểm DB/hash/size, parity, contract và lineage nguồn, metadata, số dòng; mở SQLite mode=ro/query_only. Kiểm lại hash sau đọc và từ chối WAL/journal đang hoạt động, partial build hoặc artifact bị thay. Pin không phải chữ ký: ai có quyền thay cả file lẫn cấu hình server vẫn có thể thay nguồn; tool không tự cấp xác thực HTTP hoặc quyền filesystem.

Quyền được kiểm bằng principal_role của caller trước reader I/O. Khách và role không biết bị chặn; SQL/path/role/source_id trong arguments bị từ chối. Chưa cấu hình reader thì báo thiếu cấu hình, không tự rơi về DB backend hoặc scenario khác. Constructor mới là tham số keyword tùy chọn; app mặc định/nguồn finance cũ/frontend/backend auth không đổi.

Smoke deterministic 6/6 ca đạt, kết quả lưu result.json và summary.json: đúng 67 SKU,1748 dòng sổ,99 khoản chi,24455 snapshot; ngày có giao dịch 2025-10-01..2026-09-30; sales completeness vẫn unverified. Một lượt admin đọc tại máy này mất0,0341giây, không phải SLA/benchmark tải hoặc tốc độ hội thoại LLM. Không gọi model hay dùng output sai làm nhãn.

17 test reader mới và11test tool cũ:28PASS16,29s. Có giả mạo role/SQL/path, chưa cấu hình, thay DB/parity/contract/manifest, đổi metadata nhãn dù cấp pin mới, đổi gate sang nguồn khác, active WAL, partial build và thay artifact trong lúc đọc. Raw/staging/reconciliation/eligibility/curated cũ được giữ nguyên; các test lỗi chỉ sửa fixture tạm.

Toàn bộ suite **321 test PASS128,85s**, log `AI/runtime/tests-curated-reader-r1.log`. Không chạy quality/history/model batch, GPU/embedding, fine-tune/Colab, tải model, deploy hoặc sửa frontend/config/mode.

Phạm vi tích hợp hiện tại là tool API opt-in: caller đã có thể gọi đúng tên tool với principal_role server. Planner hội thoại admin chưa có intent `data_quality`; chưa tuyên bố người dùng hỏi tự nhiên đã đi qua nhánh này hoặc chất lượng trả lời LLM tăng. Bước tiếp có căn cứ là nối intent/context và đánh giá hội thoại riêng trước khi bật. CSV/Excel mapping, số đơn từ curated và DS/backtest còn thiếu; không đếm dòng sổ thay số đơn.
