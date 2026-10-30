# Báo cáo dự án ShopBot đến 20/10/2026

Mốc báo cáo bên dưới được lập trước lượt rà lại RAG trong cùng ngày. Bản cập nhật mới nhất đã được bật trên web: [cải thiện RAG, kiểm thử và giới hạn](evaluation/rag_v1/REPORT.md). Điểm mới: 32/32 ca phát triển, 14/16 ca giữ riêng, 7/7 ca tích hợp hội thoại; tổng hợp trích xuất nhiều nguồn và đối chiếu kế hoạch admin. Các hạn chế của mốc cũ cần đọc cùng bản cập nhật này.

## Trạng thái chung

Đã có chatbot thử nghiệm local chạy bằng Ollama và Streamlit, phục vụ người mua và chủ shop. Có SQL tính số liệu, RAG tìm tài liệu, bộ nhớ trong phiên, biểu đồ và kiểm tra quyền. Chưa phải hệ thống hoàn chỉnh để giao khách hoặc vận hành doanh nghiệp thật. Toàn bộ doanh thu, giá bán, giá vốn và tồn kho trong kịch bản đang dùng là mô phỏng.

Lúc lập báo cáo, Streamlit 8501, Ollama 11435 và embedding 8011 đều phản hồi HTTP 200. Mở: http://127.0.0.1:8501/. Khởi chạy lại bằng `start-local.ps1` trong thư mục AI.

## Công việc từ đầu dự án

1. Đọc yêu cầu trong `documnets/ke-hoach-ba-chatbot-shop-dien-tu.md`, tham khảo công cụ, bộ nhớ và RAG trong `D:/Chatbot/Ai-agent-book`. Thu gọn theo yêu cầu thành một shop, 67 sản phẩm, 12 tháng; chưa đạt quy mô nhiều shop của đặc tả gốc.
2. Clone Kev, LangGraph và pc-part-dataset vào `AI/references/`. Giữ thí nghiệm và checkpoint riêng, không tự coi repo clone về là chức năng đã tích hợp.
3. Tách dữ liệu có cấu trúc và tài liệu phi cấu trúc. Theo manifest, đã tải 10 nguồn dữ liệu có cấu trúc gồm REES46, lịch sử mua điện tử, đa danh mục, laptop, eBay, Olist, UCI và giao dịch có kho/coupon. Tổng kích thước file nguồn khai báo khoảng 15,26 GB; không phải lượng dữ liệu đang nạp hết vào chatbot. Một URL dữ liệu giao dịch không tải được, có lưu lỗi.
4. Với 15 nguồn tài liệu chiến lược/kế hoạch đã theo dõi, tải được 12, còn 3 chưa tải được. Chúng là tài liệu tham khảo bên ngoài, còn chờ duyệt; không được coi là chính sách shop hoặc tự động nạp toàn bộ vào RAG vận hành.
5. Chọn 67 sản phẩm thay cho toàn bộ danh mục lớn: 19 laptop và 48 linh kiện/phụ kiện. Có nguồn và thuộc tính gốc; chưa có chứng cứ rằng tất cả là sản phẩm bán chạy nhất thị trường. Chuyển thành SQLite và SQL riêng tại `data/product_sql/`.
6. Tải và đối chiếu ảnh theo tên model cho 37/67 sản phẩm, có gallery tại `data/product_images/gallery.html`. Còn 30 sản phẩm chưa có ảnh. Ảnh đã kiểm tra ngoại hình model, chưa xác minh chính xác mọi biến thể SKU hoặc quyền sử dụng thương mại.
7. Dựng kịch bản kinh doanh đủ 365 ngày, 01/10/2025–30/09/2026, cùng mã sản phẩm ở danh mục, nhập, bán, hoàn và tồn. Có SQL dump, CSV, giả định và báo cáo đối soát.
8. Dựng Streamlit, Ollama portable, embedding tiếng Việt, LangGraph, công cụ chỉ đọc, phân quyền, xử lý tài liệu, biểu đồ và các phiên bản notebook Colab.
9. Hỏi thử nhiều lượt bằng model thật, chấm FAIL khi không hoàn thành yêu cầu, sửa thời gian/ngữ cảnh/bộ lọc/SQL và giữ nguyên các lượt thử bị loại để đối chiếu.

