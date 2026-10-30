# DE: kiểm tra nguồn sổ bán hàng trước phân tích

Ngày 23/10/2026. Đây là bước audit staging chỉ đọc, chưa phải pipeline nhập Excel hoặc phát hành dữ liệu curated.

## Đã thực hiện

Đã kiểm tra importer JSON và validator scenario hiện có. Importer chỉ nhận schema products/sales đơn giản; validator scenario có đối soát FIFO nhưng giả định bộ mô phỏng và ghi lại validation_report trong source. Không gọi validator đó để tránh ghi đè kết quả nguồn. Bổ sung module `shopbot/de_audit.py` và CLI `scripts/audit_ledger_source.py` cho audit độc lập, chỉ đọc.

Audit kiểm schema, kiểu số nguyên, NULL, ngày ISO hợp lệ, ID trùng, SKU lạ, phép tính dòng bán, dấu bán/hoàn, đối chiếu đơn–dòng bán–sổ, đối chiếu hoàn và tổng hoàn không vượt dòng bán, chi phí âm và dòng sổ không có chứng từ giải thích. Khi có lỗi, xuất mẫu quarantine có giới hạn và số vi phạm; không sửa/xóa/điền số0 hoặc loại outlier.

Nguồn SQLite và catalog có SHA256; source phải giữ nguyên trong audit. Database có WAL đang hoạt động bị từ chối để yêu cầu snapshot ổn định. CLI từ chối output revision đã tồn tại và chụp code triển khai trong `code_snapshot`. Không phát hành curated khi audit PASS.

## Kết quả trên nguồn hiện tại

- 32/32 kiểm tra qua, 0 mẫu lỗi.
- 67 SKU SQL khớp chính xác 67 ID catalog public.
- 1.427 đơn, 1.717 dòng bán, 31 lượt hoàn, 1.748 dòng sổ, 99 khoản chi.
- Khoảng ngày có bản ghi sổ: 01/10/2025–30/09/2026; không tự suy thành đầy đủ mọi ngày.
- Doanh thu thuần 13.495.418.000đ, giá vốn11.615.510.000đ, lãi gộp1.879.908.000đ; đối chiếu độc lập với manifest scenario hiện có khớp.
- SHA256 SQLite vẫn `f544a0a0255d78a06f01833275170a6f2eda89f2c9053a923433e420ca365028`. Không sửa DB, catalog, validation_report cũ hoặc ghép35đơn backend.

Tất cả giao dịch/giá/chi phí nêu trên là mô phỏng. PASS không chứng minh số liệu thị trường thật, chính sách hay tính đủ dữ liệu.

17 test audit/import qua trong10,04giây; toàn bộ261test PASS68,17giây, log `AI/runtime/tests-de-audit-r2.log`. Test có ngày không tồn tại, NULL, số lượng float, sai tiền, orphan ID/SKU, ID trùng, thiếu bảng, catalog khác, WAL hoạt động và nhiều lần hoàn riêng lẻ đúng nhưng tổng vượt đơn. Nguồn trong test được so byte trước/sau để xác nhận không tự sửa. Không cần gọi model/GPU hoặc embedding.

## Giới hạn và bước tiếp

Audit hiện hỗ trợ schema sổ SQL đã xác định. Chưa nhập CSV/Excel, chưa lưu raw snapshot bất biến, chưa mapping đơn vị/ngày từ file, chưa replay FIFO/đối soát nhận hàng–tồn, chưa kiểm thuế/tiền tệ/chính sách và chưa nối tool này vào hội thoại admin. `curated_published=false` có chủ ý.

Bước tiếp là đóng gói raw snapshot+manifest nguồn riêng, mapping và staging có quarantine, tái sử dụng đối soát FIFO hiện có theo cách không ghi đè nguồn, rồi mới phát hành curated revision và nối tool admin. Không dùng dữ liệu demo như dữ liệu shop thật; không ghép nguồn khác bằng cùng ID rồi coi là một bộ. Không cần fine-tune để tính hoặc làm sạch số.

Audit r1 giữ riêng kết quả kiểm31điều kiện trước khi bổ sung gate tổng hoàn; r2 là bản code và kết quả chốt trong lượt này. Không thay bank/gold/kết quả chatbot, mode/config hoặc frontend. Không dùng API trả phí, clone/download mới, deploy hay khởi động lại worker bị chặn.
