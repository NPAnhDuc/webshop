# Ổ SSD gần đầy có làm chậm máy không? Vì sao SSD cần chừa dung lượng trống?

SSD phải xóa khối dữ liệu cũ trước khi ghi lại, và xóa lâu hơn ghi. Để giữ tốc độ ghi, bộ điều khiển SSD chạy thu gom rác (garbage collection): gom các trang còn hợp lệ về một chỗ và xóa các khối chứa trang không còn dùng để tạo khối trống. Theo Samsung, việc này đôi khi làm chậm hiệu năng nếu thu gom rác xen vào lúc máy đang ghi; vì vậy SSD cần không gian trống để firmware hoạt động trơn tru.

Over-provisioning (OP) là phần dung lượng chỉ bộ điều khiển SSD dùng, máy tính không ghi vào được, giúp có sẵn khối trống khi thu gom rác và cân bằng hao mòn. Tăng OP giúp hiệu năng duy trì và tuổi thọ tốt hơn, đổi lại dung lượng người dùng ít hơn.

Tài liệu Samsung nói về SSD trung tâm dữ liệu; mức chậm thực tế khi ổ gần đầy phụ thuộc model, firmware và kiểu ghi. Không cam kết con số tốc độ cho một ổ cụ thể.

Nguồn: https://download.semiconductor.samsung.com/resources/white-paper/S190311-SAMSUNG-Memory-Over-Provisioning-White-paper.pdf ; https://download.semiconductor.samsung.com/resources/others/Samsung_SSD_845DC_04_Over-provisioning.pdf

Đối chiếu: 24/10/2026. Tài liệu tham khảo bên ngoài; không phải chính sách hoặc cam kết của shop.