## Dữ liệu shop đang dùng

| Hạng mục | Số lượng |
|---|---:|
| Sản phẩm | 67 |
| Đơn bán | 1.427 |
| Dòng chi tiết bán | 1.717 |
| Đơn đặt nhập | 320 |
| Dòng nhận hàng | 317 |
| Lượt hoàn | 31 |
| Bản ghi tồn kho theo ngày | 24.455 |
| Khoản chi vận hành | 99 |

Đối soát qua 41 kiểm tra, không có mã sản phẩm ngoài danh mục; cả 67 mã đều có giao dịch. Có FIFO, hoàn hàng và tồn đầu/cuối kỳ. Database: `data/business_sql/scenario_v1/shop.sqlite`.

Các số sau **chỉ mô tả kịch bản giả lập**, không phải doanh thu thật hay khảo sát thị trường:

- Doanh thu thuần năm: 13.495.418.000 đồng; bình quân khoảng 1,125 tỷ đồng/tháng.
- Doanh thu tháng dao động 609.442.000–1.493.219.000 đồng.
- Lợi nhuận gộp năm: 1.879.908.000 đồng.
- Lợi nhuận hoạt động trước lãi vay và thuế: 487.858.402 đồng.
- Có tháng lỗ; không ép dữ liệu luôn có lời. Chưa có thuế/lãi vay để tính lợi nhuận ròng sau thuế.

Có 22 tài liệu shop mô phỏng đã duyệt cho thử nghiệm và 4 bản nháp bị loại khỏi RAG: kế hoạch, mục tiêu, marketing, giá, mua hàng và định vị. Chính sách bảo hành/đổi trả/trả góp chưa đủ điều khoản để trả lời như chính sách thật.

## Chatbot hiện làm được gì

| Nhóm | Khả năng hiện có | Ví dụ |
|---|---|---|
| Tư vấn sản phẩm | Lọc laptop theo ngân sách, ưu tiên màn hình/pin; đọc giá và tồn mô phỏng | Laptop dưới 20 triệu |
| Thông số | Trả CPU/GPU từ bản ghi nguồn của model có dữ liệu | Lenovo LOQ Gaming 15IRH8 dùng chip gì? |
| Tài liệu | Tìm và trích đoạn có nguồn; lọc vai trò, hiệu lực, phiên bản, trạng thái duyệt | Chính sách giảm giá quy định gì? |
| Tổng hợp kinh doanh | Doanh thu, giá vốn, lãi gộp, chi phí và lãi hoạt động theo kỳ | Phân tích kinh doanh quý 3 năm 2026 |
| Giao dịch | Đếm đơn, tiền hoàn, giá trị hàng nhận từ nhà cung cấp, doanh thu từng kênh | Tiền hoàn cho khách tháng 7/2026? |
| Xếp hạng | Top SKU theo lượng bán ròng, doanh thu hoặc lãi gộp; lọc ngành hàng và giữ đồng hạng cao nhất | Top 3 laptop theo doanh thu tháng 9/2026 |
| So sánh | So hai kỳ về doanh thu/lãi gộp, chênh lệch tiền và phần trăm | So doanh thu quý 3 với quý 2 năm 2026 |
| Tồn kho | Đọc ảnh chụp tồn theo ngày khi có dữ liệu | Tồn kho cuối tháng 9/2026 |
| Trực quan | Biểu đồ doanh thu/lãi gộp, xu hướng theo tháng, sơ đồ lời/lỗ, tải ảnh PNG | Vẽ sơ đồ báo cáo quý 3 năm 2026 |
| Kế hoạch | Đề xuất có điều kiện dựa trên tháng/quý trước, SKU đóng góp và tài liệu; hỏi mục tiêu/ngân sách còn thiếu | Dựa tháng trước, đề xuất hướng kinh doanh tháng tới |
| Hội thoại | Giữ kỳ, tiêu chí, nhóm, số mã và tối đa 6 lượt gần nhất; hỏi lại khi thiếu kỳ/ngữ cảnh | Tháng đó món nào bán chạy? Rồi đổi sang doanh thu |
| Phân quyền | Người mua không được truy cập số liệu nội bộ; công cụ chỉ đọc | Khách xin giá vốn phải bị từ chối |

