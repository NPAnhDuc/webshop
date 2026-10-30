# DE: chụp raw và kiểm tra staging theo revision

Ngày23/10/2026. Một bước tiếp nối audit nguồn, không thay router/model hay cấu hình ứng dụng.

## Kết quả

Đã tạo revision riêng tại `AI/data/de_pipeline/retail_sim_v1/revision_20261023_1607/`:

- `raw/ledger.sqlite`:6.303.744bytes; SHA256 `f544a0a0255d78a06f01833275170a6f2eda89f2c9053a923433e420ca365028`.
- `raw/catalog_public.json`:61.775bytes; SHA256 `b3f66fafadc77b5c4824ae9b0400af7a912fa217d3b6b872a074e44f4f2da743`.
- Hai file khớp byte với nguồn tại thời điểm kiểm tra. Có manifest nguồn, thời điểm, kích thước, hash, source_id và nhãn mô phỏng; code triển khai được chụp trong code_snapshot.
- Staging kiểm32điều kiện trên bản chụp, đều qua;0mẫu quarantine. Giữ67SKU,1427đơn,1717dòng bán,31lượt hoàn,1748dòng sổ và99khoản chi. Không ghép35đơn backend.
- Status=`audit_passed_pending_reconciliation`, `curated_published=false`. Đây chưa phải dữ liệu đủ điều kiện thay nguồn phân tích production.

21test snapshot/auditPASS15,45s; toàn bộ269testPASS72,15s. Log `AI/runtime/tests-de-snapshot-r1.log`. Không cần model/GPU hoặc embedding batch vì bước này là lưu/kiểm tra dữ liệu bằng code.

## Cơ chế

`shopbot/de_snapshot.py` chỉ nhận hai file được chỉ định, không copy đệ quy thư mục, tài liệu evaluation_only hay gold. Raw giữ đúng byte nguồn; không đổi tên SKU, tiền, ngày hay chép giao dịch nguồn khác vào cùng bộ.

Hash được so trước/sau copy và trước staging. Revision raw/staging đã tồn tại không bị ghi đè. Nguồn SQLite có WAL/journal đang hoạt động yêu cầu xuất snapshot ổn định trước. Khi copy lỗi hoặc nguồn đổi, giữ thư mục và dấu vết lỗi để kiểm tra; không có completion manifest hợp lệ để dùng tiếp.

Staging dùng bản raw, không quay lại nguồn sống. Manifest staging ghi hash raw manifest/audit/quarantine. Nếu raw đổi so manifest hoặc đường dẫn bị chuyển ra ngoài revision thì dừng. Đây là quy ước hash/no-overwrite của pipeline; không phải kho WORM hoặc chữ ký chống chủ máy cố ý sửa cả file lẫn manifest.

Các test kiểm nguồn sống đổi sau capture, raw bị sửa, manifest redirect đường dẫn, active WAL, copy gặp nguồn thay đổi, từ chối ghi đè và raw sai được giữ nguyên rồi quarantine. Không tự sửa/xóa/điền0 hay coi raw sai là dữ liệu sạch.

CLI để tạo revision mới:

```powershell
AI/.venv/Scripts/python.exe -X utf8 AI/scripts/capture_ledger_revision.py AI/data/business_sql/scenario_v1/shop.sqlite --catalog AI/data/agent_platform_20261023/catalog_v1/catalog_public.json --source-id retail_sim_v1 --output AI/data/de_pipeline/retail_sim_v1/REVISION_MOI
```

CLI giữ shared runner.lock để không chồng công việc với batch đang kiểm thử. Đường dẫn/source_id do người vận hành/server cấu hình; không đưa quyền chọn file máy chủ cho model hoặc khách hàng.

## Còn thiếu

Chưa có mapping CSV/Excel, đối soát FIFO/nhận hàng/tồn trên raw mới, cơ chế duyệt/phát hành curated, tool DE trong hội thoại admin hoặc endpoint web mới. Không thay nguồn SQL đang phục vụ bot. Không huấn luyện Kev/Colab, chạy HyDE, tải model, deploy hay khởi động lại worker bị chặn.

Bước sau ưu tiên đối soát nhập–xuất–hoàn–tồn và giá vốn trên bản raw đã chốt; tái dùng logic FIFO hiện có theo cách không ghi vào nguồn/validation_report cũ. Sau đó mới mapping/staging đầu vào khác và quy tắc phát hành curated có provenance. Các revision và kết quả cũ giữ nguyên.
