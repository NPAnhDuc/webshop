# Dữ liệu số và tri thức theo tháng

Hai thư mục chính:

```text
AI/data/structured/
  raw/uci_online_retail_ii/     # nguồn công khai + manifest/hash
  shop.db                      # database đang dùng (hiện là demo)
  monthly/YYYY-MM/shop.json    # lô tháng được kiểm tra trước khi nạp
  snapshots/YYYY-MM/           # snapshot trước mỗi phiên bản báo cáo
  training/routing-seeds/      # seed, chưa dùng train
AI/data/unstructured/
  public/                      # tài liệu nền công khai
  admin/                       # tài liệu nền nội bộ
  reference/sba/               # tham khảo bên ngoài, admin-only
  monthly/YYYY-MM/             # tài liệu và manifest phiên bản
  generated/YYYY-MM/           # báo cáo tính từ SQL, admin-only
```

## Dùng trên Streamlit

Đăng nhập **Chủ shop**, mở **Dữ liệu và tri thức theo tháng**. Chọn tháng, tải lô JSON hoặc tài liệu, nhập metadata và duyệt tài liệu. Bấm **Cập nhật dữ liệu và tri thức tháng này** để chạy ngay. Nếu không bấm, worker cũng kiểm tra mỗi 60 giây khi hệ thống đang chạy.

Bản nháp không vào chatbot. Tài liệu mới hơn dùng cùng `document_id` và tăng `version`; không sửa đè phiên bản đã duyệt. Khi cập nhật tài liệu nền demo, mã tương ứng là `chinh-sach-mau` hoặc `chien-luoc-mau`. Chọn đúng người được đọc. Tài liệu tham khảo SBA không được coi là chính sách shop.

## Lô số liệu

```json
{
  "ready": true,
  "complete": true,
  "data_kind": "shop",
  "month": "2026-09",
  "inventory_as_of": "2026-09-30",
  "products": [
    {"sku":"SKU-001","name":"Tên máy","price":20000000,"stock":5,"panel":"OLED","ram":16,"battery":70,"weight":1.4,"category":"laptop"}
  ],
  "sales": [
    {"id":"invoice-line-001","day":"2026-09-01","sku":"SKU-001","quantity":1,"revenue":20000000,"cost":18000000}
  ]
}
```

Đây là **cấu trúc minh họa**, không phải dữ liệu thực. `demo` chỉ nạp vào database demo; `shop` chỉ nạp vào database thật. Giá VND nguyên; RAM GB, pin Wh, trọng lượng kg. `id` duy nhất cho từng dòng hóa đơn qua mọi tháng. Doanh thu/giá vốn là tổng dòng. Chưa hỗ trợ hoàn hàng số âm; lô đó bị từ chối để xử lý riêng. Không đưa thông tin nhận dạng khách hàng vào file.

Để bắt đầu dữ liệu thật, tạo database mới từ JSON đủ products/sales và `inventory_as_of`:

```powershell
.\.venv\Scripts\python.exe scripts\import_shop_data.py FILE.json --output data\structured\shop-v1.db
```

Đặt `SHOP_DATABASE=data/structured/shop-v1.db` trong `.env`, khởi động lại web **và worker**. Không trộn lô thật vào database demo. File ban đầu thiếu ngày tồn kho vẫn nhập được, nhưng cập nhật tháng không tự ghi đè giá/tồn cho đến khi nhập lại database có mốc tồn kho rõ ràng.

## Manifest tài liệu

Đặt `manifest-shop.json` cùng file tài liệu trong `unstructured/monthly/YYYY-MM/`:

```json
{
  "ready": true,
  "data_kind": "shop",
  "documents": [
    {"file":"bao-hanh.md","document_id":"bao-hanh","version":2,"audience":"customer","status":"approved","effective_from":"2026-10-01","effective_to":null}
  ]
}
```

`audience`: customer hoặc admin. `status`: approved hoặc draft. Định dạng: MD/TXT, PDF có chữ, DOCX; tối đa 10 MB mỗi tài liệu. PDF scan cần OCR ngoài quy trình hiện tại. Phiên bản mới cần giữ đúng mã tài liệu để thay bản cũ. Tài liệu hết hạn không làm bản trước tự hoạt động lại. Trong một workspace hiện quản lý một shop đang hoạt động.

## Chạy bằng lệnh

```powershell
.\.venv\Scripts\python.exe scripts\update_monthly.py --month 2026-09
.\.venv\Scripts\python.exe scripts\update_monthly.py --month 2026-10 --allow-current
.\.venv\Scripts\python.exe scripts\update_monthly.py --watch --refresh-references
```

Mặc định số liệu tháng hiện tại chờ chốt. `--allow-current` nạp có chủ đích và báo cáo sẽ ghi chưa đầy đủ. Tài liệu đã duyệt vẫn được kích hoạt theo ngày hiệu lực trong tháng hiện tại. Khi máy tắt, worker không chạy; khi mở lại, nó quét các tháng thiếu. Nếu không có đầu vào mới, không tự bịa số liệu. Phần làm mới nguồn tham khảo chỉ gọi các URL SBA được khai báo trong script, kiểm tra robots và giữ bản theo tháng.

Trạng thái, lỗi lô và chỉ mục: `runtime/monthly/`. Báo cáo/snapshot có phiên bản. Nạp lại cùng lô không cộng doanh thu lần hai; ID trùng nhưng nội dung khác làm cả lô bị từ chối. Số liệu cũ không ghi đè tồn kho mới hơn.

Đã chạy thử tháng 2026-09 của database demo: 210 dòng nhận diện trùng, 0 dòng cộng thêm; sinh báo cáo từ số liệu SQL có sẵn. Đây là cập nhật kho dữ liệu/tri thức, không phải huấn luyện trọng số Kev/Qwen.

`complete: true` là xác nhận đã chốt đủ số liệu tháng. Sang tháng mới không tự biến một lô đang nạp dở thành dữ liệu đầy đủ; lô thiếu xác nhận vẫn được ghi rõ chưa đầy đủ.
