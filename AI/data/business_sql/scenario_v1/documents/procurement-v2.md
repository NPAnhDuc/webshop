# Quy trình nhập hàng

DỮ LIỆU MÔ PHỎNG — SHOP GIẢ LẬP retail_sim_v1. Không phải chính sách hay kết quả kinh doanh thật.

## Nhà cung cấp giả lập

Theo bảng suppliers: Nhà phân phối laptop giả lập SUP-LAP có lead time 4 ngày, SUP-PC 3 ngày (Nhà phân phối linh kiện giả lập). Đơn nhập chưa nhận không tính là tồn kho; lấy receipts làm ngày tăng tồn. Mức đặt lại trong simulator: laptop 1 sản phẩm, nhóm khác 3; đặt lên 4 laptop hoặc 8 linh kiện. Các ngưỡng này là giả định mô phỏng, chưa tối ưu thực tế.

## Hạch toán

Đơn bán xuất FIFO. Hoàn có thể nhập lại kho hoặc không; chỉ đảo giá vốn nếu hàng bán lại được. Không xác nhận tương thích Build PC khi nguồn thiếu socket/kích thước/điện năng.