Các ví dụ thể hiện chức năng đã có, không bảo đảm mọi cách diễn đạt đều đúng. Bộ câu mới vẫn tìm thấy lỗi nhầm doanh số/số chiếc, mất bộ lọc RAM, số lượng top và chọn sai công cụ cho một số câu hỏi lãi gộp.

## Kiến trúc và model đang chọn

Luồng chính: câu hỏi + bộ nhớ → Qwen lập kế hoạch → kiểm tra quyền/lịch → SQL hoặc RAG → câu trả lời có số liệu/nguồn → cập nhật bộ nhớ.

- Ollama: Qwen3-4B-Instruct-2507 Q4_K_M, local trên RTX 2060. Chưa fine-tune trọng số Qwen.
- Embedding: `dangvantuan/vietnamese-embedding`, nền PhoBERT, PyVi, 768 chiều, giới hạn thực tế 256 token, chạy CPU.
- RAG: chia theo heading/đoạn/câu; bảng dài tách dòng và lặp header; embedding kết hợp TF-IDF bằng RRF. Đây là chia có xét cấu trúc, chưa phải model học riêng ranh giới ngữ nghĩa. Chưa có reranker.
- Kev đã có repo, model và thí nghiệm LoRA; không bật mặc định. Adapter hội thoại PhoBERT v3 cũng không được dùng để quyết định mặc định sau khi audit rộng cho thấy phạm vi phân loại chưa đủ.
- Công cụ tính tiền không chạy SQL/Python do model tự sinh. Số liệu truy vấn từ database, không học thuộc doanh thu trong trọng số.
- Bộ nhớ chỉ trong phiên, chưa xuyên thiết bị/tài khoản lâu dài. Giao diện frontend/backend hiện có chưa tích hợp đầy đủ với trợ lý Streamlit.

## Đã train những gì trên Colab

| Thành phần | Kết quả đã kiểm chứng | Trạng thái sử dụng |
|---|---|---|
| Retriever E5 | Có train 3 epochs; validation không tốt hơn baseline | Giữ baseline; hiện tìm tài liệu bằng embedding tiếng Việt |
| Kev LoRA pilot | Đã train; đúng 36/36 câu test tổng hợp nhỏ | Thử nghiệm, không bật mặc định |
| Dự báo nhu cầu | Gradient boosting dự báo số chiếc bán gộp ngày kế tiếp; test WAPE 43,68%, baseline tuần 59,54% | Chưa triển khai; không phải dự báo doanh thu dài hạn hay nhu cầu khi hết hàng |
| PhoBERT hội thoại v3 | 2.676 mẫu, 4 epochs, 440 bước, khoảng 135,9 giây trên T4; validation 93,53%, test tổng hợp 464/464 | Checkpoint đã tải/kiểm hash; giữ đối chiếu, không dùng mặc định |
| Metric v4 mới nhất | Đóng gói 4.280 mẫu: 3.520 train, 380 validation, 380 test; học đầu phân loại trên embedding đóng băng, chạy Colab CPU do hết hạn mức GPU | Đã thấy file ZIP được sinh trên Colab; chưa lấy và kiểm chứng báo cáo/trọng số, chưa kích hoạt |

Phiên Colab tiếp tục có lỗi tải JavaScript/reCAPTCHA và hạn mức GPU khi kiểm tra ngày 20/10. Không có điểm số v4 được xác nhận, không tuyên bố bản mới đã cải thiện chatbot. Các điểm 100% trên bộ tổng hợp nhỏ không phải độ chính xác với khách thật.

