# Kết quả triển khai router và hội thoại sản phẩm

Ngày 23/10/2026. Chế độ thử nghiệm `agent_tools`, không thay chế độ ứng dụng mặc định.

## Kết quả đã kiểm tra

36/36 lượt development đạt sau khi đọc nội dung, kiểm tra tham số, số liệu, danh mục, thứ tự SKU và hội thoại. Bộ này gồm 12 lượt hồi quy cũ và 24 lượt mở rộng đã lộ trong quá trình sửa; không phải validation độc lập hoặc bằng chứng độ chính xác tổng quát. Có các ca kiểm soát nhánh chưa kết nối và từ chối bộ lọc chưa hỗ trợ; chúng chỉ chứng minh xử lý trung thực.

232 unit/integration test qua trong 57,73 giây. Log: `AI/runtime/tests-agent-staged-r7.log`. Batch model giữ nguyên hash code, snapshot, SQL, bank/gold và config trong lúc chạy; `integrity.json` xác nhận 36 lượt. Snapshot nguồn code nằm ở `code_snapshot/`. Không chạy song song batch GPU.

Batch local Qwen3 4B đang nạp: tổng 25,529 giây, trung vị 0,6715 giây/lượt, p95 theo nearest-rank 1,391 giây. Đây là thời gian trong batch có cache/model đã nạp; chưa bao gồm cold start, backend production, tải đồng thời hoặc RAG. Không dùng các số này để hứa độ trễ production.

## Thay đổi

- Tách router nhận diện ý định khỏi bước trích điều kiện tìm kiếm. Không gửi cả catalog và câu trả lời cũ vào mọi bước định tuyến.
- Ngân sách, toán tử dưới/tối đa, số lượng, tên model và vị trí trong danh sách được kiểm tra bằng code trước khi gọi công cụ. Model không được tự tạo ngân sách hoặc chọn hai ID ngẫu nhiên.
- Danh mục đối chiếu với thực thể trong câu hỏi, giữ ngữ cảnh hãng/số lượng khi đổi ngân sách. RAM không bị biến thành laptop; điện thoại ngoài hợp đồng tool không bị thay bằng laptop.
- Cho phép khác biệt khoảng trắng trong trích đoạn điều kiện nhưng vẫn chặn điều kiện tự sinh. Điều kiện giá lặp lại chỉ được loại khỏi danh sách bộ lọc chưa hỗ trợ khi giá và toán tử khớp chính xác và không còn yêu cầu thông số khác.
- Thiếu ngân sách/đối tượng hoặc số lượng không hợp lệ thì hỏi lại. Giữ guard với OLED, RAM hoặc trọng lượng chưa được tool hỗ trợ. Không bỏ điều kiện rồi trả danh sách sai.
- Giá và bảng so sánh vẫn do công cụ dựng từ snapshot mô phỏng, không phải phép tính hoặc dữ kiện do model viết. Không tạo permalink giả, không gọi review mẫu là trải nghiệm thật.
- Lưu thông tin số token, `done_reason`, kích thước prompt và đầu ra từng call. Các round trước chỉ ra lỗi hiểu/trích slot, chưa có căn cứ gọi đó là lỗi thiếu tài liệu hoặc cắt context.

## Các round giữ riêng

| Round | Bộ development | Đạt ngữ nghĩa | Kết luận |
|---|---:|---:|---|
| r1 | 12 | 1 | Planner một lượt không đạt |
| r2 | 12 | 5 | Router tốt hơn, còn tự sinh số/đối tượng |
| r3 | 12 | 9 | Grounding số/ID, còn lỗi trích điều kiện |
| r4 | 12 | 10 | Còn điều kiện giá lặp và lược chủ ngữ |
| r5 | 12 | 12 | Qua bộ đã sửa, cần stress test |
| r6 | 24 câu mở rộng | 17 | Phát hiện lỗi danh mục và khoảng trắng |
| r7 | 12 + 24 | 36 | Qua hồi quy đã lộ, chưa nghiệm thu production |

Đếm theo action đơn thuần sẽ bỏ sót lỗi: r2 có câu trả danh sách nhưng dấu `<` sai; r6 tìm RAM lại gọi category laptop. `human_review.json` tách việc đọc ngữ nghĩa khỏi kiểm tra cơ học. Không thay đổi gold để nâng điểm.

## Giới hạn và bước tiếp theo

Đây là prototype opt-in, chưa nối phiên xác thực backend, API giá/tồn trực tiếp và permalink frontend. Nhánh tài liệu và hội thoại admin trong prototype vẫn thông báo chưa kết nối; tool tài chính/biểu đồ có từ bước trước nhưng chưa được router này gọi. Chưa có DE Excel ingest/đối soát đầy đủ, backtest DS, review có provenance hoặc HyDE ablation.

Bước tiếp theo ưu tiên nối hội thoại admin vào công cụ tài chính/biểu đồ theo kỳ, dùng số liệu SQL và nguồn rõ ràng; sau đó pipeline DE và DS theo ARCHITECTURE.md. Cần bank mới có ngữ cảnh nhiều lượt, phủ định, điều kiện hỗn hợp, tên model rút gọn, ngày/kỳ và quyền. Không mở validation RAG lịch sử để sửa agent này.

Đã tạo 36 nhãn ý định khởi đầu tại `AI/training/kev_agent_router_v1/seed_labels.jsonl`, có DATA_CARD về nguồn và giới hạn. Đây là development/train seed đã kiểm, thiếu độ phủ và cân bằng lớp; chưa đủ để đánh giá hay khởi chạy fine-tune Kev. Chưa train model/Colab, chưa tải model mới, chưa thay model/config. Không dùng câu trả lời sai làm tri thức huấn luyện. Worker embedding bị chặn trước đó không được retry hoặc tìm đường vòng.
