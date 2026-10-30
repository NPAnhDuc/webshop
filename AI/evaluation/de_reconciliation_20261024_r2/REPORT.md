# Đối soát raw: nhập, bán, hoàn, tồn và FIFO

Ngày24/10/2026 giờ địa phương. Đọc bản raw đã có `AI/data/de_pipeline/retail_sim_v1/revision_20261023_1607`, không tạo capture mới hoặc sửa nguồn.

## Kết quả

58/58 kiểm tra qua trên dữ liệu mô phỏng. Đã đối soát2.126 chuyển động kho với24.455 snapshot tồn theo ngày,67SKU. Phương trình giá vốn khớp:

```text
Tồn đầu:             1.502.710.000 VND
+ Hàng đã nhận:     11.767.250.000 VND
− Giá vốn thuần:    11.615.510.000 VND
= Tồn cuối:          1.654.450.000 VND
Số đơn vị tồn cuối:            312
```

Bốn tổng tiền khớp độc lập với validation_report scenario cũ. Raw và source vẫn có SHA256 `f544a0a0255d78a06f01833275170a6f2eda89f2c9053a923433e420ca365028`; validation_report cũ, raw/staging manifest và nguồn bot không đổi. Không ghép35đơn backend vào1427đơn scenario.

15test đối soátPASS16,10giây; toàn bộ284testPASS82,97giây. Log `AI/runtime/tests-de-reconciliation-r2.log`. Không cần model/GPU hoặc embedding vì mọi kiểm tra đều là SQL/Python có thể tái lập.

## Đã kiểm tra

- Schema, kiểu dữ liệu, ngày, ID trùng và SKU lạ cho mua/nhận/chuyển động/tồn.
- Phiếu nhận phải khớp dòng đặt mua và không nhận vượt số lượng; không áp giả định phải nhận đúng ngày dự kiến hoặc nhận toàn bộ một lần.
- Chuyển động bán/nhận/hoàn phải khớp chứng từ về ngày, SKU, số lượng và giá vốn. Hoàn không nhập lại không làm tăng tồn hoặc đảo giá vốn.
- Replay FIFO độc lập bằng hàng đợi lô, kiểm giá vốn xuất và tồn âm ngay trong ngày. Tái sử dụng thuật toán từ validator scenario hiện có, tách khỏi phần ghi report vào source.
- Từng snapshot ngày khớp replay; kiểm độ phủ theo kỳ inventory được khai báo và khóa(day,SKU), không điền ngày thiếu thành0.
- Số tồn hiện tại khớp replay; bảo toàn giá vốn đầu+nhận−COGS=cuối. Opening phải nằm đúng đầu kỳ, không cho đổi nhãn tăng tồn giữa kỳ thành vốn đầu.

Test gồm trường hợp phương trình tổng vẫn cân nhưng giá vốn không đúng FIFO, ngày snapshot bị thiếu, receipt sai giá, receipt/movement thiếu, tồn âm, trùng phiếu, hoàn không nhập lại và dữ liệu đầu vào bị sửa. Fixture ba ngày chứng minh không ép nguồn khác thành365ngày hoặc chính sách hoàn14ngày của simulator.

## Lineage và trạng thái

`reconcile_revision` xác minh raw hash và staging hash, yêu cầu staging auditPASS rồi mới chạy. Kết quả ghi vào thư mục mới, không ghi đè raw/staging/report cũ. Manifest liên kết source_id, raw manifest, staging manifest và report đối soát. CLI giữ shared runner.lock. R1 với57check trước guard ngày opening được giữ riêng; R2 là bản chốt58check và có code_snapshot.

Status=`reconciled_pending_curated_design`; `curated_published=false`. Kết quả này chưa tự thay cơ sở dữ liệu đang phục vụ chatbot và chưa cấp quyền truy cập cho người mua.

## Giới hạn và bước tiếp

FIFO hiện dùng đơn giá nguyên, một chuyển động cho mỗi chứng từ và thứ tự intraday(day,id). Hàng hoàn nhập lại được thêm thành lô mới theo giá vốn đảo. Chưa suy timestamp thiếu hoặc hỗ trợ mọi kiểu điều chỉnh kho; trường hợp ngoài hợp đồng phải đối soát, không được tự sửa.

Chưa kiểm tiền tệ, thuế, quyền dùng dữ liệu hoặc chính sách thương mại; chưa có CSV/Excel mapping, curated publication, tool DE trong hội thoại hoặc thay mode/frontend. Độ phủ inventory không chứng minh đủ toàn bộ dữ liệu bán hay nhu cầu thực. Các số trên là mô phỏng, không phải hoạt động thực của shop.

Bước tiếp là thiết kế curated có hợp đồng nguồn/tiền tệ/kỳ/grain và lineage, chỉ phát hành revision mới sau các gate; không bật nguồn mới mặc định hoặc gộp dataset khác. Mapping Excel/CSV và baseline dự báo nằm ở các bước sau. Không dùng bank/gold/evaluation_only làm tri thức hoặc train, không fine-tune/Colab/HyDE hay tải model trong lượt này.