## Kết quả kiểm thử chatbot

| Bộ kiểm tra | Kết quả đã xác nhận | Ý nghĩa |
|---|---|---|
| Unit/integration | 100 bài qua | Hợp đồng công cụ, dữ liệu, quyền, lịch, bộ nhớ, báo cáo và bộ chấm; không phải 100 câu hỏi người dùng |
| Đối soát dữ liệu FIFO | 41/41 kiểm tra | Nhất quán dữ liệu mô phỏng; không chứng minh sát thị trường |
| Công cụ SQL v2 | 96/96 ca | Phép tính/công cụ; không đo toàn bộ model |
| Bộ hội thoại chính | 69/106 → 93/106 PASS | 24 câu được sửa, không hồi quy trong lượt chọn bản |
| Câu bổ sung | 10/12 PASS | Vẫn còn nhầm tiêu chí và lỗi kéo theo trong hội thoại |
| Cách hỏi mới | 32/40 PASS | Đã sửa lỗi bộ chấm coi category=all là ngành hàng; giữ nguyên kết quả thô và bản rà soát |

158 câu model thật hiện có tổng 135 PASS / 23 FAIL, thuộc các bộ phát triển khác nhau. Đây không phải ước lượng chất lượng production. Chưa chạy đủ 158 câu với trọng số metric v4 mới. Thử thêm few-shot từng đạt 12/12 câu nhỏ nhưng làm bộ chính giảm xuống 92/106 nên bị loại.

## Phần chưa hoàn thành

- Chưa hiểu đúng mọi cách nói hoặc nhớ ngữ cảnh hoàn toàn ổn định.
- Chưa có dữ liệu shop thật và điều khoản shop được chủ shop phê duyệt đầy đủ. Không tự lấy chính sách hãng/chuỗi khác làm chính sách shop.
- Chưa xuất Excel từ yêu cầu chat; hiện có bảng và ảnh PNG.
- Chưa có RFM hoàn chỉnh; chưa xác minh tương thích Build PC đầy đủ.
- Chưa có dự báo doanh thu tháng tới kèm khoảng dự báo 95% đã kiểm định; chưa chứng minh tác động nhân quả của quảng cáo.
- Chưa có thuế, lãi vay hoặc giao dịch tương lai để trả các câu đó.
- Pipeline cập nhật tháng đã có cơ chế kiểm tra lô, phiên bản và snapshot cho dữ liệu phù hợp, nhưng bộ FIFO hiện tại chưa nhận định dạng lô demo cũ. Chưa có tự cào web tuần/tháng vận hành hoàn chỉnh. Upload tài liệu không tự huấn luyện lại trọng số.
- Chưa có trí nhớ lâu dài theo người dùng, đặt hàng/chuyển nhân viên thực tế, tự nhập hàng/đổi giá.
- Chưa tích hợp hoàn chỉnh với frontend/backend, chưa đóng gói Docker và triển khai công khai.

## Đường dẫn bàn giao

- Web và hướng dẫn: `AI/README.md`, `AI/start-local.ps1`.
- Danh mục: `AI/data/structured/processed/product_catalog.jsonl`.
- SQL sản phẩm riêng: `AI/data/product_sql/`.
- Kinh doanh và tài liệu mô phỏng: `AI/data/business_sql/scenario_v1/`.
- Nguồn tải về: `AI/data/structured/raw/`, `AI/data/unstructured/reference/`.
- Ảnh: `AI/data/product_images/`.
- Báo cáo cải thiện: `AI/training/conversation_v3/IMPROVEMENT_REPORT.md`.
- Train mới và trạng thái: `AI/training/metric_v4/`.

Ưu tiên tiếp theo: lấy và kiểm chứng artifact v4; chạy đủ hồi quy; sửa các lỗi hiểu câu và bộ nhớ còn lại; bổ sung Excel/RFM bằng công cụ có đối soát; hoàn thiện nhập dữ liệu thật và tích hợp web trước Docker/triển khai.
