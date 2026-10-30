# Gia sư RAG và huấn luyện Colab

## Đang huấn luyện gì?

1. Encoder `intfloat/multilingual-e5-small`: điều chỉnh trọng số để ghép câu hỏi với đúng đoạn dữ liệu sản phẩm. Đây là phần có huấn luyện trọng số trong RAG.
2. Kev 0.8B: fine-tune từ checkpoint phát hành để chọn `products/documents/handoff/clarify` cho câu hỏi tiếng Việt.

Chưa fine-tune Qwen sinh văn bản, chưa nối artifact mới vào frontend/backend, chưa tự triển khai model. Việc thêm tài liệu hàng tháng vẫn là nhập dữ liệu/lập chỉ mục, không cần train mỗi lần.

## Dữ liệu pilot

- 37 sản phẩm có nguồn, 1.099 câu hỏi: train 809, validation 98, test 192.
- 219 câu định tuyến, 73 nhóm ý nghĩa: train 147, validation 36, test 36.
- Câu hỏi sinh bằng khung có nhãn, không phải 1.099 câu hỏi độc lập từ khách thật. Tách nhóm theo sản phẩm/ý nghĩa trước khi tạo biến thể.
- Giá shop, giá vốn, tồn kho chưa biết có đáp án từ chối bịa. Không đưa chúng vào loss truy xuất.
- Gói Colab không có `.env`, dữ liệu khách, toàn bộ `backend/data`, ảnh, hoặc nội dung đầy đủ báo cáo bên thứ ba.

## Chạy

Mở `ShopBot_Tutor_Colab.ipynb` trong Google Colab, chọn GPU T4, chạy lần lượt. Notebook chứa sẵn bộ dữ liệu và mã Python dưới dạng payload nén; không cần cung cấp API key.

Nếu trình duyệt không cho tải notebook lên, `launcher.html` cung cấp mã tương đương để dán vào một ô mã Colab. `colab_run_all.py` là bản mã thuần.

Colab đang dùng Python 3.13; Kev yêu cầu Python 3.12/3.13 và Torch dưới 2.9. Notebook tạo môi trường Python 3.12 riêng cho Kev để không thay Torch của kernel. Thời gian cài và GPU được cấp phụ thuộc Colab.

## Vòng gia sư

Hỏi → truy xuất → đối chiếu đúng nguồn → phân loại lỗi → đề xuất sửa có dẫn chứng → duyệt → chạy lại phiên huấn luyện mới. Lỗi có thể do thiếu tài liệu, chia đoạn, định tuyến, lấy nhầm nguồn hoặc câu hỏi vượt dữ liệu. Không mặc định mọi lỗi đều cần fine-tune.

`outputs/retriever/tutor-review-queue.json` chứa lỗi validation để phân tích. Không chép các ví dụ validation/test vào train. Muốn thêm bài tập train phải dùng nhóm nguồn dành cho train hoặc tạo nhóm mới rồi chốt lại phiên bản bộ kiểm thử.

`review_corrections.py` kiểm tra bài sửa do gia sư duyệt: phải có người duyệt, câu trích nguyên văn, giá trị khớp nguồn và thuộc nhóm train. Tạo file `data/qa-train-corrections.jsonl` riêng; chưa tự nạp vào phiên đã chạy. Cần tạo phiên dữ liệu mới, hợp nhất các dòng được duyệt vào train và chạy kiểm thử lại trước lượt train kế tiếp. Script từ chối bịa trường thiếu và từ chối chuyển nhóm validation/test sang train.

Điểm retrieval recall@1/3 chỉ đo lấy đúng tài liệu, không phải độ chính xác toàn bộ chatbot. Dữ liệu hiện thiên về thông số sản phẩm; cần bổ sung câu hỏi chiến lược từ tài liệu được kiểm chứng và câu hỏi thật trước khi kết luận chất lượng toàn hệ thống.

## Artifact

- `outputs/retriever/last-trained`: encoder sau train.
- `outputs/retriever/candidate`: encoder được chọn theo validation; có thể vẫn là baseline nếu fine-tune không cải thiện.
- `outputs/retriever/*validation.json`, `frozen-candidate-test.json`: kết quả truy xuất.
- `outputs/kev/trained`: adapter/head Kev sau fine-tune.
- `outputs/kev/*/report.json`: đánh giá Kev trước/sau.
- File ZIP tải về cuối phiên để giữ kết quả khi Colab ngắt. LoRA Kev phiên bản đang dùng không hỗ trợ resume giữa lượt; nó lưu checkpoint cuối lượt.

Kiểm tra dữ liệu tại máy: `.\.venv\Scripts\python.exe training/test_tutor_pack.py` từ thư mục AI.

## Kết quả lượt đầu trên Colab T4

Đã xác nhận encoder chạy GPU và train đủ 3 epoch. Loss lần lượt 0,9184 / 0,5028 / 0,2446. Validation retrieval recall@1 bằng 1,0 ở cả baseline và sau train; bản được chọn vẫn là baseline. Test gồm 174 câu có nguồn cho retrieval, recall@1 bằng 1,0. Đây là bộ câu hỏi theo khung khá dễ; không phải độ chính xác trả lời hoặc kết quả trên câu hỏi thật.

TF-IDF cơ bản cũng đạt recall@1 bằng 1,0 trên cùng bộ thử, cho thấy chưa có bằng chứng cần thay bộ truy xuất ở bộ dữ liệu này. Báo cáo nằm trong `results/lexical-baseline.json` và bản ghi đầu ra Colab `results/retriever-visible-summary.json`.

Trạng thái Kev và tải checkpoint cần xem `colab-run.json`: giao diện Colab đã báo lỗi tải JavaScript/phiên Google sau khi encoder hoàn tất. Chưa có bằng chứng Kev train xong hoặc artifact đã tải về máy. Không đánh dấu toàn bộ pipeline hoàn thành khi chưa kiểm chứng các phần này.
