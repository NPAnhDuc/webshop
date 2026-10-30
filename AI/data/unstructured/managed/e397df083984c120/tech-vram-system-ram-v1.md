# VRAM khác RAM máy tính ở đâu?

VRAM (bộ nhớ đồ họa, frame buffer) là bộ nhớ tốc độ cao nằm trên card đồ họa, phục vụ GPU xử lý và hiển thị hình ảnh. RAM máy tính (bộ nhớ hệ thống) là bộ nhớ chung của máy. Theo NVIDIA, khi dữ liệu không có trong bộ nhớ đệm của GPU, GPU lấy từ VRAM; nếu VRAM không có, GPU phải lấy từ bộ nhớ hệ thống ở xa hơn, và mỗi lần đọc ghi xa hơn làm chậm và tốn điện hơn.

Với đồ họa tích hợp Intel, Intel cho biết GPU không có bộ nhớ riêng mà dùng bộ nhớ chia sẻ được cấp phát tự động; vì vậy dung lượng RAM của máy không phải VRAM riêng.

NVIDIA lưu ý chỉ số "VRAM đang dùng" trên công cụ hiển thị không hoàn toàn chính xác: game thường giữ trước VRAM, không có nghĩa thực sự cần hết. Không đổi dung lượng RAM thành VRAM hay ngược lại khi tư vấn.

Nguồn: https://www.nvidia.com/en-in/geforce/news/rtx-40-series-vram-video-memory-explained/ ; https://www.intel.com/content/www/us/en/support/articles/000041253/graphics.html (Intel Support 000041253, ngày rà soát trên trang 23/05/2025)

Đối chiếu: 24/10/2026. Tài liệu tham khảo bên ngoài; không phải chính sách hoặc cam kết của shop.