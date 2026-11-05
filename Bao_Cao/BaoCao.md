<!-- trang-bia -->
TRƯỜNG: [Tên trường]
KHOA: [Tên khoa]

BÁO CÁO MÔN HỌC
KHO DỮ LIỆU VÀ KHAI PHÁ DỮ LIỆU

ĐỀ TÀI:
XÂY DỰNG CHATBOT TƯ VẤN BÁN HÀNG TECHSTORE
ỨNG DỤNG TRUY XUẤT THÔNG TIN LAI
VÀ PHÂN LỚP Ý ĐỊNH

Giảng viên hướng dẫn: [Họ tên giảng viên]
Sinh viên thực hiện: [Họ tên, mã sinh viên]
Lớp: [Tên lớp]

Năm 2026
<!-- het-trang-bia -->

# MỤC LỤC

<!-- muc-luc -->
- Danh mục từ viết tắt và thuật ngữ
- Lời mở đầu
- Chương 1. Tổng quan về kho dữ liệu và phương pháp khai phá dữ liệu
- Chương 2. Các phương pháp khai phá dữ liệu cùng nhánh với đề tài
- Chương 3. Ứng dụng vào chatbot TechStore
- Kết luận
- Tài liệu tham khảo
- Phụ lục
<!-- het-muc-luc -->

# DANH MỤC TỪ VIẾT TẮT VÀ THUẬT NGỮ

Bảng dưới đây giải thích các từ chuyên môn dùng trong báo cáo. Khi một từ xuất hiện lần đầu trong bài, báo cáo cũng giải thích ngắn ngay tại chỗ.

*Bảng 0.1. Từ viết tắt và thuật ngữ*

| Thuật ngữ | Viết đầy đủ | Giải thích dễ hiểu |
|---|---|---|
| CSDL | Cơ sở dữ liệu | Nơi lưu dữ liệu có cấu trúc, ví dụ các bảng đơn hàng, khách hàng. |
| OLTP | Online Transaction Processing | Hệ thống ghi giao dịch hằng ngày: tạo đơn, trừ kho, thanh toán. Ưu tiên ghi nhanh, đúng. |
| OLAP | Online Analytical Processing | Hệ thống phân tích: cộng dồn, so sánh, cắt lát dữ liệu lớn để ra báo cáo. Ưu tiên đọc nhanh. |
| DW | Data Warehouse (kho dữ liệu) | Nơi gom dữ liệu từ nhiều nguồn, làm sạch, giữ lịch sử, dùng để phân tích. |
| Data mart | Kho dữ liệu chủ đề | Một phần nhỏ của kho, phục vụ một phòng ban (bán hàng, kho, tài chính). |
| ETL | Extract – Transform – Load | Ba bước đưa dữ liệu vào kho: lấy ra, biến đổi cho sạch và thống nhất, nạp vào. |
| Fact table | Bảng sự kiện | Bảng ghi các con số đo được của nghiệp vụ, ví dụ số lượng bán, doanh thu. |
| Dimension table | Bảng chiều | Bảng mô tả ngữ cảnh của con số: ngày nào, sản phẩm gì, khách nào. |
| Grain | Độ mịn | Một dòng trong bảng sự kiện biểu diễn điều gì, ví dụ "một dòng = một sản phẩm trong một đơn". |
| Degenerate dimension | Chiều suy biến | Mã (ví dụ mã đơn hàng) nằm luôn trong bảng sự kiện, không cần bảng chiều riêng vì không có thuộc tính mô tả nào khác. |
| ROLAP / MOLAP / HOLAP | Relational / Multidimensional / Hybrid OLAP | Ba kiểu máy chủ OLAP: tính trên bảng quan hệ, tính trên khối dữ liệu dựng sẵn, hoặc kết hợp cả hai. |
| Medallion | Kiến trúc ba tầng đồng – bạc – vàng | Cách chia tầng dữ liệu: thô (bronze), đã kiểm tra (silver), đã tổng hợp để dùng (gold). |
| Support / Confidence / Lift | Độ hỗ trợ / độ tin cậy / độ nâng | Ba con số đo một luật kết hợp "mua A thì mua B": hay gặp đến đâu, chắc đến đâu, hơn ngẫu nhiên bao nhiêu lần. |
| Text-to-SQL | — | Hỏi bằng ngôn ngữ tự nhiên, máy tự viết câu SQL để lấy số liệu. |
| KDD | Knowledge Discovery in Databases | Toàn bộ quá trình đi từ dữ liệu thô đến tri thức dùng được. Khai phá dữ liệu là một bước trong đó. |
| CRISP-DM | Cross-Industry Standard Process for Data Mining | Quy trình chuẩn 6 giai đoạn để làm một dự án khai phá dữ liệu. |
| Khai phá văn bản | Text mining | Khai phá dữ liệu trên văn bản tự nhiên (câu hỏi, bài viết). |
| Truy xuất thông tin | Information Retrieval (IR) | Bài toán tìm ra tài liệu liên quan nhất với một câu hỏi, giống máy tìm kiếm. |
| Token | Đơn vị từ | Mảnh nhỏ nhất máy xử lý: một từ, một âm tiết hoặc một mảnh từ. |
| Chunking | Chia đoạn | Cắt tài liệu dài thành các đoạn ngắn để tìm kiếm và đưa vào mô hình. |
| TF-IDF | Term Frequency – Inverse Document Frequency | Cách cho điểm một từ: xuất hiện nhiều trong tài liệu này nhưng hiếm ở tài liệu khác thì điểm cao. |
| BM25 | Best Matching 25 | Công thức chấm điểm tài liệu theo từ khóa, cải tiến từ TF-IDF, dùng trong nhiều máy tìm kiếm. |
| Embedding | Vector nhúng | Dãy số (ví dụ 768 số) biểu diễn nghĩa của một câu. Hai câu cùng nghĩa có vector gần nhau. |
| Cosine | Độ tương tự cosine | Đo góc giữa hai vector. Góc càng nhỏ thì hai câu càng giống nghĩa. Giá trị từ −1 đến 1. |
| RRF | Reciprocal Rank Fusion | Cách trộn nhiều bảng xếp hạng thành một, chỉ dựa trên thứ hạng. |
| RAG | Retrieval-Augmented Generation | Mô hình ngôn ngữ trả lời dựa trên tài liệu tìm được, thay vì trả lời theo trí nhớ. |
| LLM | Large Language Model | Mô hình ngôn ngữ lớn, ví dụ Qwen, GPT. Đọc và sinh văn bản. |
| Fine-tune | Tinh chỉnh | Huấn luyện thêm một mô hình có sẵn trên dữ liệu riêng để nó làm tốt một việc cụ thể. |
| LoRA | Low-Rank Adaptation | Cách tinh chỉnh tiết kiệm: giữ nguyên mô hình gốc, chỉ học thêm hai ma trận nhỏ. |
| Router | Bộ định tuyến | Phần của chatbot quyết định câu hỏi đi đường nào: trả lời, hỏi lại, từ chối… |
| Intent | Ý định | Mục đích của câu hỏi, ví dụ "hỏi bảo hành", "muốn đặt hàng". |
| kNN | k-Nearest Neighbors | Thuật toán phân lớp: xem k điểm gần nhất thuộc nhãn nào nhiều nhất. |
| SVM | Support Vector Machine | Thuật toán phân lớp: tìm đường ranh giới cách xa hai nhóm nhất. |
| Precision | Độ chính xác | Trong các kết quả máy trả về, bao nhiêu phần đúng. |
| Recall | Độ phủ | Trong các kết quả đúng có thật, máy tìm được bao nhiêu phần. |
| F1 | F1-score | Trung bình điều hòa của precision và recall, một con số tóm tắt cả hai. |
| Macro-F1 / Micro-F1 | — | Macro-F1: tính F1 riêng từng nhãn rồi lấy trung bình, nhãn hiếm được tính ngang nhãn phổ biến. Micro-F1: gộp mọi câu rồi mới tính, nên nghiêng về nhãn phổ biến. |
| Hit@k | Success@k | Tỉ lệ câu hỏi có ít nhất một kết quả đúng trong k kết quả đầu. |
| MRR | Mean Reciprocal Rank | Trung bình của 1/hạng của kết quả đúng đầu tiên. Kết quả đúng càng lên đầu thì càng cao. |
| Train / dev / test | Tập huấn luyện / kiểm định / kiểm tra | Ba phần dữ liệu tách riêng: để học, để chỉnh, để chấm điểm cuối. |
| Rò rỉ dữ liệu | Data leakage | Lỗi để dữ liệu dùng chấm điểm lọt vào lúc học, làm điểm cao giả. |
| SQL | Structured Query Language | Ngôn ngữ truy vấn cơ sở dữ liệu quan hệ. |
| API | Application Programming Interface | Cổng để chương trình này gọi chương trình khác, ví dụ web gọi dịch vụ AI. |
| GPU | Graphics Processing Unit | Card đồ họa, tính song song nhanh, dùng để chạy và huấn luyện mô hình. |
| GGUF | — | Định dạng file nén model để chạy bằng Ollama hoặc llama.cpp. |
| Ollama | — | Phần mềm chạy mô hình ngôn ngữ trên máy riêng. |
| FIFO | First In, First Out | Cách tính giá vốn: hàng nhập trước thì xuất trước. |

# LỜI MỞ ĐẦU

## Lý do chọn đề tài

Cửa hàng bán máy tính và linh kiện nhận rất nhiều câu hỏi lặp lại: máy này RAM bao nhiêu, bảo hành mấy tháng, trả góp thế nào, tầm 20 triệu nên mua máy nào. Người quản lý cửa hàng cũng thường hỏi các câu về số liệu: doanh thu tháng này, lãi gộp quý trước, mặt hàng nào bán chạy. Trả lời tay mất thời gian, còn trả lời sai thì mất khách hoặc ra quyết định sai.

Chatbot dùng mô hình ngôn ngữ lớn (LLM) trả lời rất trôi chảy, nhưng có một nhược điểm lớn: **nó có thể "bịa"**. Nghĩa là nó nói ra một con số hoặc một chính sách nghe rất hợp lý nhưng không có trong dữ liệu của cửa hàng. Với một cửa hàng thật, một câu bịa về giá hoặc bảo hành gây hại nhiều hơn một câu "tôi chưa có thông tin".

Vì vậy đề tài chọn hướng **lấy dữ liệu làm gốc**: mọi câu trả lời phải dựa trên tài liệu hoặc bảng số liệu của cửa hàng, có ghi nguồn. Đây đúng là chỗ môn Kho dữ liệu và Khai phá dữ liệu đi vào: phải tổ chức dữ liệu cho tốt (kho dữ liệu), rồi dùng thuật toán khai phá văn bản để tìm đúng đoạn dữ liệu cho từng câu hỏi (truy xuất thông tin) và hiểu câu hỏi muốn gì (phân lớp ý định).

## Mục tiêu

1. Trình bày tổng quan về kho dữ liệu và khai phá dữ liệu: khái niệm, phân loại, các bước, lĩnh vực ứng dụng và hướng nghiên cứu.
2. Trình bày chi tiết các thuật toán cùng nhánh với thuật toán dùng trong đề tài: biểu diễn văn bản, đo độ tương tự, xếp hạng tài liệu (TF-IDF, BM25, vector nhúng, RRF) và phân lớp (kNN, Naive Bayes, SVM, cây quyết định, mô hình ngôn ngữ tinh chỉnh bằng LoRA).
3. Áp dụng vào chatbot TechStore: tổ chức dữ liệu cửa hàng thành một kho dữ liệu nhỏ, xây dựng luồng hỏi đáp có dẫn nguồn, đo chất lượng bằng các bộ câu hỏi tách riêng.

## Phạm vi

- Dữ liệu: 67 sản phẩm (48 linh kiện, 19 laptop) lấy thông số từ bộ dữ liệu công khai; dữ liệu bán hàng một năm (10/2025 – 9/2026) là **dữ liệu mô phỏng**, không phải số của cửa hàng thật. Nguồn ghi đầy đủ ở mục 3.2 và Phụ lục A.
- Ngôn ngữ: tiếng Việt.
- Người dùng: khách mua (hỏi sản phẩm, chính sách) và quản trị viên (hỏi số liệu kinh doanh).
- Không làm: thanh toán, đặt hàng thật qua chat, giá và tồn kho theo thời gian thực.

## Phương pháp thực hiện

- Nghiên cứu tài liệu: sách giáo trình, bài báo gốc của từng thuật toán, tài liệu kỹ thuật (danh sách ở phần Tài liệu tham khảo).
- Thực nghiệm: cài đặt bằng Python, huấn luyện trên GPU miễn phí của Kaggle, đo bằng hơn 1.500 câu hỏi chia thành nhiều bộ. Mô hình chạy với temperature = 0 (luôn chọn từ có xác suất cao nhất) và mỗi bản chạy hai lần để phát hiện các câu còn dao động.

## Bố cục báo cáo

- **Chương 1** trình bày tổng quan về kho dữ liệu và khai phá dữ liệu.
- **Chương 2** đi sâu vào các thuật toán của nhánh khai phá văn bản, truy xuất thông tin và phân lớp, có ví dụ tính tay.
- **Chương 3** mô tả cách áp dụng vào chatbot TechStore: nguồn dữ liệu, kho dữ liệu, kiến trúc, luồng xử lý, huấn luyện và kết quả đo.
- Cuối báo cáo là kết luận, tài liệu tham khảo và phụ lục.

# CHƯƠNG 1. TỔNG QUAN VỀ KHO DỮ LIỆU VÀ PHƯƠNG PHÁP KHAI PHÁ DỮ LIỆU

## 1.1. Dữ liệu, thông tin và tri thức

Ba khái niệm này hay bị dùng lẫn, nhưng chúng là ba mức khác nhau:

- **Dữ liệu (data)** là các con số, ký hiệu thô, chưa có ý nghĩa nếu đứng một mình. Ví dụ: một dòng `2026-03-14, SKU-12, 2, 31.980.000`.
- **Thông tin (information)** là dữ liệu đã được đặt vào ngữ cảnh. Ví dụ: "Ngày 14/3/2026 cửa hàng bán 2 chiếc MSI Modern 15, thu 31.980.000 đồng."
- **Tri thức (knowledge)** là quy luật rút ra từ nhiều thông tin, dùng để ra quyết định. Ví dụ: "Laptop bán chạy nhất vào quý 4 (mùa mua sắm cuối năm), nên nhập thêm hàng từ tháng 9."

Kho dữ liệu lo việc biến **dữ liệu** thành **thông tin** sạch, thống nhất. Khai phá dữ liệu lo việc đi từ **thông tin** đến **tri thức**.

## 1.2. Kho dữ liệu

### 1.2.1. Khái niệm

Định nghĩa được dùng nhiều nhất là của W. H. Inmon, người được gọi là "cha đẻ của kho dữ liệu" [3]:

> **Định nghĩa (Inmon):** Kho dữ liệu là một tập dữ liệu **hướng chủ đề, tích hợp, gắn với thời gian và không thay đổi**, dùng để hỗ trợ quá trình ra quyết định của nhà quản lý.

Bốn đặc điểm trong định nghĩa được hiểu như sau:

1. **Hướng chủ đề (subject-oriented):** dữ liệu được sắp theo chủ đề kinh doanh (bán hàng, khách hàng, tồn kho), không sắp theo từng phần mềm. Phần mềm bán hàng, phần mềm kho, file Excel kế toán có thể khác nhau, nhưng trong kho dữ liệu chúng gom về chung một chủ đề "bán hàng".
2. **Tích hợp (integrated):** dữ liệu từ nhiều nguồn được thống nhất về cách ghi. Ví dụ nguồn A ghi giới tính là "Nam/Nữ", nguồn B ghi "M/F", nguồn C ghi "1/0"; vào kho thì phải về một kiểu. Đơn vị tiền, định dạng ngày, mã sản phẩm cũng phải thống nhất.
3. **Gắn với thời gian (time-variant):** mỗi dòng dữ liệu đều có mốc thời gian, và kho giữ lịch sử nhiều năm. CSDL giao dịch thường chỉ giữ trạng thái hiện tại (tồn kho hôm nay), còn kho giữ cả tồn kho của từng ngày trong quá khứ.
4. **Không thay đổi (non-volatile):** dữ liệu vào kho rồi thì chỉ đọc và thêm mới, không sửa hay xóa từng dòng như CSDL giao dịch. Nhờ vậy báo cáo chạy hôm nay và chạy lại sau một tháng cho cùng kết quả.

Ralph Kimball đưa ra một cách nhìn thực tế hơn: kho dữ liệu là **"bản sao dữ liệu giao dịch được tổ chức riêng để truy vấn và phân tích"** [4]. Hai định nghĩa không mâu thuẫn mà nhấn mạnh hai mặt khác nhau: Inmon nhấn mạnh tính chất của dữ liệu, Kimball nhấn mạnh cách dùng.

### 1.2.2. Vì sao cần kho dữ liệu: OLTP và OLAP

Cửa hàng đã có CSDL bán hàng, vậy tại sao không phân tích thẳng trên đó? Vì hai loại công việc này có yêu cầu ngược nhau.

*Bảng 1.1. So sánh hệ thống giao dịch (OLTP) và hệ thống phân tích (OLAP)*

| Tiêu chí | OLTP (CSDL giao dịch) | OLAP (kho dữ liệu) |
|---|---|---|
| Mục đích | Ghi nhận nghiệp vụ hằng ngày | Phân tích, báo cáo, ra quyết định |
| Người dùng | Nhân viên bán hàng, thu ngân | Quản lý, nhà phân tích |
| Thao tác chính | Thêm, sửa, xóa từng dòng | Đọc, cộng dồn hàng triệu dòng |
| Dữ liệu | Hiện tại, chi tiết | Lịch sử nhiều năm, đã tổng hợp |
| Thiết kế bảng | Chuẩn hóa cao (3NF) để tránh trùng | Phi chuẩn hóa (lược đồ hình sao) để đọc nhanh |
| Câu truy vấn | Ngắn, biết trước ("đơn số 123") | Phức tạp, thay đổi ("doanh thu laptop theo quý, theo kênh") |
| Ưu tiên | Ghi nhanh, không mất giao dịch | Đọc nhanh, số liệu nhất quán |

Nếu chạy một câu phân tích nặng ngay trên CSDL giao dịch, câu đó có thể khóa bảng và làm chậm việc bán hàng. Ngoài ra dữ liệu giao dịch thường nằm rải rác ở nhiều hệ thống khác nhau, không cái nào có đủ bức tranh. Kho dữ liệu giải quyết cả hai: tách việc phân tích ra chỗ riêng, và gom mọi nguồn về một chỗ.

### 1.2.3. Kiến trúc kho dữ liệu

![Hình 1.1. Kiến trúc kho dữ liệu nhiều tầng](hinh/h1_1_kien_truc_kho_du_lieu.png)

Một kho dữ liệu điển hình có các tầng sau (Hình 1.1):

1. **Tầng nguồn:** CSDL bán hàng, file Excel/CSV, dữ liệu từ web hoặc API của đối tác, nhật ký (log) truy cập website.
2. **Tầng ETL** (trích xuất – biến đổi – nạp):
   - *Trích xuất (Extract):* lấy dữ liệu ra khỏi nguồn, thường theo lịch (mỗi đêm, mỗi giờ). Có thể lấy toàn bộ hoặc chỉ phần thay đổi kể từ lần trước.
   - *Biến đổi (Transform):* làm sạch (bỏ trùng, sửa lỗi), thống nhất mã và đơn vị, tính các cột mới (doanh thu = số lượng × đơn giá − giảm giá), nối dữ liệu từ nhiều nguồn.
   - *Nạp (Load):* ghi vào kho. Nạp lần đầu là nạp toàn bộ, các lần sau thường chỉ nạp thêm phần mới.
3. **Vùng tạm (staging area):** nơi để dữ liệu thô vừa lấy về trước khi biến đổi. Có vùng tạm thì khi biến đổi lỗi, ta chạy lại từ đây mà không phải lấy lại từ nguồn.
4. **Kho dữ liệu trung tâm:** dữ liệu đã sạch, tích hợp, có lịch sử.
5. **Data mart:** các kho nhỏ theo phòng ban (bán hàng, kho, tài chính), tách ra từ kho trung tâm cho gọn và nhanh.
6. **Tầng khai thác:** báo cáo, công cụ BI (Business Intelligence), phân tích OLAP, khai phá dữ liệu, và ngày nay cả chatbot hỏi đáp.
7. **Siêu dữ liệu (metadata):** "dữ liệu về dữ liệu", ghi bảng nào lấy từ nguồn nào, cập nhật lúc nào, cột nào nghĩa là gì. Thiếu siêu dữ liệu thì người dùng không biết tin số liệu đến đâu.

> **Điểm kỹ thuật – ETL hay ELT:** với kho dữ liệu trên cloud hiện nay, nhiều nơi làm theo thứ tự **ELT**: nạp dữ liệu thô vào kho trước, rồi biến đổi ngay trong kho bằng SQL, vì kho cloud tính rất mạnh. ETL truyền thống biến đổi trước khi nạp, phù hợp khi kho có tài nguyên hạn chế hoặc dữ liệu thô không được phép lưu.

### 1.2.4. Mô hình dữ liệu nhiều chiều

Kho dữ liệu thường không thiết kế theo kiểu chuẩn hóa như CSDL giao dịch, mà theo **mô hình nhiều chiều (dimensional model)**. Mô hình này có hai loại bảng:

- **Bảng sự kiện (fact table):** mỗi dòng là một sự kiện nghiệp vụ đo được, chứa các **độ đo (measure)** là con số: số lượng, doanh thu, giá vốn. Bảng này rất dài (hàng triệu dòng) nhưng hẹp (ít cột).
- **Bảng chiều (dimension table):** mô tả ngữ cảnh: thời gian, sản phẩm, khách hàng, cửa hàng. Bảng này ngắn nhưng rộng (nhiều cột mô tả).

Trước khi thiết kế phải chốt **độ mịn (grain)**: một dòng trong bảng sự kiện là gì. Ví dụ "một dòng = một sản phẩm trong một đơn hàng". Chọn độ mịn quá thô (một dòng = tổng một ngày) thì không trả lời được câu hỏi chi tiết; chọn quá mịn thì bảng phình to.

![Hình 1.2. Lược đồ hình sao với bảng sự kiện bán hàng ở giữa](hinh/h1_2_luoc_do_hinh_sao.png)

Có ba kiểu lược đồ:

1. **Lược đồ hình sao (star schema):** một bảng sự kiện ở giữa, các bảng chiều xung quanh nối trực tiếp vào (Hình 1.2). Đơn giản, truy vấn ít phép nối, nên được dùng nhiều nhất.
2. **Lược đồ bông tuyết (snowflake schema):** bảng chiều được tách nhỏ thêm. Ví dụ bảng sản phẩm tách thành sản phẩm → danh mục → ngành hàng. Tiết kiệm chỗ, nhưng truy vấn phải nối nhiều bảng hơn.
3. **Lược đồ chòm sao (galaxy / fact constellation):** nhiều bảng sự kiện dùng chung bảng chiều. Ví dụ bảng "bán hàng" và bảng "tồn kho" cùng dùng chiều thời gian và chiều sản phẩm. Kho dữ liệu của đề tài (mục 3.3) thuộc kiểu này.

> **Điểm kỹ thuật – chiều thay đổi chậm (SCD):** thuộc tính của chiều có thể đổi theo thời gian, ví dụ khách chuyển từ phân khúc "mua một lần" sang "thân thiết". Có ba cách xử lý chính: **SCD loại 1** ghi đè (mất lịch sử), **SCD loại 2** thêm dòng mới kèm ngày hiệu lực (giữ lịch sử đầy đủ), **SCD loại 3** thêm cột "giá trị cũ" (giữ được một bước lịch sử).

### 1.2.5. Các thao tác OLAP

Dữ liệu nhiều chiều thường được hình dung như một **khối lập phương dữ liệu (data cube)**: mỗi cạnh là một chiều (thời gian, sản phẩm, kênh bán), mỗi ô chứa độ đo (doanh thu). Các thao tác OLAP là các cách "xoay, cắt, gộp" khối này.

*Bảng 1.2. Các thao tác OLAP, ví dụ trên dữ liệu cửa hàng của đề tài*

| Thao tác | Ý nghĩa | Ví dụ với dữ liệu đề tài |
|---|---|---|
| Roll-up (cuộn lên) | Gộp lên mức cao hơn của một chiều | Từ doanh thu laptop theo quý lên doanh thu laptop cả năm: 9.043.111.000 đ |
| Drill-down (khoan xuống) | Đi xuống mức chi tiết hơn | Từ doanh thu quý 4/2025 (3.952.314.000 đ) xuống từng tháng: tháng 10 là 984.310.000 đ, tháng 11 là 1.493.219.000 đ, tháng 12 là 1.474.785.000 đ |
| Slice (cắt lát) | Cố định một chiều ở một giá trị | Chỉ xem kênh "cửa hàng": 768 trên 1.427 đơn |
| Dice (cắt khối) | Lọc nhiều chiều cùng lúc | Laptop, quý 1/2026, kênh website |
| Pivot (xoay) | Đổi hàng thành cột để nhìn khác | Bảng nhóm hàng × quý thành bảng quý × nhóm hàng |

Các số trong Bảng 1.2 lấy từ cơ sở dữ liệu mô phỏng của đề tài (`shop.sqlite`). Phép roll-up được kiểm tra lại: cộng doanh thu bốn quý của laptop, và cộng doanh thu ba tháng của quý 4/2025, đều khớp với view tổng hợp `monthly_pnl`.

### 1.2.6. Các kiểu máy chủ OLAP: ROLAP, MOLAP, HOLAP

Thao tác OLAP thì giống nhau, nhưng **máy chủ OLAP** (phần mềm thực hiện các thao tác đó) có ba cách lưu và tính dữ liệu [1]:

*Bảng 1.3. So sánh ba kiểu máy chủ OLAP*

| Kiểu | Lưu dữ liệu ở đâu | Cách tính | Ưu điểm | Nhược điểm |
|---|---|---|---|---|
| **ROLAP** (Relational OLAP) | Bảng quan hệ thường (bảng sự kiện, bảng chiều) | Mỗi thao tác được dịch thành câu SQL `GROUP BY`, tính lúc hỏi | Chứa được dữ liệu rất lớn; dữ liệu mới vào là hỏi được ngay | Câu hỏi gộp nhiều chiều có thể chậm |
| **MOLAP** (Multidimensional OLAP) | Khối dữ liệu (cube) dựng sẵn, lưu dạng mảng nhiều chiều | Các tổng đã tính trước, chỉ việc đọc ra | Trả lời rất nhanh | Tốn chỗ khi nhiều chiều; phải dựng lại khối khi dữ liệu đổi |
| **HOLAP** (Hybrid OLAP) | Dữ liệu chi tiết ở bảng quan hệ, các tổng hay dùng ở khối | Tổng thì đọc từ khối, chi tiết thì chạy SQL | Cân bằng giữa tốc độ và dung lượng | Phức tạp hơn khi vận hành |

Đề tài thuộc kiểu **ROLAP**: mọi con số được tính bằng câu SQL trên các bảng của `shop.sqlite` ngay lúc hỏi. View `monthly_pnl` gần giống một bảng tổng hợp dựng sẵn, nhưng vẫn là view SQL, được tính lại mỗi lần đọc. Với một năm dữ liệu (1.427 đơn), ROLAP đã đủ nhanh, không cần dựng khối.

### 1.2.7. Hai trường phái xây dựng: Inmon và Kimball

*Bảng 1.4. So sánh cách tiếp cận Inmon và Kimball*

| Tiêu chí | Inmon (từ trên xuống) | Kimball (từ dưới lên) |
|---|---|---|
| Cách làm | Xây kho trung tâm chuẩn hóa trước, rồi tách data mart | Xây từng data mart theo lược đồ hình sao, nối bằng các chiều dùng chung |
| Thời gian ra kết quả đầu tiên | Lâu | Nhanh |
| Tính nhất quán toàn công ty | Cao | Phụ thuộc vào việc giữ chiều dùng chung (conformed dimension) |
| Phù hợp | Tổ chức lớn, nhiều nguồn phức tạp | Doanh nghiệp vừa và nhỏ, cần kết quả sớm |

Hiện nay còn có **hồ dữ liệu (data lake)**: lưu mọi dữ liệu thô (cả văn bản, ảnh, log) với chi phí rẻ, chưa cần thiết kế trước. Kết hợp hồ dữ liệu với khả năng quản lý của kho dữ liệu thì gọi là **lakehouse**. Đề tài dùng cả hai ý: bảng số liệu có cấu trúc nằm trong SQLite (giống kho dữ liệu), còn tài liệu văn bản nằm trong thư mục có file kê khai `manifest.json` (giống hồ dữ liệu có siêu dữ liệu).

**Kiến trúc medallion (đồng – bạc – vàng).** Đây là cách chia tầng phổ biến hiện nay trong lakehouse [46]. Dữ liệu đi qua ba tầng, tầng sau chỉ đọc tầng trước:

- **Bronze (đồng):** dữ liệu thô, chép nguyên từ nguồn, không sửa gì. Dùng để chạy lại khi các bước sau có lỗi.
- **Silver (bạc):** dữ liệu đã kiểm tra, làm sạch và thống nhất (đúng kiểu, không trùng, khớp khóa).
- **Gold (vàng):** dữ liệu đã tổng hợp theo nhu cầu sử dụng: báo cáo, chỉ số, bảng cho phân tích.

Quy trình nạp dữ liệu của đề tài (mục 3.4) khớp **gần đúng** với ba tầng này:

*Bảng 1.5. Các module dữ liệu của đề tài theo kiến trúc medallion*

| Tầng | Module trong đề tài | Việc làm |
|---|---|---|
| Bronze | `de_snapshot` | Chụp bản thô có mã băm, phát hiện nếu file nguồn bị đổi |
| Silver | `de_audit`, `de_reconcile` | Kiểm tra kiểu, khóa, phép tính từng dòng; chạy lại nhập – xuất FIFO để đối soát tồn kho |
| Gold | `de_curated`, view `monthly_pnl` | Bản tổng hợp cho admin; lãi lỗ theo tháng |

Điểm khác với medallion chuẩn: tầng silver của đề tài **không tự sửa** dữ liệu. `de_audit` chỉ đọc, ghi lại dòng lỗi và dừng nếu có lỗi (fail-closed), vì với số liệu kế toán, tự sửa sai còn nguy hiểm hơn dừng lại báo lỗi.

### 1.2.8. Phân loại kho dữ liệu

- **Kho dữ liệu doanh nghiệp (Enterprise Data Warehouse – EDW):** kho trung tâm cho toàn công ty.
- **Data mart phụ thuộc:** lấy dữ liệu từ EDW. **Data mart độc lập:** lấy thẳng từ nguồn (nhanh nhưng dễ lệch số giữa các phòng).
- **Kho dữ liệu tác nghiệp (Operational Data Store – ODS):** dữ liệu gần thời gian thực, ít lịch sử, phục vụ báo cáo trong ngày.
- **Kho dữ liệu ảo:** không chép dữ liệu, chỉ tạo lớp truy vấn đứng trên các nguồn.

## 1.3. Khai phá dữ liệu

### 1.3.1. Khái niệm

> **Định nghĩa:** Khai phá dữ liệu (data mining) là quá trình tìm ra các **mẫu (pattern)** có giá trị, mới, có thể hiểu được và có ích trong một lượng dữ liệu lớn [1], [2].

Bốn chữ quan trọng trong định nghĩa:

- **Có giá trị (valid):** mẫu phải đúng với cả dữ liệu mới, không chỉ đúng với dữ liệu đã thấy.
- **Mới (novel):** không phải điều ai cũng biết sẵn. "Khách mua laptop thì mua laptop" không phải phát hiện.
- **Hiểu được (understandable):** người dùng đọc được và giải thích được.
- **Có ích (useful):** dùng được để hành động, ví dụ quyết định nhập hàng, chạy khuyến mãi.

Fayyad và cộng sự (1996) phân biệt rõ: **KDD** (khám phá tri thức trong CSDL) là **toàn bộ quá trình** từ chọn dữ liệu đến diễn giải kết quả; **khai phá dữ liệu** chỉ là **một bước** trong quá trình đó, bước áp dụng thuật toán để tìm mẫu [2]. Trong thực tế hai từ này thường dùng lẫn cho nhau.

Cũng cần phân biệt với những việc **không** phải khai phá dữ liệu:

- Chạy câu SQL "tổng doanh thu tháng 3" là **truy vấn**, không phải khai phá: câu trả lời đã biết cách tính, chỉ cần tính.
- Vẽ biểu đồ doanh thu theo tháng là **thống kê mô tả**.
- Khai phá là khi ta **chưa biết trước** quy luật, ví dụ: "những khách nào sắp bỏ đi", "sản phẩm nào hay được mua cùng nhau", "câu hỏi này thuộc loại nào".

### 1.3.2. Quan hệ với các ngành khác

Khai phá dữ liệu là chỗ giao nhau của nhiều ngành:

- **Thống kê:** cung cấp lý thuyết về mẫu, ước lượng, kiểm định.
- **Học máy (machine learning):** cung cấp thuật toán học từ dữ liệu (cây quyết định, mạng nơ-ron…).
- **Cơ sở dữ liệu:** cung cấp cách lưu và truy vấn dữ liệu lớn hiệu quả, chính là kho dữ liệu.
- **Truy xuất thông tin và xử lý ngôn ngữ tự nhiên:** cung cấp cách làm việc với văn bản. Đây là nhánh đề tài dùng nhiều nhất.
- **Trực quan hóa:** giúp con người nhìn ra và kiểm tra mẫu.

## 1.4. Phân loại khai phá dữ liệu

Có nhiều cách phân loại, tùy nhìn theo mục đích, loại dữ liệu, kỹ thuật hay cách học.

### 1.4.1. Theo mục đích

![Hình 1.3. Phân loại các bài toán khai phá dữ liệu theo mục đích; ô đỏ là nhánh của đề tài](hinh/h1_5_phan_loai_khai_pha.png)

**Khai phá dự đoán (predictive):** dùng dữ liệu đã có nhãn (đã biết đáp án) để đoán giá trị cho dữ liệu mới.

- **Phân lớp (classification):** đoán nhãn rời rạc. Ví dụ: email là "rác" hay "không rác"; câu hỏi của khách thuộc loại "hỏi sản phẩm", "hỏi chính sách" hay "muốn đặt hàng".
- **Hồi quy (regression):** đoán giá trị liên tục. Ví dụ: giá một chiếc laptop theo cấu hình.
- **Dự báo chuỗi thời gian (forecasting):** đoán giá trị tương lai dựa vào quá khứ. Ví dụ: số máy bán ngày mai.

**Khai phá mô tả (descriptive):** không có nhãn, tìm cấu trúc ẩn trong dữ liệu.

- **Phân cụm (clustering):** gom các đối tượng giống nhau thành nhóm. Ví dụ: chia khách thành nhóm "săn khuyến mãi", "thân thiết", "mua một lần".
- **Luật kết hợp (association rules):** tìm các thứ hay đi cùng nhau, dạng "mua A thì thường mua B" (thuật toán Apriori [5]). Ví dụ tính tay ở cuối mục này.
- **Phát hiện bất thường (anomaly detection):** tìm điểm lạ. Ví dụ: giao dịch gian lận, đơn hoàn trả bất thường.

**Ví dụ tính tay luật kết hợp trên dữ liệu của đề tài.** Một luật A → B ("mua A thì mua B") được đo bằng ba con số:

```math
\mathrm{support}(A \to B) = \frac{\text{số đơn có cả A và B}}{\text{tổng số đơn}}
\mathrm{confidence}(A \to B) = \frac{\text{số đơn có cả A và B}}{\text{số đơn có A}}
\mathrm{lift}(A \to B) = \frac{\mathrm{confidence}(A \to B)}{P(B)}, \qquad P(B) = \frac{\text{số đơn có B}}{\text{tổng số đơn}}
```

- **Support (độ hỗ trợ):** luật gặp thường xuyên đến đâu. Support quá thấp thì luật có thể chỉ là trùng hợp.
- **Confidence (độ tin cậy):** trong các đơn có A, bao nhiêu phần trăm có B.
- **Lift (độ nâng):** có A thì khả năng có B **cao gấp bao nhiêu lần** so với bình thường. Lift > 1: A và B hay đi cùng nhau; lift = 1: không liên quan; lift < 1: ít đi cùng nhau.

Đếm trên `shop.sqlite` (1.427 đơn, theo nhóm hàng của từng đơn): 558 đơn có laptop, 297 đơn có chuột, 178 đơn có cả hai.

```text
support(laptop → chuột)    = 178 / 1.427 = 0,1247   (12,5% số đơn)
confidence(laptop → chuột) = 178 / 558   = 0,3190   (31,9% đơn có laptop thì có chuột)
P(chuột)                   = 297 / 1.427 = 0,2081
lift(laptop → chuột)       = 0,3190 / 0,2081 = 1,53
confidence(chuột → laptop) = 178 / 297   = 0,5993
```

Khách mua laptop thì khả năng mua kèm chuột cao gấp **1,53 lần** so với một đơn bất kỳ. Ví dụ cũng cho thấy luật **có chiều**: support và lift của hai chiều bằng nhau, nhưng confidence thì khác: 31,9% theo chiều laptop → chuột, 59,9% theo chiều chuột → laptop. Lưu ý: dữ liệu bán hàng của đề tài là mô phỏng, nên luật này phản ánh cách bộ mô phỏng tạo đơn chứ không phải hành vi của khách thật. Trong dữ liệu này cũng **không có** đơn nào mua cả CPU lẫn mainboard, nên không thể lấy ví dụ "mua CPU thì mua mainboard".

Nhánh của đề tài là **khai phá văn bản và truy xuất thông tin**, nằm giữa hai nhóm (Hình 1.3): phần **phân lớp ý định** thuộc khai phá dự đoán, còn phần **xếp hạng tài liệu theo độ tương tự** dùng cùng ý tưởng "đo khoảng cách" với phân cụm và thuật toán láng giềng gần.

### 1.4.2. Theo loại dữ liệu

- **Dữ liệu quan hệ và giao dịch:** bảng đơn hàng, giỏ hàng. Dùng cho luật kết hợp, phân lớp khách hàng.
- **Chuỗi thời gian:** doanh thu theo ngày, giá cổ phiếu. Dùng cho dự báo.
- **Văn bản (text mining):** bài viết, câu hỏi, đánh giá sản phẩm. Dùng cho phân loại văn bản, tìm kiếm, tóm tắt.
- **Web mining:** gồm khai phá nội dung trang, cấu trúc liên kết (thuật toán PageRank) và hành vi duyệt web (log).
- **Dữ liệu không gian:** bản đồ, vị trí cửa hàng.
- **Đồ thị và mạng xã hội:** quan hệ giữa người dùng.
- **Đa phương tiện:** ảnh, âm thanh, video.

### 1.4.3. Theo kỹ thuật

- Phương pháp thống kê (hồi quy, Naive Bayes).
- Cây quyết định (ID3, C4.5, CART).
- Phương pháp dựa trên khoảng cách (kNN, k-means).
- Mạng nơ-ron và học sâu (transformer, mô hình ngôn ngữ lớn).
- Phương pháp dựa trên luật (Apriori, luật do chuyên gia viết).
- Phương pháp kết hợp (ensemble: rừng ngẫu nhiên, boosting).

Năm 2006, hội nghị IEEE ICDM bình chọn **10 thuật toán khai phá dữ liệu có ảnh hưởng nhất**: C4.5, k-Means, SVM, Apriori, EM, PageRank, AdaBoost, kNN, Naive Bayes và CART [6]. Chương 2 trình bày những thuật toán trong danh sách này thuộc cùng nhánh với đề tài (kNN, Naive Bayes, SVM, C4.5/CART).

### 1.4.4. Theo cách học

- **Học có giám sát (supervised):** có đáp án mẫu để học. Ví dụ phân lớp, hồi quy.
- **Học không giám sát (unsupervised):** không có đáp án. Ví dụ phân cụm.
- **Học bán giám sát (semi-supervised):** ít dữ liệu có nhãn, nhiều dữ liệu không nhãn.
- **Học tăng cường (reinforcement):** học qua thử – sai và phần thưởng.
- **Học tự giám sát (self-supervised):** tự tạo nhãn từ dữ liệu. Ví dụ che một từ trong câu rồi bắt mô hình đoán lại. Các mô hình ngôn ngữ như BERT, Qwen được huấn luyện ban đầu theo cách này.

## 1.5. Các bước thực hiện khai phá dữ liệu

### 1.5.1. Quy trình KDD

![Hình 1.4. Quy trình khám phá tri thức (KDD) theo Fayyad và cộng sự](hinh/h1_3_quy_trinh_kdd.png)

Theo Fayyad và cộng sự [2], quá trình KDD gồm 5 bước chính (Hình 1.4):

1. **Chọn lọc (selection):** xác định bài toán và chọn phần dữ liệu liên quan. Ví dụ muốn dự báo doanh số laptop thì chỉ lấy dữ liệu bán laptop, không cần dữ liệu chuột.
2. **Tiền xử lý (preprocessing):** làm sạch dữ liệu: xử lý giá trị thiếu, bỏ trùng, sửa lỗi nhập. Bước này **thường được cho là** chiếm phần lớn thời gian của dự án (con số hay được nhắc là 60–80%). Đây là ước lượng từ khảo sát người làm nghề, không phải số đo chính xác.
3. **Biến đổi (transformation):** đưa dữ liệu về dạng thuật toán dùng được: chuẩn hóa thang đo, tạo đặc trưng mới, giảm số chiều. Với văn bản, bước này là biến câu chữ thành vector số.
4. **Khai phá (data mining):** chọn và chạy thuật toán: phân lớp, phân cụm, luật kết hợp…
5. **Diễn giải và đánh giá (interpretation/evaluation):** kiểm tra mẫu tìm được có đúng, có ích không, rồi trình bày cho người dùng.

Quá trình này **lặp**: kết quả bước 5 không tốt thì quay lại bước trước, ví dụ chọn thêm dữ liệu hoặc đổi cách biến đổi.

### 1.5.2. Quy trình CRISP-DM

![Hình 1.5. Mô hình CRISP-DM gồm 6 giai đoạn lặp vòng](hinh/h1_4_crisp_dm.png)

CRISP-DM là quy trình chuẩn dùng trong công nghiệp [7], gồm 6 giai đoạn (Hình 1.5):

*Bảng 1.6. Sáu giai đoạn CRISP-DM và cách đề tài thực hiện*

| Giai đoạn | Việc chính | Trong đề tài |
|---|---|---|
| 1. Hiểu bài toán kinh doanh | Xác định mục tiêu, tiêu chí thành công | Bot trả lời đúng theo dữ liệu cửa hàng, không bịa, có nguồn |
| 2. Hiểu dữ liệu | Thu thập, mô tả, kiểm tra chất lượng | Rà 11 bộ dữ liệu công khai, chọn 2 bộ làm thông số sản phẩm |
| 3. Chuẩn bị dữ liệu | Làm sạch, tích hợp, tạo đặc trưng | Dựng `products.sqlite`, mô phỏng một năm bán hàng, chia đoạn tài liệu |
| 4. Xây dựng mô hình | Chọn thuật toán, huấn luyện | Truy xuất lai TF-IDF + BM25 + vector nhúng; luật định tuyến; Qwen3 4B làm router; tinh chỉnh LoRA cho bước chọn bằng chứng |
| 5. Đánh giá | Đo trên dữ liệu chưa thấy, so với mục tiêu | Hơn 1.500 câu hỏi, mỗi bản chạy hai lần; bản mới chỉ được dùng khi không có câu nào trước đạt mà sau bị trượt (lỗi lùi – regression) |
| 6. Triển khai | Đưa vào sử dụng, theo dõi | Dịch vụ FastAPI, web gọi qua `AI_SERVICE_URL` |

Điểm khác của CRISP-DM so với KDD là nó **bắt đầu và kết thúc bằng nghiệp vụ**: giai đoạn đầu là hiểu bài toán kinh doanh, giai đoạn cuối là triển khai vào thực tế, chứ không dừng ở chỗ tìm ra mẫu.

### 1.5.3. Tiền xử lý dữ liệu chi tiết

Dữ liệu thực tế thường "bẩn". Theo Han và cộng sự [1], tiền xử lý gồm bốn việc:

**a) Làm sạch dữ liệu (data cleaning)**

- *Giá trị thiếu:* bỏ dòng, điền bằng trung bình hoặc trung vị, điền bằng giá trị hay gặp nhất, hoặc dùng mô hình để đoán. Với dữ liệu sản phẩm, đề tài **không điền đoán** thông số còn thiếu: thông số nào nguồn không có thì để trống, và bot trả lời "chưa có thông tin", vì đoán sai thông số còn tệ hơn không trả lời.
- *Dữ liệu nhiễu:* giá trị sai lệch, ví dụ giá âm, RAM 1.600 GB. Xử lý bằng chia khoảng (binning), hồi quy, hoặc loại bỏ các điểm vượt ngưỡng.
- *Dữ liệu trùng:* cùng một sản phẩm xuất hiện hai lần với tên hơi khác nhau ("MSI Modern 15" và "MSI Modern15").
- *Dữ liệu mâu thuẫn:* hai nguồn ghi khác nhau. Ví dụ trong đề tài, thông số chuột Logitech G305 ở hai nguồn không khớp nhau; tài liệu ghi rõ cả hai số kèm nguồn thay vì tự chọn một.

**b) Tích hợp dữ liệu (data integration):** gộp nhiều nguồn, xử lý xung đột tên cột, đơn vị (USD và VND), mã sản phẩm.

**c) Thu gọn dữ liệu (data reduction):** giảm số dòng (lấy mẫu), giảm số cột (chọn đặc trưng, PCA), hoặc nén.

**d) Biến đổi dữ liệu (data transformation):**

- *Chuẩn hóa min–max:* đưa về khoảng [0, 1].

```math
x' = \frac{x - \min}{\max - \min}
```

Ví dụ: RAM 8, 16, 32 GB → 0; 0,333; 1.

- *Chuẩn hóa z-score:* đưa về trung bình 0, độ lệch chuẩn 1.

```math
x' = \frac{x - \mu}{\sigma}
```

Trong đó μ là trung bình, σ là độ lệch chuẩn.

- *Rời rạc hóa:* biến số liên tục thành nhóm. Ví dụ giá thành "dưới 15 triệu", "15–25 triệu", "trên 25 triệu".
- *Với văn bản:* chuyển chữ thường, chuẩn hóa dấu, tách từ, biến thành vector (chi tiết ở Chương 2).

**e) Các tiêu chí chất lượng dữ liệu**

Trước khi làm sạch, cần biết dữ liệu "bẩn" ở chỗ nào. Wang và Strong [45] đưa ra nhiều chiều chất lượng dữ liệu; bốn chiều hay dùng nhất là đầy đủ, chính xác, nhất quán và kịp thời. Module `de_audit` của đề tài (chỉ đọc, không sửa dữ liệu) kiểm tra các chiều này bằng các phép kiểm cụ thể:

*Bảng 1.7. Tiêu chí chất lượng dữ liệu và phép kiểm tương ứng trong `de_audit`*

| Tiêu chí | Ý nghĩa | Phép kiểm trong `de_audit` |
|---|---|---|
| Đầy đủ (completeness) | Không thiếu cột, không thiếu giá trị bắt buộc | `schema:*`: bảng có đủ cột cần thiết; `typed_values:*`: ô chữ không được rỗng |
| Chính xác (accuracy, validity) | Giá trị đúng kiểu, đúng miền, đúng phép tính | Số phải là số nguyên, ngày phải đúng dạng `YYYY-MM-DD`; `line_arithmetic`: doanh thu = số lượng × đơn giá − giảm giá; `ledger_signs`: dòng bán có số dương, dòng trả hàng có số âm; `nonnegative_expenses`: chi phí không âm |
| Nhất quán (consistency) | Các bảng khớp nhau, không mâu thuẫn | `foreign_keys`, `known_sku:*`: mã sản phẩm phải có trong bảng sản phẩm; `sale_matches_source`, `return_matches_source`: sổ cái khớp đơn hàng và phiếu trả; `return_totals_within_sale`: không trả nhiều hơn số đã bán; `unique_identity:*`: không trùng mã |
| Kịp thời (timeliness) | Dữ liệu đủ mới, phủ đúng khoảng thời gian | Ghi lại ngày đầu và ngày cuối quan sát được của từng bảng. `de_audit` **không** tự kết luận dữ liệu đã đủ, vì thấy ngày đầu và ngày cuối chưa chứng minh được giữa hai ngày đó không thiếu ngày nào |

Ngoài ra, `de_audit` tính mã băm SHA-256 của file trước và sau khi kiểm. Nếu file bị đổi trong lúc kiểm thì báo cáo kiểm tra bị hủy.

### 1.5.4. Đánh giá và chống rò rỉ dữ liệu

Một mô hình chỉ đáng tin khi được chấm trên dữ liệu **nó chưa từng thấy**. Vì vậy dữ liệu được chia làm ba phần:

- **Tập huấn luyện (train):** để mô hình học.
- **Tập kiểm định (validation/dev):** để chọn tham số, so sánh các phiên bản.
- **Tập kiểm tra (test/held-out):** chỉ dùng **một lần** ở cuối để báo cáo kết quả.

> **Điểm kỹ thuật – rò rỉ dữ liệu (data leakage):** nếu câu hỏi trong tập kiểm tra lọt vào lúc huấn luyện, hoặc người làm nhìn tập kiểm tra rồi sửa code cho riêng các câu đó, điểm sẽ cao giả. Đề tài chặn việc này bằng ba cách: (1) loại câu hỏi của mọi bộ đánh giá khỏi dữ liệu huấn luyện, kể cả câu gần giống; (2) phần validation của một số bộ đề chỉ được xem **số đếm** đạt/trượt, không được xem nội dung câu; (3) bộ câu khóa (held-out) chỉ chạy **một lần** khi chốt phiên bản cuối.

## 1.6. Lĩnh vực ứng dụng

*Bảng 1.8. Một số lĩnh vực ứng dụng khai phá dữ liệu*

| Lĩnh vực | Bài toán điển hình | Kỹ thuật hay dùng |
|---|---|---|
| Bán lẻ, thương mại điện tử | Phân tích giỏ hàng, gợi ý sản phẩm, dự báo nhu cầu, phân khúc khách hàng, chatbot tư vấn | Luật kết hợp, lọc cộng tác, phân cụm, dự báo, truy xuất văn bản |
| Tài chính, ngân hàng | Chấm điểm tín dụng, phát hiện gian lận thẻ, chống rửa tiền | Phân lớp, phát hiện bất thường |
| Y tế | Hỗ trợ chẩn đoán, dự đoán tái nhập viện, khai phá hồ sơ bệnh án | Phân lớp, khai phá văn bản |
| Viễn thông | Dự đoán khách rời mạng (churn), tối ưu mạng | Phân lớp, phân cụm |
| Sản xuất | Bảo trì dự đoán, phát hiện lỗi sản phẩm | Chuỗi thời gian, phát hiện bất thường |
| Giáo dục | Dự đoán sinh viên có nguy cơ bỏ học, gợi ý lộ trình | Phân lớp, luật kết hợp |
| Chăm sóc khách hàng | Phân loại yêu cầu, trả lời tự động, phân tích cảm xúc | Phân lớp văn bản, truy xuất thông tin, mô hình ngôn ngữ |
| Khu vực công | Phát hiện gian lận thuế, quy hoạch giao thông | Phát hiện bất thường, dữ liệu không gian |

Lĩnh vực của đề tài là **bán lẻ và chăm sóc khách hàng**. Ở đây khai phá dữ liệu phục vụ hai nhóm người:

- **Khách mua:** cần câu trả lời nhanh, đúng về sản phẩm và chính sách. Đây là bài toán truy xuất thông tin.
- **Người quản lý:** cần số liệu kinh doanh đúng, giải thích được. Đây là bài toán OLAP trên kho dữ liệu, có thêm khả năng hỏi bằng tiếng Việt tự nhiên.

## 1.7. Thách thức và hướng nghiên cứu

1. **Dữ liệu lớn và dữ liệu luồng:** dữ liệu sinh ra liên tục (log, cảm biến), thuật toán phải xử lý từng phần, không chờ đủ dữ liệu. Hướng nghiên cứu: thuật toán trực tuyến, xấp xỉ, xử lý phân tán.
2. **Chất lượng dữ liệu:** dữ liệu sai thì kết quả sai ("garbage in, garbage out"). Hướng nghiên cứu: tự động phát hiện lỗi, theo dõi nguồn gốc dữ liệu (data lineage).
3. **Quyền riêng tư:** khai phá dữ liệu khách hàng có thể lộ thông tin cá nhân. Hướng nghiên cứu: ẩn danh hóa (k-anonymity), **riêng tư vi phân (differential privacy)** – thêm nhiễu có kiểm soát để không truy ngược ra từng người, và **học liên kết (federated learning)** – mô hình học trên máy của từng bên mà không gom dữ liệu về một chỗ.
4. **Giải thích được (Explainable AI – XAI):** mô hình học sâu cho kết quả tốt nhưng khó giải thích vì sao. Trong ngân hàng, y tế, người ta bắt buộc phải giải thích được. Hướng nghiên cứu: SHAP, LIME, chỉ ra bằng chứng.
5. **Công bằng (fairness):** mô hình học từ dữ liệu lịch sử có thể mang theo thiên lệch, ví dụ từ chối tín dụng một nhóm người nhiều hơn.
6. **Mô hình ngôn ngữ lớn và truy xuất tăng cường (RAG):** đây là hướng phát triển mạnh nhất hiện nay. LLM hiểu ngôn ngữ rất tốt nhưng hay "bịa" (hallucination). RAG khắc phục bằng cách bắt LLM trả lời dựa trên tài liệu tìm được [8], [9]. Các vấn đề còn mở: tìm đúng tài liệu cho câu hỏi khó, kiểm tra câu trả lời có đúng với tài liệu không, đánh giá tự động.
7. **Ngôn ngữ ít tài nguyên, trong đó có tiếng Việt:** tiếng Việt có dấu, từ ghép nhiều âm tiết, người dùng hay gõ không dấu hoặc viết tắt. Các mô hình như PhoBERT [10] được huấn luyện riêng cho tiếng Việt cho kết quả tốt hơn mô hình đa ngôn ngữ chung.
8. **Khai phá đồ thị và tri thức:** đồ thị tri thức (knowledge graph) kết hợp với LLM để trả lời câu hỏi nhiều bước.
9. **Tự động hóa (AutoML) và vận hành (MLOps):** tự chọn thuật toán và tham số; theo dõi mô hình sau khi triển khai, phát hiện khi chất lượng giảm.
10. **Hỏi số liệu bằng ngôn ngữ tự nhiên (Text-to-SQL):** người dùng hỏi "doanh thu quý 2 so với quý 1 tăng bao nhiêu?", máy tự viết câu SQL rồi chạy trên kho dữ liệu. Bộ dữ liệu Spider [44] là mốc đánh giá phổ biến của hướng này. Các vấn đề còn mở: câu SQL sinh ra có thể chạy được nhưng tính sai (nối nhầm bảng, lọc nhầm kỳ); câu hỏi mơ hồ ("tháng trước" là tháng nào); và an toàn (không để câu SQL sửa hoặc xóa dữ liệu).

Đề tài đụng tới các hướng 2, 3, 4, 6, 7 và 10: kiểm soát chất lượng và nguồn dữ liệu, không để lộ dữ liệu nội bộ cho khách, mọi câu trả lời phải chỉ ra được nguồn, dùng RAG cho tiếng Việt. Với hướng 10, đề tài **chưa** cho mô hình tự viết SQL. Module `shop_calc` nhận diện câu hỏi rồi điền vào các câu SQL viết sẵn có tham số (kỳ, chỉ số, phép tính). Cách này kém linh hoạt hơn Text-to-SQL, nhưng con số luôn đúng và câu SQL không bao giờ ghi vào dữ liệu. Text-to-SQL có kiểm tra là hướng mở rộng tự nhiên của phần trả lời cho quản trị viên.

## 1.8. Liên hệ giữa lý thuyết và đề tài

*Bảng 1.9. Các khái niệm của Chương 1 xuất hiện trong đề tài*

| Khái niệm | Thành phần tương ứng trong đề tài |
|---|---|
| Nguồn dữ liệu | Bộ dữ liệu linh kiện trên GitHub, bộ laptop trên Kaggle, trang tài liệu của hãng |
| ETL, vùng tạm, medallion | Các module `de_snapshot` (chụp bản thô, tầng bronze), `de_audit` (kiểm tra) và `de_reconcile` (đối soát) (tầng silver), `de_curated` (tổng hợp, tầng gold) |
| Chất lượng dữ liệu | Các phép kiểm của `de_audit` (Bảng 1.7) |
| Máy chủ OLAP | Kiểu ROLAP: tính bằng SQL trên `shop.sqlite` lúc hỏi |
| Kho dữ liệu | `shop.sqlite`: 17 bảng, có bảng sự kiện và bảng chiều |
| Bảng sự kiện | `order_items` (độ mịn: một sản phẩm trong một đơn), `financial_ledger`, `inventory_daily`, `returns`… |
| Bảng chiều | `products`, `customers`, `campaigns`, `suppliers` |
| Bảng đầu đơn và chiều suy biến | `orders` giữ ngày, kênh, khách, chiến dịch của từng đơn. Theo Kimball [4], đây là phần "đầu đơn" của sự kiện bán hàng, không phải một chiều thật: mã đơn đóng vai **chiều suy biến** trong `order_items`, còn ngày, kênh, khách, chiến dịch là khóa trỏ tới các chiều |
| Luật kết hợp | Ví dụ laptop → chuột ở mục 1.4.1 |
| Data mart / view tổng hợp | View `monthly_pnl` (lãi lỗ theo tháng) |
| Siêu dữ liệu | Bảng `metadata`, file `manifest.json` của tài liệu, file kê khai nguồn ảnh |
| Khai phá văn bản | Tìm đoạn tài liệu liên quan cho câu hỏi |
| Phân lớp | Chọn hướng xử lý cho câu hỏi (trả lời, hỏi lại, từ chối…) |
| Đánh giá, chống rò rỉ | Các bộ câu hỏi chia development / validation / held-out |

## Tiểu kết Chương 1

Chương 1 đã trình bày:

- Kho dữ liệu là nơi tổ chức dữ liệu cho phân tích, khác với CSDL giao dịch. Kho có kiến trúc nhiều tầng, dùng mô hình nhiều chiều (bảng sự kiện, bảng chiều) và các thao tác OLAP.
- Khai phá dữ liệu là bước tìm mẫu trong quá trình KDD. Có thể phân loại theo mục đích, loại dữ liệu, kỹ thuật và cách học. Quy trình thực hiện theo KDD hoặc CRISP-DM, trong đó tiền xử lý và đánh giá đúng cách là hai khâu quan trọng nhất.
- Đề tài thuộc nhánh khai phá văn bản và truy xuất thông tin, kết hợp phân lớp. Chương 2 sẽ đi sâu vào các thuật toán của nhánh này.

# CHƯƠNG 2. CÁC PHƯƠNG PHÁP KHAI PHÁ DỮ LIỆU CÙNG NHÁNH VỚI ĐỀ TÀI

## 2.1. Xác định nhánh thuật toán của đề tài

Chatbot của đề tài phải giải hai bài toán khai phá văn bản:

1. **Bài toán phân lớp ý định (intent classification):** đọc câu hỏi và quyết định nó thuộc loại nào: cần tra tài liệu để trả lời, cần hỏi lại vì chưa rõ, nằm ngoài phạm vi cửa hàng, đòi thông tin nội bộ (phải từ chối), hay muốn gặp nhân viên. Đây là bài toán **phân lớp có giám sát**.
2. **Bài toán xếp hạng tài liệu (document ranking):** trong 144 tài liệu đang hiệu lực (chia thành 433 đoạn nhỏ), tìm ra vài đoạn liên quan nhất với câu hỏi. Đây là bài toán **truy xuất thông tin**, dựa trên **độ tương tự** giữa câu hỏi và đoạn văn.

Hai bài toán có chung các bước: tiền xử lý văn bản, biến văn bản thành vector, rồi đo khoảng cách hoặc độ tương tự. Chương này lần lượt trình bày từng bước, và với mỗi bước giới thiệu các thuật toán cùng nhánh, kể cả những thuật toán đề tài không chọn, để thấy vì sao đề tài chọn cách hiện tại.

![Hình 2.1. Các bước khai phá văn bản dùng trong truy xuất thông tin](hinh/h2_1_quy_trinh_khai_pha_van_ban.png)

## 2.2. Tiền xử lý văn bản tiếng Việt

Máy tính không hiểu chữ, chỉ hiểu số. Trước khi biến chữ thành số, cần làm sạch và chuẩn hóa văn bản.

### 2.2.1. Chuẩn hóa Unicode và chữ thường

Một chữ có dấu như "ệ" có thể được lưu theo hai cách: một ký tự ghép sẵn (dạng NFC), hoặc chữ "e" cộng với các dấu rời (dạng NFD). Mắt người thấy giống hệt, nhưng máy so sánh thì thấy khác. Vì vậy bước đầu tiên là đưa mọi văn bản về cùng một dạng, sau đó chuyển hết sang chữ thường.

### 2.2.2. Bỏ dấu

Người dùng hay gõ không dấu: "bao hanh laptop" thay vì "bảo hành laptop". Nếu tài liệu có dấu mà câu hỏi không dấu thì so khớp từ sẽ trượt. Đề tài xử lý bằng cách **bỏ dấu cả hai phía** khi so khớp từ khóa: tách chữ về dạng NFD, xóa các ký tự dấu, đổi "đ" thành "d".

```python
def normalize(text):
    text = unicodedata.normalize('NFD', text.lower().replace('đ', 'd'))
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')
# "Bảo hành Laptop"  →  "bao hanh laptop"
```

> **Điểm kỹ thuật – cái giá của việc bỏ dấu:** bỏ dấu làm nhiều từ khác nghĩa trở nên giống nhau ("bán" và "bàn" đều thành "ban"). Vì vậy đề tài **chỉ bỏ dấu ở phần so khớp từ khóa** (TF-IDF, BM25). Phần vector nhúng vẫn dùng câu có dấu đầy đủ để giữ đúng nghĩa.

### 2.2.3. Tách từ (tokenization)

Tiếng Anh tách từ bằng dấu cách là gần đủ. Tiếng Việt thì khác: dấu cách tách **âm tiết**, không tách **từ**. "Máy tính xách tay" là một từ gồm 4 âm tiết. Có hai cách làm:

- **Tách theo âm tiết**, rồi dùng **n-gram** (ghép n âm tiết liền nhau) để giữ được từ ghép. Với n-gram 1–2, câu "bảo hành laptop" cho các đơn vị: "bảo", "hành", "laptop", "bảo hành", "hành laptop". Đề tài dùng cách này cho TF-IDF.
- **Tách từ bằng công cụ riêng cho tiếng Việt**, như `pyvi`, cho ra "bảo_hành laptop". Đề tài dùng cách này trước khi đưa câu vào mô hình vector nhúng, vì mô hình PhoBERT được huấn luyện trên văn bản đã tách từ.

Đề tài giữ lại các mã có gạch ngang như "C-BTS", "B12M-081SG" thành một token, vì đây là mã khuyến mãi hoặc mã máy, không được cắt rời.

Tách từ không phải lúc nào cũng có lợi. Dao và cộng sự (VinAI) [38] dựng bộ dữ liệu PhoATIS (5.871 câu, 28 ý định, 82 loại thông tin cần trích) cho bài toán nhận diện ý định tiếng Việt. Kết luận của họ: với bài toán nhận diện ý định và trích thông tin, tách từ tự động và PhoBERT **kém hiệu quả hơn** so với ở các bài toán tiếng Việt khác; mô hình làm trên âm tiết không thua mô hình làm trên từ đã tách. Vì vậy đề tài chỉ tách từ cho bước vector nhúng (mô hình bắt buộc), còn TF-IDF và BM25 làm việc trên âm tiết.

### 2.2.4. Sửa lỗi gõ và từ viết tắt

Người dùng hay viết tắt: "bh" (bảo hành), "ko" hoặc "k" (không), "hd" (hóa đơn). Đề tài có một bảng viết tắt nhỏ để mở rộng trước khi tìm. Với lỗi gõ, đề tài so mỗi từ (từ 4 chữ cái trở lên) với kho từ vựng của tài liệu bằng thư viện `difflib`. Nếu có **đúng một** từ trong kho đủ giống (độ giống từ 0,75 đến 0,85 tùy độ dài) thì sửa theo từ đó; có nhiều ứng viên thì giữ nguyên, để tránh sửa sai.

> **Điểm kỹ thuật:** việc sửa lỗi chỉ dùng cho **phần tìm kiếm**. Câu hỏi gốc của người dùng không bị thay đổi, và các con số không bao giờ bị "sửa".

### 2.2.5. Từ dừng (stop words)

Từ dừng là các từ xuất hiện ở hầu hết mọi câu nhưng ít mang nghĩa: "là", "và", "của", "thì". Nhiều hệ thống bỏ chúng đi. Đề tài **không bỏ** từ dừng một cách cứng nhắc. Lý do là TF-IDF và BM25 đã tự giảm trọng số của các từ xuất hiện khắp nơi (xem mục 2.3.2), còn bỏ cứng có thể làm mất nghĩa, ví dụ chữ "không" trong "có trả góp không".

## 2.3. Biểu diễn văn bản

### 2.3.1. Túi từ (Bag of Words)

Cách đơn giản nhất: lập danh sách mọi từ có trong kho tài liệu (gọi là **từ vựng**), rồi biểu diễn mỗi văn bản bằng một vector đếm số lần mỗi từ xuất hiện. Thứ tự từ bị bỏ qua, như đổ tất cả từ vào một cái túi.

Ví dụ với từ vựng [bảo, hành, laptop, gaming]:

- "bảo hành laptop" → (1, 1, 1, 0)
- "laptop gaming" → (0, 0, 1, 1)

Nhược điểm: từ nào cũng được coi quan trọng như nhau. Từ "laptop" có ở mọi tài liệu về laptop nên chẳng giúp phân biệt được gì, nhưng vẫn được tính điểm như từ "bảo hành".

### 2.3.2. TF-IDF

TF-IDF sửa nhược điểm trên bằng cách nhân hai thành phần [11], [12]:

```math
\mathrm{TF}(t, d) = \frac{\text{số lần từ } t \text{ xuất hiện trong } d}{\text{tổng số từ của } d}
\mathrm{IDF}(t) = \ln \frac{N}{\mathrm{df}(t)}
\mathrm{TF\text{-}IDF}(t, d) = \mathrm{TF}(t, d) \times \mathrm{IDF}(t)
```

Trong đó N là tổng số tài liệu, df(t) là số tài liệu có chứa từ t.

Ý nghĩa:

- **TF** (tần suất từ): từ xuất hiện nhiều trong tài liệu này thì quan trọng với tài liệu này.
- **IDF** (nghịch đảo tần suất tài liệu): từ xuất hiện trong càng nhiều tài liệu thì càng ít giá trị phân biệt. Từ có ở **mọi** tài liệu thì IDF = ln(1) = 0.

**Ví dụ tính tay.** Kho có 3 tài liệu (đã bỏ dấu):

- D1 = "laptop gaming ram 16gb man hinh 144hz" (7 từ)
- D2 = "chinh sach bao hanh laptop 24 thang tai cua hang" (10 từ)
- D3 = "ram ddr5 toc do cao cho laptop gaming" (8 từ)

Câu hỏi q = "bao hanh laptop".

*Bảng 2.1. Tính IDF cho các từ trong câu hỏi*

| Từ | df (số tài liệu chứa) | IDF = ln(3/df) |
|---|---|---|
| bao | 1 (chỉ D2) | ln 3 = 1,0986 |
| hanh | 1 (chỉ D2) | 1,0986 |
| laptop | 3 (cả ba) | ln 1 = 0 |

**Bản đơn giản hóa: cộng TF-IDF của các từ trong câu hỏi.** Điểm của D2 = (1/10)×1,0986 + (1/10)×1,0986 + (1/10)×0 = **0,2197**. D1 và D3 không chứa "bao", "hanh" nên được **0**. Như vậy D2 (tài liệu bảo hành) đứng đầu, đúng như mong đợi.

**Bản đúng quy trình: cosine giữa hai vector TF-IDF** (mô hình không gian vector, mục 2.5.1). Vector câu hỏi chỉ có hai số khác 0: "bao" và "hanh", mỗi số bằng (1/3) × 1,0986 = 0,3662. Vector D2 có 9 số bằng (1/10) × 1,0986 = 0,1099 (9 từ chỉ có ở D2) và số 0 ở chỗ "laptop".

```text
q · D2   = 0,3662 × 0,1099 + 0,3662 × 0,1099      = 0,0805
‖q‖      = 0,3662 × √2                            = 0,5179
‖D2‖     = 0,1099 × √9                            = 0,3296
cos(q, D2) = 0,0805 / (0,5179 × 0,3296)           = 0,4714
cos(q, D1) = cos(q, D3) = 0      (không có từ chung nào có IDF > 0)
```

Hai cách cho cùng thứ tự ở ví dụ này. Cosine còn chia cho độ dài vector, nên tài liệu dài không được lợi chỉ vì có nhiều từ.

Ví dụ cũng cho thấy một điểm yếu: từ "laptop" có IDF = 0, tức là bị bỏ hẳn. Nếu câu hỏi chỉ là "laptop" thì không tài liệu nào có điểm. BM25 ở mục 2.5.2 khắc phục điểm này.

> **Điểm kỹ thuật – TF-IDF trong thư viện:** đề tài dùng `TfidfVectorizer` của scikit-learn [37] với n-gram 1–2. Thư viện này dùng IDF "làm trơn" `ln((1+N)/(1+df)) + 1`, nên từ có ở mọi tài liệu vẫn được IDF = 1 thay vì 0. Sau đó mỗi vector được chuẩn hóa về độ dài 1, để tài liệu dài không được lợi chỉ vì dài.

### 2.3.3. Vector nhúng (embedding)

TF-IDF chỉ so **mặt chữ**. Câu "máy này pin trâu không" và tài liệu "thời lượng sử dụng lên tới 10 giờ" không có từ nào chung, nên TF-IDF cho điểm 0, dù nghĩa rất liên quan. Vector nhúng giải quyết bằng cách biểu diễn **nghĩa** chứ không phải mặt chữ.

Các bước phát triển:

1. **Word2Vec, GloVe (2013–2014):** mỗi từ có một vector cố định, học từ việc từ nào hay đứng cạnh từ nào. "vua" − "đàn ông" + "phụ nữ" ≈ "nữ hoàng". Nhược điểm: một từ chỉ có một vector, dù từ đó nhiều nghĩa ("đường" ăn hay "đường" đi).
2. **BERT (2018) [16]:** mô hình transformer đọc **cả câu** rồi mới cho vector của từng từ, nên cùng một từ trong hai ngữ cảnh khác nhau có vector khác nhau. BERT được huấn luyện bằng cách che bớt từ trong câu rồi bắt đoán lại (học tự giám sát).
3. **PhoBERT (2020) [10]:** BERT huấn luyện riêng trên 20 GB văn bản tiếng Việt, đã tách từ. Cho kết quả tốt hơn mô hình đa ngôn ngữ trên các bài toán tiếng Việt.
4. **Sentence-BERT (2019) [15]:** tinh chỉnh BERT để vector **của cả câu** có ý nghĩa: hai câu cùng nghĩa thì vector gần nhau. Vector câu thường lấy bằng **trung bình cộng** vector các từ (mean pooling).

Đề tài dùng mô hình **vietnamese-embedding** [32]: một Sentence-BERT xây trên PhoBERT, cho mỗi câu một vector **768 số**. Vector được chuẩn hóa về độ dài 1 (chuẩn L2), nên phép nhân vô hướng giữa hai vector chính bằng cosine của góc giữa chúng.

> **Điểm kỹ thuật – giới hạn độ dài là 256 token, không phải 512:** hai file cấu hình của mô hình [49] ghi hai con số khác nhau. File `sentence_bert_config.json` ghi `max_seq_length = 512`, nhưng file `config.json` ghi `max_position_embeddings = 258`, tức bảng vị trí của mô hình chỉ có 258 ô. Mô hình kiểu RoBERTa (PhoBERT thuộc loại này) dành 2 ô cho ký hiệu đặc biệt, nên đọc được tối đa **258 − 2 = 256 token**. Đưa vào dài hơn sẽ lỗi, vì vị trí thứ 257 không có trong bảng. Code của đề tài lấy con số thật từ mô hình: `limit = min(512, model.config.max_position_embeddings − 2) = 256` (file `scripts/vietnamese_embedding_service.py`). Phần vượt 256 token bị cắt và không được tính vào vector; mỗi đoạn có cờ `truncated` ghi lại việc này.

Con số 256 token là lý do đề tài chia đoạn **100 từ** khi bật vector nhúng, thay vì 180 từ. Đo trên 144 tài liệu đang hiệu lực, bằng chính bộ tách token của mô hình (sau khi tách từ bằng `pyvi`): mỗi "từ" (đếm theo dấu cách, tức là âm tiết) trung bình thành khoảng 1,85 token, vì chữ hiếm, số và mã sản phẩm bị cắt thành nhiều mảnh.

*Bảng 2.2. Độ dài đoạn theo token và tỉ lệ đoạn bị cắt*

| Giới hạn | Số đoạn | Trung vị số token | 95% số đoạn dưới | Dài nhất | Số đoạn vượt 256 token |
|---|---|---|---|---|---|
| 100 từ | 433 | 136 | 268 | 368 | 25 (5,8%) |
| 180 từ | 311 | 145 | 414 | 522 | 60 (19,3%) |

Với đoạn 180 từ, gần một phần năm số đoạn bị cắt mất phần cuối; với đoạn 100 từ chỉ còn 5,8%. Số 25 đoạn bị cắt cũng khớp với số đoạn có cờ `truncated` trong bộ nhớ đệm vector của hệ thống.

**Vì sao chọn mô hình dựa trên PhoBERT.** Bộ đánh giá VN-MTEB [39] (41 bộ dữ liệu, 6 loại tác vụ, 18 mô hình) cho thấy các mô hình lớn hơn, dùng mã hóa vị trí xoay (RoPE), làm tốt hơn các mô hình dùng vị trí tuyệt đối như kiểu BERT. Các lựa chọn mạnh hơn gồm bge-m3 [51] (khoảng 568 triệu tham số, đọc được 8.192 token) và multilingual-e5 [52]. Đề tài vẫn chọn vietnamese-embedding vì: (1) nhẹ, khoảng 135 triệu tham số, file 540 MB, chạy được trên CPU của máy cá nhân cùng lúc với Qwen3 4B; (2) huấn luyện riêng cho tiếng Việt; (3) giới hạn 256 token không phải vấn đề lớn khi đoạn đã được chia 100 từ. Đổi sang mô hình RoPE là một hướng cải tiến, cần đo lại trên các bộ câu hỏi trước khi dùng.

## 2.4. Các độ đo tương tự

Khi văn bản đã thành vector, "hai văn bản giống nhau" trở thành "hai vector gần nhau". Có nhiều cách đo:

*Bảng 2.3. Các độ đo tương tự và khoảng cách thường dùng*

| Độ đo | Công thức | Ý nghĩa | Dùng khi |
|---|---|---|---|
| Cosine | cos(a, b) = (a · b) / (‖a‖ × ‖b‖) | Góc giữa hai vector, không quan tâm độ dài | Văn bản (TF-IDF, vector nhúng) |
| Tích vô hướng | a · b = Σ aᵢ × bᵢ | Như cosine nhưng có tính độ dài | Vector đã chuẩn hóa (khi đó bằng cosine) |
| Khoảng cách Euclid | d = √Σ (aᵢ − bᵢ)² | Khoảng cách đường thẳng | Dữ liệu số đã chuẩn hóa thang đo |
| Jaccard | \|A ∩ B\| / \|A ∪ B\| | Tỉ lệ phần chung của hai tập | Tập từ khóa, giỏ hàng |

![Hình 2.2. Mô hình không gian vector: câu hỏi gần với tài liệu bảo hành hơn tài liệu gaming](hinh/h2_2_khong_gian_vector.png)

**Ví dụ tính cosine** với vector 3 chiều:

```text
q  = (0,8; 0,1; 0,3)      câu hỏi
d1 = (0,7; 0,2; 0,4)      tài liệu cùng chủ đề
d2 = (0,1; 0,9; 0,2)      tài liệu khác chủ đề

q · d1 = 0,56 + 0,02 + 0,12 = 0,70
‖q‖  = √(0,64 + 0,01 + 0,09) = 0,8602
‖d1‖ = √(0,49 + 0,04 + 0,16) = 0,8307
cos(q, d1) = 0,70 / (0,8602 × 0,8307) = 0,9796   → rất giống

cos(q, d2) = 0,2883                                → khác
```

Cosine được ưa dùng cho văn bản vì nó không bị ảnh hưởng bởi độ dài: một tài liệu dài gấp đôi nhưng cùng tỉ lệ từ thì vẫn có cùng hướng, nên cosine bằng nhau.

## 2.5. Các thuật toán xếp hạng tài liệu

### 2.5.1. Mô hình không gian vector với TF-IDF

Mô hình không gian vector (Vector Space Model – Salton) [12] là thuật toán xếp hạng kinh điển:

1. Biến mọi tài liệu thành vector TF-IDF (làm một lần, lưu lại).
2. Biến câu hỏi thành vector TF-IDF bằng cùng từ vựng.
3. Tính cosine giữa câu hỏi và từng tài liệu.
4. Sắp xếp giảm dần, lấy k tài liệu đầu (**top-k**).

Ưu điểm: nhanh, dễ hiểu, không cần huấn luyện. Nhược điểm: chỉ so mặt chữ, không hiểu từ đồng nghĩa.

### 2.5.2. BM25

BM25 (Okapi BM25) do Robertson và cộng sự phát triển, dựa trên mô hình xác suất về độ liên quan [13]. Đây là thuật toán mặc định của nhiều máy tìm kiếm như Elasticsearch, Lucene.

```math
\mathrm{BM25}(D, Q) = \sum_{t \in Q} \mathrm{IDF}(t) \cdot \frac{f(t, D) \cdot (k_1 + 1)}{f(t, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\mathrm{avgdl}}\right)}
\mathrm{IDF}(t) = \ln\left(1 + \frac{N - n(t) + 0{,}5}{n(t) + 0{,}5}\right)
```

Trong đó:

- f(t, D): số lần từ t xuất hiện trong tài liệu D;
- |D|: độ dài tài liệu D (số từ); avgdl: độ dài trung bình của các tài liệu;
- n(t): số tài liệu chứa t; N: tổng số tài liệu;
- k₁, b: hai tham số, thường k₁ = 1,2 và b = 0,75.

BM25 cải tiến TF-IDF ở ba điểm:

1. **Bão hòa tần suất (tham số k1):** với TF-IDF, từ xuất hiện 10 lần được điểm gấp 10 lần xuất hiện 1 lần. Với BM25, phần tần suất tăng chậm dần rồi chạm trần là k1 + 1 = 2,2. Lý do: một tài liệu nhắc "bảo hành" 10 lần không liên quan hơn gấp 10 lần tài liệu nhắc 2 lần.
2. **Chuẩn hóa độ dài (tham số b):** tài liệu dài tự nhiên chứa nhiều từ hơn. Với b = 0,75, tài liệu dài hơn trung bình bị giảm điểm, tài liệu ngắn hơn được tăng điểm. Khi b = 0 thì bỏ hẳn phần chuẩn hóa này.
3. **IDF luôn dương:** nhờ "1 +" trong logarit, từ có ở mọi tài liệu vẫn được một chút điểm, không bị về 0 như TF-IDF cổ điển.

> **Điểm kỹ thuật – có nhiều phiên bản BM25, đề tài dùng bản nào:** công thức IDF có "1 +" ở trên là bản của Lucene và Elasticsearch [47]. Bản gốc của Robertson [13] là IDF(t) = ln((N − n(t) + 0,5) / (n(t) + 0,5)), **không có "1 +"**. Với bản gốc, từ có ở hơn một nửa số tài liệu sẽ có IDF âm, tức là càng chứa từ đó thì điểm càng thấp. Thư viện `rank_bm25` (lớp `BM25Okapi`) [48] dùng bản gốc, rồi thay các IDF âm bằng một giá trị sàn nhỏ (epsilon × IDF trung bình). Đề tài **không dùng thư viện** mà tự cài BM25 trong hàm `bm25_scores` của file `shopbot/retrieval.py`, theo bản Lucene có "1 +", với k₁ = 1,2 và b = 0,75. Công thức trong mục này và ví dụ tính tay dưới đây đều đúng với code đó (code rút gọn ở mục 3.7).

**Ví dụ tính tay** với cùng ba tài liệu ở mục 2.3.2 (N = 3, avgdl = (7 + 10 + 8)/3 = 8,333):

*Bảng 2.4. IDF theo công thức BM25*

| Từ | n(t) | IDF = ln(1 + (3 − n + 0,5)/(n + 0,5)) |
|---|---|---|
| bao | 1 | ln(1 + 2,5/1,5) = 0,9808 |
| hanh | 1 | 0,9808 |
| laptop | 3 | ln(1 + 0,5/3,5) = 0,1335 |

Với D2 (|D| = 10, mỗi từ xuất hiện 1 lần), phần mẫu số là 1 + 1,2 × (0,25 + 0,75 × 10/8,333) = 2,38:

```text
bao    : 0,9808 × (1 × 2,2) / 2,38 = 0,9066
hanh   : 0,9066
laptop : 0,1335 × 2,2 / 2,38       = 0,1234
BM25(D2) = 1,9366
```

*Bảng 2.5. Kết quả xếp hạng bằng BM25 so với TF-IDF cổ điển*

| Tài liệu | TF-IDF cổ điển | BM25 | Ghi chú |
|---|---|---|---|
| D2 (chính sách bảo hành) | 0,2197 | **1,9366** | Đứng đầu ở cả hai cách |
| D1 (laptop gaming, 7 từ) | 0 | 0,1429 | BM25 vẫn cho điểm vì có "laptop" |
| D3 (RAM DDR5, 8 từ) | 0 | 0,1358 | D3 dài hơn D1 nên điểm thấp hơn một chút |

Kết quả cho thấy: BM25 vẫn xếp D2 lên đầu với khoảng cách rất xa, đồng thời phân biệt được D1 và D3 (TF-IDF cổ điển coi chúng bằng nhau ở 0). D3 dài hơn D1 nên bị phạt nhẹ nhờ tham số b.

> **Điểm kỹ thuật – vì sao đề tài giữ cả TF-IDF lẫn BM25:** hai cách chuẩn hóa khác nhau. TF-IDF có n-gram 2 từ nên bắt tốt cụm từ ("bao hanh"), còn BM25 tách token giữ nguyên mã có gạch ngang ("c-bts", "b12m-081sg") nên bắt tốt mã sản phẩm và mã khuyến mãi. Khi trộn thứ hạng (mục 2.5.4), mỗi cách bù chỗ yếu của cách kia.

### 2.5.3. Truy xuất dày (dense retrieval) và xếp hạng lại

TF-IDF và BM25 được gọi là **truy xuất thưa (sparse retrieval)**, vì vector có hàng chục nghìn chiều (mỗi từ một chiều) nhưng gần như toàn số 0. Dùng vector nhúng 768 chiều, chiều nào cũng có giá trị, thì gọi là **truy xuất dày (dense retrieval)** [17].

![Hình 2.3. Bi-encoder mã hóa riêng từng bên; cross-encoder đọc cả câu hỏi và đoạn văn cùng lúc](hinh/h2_4_bi_cross_encoder.png)

Có hai kiến trúc (Hình 2.3):

- **Bi-encoder:** mã hóa câu hỏi và đoạn văn **riêng rẽ** thành hai vector, rồi tính cosine. Vector của đoạn văn tính trước một lần và lưu lại, nên khi có câu hỏi mới chỉ cần mã hóa câu hỏi. Đây là cách dùng để **tìm** trong kho lớn. Đề tài dùng cách này.
- **Cross-encoder:** đưa **cả câu hỏi và đoạn văn** vào mô hình cùng lúc, mô hình so từng từ của hai bên với nhau rồi cho ra một điểm liên quan [18]. Chính xác hơn, nhưng phải chạy mô hình một lần cho **mỗi cặp**, nên chỉ dùng để **xếp lại** vài chục ứng viên đã tìm bằng bi-encoder. Đề tài đã huấn luyện thử một bộ xếp lại kiểu này (`evidence_reranker`) nhưng chưa bật, vì chưa qua hết các bộ đánh giá.

Khi kho rất lớn (hàng triệu đoạn), tính cosine với từng đoạn quá chậm. Khi đó người ta dùng **tìm láng giềng gần đúng (Approximate Nearest Neighbor – ANN)**, như đồ thị HNSW [19] hoặc thư viện FAISS: chấp nhận đôi khi sót một kết quả để đổi lấy tốc độ nhanh gấp hàng trăm lần. Kho của đề tài chỉ khoảng 430 đoạn, nên **tính đúng với từng đoạn** vẫn nhanh, không cần ANN. Vector được lưu đệm (cache) theo mã băm của nội dung đoạn, nên chỉ đoạn mới hoặc đoạn bị sửa mới phải tính lại.

### 2.5.4. Trộn nhiều cách xếp hạng (rank fusion)

Mỗi cách xếp hạng có điểm mạnh riêng:

- TF-IDF giỏi cụm từ.
- BM25 giỏi mã sản phẩm, từ hiếm.
- Vector nhúng giỏi từ đồng nghĩa, cách hỏi khác mặt chữ.

Kết hợp chúng gọi là **truy xuất lai (hybrid retrieval)**. Vấn đề là ba cách cho điểm theo ba thang khác nhau: cosine TF-IDF từ 0 đến 1, BM25 có thể lên 5–10, cosine vector nhúng thường từ 0,3 đến 0,9. Cộng thẳng thì BM25 lấn át hết.

Có hai hướng giải quyết:

1. **Trộn theo điểm (CombSUM, tổ hợp lồi):** chuẩn hóa điểm của mỗi cách về [0, 1] rồi cộng có trọng số. Có thể tốt hơn nếu chỉnh trọng số kỹ, nhưng phải có dữ liệu để chỉnh, và trọng số tốt cho bộ này chưa chắc tốt cho bộ khác.
2. **Trộn theo thứ hạng (Reciprocal Rank Fusion – RRF)** [14]: bỏ qua điểm, chỉ dùng **thứ hạng**.

```math
\mathrm{RRF}(d) = \sum_{r \in R} \frac{1}{k + \mathrm{hạng}_r(d)}
```

Trong đó R là tập các bảng xếp hạng; hạng_r(d) là vị trí của d trong bảng r (bắt đầu từ 1); k là hằng số, Cormack và cộng sự đề xuất k = 60.

Hằng số k = 60 làm chênh lệch giữa hạng 1 và hạng 2 không quá lớn, nên một đoạn **được nhiều cách xếp khá cao** sẽ thắng một đoạn **chỉ được một cách xếp hạng 1**.

![Hình 2.4. Ví dụ trộn thứ hạng RRF với ba bảng xếp hạng](hinh/h2_5_tron_thu_hang_rrf.png)

**Ví dụ tính tay** (Hình 2.4). Bốn đoạn A, B, C, D được ba cách xếp như sau:

*Bảng 2.6. Tính điểm RRF*

| Đoạn | Hạng TF-IDF | Hạng BM25 | Hạng vector | Điểm RRF |
|---|---|---|---|---|
| A | 1 | 2 | 3 | 1/61 + 1/62 + 1/63 = 0,04840 |
| B | 2 | 1 | 2 | 1/62 + 1/61 + 1/62 = **0,04865** |
| C | 3 | 4 | 1 | 1/63 + 1/64 + 1/61 = 0,04789 |
| D | 4 | 3 | 4 | 1/64 + 1/63 + 1/64 = 0,04712 |

Đoạn B không đứng đầu ở TF-IDF hay vector, nhưng đứng thứ 1 hoặc 2 ở cả ba bảng, nên lên đầu sau khi trộn. Đoạn C được vector xếp hạng 1, nhưng hai cách kia xếp thấp, nên chỉ đứng thứ ba.

> **Điểm kỹ thuật – vì sao đề tài chọn RRF:** RRF không cần dữ liệu để chỉnh trọng số, không cần chuẩn hóa điểm, và khi một nguồn bị lỗi (ví dụ dịch vụ vector không chạy) thì chỉ cần bỏ bảng đó ra. Cormack và cộng sự cho thấy RRF tốt hơn từng hệ thống riêng lẻ và tốt hơn phương pháp Condorcet trên nhiều bộ dữ liệu TREC [14].

### 2.5.5. Chia đoạn tài liệu (chunking)

Các thuật toán xếp hạng ở trên không chấm cả tài liệu mà chấm từng **đoạn**. Lý do: tài liệu dài thường bàn nhiều ý, trong khi câu hỏi chỉ cần một ý; mô hình vector nhúng có giới hạn độ dài (256 token, mục 2.3.3); và bước trả lời chỉ đọc được vài đoạn. Cách chia đoạn vì vậy ảnh hưởng trực tiếp tới việc tìm đúng.

*Bảng 2.7. Các cách chia đoạn tài liệu*

| Cách chia | Làm thế nào | Ưu điểm | Nhược điểm |
|---|---|---|---|
| Theo số từ (hoặc số token) cố định | Cắt mỗi n từ một lần | Đơn giản, đoạn đều nhau | Hay cắt ngang câu, ngang bảng |
| Theo câu | Gom các câu liền nhau đến khi đủ độ dài | Không cắt ngang câu | Đoạn dài ngắn không đều |
| Theo nghĩa (semantic) | Dùng vector nhúng của từng câu, cắt ở chỗ hai câu liền nhau khác nghĩa nhiều | Mỗi đoạn một ý | Tốn công tính vector khi lập chỉ mục |
| Theo cấu trúc | Cắt theo tiêu đề, đoạn văn, bảng | Giữ được ngữ cảnh "đoạn này thuộc mục nào" | Cần tài liệu có cấu trúc rõ |
| Có chồng lấn (overlap) | Đoạn sau lặp lại vài câu cuối của đoạn trước | Ý nằm ở ranh giới không bị mất | Nhiều đoạn hơn, tốn chỗ và thời gian lập chỉ mục |

Bennani và Moslonka (2026) [40] so sánh các cách này cho bài toán hỏi đáp có truy xuất. Ba kết luận chính: **chồng lấn không giúp gì đo được mà còn tăng chi phí lập chỉ mục**; **chia theo câu là cách lợi nhất về chi phí**, cho kết quả ngang chia theo nghĩa khi ngữ cảnh đến khoảng 5.000 token; và chất lượng tụt khi ngữ cảnh đưa cho mô hình vượt khoảng 2.500 token.

> **Liên hệ đề tài:** hàm `chunk_document` (file `shopbot/chunking.py`) chia **theo cấu trúc rồi theo câu**, không có chồng lấn. Cụ thể: cắt theo tiêu đề; mỗi đoạn mang đường dẫn tiêu đề ở đầu ("Chính sách bảo hành > Điều kiện"); bảng được chia theo nhóm dòng và lặp lại dòng tiêu đề của bảng; đoạn văn dài được gom theo câu đến khi gần chạm giới hạn 100 từ (180 từ khi không dùng vector nhúng); chỉ câu dài bất thường mới bị cắt theo số từ, và không bỏ mất từ nào. Cách làm này khớp với kết luận của [40]: không tốn chi phí cho chồng lấn, không cắt ngang câu. Giới hạn 100 từ được chọn theo số token đo được ở Bảng 2.2.

### 2.5.6. Các hướng khác cùng nhánh

Một số kỹ thuật truy xuất khác thuộc cùng nhánh, đề tài chưa dùng:

- **Mở rộng câu hỏi (query expansion), thuật toán Rocchio [43]:** thêm vào câu hỏi những từ hay đi cùng trong các tài liệu tìm được đầu tiên, rồi tìm lại. Ví dụ câu hỏi "pin trâu" được thêm "thời lượng", "giờ sử dụng". Đề tài mới làm một phần nhỏ của ý này: mở rộng từ viết tắt ("bh" → "bảo hành").
- **SPLADE [41] (truy xuất thưa có học):** vẫn là vector thưa như BM25, nhưng trọng số mỗi từ do mô hình transformer học ra, và mô hình còn tự thêm các từ liên quan không có trong câu. Có được cái lợi của so khớp từ khóa (nhanh, giải thích được) lẫn hiểu nghĩa.
- **ColBERT [42] (tương tác muộn):** nằm giữa bi-encoder và cross-encoder. Mỗi **từ** của đoạn văn có một vector, tính trước và lưu lại; khi có câu hỏi, mỗi từ của câu hỏi tìm từ giống nhất trong đoạn rồi cộng điểm. Chính xác gần cross-encoder nhưng vẫn tìm được trong kho lớn, đổi lại tốn chỗ lưu hơn nhiều.

## 2.6. Các thuật toán phân lớp cùng nhánh

### 2.6.1. Bài toán phân lớp ý định

- **Đầu vào:** câu hỏi (kèm vai trò người hỏi và vài lượt hội thoại trước).
- **Đầu ra:** một nhãn trong tập nhãn cố định. Trong đề tài, các nhãn chính là: `answer` (tra tài liệu để trả lời), `clarify` (hỏi lại vì chưa rõ), `outside` (ngoài phạm vi), `deferred` (cần công cụ chưa có), `live_product` (cần giá/tồn kho thời gian thực, đặt hàng), `handoff` (gặp nhân viên), `denied` (từ chối vì là thông tin nội bộ).
- **Dữ liệu học:** các cặp (câu hỏi, nhãn đúng).

**Nhãn bị lệch (mất cân bằng).** Phần lớn câu hỏi là câu cần tra tài liệu để trả lời; các nhãn khác rất hiếm. Trong dữ liệu huấn luyện router v5 (640 câu), nhãn `answer` chiếm 530 câu (82,8%), còn `handoff` chỉ có 4 câu và `live_product` 6 câu. Trên 810 câu hỏi development của các bộ đánh giá mở, `answer` chiếm 679 câu (83,8%). Một mô hình chỉ luôn đoán `answer` đã đúng 83,8%, nên **độ chính xác chung (accuracy) không nói được mô hình có tốt hay không**. Cách đo và cách xử lý nhãn lệch ở mục 2.8.1.

Dưới đây là các thuật toán phân lớp kinh điển. kNN, Naive Bayes, SVM và C4.5/CART nằm trong danh sách 10 thuật toán khai phá dữ liệu tiêu biểu [6]. Hồi quy logistic không có trong danh sách đó, nhưng được trình bày vì đây là mốc so sánh chuẩn cho bài toán phân loại văn bản.

### 2.6.2. k láng giềng gần nhất (kNN)

![Hình 2.5. kNN với k = 5: câu hỏi mới được gán nhãn theo đa số trong 5 điểm gần nhất](hinh/h2_3_knn.png)

**Ý tưởng:** "Gần mực thì đen". Câu hỏi mới giống những câu hỏi nào đã có nhãn, thì có lẽ cùng nhãn với chúng [20].

**Thuật toán:**

1. Biến mọi câu hỏi có nhãn thành vector (TF-IDF hoặc vector nhúng).
2. Với câu hỏi mới, tính khoảng cách (hoặc cosine) tới mọi câu đã có nhãn.
3. Lấy k câu gần nhất.
4. Gán nhãn chiếm đa số trong k câu đó. Có thể cho câu gần hơn phiếu nặng hơn (kNN có trọng số).

**Ưu điểm:** không cần huấn luyện, thêm ví dụ mới là dùng được ngay, giải thích dễ ("vì giống 5 câu này").
**Nhược điểm:** chậm khi dữ liệu lớn (phải so với mọi điểm); nhạy với việc chọn k và cách đo khoảng cách; kém khi các nhãn có số mẫu chênh lệch nhiều.
**Chọn k:** thường thử nhiều giá trị lẻ (3, 5, 7…) trên tập kiểm định. k nhỏ thì dễ bị nhiễu, k lớn thì ranh giới bị nhòe.

> **Liên hệ đề tài:** việc **tìm tài liệu** bằng cosine chính là phiên bản "không bỏ phiếu" của kNN: lấy k đoạn gần câu hỏi nhất. Vì vậy truy xuất thông tin và kNN cùng một nhánh dựa trên khoảng cách.

### 2.6.3. Naive Bayes đa thức

**Ý tưởng:** dùng định lý Bayes để tính xác suất câu hỏi thuộc mỗi nhãn, với giả định "ngây thơ" rằng các từ xuất hiện độc lập với nhau [29].

```math
P(c \mid \text{câu}) \propto P(c) \cdot \prod_{i} P(w_i \mid c)
P(w \mid c) = \frac{\mathrm{count}(w, c) + 1}{\mathrm{count}(c) + |V|}
```

Trong đó c là nhãn; count(w, c) là số lần từ w xuất hiện trong các câu của nhãn c; count(c) là tổng số từ của nhãn c; |V| là số từ khác nhau trong dữ liệu học. Phép cộng 1 ở tử số gọi là **làm trơn Laplace**: nó tránh trường hợp một từ chưa từng gặp ở một nhãn làm cả tích bằng 0.

**Ví dụ tính tay.** Dữ liệu học có 4 câu (đã bỏ dấu), hai nhãn CS ("hỏi chính sách") và SP ("hỏi sản phẩm"):

*Bảng 2.8. Dữ liệu học cho ví dụ Naive Bayes*

| Câu | Nhãn |
|---|---|
| bao hanh bao lau | CS |
| bao hanh doi tra | CS |
| laptop ram bao nhieu | SP |
| chuot bao nhieu tien | SP |

Mỗi nhãn có 8 từ, từ vựng có |V| = 10 từ khác nhau, P(CS) = P(SP) = 2/4 = 0,5. Câu mới: "bao hanh laptop".

```text
                 Nhãn CS                         Nhãn SP
P(bao | ·)    = (3 + 1)/(8 + 10) = 4/18       = (2 + 1)/(8 + 10) = 3/18
P(hanh | ·)   = (2 + 1)/18       = 3/18       = (0 + 1)/18       = 1/18
P(laptop | ·) = (0 + 1)/18       = 1/18       = (1 + 1)/18       = 2/18

Điểm CS = 0,5 × 4 × 3 × 1 / 18³ = 6 / 5.832 = 0,001029
Điểm SP = 0,5 × 3 × 1 × 2 / 18³ = 3 / 5.832 = 0,000514
```

Điểm CS gấp đôi điểm SP, nên câu được gán nhãn **CS** (hỏi chính sách). Có thể thấy rõ cách mô hình "cân" từng từ: "laptop" kéo về SP, nhưng "hanh" chỉ có ở CS nên kéo mạnh hơn. Nhờ làm trơn Laplace, "hanh" chưa từng gặp ở SP vẫn được 1/18 thay vì 0; nếu không có bước này, điểm SP sẽ bằng 0 chỉ vì một từ.

**Ưu điểm:** rất nhanh, cần ít dữ liệu, là mốc so sánh tốt cho phân loại văn bản.
**Nhược điểm:** giả định độc lập sai với ngôn ngữ thật ("không" + "được" khác nghĩa hẳn với từng từ riêng); xác suất tính ra thường bị đẩy quá về 0 hoặc 1.

### 2.6.4. Hồi quy logistic (softmax)

**Ý tưởng:** học một trọng số cho mỗi từ ứng với mỗi nhãn; cộng trọng số của các từ trong câu rồi đưa qua hàm softmax để ra xác suất.

```math
z_c = \mathbf{w}_c \cdot \mathbf{x} + b_c
P(c \mid \mathbf{x}) = \frac{e^{z_c}}{\sum_{j} e^{z_j}}
```

Trong đó **x** là vector TF-IDF của câu, z_c là điểm của nhãn c. Hàm softmax biến các điểm thành xác suất có tổng bằng 1.

Mô hình học bằng cách giảm dần **hàm mất mát cross-entropy** qua nhiều vòng (gradient descent). Ưu điểm: nhanh, xác suất đáng tin hơn Naive Bayes, xem được trọng số để biết từ nào quan trọng. Nhược điểm: vẫn chỉ nhìn từng từ riêng lẻ trên vector TF-IDF, không hiểu thứ tự từ.

### 2.6.5. Máy vector hỗ trợ (SVM)

**Ý tưởng:** tìm một siêu phẳng (đường thẳng trong 2 chiều, mặt phẳng trong 3 chiều…) chia hai nhóm sao cho **khoảng cách tới điểm gần nhất của mỗi nhóm là lớn nhất** [21]. Các điểm nằm sát ranh giới gọi là **vector hỗ trợ**; chỉ chúng quyết định vị trí ranh giới.

- Khi dữ liệu không chia được bằng đường thẳng, SVM dùng **hàm nhân (kernel)** để đưa dữ liệu lên không gian nhiều chiều hơn, nơi có thể chia được.
- Với văn bản (vector TF-IDF rất nhiều chiều), SVM tuyến tính thường đã rất tốt. Trước thời học sâu, đây là một trong những thuật toán phân loại văn bản mạnh nhất.
- Nhiều nhãn: huấn luyện nhiều bộ "một nhãn so với phần còn lại".

### 2.6.6. Cây quyết định và các phương pháp kết hợp

**Cây quyết định (C4.5 [22], CART [23]):** chia dữ liệu bằng chuỗi câu hỏi có/không, ví dụ "câu có chứa 'bảo hành' không?" → "có chứa tên sản phẩm không?" → nhãn. Mỗi lần chia chọn câu hỏi làm dữ liệu "thuần" nhất, đo bằng **entropy** hoặc **độ vẩn đục Gini**:

```math
\mathrm{Entropy}(S) = -\sum_{i} p_i \log_2 p_i
\mathrm{Gini}(S) = 1 - \sum_{i} p_i^2
\mathrm{IG}(S, A) = \mathrm{Entropy}(S) - \sum_{v} \frac{|S_v|}{|S|}\,\mathrm{Entropy}(S_v)
```

Trong đó p_i là tỉ lệ mẫu thuộc nhãn i trong tập S. **Độ lợi thông tin (information gain – IG)** của một câu hỏi chia A là entropy giảm được sau khi chia; S_v là phần dữ liệu ứng với câu trả lời v. C4.5 chọn câu hỏi chia có IG lớn nhất (chính xác hơn là tỉ số IG, để không thiên vị câu hỏi có nhiều nhánh); CART chọn câu hỏi làm Gini giảm nhiều nhất.

**Ví dụ tính tay.** Có 8 câu hỏi: 4 câu "hỏi chính sách" (CS), 4 câu "hỏi sản phẩm" (SP). So hai câu hỏi chia:

- A₁ = "câu có chứa 'bảo hành' không?": nhánh **có** gồm 3 câu, cả 3 là CS; nhánh **không** gồm 5 câu: 1 CS, 4 SP.
- A₂ = "câu có dấu chấm hỏi không?": nhánh **có** gồm 6 câu: 3 CS, 3 SP; nhánh **không** gồm 2 câu: 1 CS, 1 SP.

```text
Entropy(S)            = −(0,5 × log2 0,5 + 0,5 × log2 0,5)      = 1
A₁: Entropy(có)       = 0                                        (toàn CS, đã "thuần")
    Entropy(không)    = −(0,2 × log2 0,2 + 0,8 × log2 0,8)      = 0,7219
    IG(A₁)            = 1 − (3/8 × 0 + 5/8 × 0,7219)             = 0,5488
A₂: Entropy(có)       = Entropy(không) = 1                       (vẫn nửa nọ nửa kia)
    IG(A₂)            = 1 − (6/8 × 1 + 2/8 × 1)                  = 0
Gini(S) = 1 − (0,5² + 0,5²) = 0,5;   Gini(nhánh không của A₁) = 1 − (0,2² + 0,8²) = 0,32
```

Cây chọn A₁ ("có chứa 'bảo hành' không") làm câu hỏi đầu tiên, vì nó tách dữ liệu rõ hơn hẳn. A₂ có IG = 0, tức là hỏi xong không biết thêm gì về nhãn.

Ưu điểm: dễ hiểu, đọc được như luật. Nhược điểm: dễ "học thuộc" dữ liệu (quá khớp – overfitting).

**Các phương pháp kết hợp (ensemble):**

- **Rừng ngẫu nhiên (random forest):** nhiều cây, mỗi cây học trên một phần dữ liệu và một phần đặc trưng ngẫu nhiên, rồi bỏ phiếu.
- **Boosting (AdaBoost, gradient boosting [30]):** các cây học nối tiếp, cây sau sửa lỗi của cây trước. Đề tài dùng `HistGradientBoostingRegressor` trong thử nghiệm dự báo số lượng bán theo ngày, với đặc trưng là số bán của 1, 7, 14, 28 ngày trước và trung bình 7, 28 ngày gần nhất [31].

Với văn bản, cây quyết định làm việc kém hơn SVM hay hồi quy logistic, vì vector TF-IDF có quá nhiều chiều thưa.

### 2.6.7. Mạng nơ-ron và mô hình ngôn ngữ lớn

Các thuật toán trên đều nhìn câu như một túi từ. Mạng nơ-ron hiện đại, cụ thể là **transformer** [27], đọc cả thứ tự từ và ngữ cảnh nhờ cơ chế **chú ý (attention)**: khi xử lý một từ, mô hình "nhìn" sang mọi từ khác trong câu và quyết định từ nào quan trọng với nó. Nhờ vậy nó phân biệt được "máy này có trả góp không" với "máy này không trả góp à".

**Mô hình ngôn ngữ lớn (LLM)** như Qwen3 [26] là transformer có hàng tỉ tham số, học từ lượng văn bản khổng lồ. Có thể dùng LLM để phân lớp theo hai cách:

1. **Không huấn luyện (zero-shot / few-shot):** viết hướng dẫn và vài ví dụ vào câu lệnh (prompt), để mô hình tự chọn nhãn. Nhanh nhưng kết quả dao động, dễ chọn nhãn lạ.
2. **Tinh chỉnh (fine-tune):** huấn luyện thêm trên dữ liệu có nhãn của mình. Kết quả ổn định và đúng định dạng hơn.

Tinh chỉnh toàn bộ một mô hình 4 tỉ tham số cần rất nhiều bộ nhớ GPU. **LoRA** [24] giải quyết việc này.

![Hình 2.6. LoRA: ma trận gốc W đóng băng, chỉ học hai ma trận nhỏ A và B](hinh/h2_6_lora.png)

**Ý tưởng LoRA:** khi tinh chỉnh, phần thay đổi của một ma trận trọng số thường có "hạng thấp", tức là có thể viết gần đúng bằng tích hai ma trận rất hẹp. Vì vậy:

```math
\mathbf{h} = W\mathbf{x} + \frac{\alpha}{r}\, B A \mathbf{x}
```

Trong đó:

- W là ma trận gốc kích thước d_out × d_in, **đóng băng** (không học);
- A là ma trận r × d_in, được học;
- B là ma trận d_out × r, được học, khởi tạo bằng 0;
- r là hạng (rank), rất nhỏ so với d_in và d_out; α là hệ số tỉ lệ.

Một lớp gắn LoRA chỉ học thêm r × (d_in + d_out) tham số thay vì d_in × d_out. Do B khởi tạo bằng 0, lúc bắt đầu mô hình giữ nguyên hành vi gốc, rồi lệch dần theo dữ liệu học.

> **Điểm kỹ thuật – số tham số LoRA thật của đề tài:** các lớp trong Qwen3-4B **không vuông**. Theo file `config.json` của Qwen3-4B-Instruct-2507 [26]: kích thước ẩn 2.560; phần chú ý có 32 đầu truy vấn và 8 đầu khóa/giá trị, mỗi đầu 128 chiều; phần mạng truyền thẳng rộng 9.728; có 36 tầng. Với r = 16, gắn vào 7 lớp chiếu như ở mục 3.8, mỗi tầng có số tham số học như Bảng 2.9.

*Bảng 2.9. Số tham số LoRA (r = 16) của một tầng Qwen3-4B*

| Lớp | d_in → d_out | Tham số gốc | Tham số LoRA = 16 × (d_in + d_out) |
|---|---|---|---|
| q_proj | 2.560 → 4.096 | 10.485.760 | 106.496 |
| k_proj | 2.560 → 1.024 | 2.621.440 | 57.344 |
| v_proj | 2.560 → 1.024 | 2.621.440 | 57.344 |
| o_proj | 4.096 → 2.560 | 10.485.760 | 106.496 |
| gate_proj | 2.560 → 9.728 | 24.903.680 | 196.608 |
| up_proj | 2.560 → 9.728 | 24.903.680 | 196.608 |
| down_proj | 9.728 → 2.560 | 24.903.680 | 196.608 |
| **Một tầng** | | **100.925.440** | **917.504** |

Nhân với 36 tầng: 917.504 × 36 = **33.030.144 tham số được học**, khoảng **0,82%** của khoảng 4,02 tỉ tham số của mô hình. Nói cách khác, LoRA chỉ học chưa tới 1% số tham số mà vẫn đổi được hành vi của mô hình. Cách tính này giống cách thư viện PEFT đếm "trainable parameters", nhưng con số được tính từ cấu hình chứ chưa in ra từ lần huấn luyện; lần train v6 sẽ in con số thật để đối chiếu.

**QLoRA** [25] đi xa thêm một bước: nén mô hình gốc xuống 4 bit để tiết kiệm bộ nhớ, rồi gắn LoRA lên trên. Đề tài dùng cách này để tinh chỉnh Qwen3 4B trên GPU T4 16 GB miễn phí của Kaggle (chi tiết ở mục 3.8).

### 2.6.8. So sánh các thuật toán phân lớp

*Bảng 2.10. So sánh các thuật toán phân lớp văn bản*

| Thuật toán | Cần bao nhiêu dữ liệu | Tốc độ | Hiểu ngữ cảnh, thứ tự từ | Dễ giải thích | Ghi chú |
|---|---|---|---|---|---|
| kNN | Ít | Chậm khi dữ liệu lớn | Tùy vector (TF-IDF: không; vector nhúng: có) | Dễ | Thêm ví dụ là dùng ngay |
| Naive Bayes | Ít | Rất nhanh | Không | Dễ | Mốc so sánh tốt |
| Hồi quy logistic | Vừa | Nhanh | Không | Khá | Xác suất đáng tin |
| SVM | Vừa | Nhanh | Không | Khó | Mạnh với văn bản trước thời học sâu |
| Cây quyết định | Vừa | Nhanh | Không | Rất dễ | Dễ quá khớp, kém với văn bản thưa |
| PhoBERT tinh chỉnh làm bộ phân lớp | Vừa (vài nghìn câu có nhãn) | Nhanh, chạy được trên CPU | Có | Khó | Mốc so sánh mạnh cho tiếng Việt [38] |
| LLM không huấn luyện (zero-shot, có JSON schema) | Không cần, chỉ cần lời nhắc | Chậm, cần GPU | Có | Khó | Router đang dùng của đề tài (Qwen3 4B bản gốc) |
| LLM tinh chỉnh (LoRA) | Vừa đến nhiều | Chậm, cần GPU | Có | Khó | Đề tài dùng cho bước chọn bằng chứng sản phẩm; router tinh chỉnh v5 chưa qua cổng (mục 3.8) |

## 2.7. Kết hợp luật và học máy

Mô hình học máy luôn có tỉ lệ sai nhất định. Với một số trường hợp **rõ ràng và có hậu quả lớn**, ví dụ khách đòi xem lương nhân viên hoặc mật khẩu của người khác, không nên để mô hình "đoán". Cách làm phổ biến là **hệ lai luật – học máy**:

1. **Luật viết tay chạy trước**, bắt các trường hợp chắc chắn bằng biểu thức chính quy (regex). Luật được viết **thận trọng**: chỉ bắt khi rất chắc; không chắc thì nhường cho mô hình.
2. **Mô hình học máy** lo phần còn lại, nơi cách hỏi đa dạng không viết hết thành luật được.

Ưu điểm: những ca quan trọng thì đúng tuyệt đối và giải thích được; mô hình không phải học những ca hiếm. Nhược điểm: luật phải được kiểm thử kỹ để không bắt nhầm câu bình thường. Đề tài kiểm tra mỗi luật mới trên 1.285 câu hỏi mở và đếm số câu bị đổi quyết định (mục 3.6).

**Ngưỡng tin cậy và "không chắc thì hỏi lại".** Một hướng khác để bớt sai là cho mô hình được **từ chối đoán**: nếu xác suất của nhãn tốt nhất thấp hơn một ngưỡng, hệ thống không làm theo nhãn đó mà hỏi lại người dùng. Kỹ thuật này gọi là **phân lớp có lựa chọn (selective classification)** [50]. Hạ ngưỡng thì hệ thống trả lời được nhiều câu hơn nhưng sai nhiều hơn; nâng ngưỡng thì ít sai hơn nhưng hỏi lại nhiều hơn. Điều kiện để dùng được là xác suất của mô hình phải "đáng tin": mô hình nói 90% thì khoảng 90% số lần phải đúng.

Đề tài áp dụng ý này ở ba chỗ, theo đúng mục tiêu "không bịa":

1. **Truy xuất có ngưỡng:** đoạn văn chỉ được dùng khi cosine TF-IDF > 0,08 hoặc cosine vector > 0,45. Không đoạn nào qua ngưỡng thì bot nói "chưa có nguồn", không đoán.
2. **Bước chọn bằng chứng có ô "thiếu":** mô hình phải liệt kê phần nào của câu hỏi chưa có nguồn trả lời (`missing`). Phần đó được trả lời là chưa có thông tin, thay vì để mô hình tự điền.
3. **Câu chỉ trỏ mơ hồ** ("con đó", "máy vừa nói" khi chưa có máy nào) được luật chuyển sang `clarify`.

Router của đề tài là LLM trả về JSON, không trả về xác suất đã hiệu chỉnh, nên **chưa có ngưỡng tin cậy cho router**. Đây là một hướng cải tiến: lấy xác suất của token nhãn, hoặc chạy vài lần rồi đo mức đồng thuận, sau đó chọn ngưỡng trên phần development.

## 2.8. Đánh giá mô hình

### 2.8.1. Đánh giá phân lớp

Với một nhãn cụ thể, ví dụ "từ chối":

*Bảng 2.11. Ma trận nhầm lẫn cho một nhãn*

| | Thực tế: cần từ chối | Thực tế: không cần |
|---|---|---|
| **Máy đoán: từ chối** | TP (đúng) | FP (từ chối oan) |
| **Máy đoán: không từ chối** | FN (để lọt) | TN (đúng) |

```math
\mathrm{Precision} = \frac{TP}{TP + FP}
\mathrm{Recall} = \frac{TP}{TP + FN}
F_1 = \frac{2 \cdot \mathrm{Precision} \cdot \mathrm{Recall}}{\mathrm{Precision} + \mathrm{Recall}}
\mathrm{Accuracy} = \frac{TP + TN}{\text{tổng số câu}}
```

- **Precision:** trong các câu máy từ chối, bao nhiêu câu đáng từ chối.
- **Recall:** trong các câu đáng từ chối, máy bắt được bao nhiêu.

Với nhãn "từ chối", để lọt (FN) nguy hiểm hơn từ chối oan (FP), nên cần ưu tiên **recall**. Với nhãn "trả lời", trả lời bừa (FP) nguy hiểm hơn, nên cần ưu tiên **precision**. Vì vậy không thể chỉ nhìn một con số accuracy chung.

**Nhiều nhãn và nhãn lệch: macro-F1, micro-F1.** Khi có nhiều nhãn, ma trận nhầm lẫn có một hàng và một cột cho mỗi nhãn. Từ đó tính precision, recall, F1 cho **từng** nhãn (coi nhãn đó là "dương", mọi nhãn khác là "âm"), rồi gộp lại theo hai cách:

```math
\text{Macro-}F_1 = \frac{1}{K}\sum_{k=1}^{K} F_{1,k}
\text{Micro-}F_1 = F_1 \text{ tính trên tổng } TP, FP, FN \text{ của mọi nhãn}
```

K là số nhãn. Macro-F1 tính mỗi nhãn **ngang nhau**, nên nhãn hiếm bị sai sẽ kéo điểm xuống rõ. Micro-F1 tính mỗi **câu** ngang nhau; với bài toán mỗi câu một nhãn, micro-F1 bằng đúng accuracy, nên bị nhãn phổ biến lấn át.

Ví dụ thật trên 810 câu development (83,8% là `answer`), mô hình TF-IDF + hồi quy logistic học từ 640 câu của dữ liệu router v5 (chi tiết ở mục 3.10.4):

*Bảng 2.12. Accuracy và macro-F1 khi nhãn bị lệch*

| Mô hình | Accuracy (= micro-F1) | Macro-F1 |
|---|---|---|
| Luôn đoán `answer` | 0,838 | 0,130 |
| TF-IDF + hồi quy logistic, không cân bằng nhãn | 0,872 | 0,396 |
| TF-IDF + hồi quy logistic, có trọng số theo lớp | 0,863 | 0,501 |

Mô hình "luôn đoán `answer`" không làm được gì có ích mà accuracy vẫn 0,838; macro-F1 0,130 mới cho thấy điều đó.

**Trọng số theo lớp (class weight)** là cách xử lý nhãn lệch đơn giản nhất: khi tính hàm mất mát, lỗi ở nhãn hiếm bị phạt nặng hơn, tỉ lệ nghịch với số mẫu của nhãn. Bảng trên cho thấy cái giá: accuracy giảm nhẹ (0,872 → 0,863) vì mô hình bớt đoán `answer`, nhưng macro-F1 tăng rõ (0,396 → 0,501) vì các nhãn hiếm được bắt nhiều hơn. Ma trận nhầm lẫn của mô hình có trọng số:

*Bảng 2.13. Ma trận nhầm lẫn nhiều nhãn (TF-IDF + hồi quy logistic có trọng số theo lớp; hàng: nhãn đúng, cột: nhãn đoán)*

| Đúng / Đoán | answer | clarify | deferred | denied | handoff | live_product | outside |
|---|---|---|---|---|---|---|---|
| answer (679) | **639** | 8 | 11 | 16 | 0 | 2 | 3 |
| clarify (24) | 7 | **15** | 0 | 1 | 0 | 0 | 1 |
| deferred (2) | 1 | 0 | **1** | 0 | 0 | 0 | 0 |
| denied (27) | 2 | 0 | 3 | **20** | 2 | 0 | 0 |
| handoff (11) | 2 | 0 | 1 | 1 | **7** | 0 | 0 |
| live_product (19) | 8 | 0 | 0 | 3 | 0 | **2** | 6 |
| outside (48) | 25 | 1 | 5 | 2 | 0 | 0 | **15** |

Đọc theo hàng: trong 48 câu ngoài phạm vi, mô hình chỉ nhận ra 15 câu, còn 25 câu bị coi là câu cần trả lời. Đây đúng là loại lỗi nguy hiểm nhất: bot đem tài liệu không liên quan ra trả lời một câu không phải việc của shop.

Còn một cách khác là **lấy mẫu lại**: nhân bản câu của nhãn hiếm, hoặc bớt câu của nhãn phổ biến. Khi huấn luyện router v5, đề tài dùng cách nhân bản: các nhóm câu mới được đưa vào dữ liệu học hai lần (mục 3.8).

### 2.8.2. Đánh giá truy xuất

- **Hit@k (còn gọi Success@k):** tỉ lệ câu hỏi có **ít nhất một** đoạn đúng nằm trong k kết quả đầu.
- **Recall@k:** với từng câu hỏi, lấy số đoạn đúng tìm được trong k kết quả đầu chia cho **tổng số đoạn đúng** của câu đó, rồi lấy trung bình trên các câu hỏi. Khi mỗi câu hỏi chỉ có đúng một đoạn đúng, Recall@k bằng Hit@k; khi một câu cần nhiều đoạn (ví dụ so sánh hai sản phẩm), hai con số khác nhau.
- **MRR (Mean Reciprocal Rank):** trung bình của 1/hạng của đoạn đúng đầu tiên.
- **nDCG@k [28]:** có tính mức độ liên quan (rất liên quan, hơi liên quan), và phạt khi đoạn đúng nằm thấp.

```math
\mathrm{Recall@}k = \frac{1}{|Q|}\sum_{q \in Q} \frac{|\text{đoạn đúng của } q \text{ trong top } k|}{|\text{đoạn đúng của } q|}
\mathrm{MRR} = \frac{1}{|Q|}\sum_{q \in Q} \frac{1}{\mathrm{hạng}_q}
```

**Ví dụ:** 10 câu hỏi, **mỗi câu có đúng một đoạn đúng**, hạng của đoạn đúng lần lượt là 1, 1, 2, (không có trong top 5), 1, 3, 1, (không có), 2, 1. Vì mỗi câu chỉ có một đoạn đúng nên ở đây Hit@k = Recall@k.

```text
Hit@1 = Recall@1 = 5/10 = 0,5     (5 câu có đoạn đúng ở hạng 1)
Hit@3 = Recall@3 = 8/10 = 0,8
MRR = (1 + 1 + 1/2 + 0 + 1 + 1/3 + 1 + 0 + 1/2 + 1) / 10 = 0,6333
```

Nếu câu thứ 3 cần **hai** đoạn đúng và chỉ đoạn thứ nhất (hạng 2) nằm trong top 3, thì câu đó vẫn được tính "trúng" khi đo Hit@3, nhưng chỉ được 1/2 khi đo Recall@3. Khi đó Recall@3 = (7 + 0,5)/10 = 0,75, còn Hit@3 vẫn là 0,8.

### 2.8.3. Đánh giá cả hệ thống chatbot

Đo từng bộ phận riêng chưa đủ: bộ tìm kiếm đúng mà bộ trả lời viết sai thì người dùng vẫn nhận câu sai. Đề tài chấm **cả hệ thống** theo từng câu hỏi với các kiểm tra cụ thể:

- Chọn đúng hướng xử lý (`basic_action`) không.
- Có trích đúng tài liệu nguồn không.
- Câu trả lời có chứa câu bằng chứng bắt buộc không (cho phép vài cách diễn đạt tương đương).
- Con số có khớp với số tính bằng SQL từ cơ sở dữ liệu không.

**Giảm dao động giữa các lần chạy.** Mọi lời gọi mô hình dùng **temperature = 0** (luôn chọn từ có xác suất cao nhất, không lấy mẫu ngẫu nhiên) và đầu ra bị ràng buộc theo một **JSON schema** (mô hình chỉ được sinh JSON đúng các trường và giá trị cho phép). Đề tài không đặt seed riêng: với temperature = 0 thì không có bước lấy mẫu nào cần seed. Dù vậy, kết quả vẫn có thể lệch nhẹ giữa hai lần chạy, do phép tính số thực trên GPU không hoàn toàn cố định và do dịch vụ phụ (vector nhúng) đôi khi quá thời gian chờ. Vì vậy mỗi phiên bản chạy **hai lần**. Một câu chỉ bị tính là "từ đạt thành trượt" khi nó trượt ở **mọi** lần chạy, còn câu đạt lần này trượt lần kia được tách riêng là **dao động**. Hai lần chạy chỉ **giảm** và **phát hiện** được dao động, không loại bỏ hẳn được nó.

## 2.9. Lý do chọn phương pháp cho đề tài

*Bảng 2.14. Yêu cầu của đề tài và phương pháp được chọn*

| Yêu cầu | Phương pháp chọn | Lý do |
|---|---|---|
| Tìm đúng mã sản phẩm, mã khuyến mãi | BM25 giữ token có gạch ngang | So khớp chính xác, không cần học |
| Hiểu cách hỏi khác mặt chữ | Vector nhúng PhoBERT | Hiểu nghĩa tiếng Việt |
| Bắt cụm từ ("bảo hành", "trả góp") | TF-IDF n-gram 1–2 | Rẻ, ổn định |
| Gộp ba cách mà không cần dữ liệu chỉnh trọng số | RRF k = 60 | Không phụ thuộc thang điểm |
| Phân lớp ý định đa dạng, tiếng Việt tự nhiên | Qwen3 4B bản gốc, có lời nhắc và JSON schema | Hiểu ngữ cảnh, không cần dữ liệu có nhãn thật; đồng thời viết lại câu tìm kiếm và chọn loại tài liệu |
| Chọn đúng câu bằng chứng trong bản ghi sản phẩm | Qwen3 4B tinh chỉnh LoRA (bản v1) | Bản gốc hay lấy thêm dòng thông số không được hỏi |
| Ca nhạy cảm phải chắc chắn đúng | Luật viết tay chạy trước mô hình | Giải thích được, không phụ thuộc xác suất |
| Số liệu kinh doanh phải đúng tuyệt đối | Tính bằng SQL, không để mô hình tự tính | Mô hình ngôn ngữ cộng trừ không đáng tin |

**Vì sao không dùng PhoBERT tinh chỉnh làm bộ phân lớp ý định?** Đây là cách làm chuẩn cho tiếng Việt: mô hình JointIDSF xây trên PhoBERT cho kết quả tốt trên PhoATIS [38], và PhoBERT nhỏ (khoảng 135 triệu tham số so với 4 tỉ của Qwen3 4B), chạy nhanh trên CPU. Đề tài chưa chọn cách này vì ba lý do:

1. **Không có dữ liệu có nhãn thật.** PhoATIS có 5.871 câu do người gán nhãn. Đề tài chỉ có 640 câu router tự sinh, trong đó nhiều nhãn chỉ có 4–13 câu. Mô hình phân lớp học từ chừng đó câu rất dễ học thuộc khuôn câu tự sinh. LLM bản gốc thì không cần dữ liệu có nhãn: chỉ cần mô tả nhãn trong lời nhắc.
2. **Router không chỉ chọn nhãn.** Mỗi lần gọi, router trả về một JSON gồm hướng xử lý, câu tìm kiếm đã viết lại (ví dụ thay "nó" bằng tên máy ở lượt trước), loại tài liệu cần tìm, nhóm sản phẩm, và cờ "đòi dữ liệu nội bộ". Bộ phân lớp PhoBERT chỉ làm được phần đầu, phần còn lại cần thêm mô hình khác.
3. **Đo thử bằng mốc so sánh đơn giản.** Một mô hình TF-IDF + hồi quy logistic (cùng họ "túi từ + bộ phân lớp tuyến tính" như các thuật toán ở mục 2.6), học từ 640 câu router, đạt macro-F1 0,626 trên phần validation; cả hệ thống (luật + Qwen3 4B) đạt 0,828 (mục 3.10.4).

PhoBERT tinh chỉnh vẫn là hướng đáng thử khi có câu hỏi thật của khách để gán nhãn. Khi đó nên đo nó trên cùng các bộ câu hỏi, so với mốc TF-IDF + hồi quy logistic và với router hiện tại.

## Tiểu kết Chương 2

Chương 2 đã trình bày các thuật toán của nhánh khai phá văn bản – truy xuất thông tin – phân lớp:

- tiền xử lý tiếng Việt;
- biểu diễn văn bản: túi từ, TF-IDF, vector nhúng;
- độ đo tương tự;
- xếp hạng: vector space, BM25, truy xuất dày, RRF, cùng cách chia đoạn tài liệu;
- phân lớp: kNN, Naive Bayes, hồi quy logistic, SVM, cây quyết định, transformer tinh chỉnh bằng LoRA, và cách xử lý nhãn lệch;
- cách đánh giá: macro-F1, Hit@k, Recall@k, MRR.

Các ví dụ tính tay cho thấy:

- BM25 khắc phục điểm yếu IDF bằng 0 của TF-IDF cổ điển.
- RRF gộp được nhiều bảng xếp hạng mà không cần chuẩn hóa điểm.
- Naive Bayes và cây quyết định "cân" từng từ để chọn nhãn.
- Với nhãn lệch, accuracy có thể cao mà mô hình vô dụng.

Các con số kỹ thuật đều lấy từ cấu hình và code thật: giới hạn 256 token của mô hình vector nhúng, bản BM25 kiểu Lucene, 33 triệu tham số LoRA. Chương 3 trình bày cách đề tài ghép các thuật toán này thành một chatbot hoàn chỉnh.

# CHƯƠNG 3. ỨNG DỤNG VÀO CHATBOT TECHSTORE

## 3.1. Bài toán và yêu cầu

TechStore là một cửa hàng (mô phỏng) bán laptop và linh kiện máy tính. Chatbot phục vụ hai vai trò:

- **Khách mua:** hỏi thông số sản phẩm, so sánh máy, tư vấn theo ngân sách, hỏi bảo hành, đổi trả, giao hàng, trả góp, khuyến mãi.
- **Quản trị viên (admin):** hỏi số liệu kinh doanh: doanh thu, lãi gộp, chi phí theo tháng hoặc quý, so sánh hai kỳ, mặt hàng bán chạy, đọc kế hoạch và báo cáo tháng.

Các yêu cầu chất lượng được đặt ra từ đầu:

1. **Mọi con số phải khớp cơ sở dữ liệu** `shop.sqlite`. Mô hình ngôn ngữ không được tự cộng trừ.
2. **Không bịa:** không có trong dữ liệu thì nói chưa có thông tin, không đoán.
3. **Có nguồn:** câu trả lời chỉ ra được tài liệu hoặc bảng số liệu đã dùng.
4. **Phân quyền:** khách không được xem tài liệu nội bộ, dữ liệu của khách khác, lương nhân viên.
5. **Biết giới hạn:** câu ngoài phạm vi (giải toán, viết code, hỏi về cửa hàng khác) thì nói rõ là ngoài phạm vi; câu chưa rõ ("con màu đen đó") thì hỏi lại.

## 3.2. Nguồn dữ liệu

![Hình 3.1. Bản đồ nguồn dữ liệu của đề tài](hinh/h3_2_ban_do_nguon_du_lieu.png)

Mọi dữ liệu, ảnh, tài liệu và mô hình đều được ghi nguồn: link gốc, ngày lấy, giấy phép, đã đổi gì. Danh sách đầy đủ nằm ở Phụ lục A. Tóm tắt như sau.

### 3.2.1. Thông số sản phẩm (67 sản phẩm)

*Bảng 3.1. Nguồn thông số sản phẩm*

| Nguồn | Số sản phẩm | Giấy phép | Ghi chú |
|---|---|---|---|
| [docyx/pc-part-dataset](https://github.com/docyx/pc-part-dataset) trên GitHub (commit `c52a04c`, dữ liệu chụp ngày 23/7/2025) [33] | 48 linh kiện: CPU, mainboard, RAM, ổ cứng, card đồ họa, nguồn, vỏ case, chuột, màn hình | Mã nguồn MIT | Dữ liệu gốc lấy từ PCPartPicker; điều khoản của PCPartPicker cần xem riêng trước khi phân phối lại. Giá gốc tính bằng USD |
| [Ryans laptop inventory](https://www.kaggle.com/datasets/msjahid/ryans-laptop-inventory-and-specifications) trên Kaggle [34] | 19 laptop | Apache 2.0 | Giữ ghi công tác giả |

Mỗi sản phẩm trong `products.sqlite` lưu `source_id`, `source_file`, `source_row`, `source_sha256`, nên truy được về **đúng dòng** trong file gốc và kiểm tra được file gốc chưa bị sửa.

### 3.2.2. Dữ liệu kinh doanh (mô phỏng)

**Toàn bộ đơn hàng, giá bán VND, tồn kho, giá vốn, chi phí và khách hàng đều là dữ liệu mô phỏng**, không phải số của một cửa hàng thật. Lý do: dữ liệu bán hàng thật của cửa hàng là bí mật kinh doanh, không có bộ công khai nào vừa có đủ bán – nhập – tồn – hoàn – chi phí cho một cửa hàng máy tính Việt Nam.

- Kỳ dữ liệu: 01/10/2025 – 30/09/2026 (365 ngày).
- 1.427 đơn bán, 1.717 dòng bán, 320 đơn nhập, 317 phiếu nhận hàng, 31 lượt hoàn, 99 khoản chi, 1.200 khách.
- Bộ mô phỏng **chỉ lấy phân phối thống kê** từ các bộ dữ liệu công khai về thương mại điện tử (tỉ lệ xem/thêm giỏ/mua, phân bố theo nhóm hàng, theo tháng) để dữ liệu sinh ra có hình dạng giống thật. Các bộ tham khảo (Kaggle và UCI) liệt kê ở Phụ lục A, mỗi bộ ghi giấy phép riêng.
- Giá vốn tính theo **FIFO**, doanh thu ghi theo **dồn tích**, mọi giá trị **chưa gồm VAT**, chưa mô hình hóa lãi vay và thuế thu nhập (ghi trong bảng `metadata`).
- 27 tài liệu nội bộ (kế hoạch bán hàng, báo cáo tháng, chiến lược, marketing) được sinh cùng kịch bản, số liệu trong đó lấy từ SQL.

### 3.2.3. Tài liệu bot dùng để trả lời

*Bảng 3.2. Kho tài liệu của chatbot*

| Nhóm | Số tài liệu | Nguồn |
|---|---|---|
| Catalog sản phẩm | 201 | Sinh tự động từ `products.sqlite`, 3 tài liệu cho mỗi sản phẩm |
| Bài kỹ thuật, giải thích thuật ngữ | 43 | Nhóm viết tóm tắt bằng tiếng Việt từ trang chính thức của Intel, Kingston, Samsung, BenQ, Lenovo, MSI, Apple, AMD, NVIDIA…; mỗi bài ghi link nguồn |
| Sổ tay phân tích kinh doanh | 10 | Nhóm tự viết (phương pháp, từ điển dữ liệu, câu SQL mẫu) |
| Chính sách cửa hàng | 5 | Nhóm tự soạn cho bản demo (bảo hành, đổi trả, giao hàng, trả góp, khuyến mãi); không phải chính sách thật |
| Tài liệu nội bộ mô phỏng | 27 | Sinh cùng dữ liệu kinh doanh, chỉ admin xem được |
| **Tổng** | **286** | Tính cả các bản không còn hiệu lực. Tại ngày 31/10/2026, bộ tìm kiếm chỉ dùng tài liệu đang hiệu lực: 144 tài liệu với admin, 115 với khách. 144 tài liệu của admin chia thành 433 đoạn (mỗi đoạn tối đa 100 từ) hoặc 311 đoạn (tối đa 180 từ) |

### 3.2.4. Ảnh sản phẩm và mô hình

- **Ảnh:** 37 ảnh tải từ trang của hãng và nhà bán lẻ, mỗi ảnh ghi trang nguồn, link ảnh, ngày tải, mã băm SHA-256. 30 ảnh còn lại được tải bổ sung ngày 3/11/2026, cũng ghi nguồn đầy đủ. **Mọi ảnh đều thuộc bản quyền của trang gốc và chưa được cấp phép dùng thương mại**; chỉ dùng cho mục đích học tập. Ảnh chỉ hiển thị trên web, chatbot không dùng ảnh.
- **Mô hình:** Qwen3-4B-Instruct-2507 [26] và vietnamese-embedding [32], cùng giấy phép Apache 2.0.

## 3.3. Kho dữ liệu cửa hàng `shop.sqlite`

![Hình 3.2. Lược đồ dữ liệu shop.sqlite: bảng sự kiện (vàng) xoay quanh bảng chiều sản phẩm](hinh/h3_3_luoc_do_shop_sqlite.png)

`shop.sqlite` là một kho dữ liệu nhỏ, thiết kế theo **lược đồ chòm sao**: nhiều bảng sự kiện dùng chung bảng chiều sản phẩm (Hình 3.2). Cơ sở dữ liệu gồm 17 bảng và 2 view.

*Bảng 3.3. Các bảng chính và vai trò trong mô hình nhiều chiều*

| Bảng | Số dòng | Vai trò | Độ mịn (một dòng là) |
|---|---|---|---|
| `order_items` | 1.717 | Sự kiện | Một sản phẩm trong một đơn bán |
| `financial_ledger` | 1.748 | Sự kiện | Một bút toán bán hoặc hoàn (doanh thu, giá vốn) |
| `inventory_daily` | 24.455 | Sự kiện (ảnh chụp) | Tồn kho của một SKU trong một ngày |
| `inventory_moves` | 2.126 | Sự kiện | Một lần nhập hoặc xuất kho |
| `returns` | 31 | Sự kiện | Một lượt hoàn hàng |
| `purchase_lines`, `receipts` | 320, 317 | Sự kiện | Một dòng đặt nhập, một lần nhận hàng |
| `operating_expenses` | 99 | Sự kiện | Một khoản chi |
| `products` (+ `product_facts`) | 67 | Chiều | Một sản phẩm |
| `orders` | 1.427 | Đầu đơn (thuộc sự kiện bán hàng) | Một đơn (ngày, kênh, khách, chiến dịch) |
| `customers` | 1.200 | Chiều | Một khách (phân khúc) |
| `campaigns`, `suppliers` | 3, 2 | Chiều | Một chiến dịch, một nhà cung cấp |
| `monthly_targets` | 12 | Chỉ tiêu | Mục tiêu doanh thu, biên lãi của một tháng |
| `metadata` | 9 | Siêu dữ liệu | Kỳ dữ liệu, đơn vị tiền, cách tính giá vốn |

Bảng `orders` cần nói rõ hơn. Theo cách thiết kế của Kimball [4], một đơn hàng gồm phần **đầu đơn** (ngày, kênh, khách, chiến dịch) và các **dòng đơn** (từng sản phẩm). Bảng sự kiện nên đặt ở mức dòng đơn (`order_items`). Mã đơn khi đó là **chiều suy biến (degenerate dimension)**: nó nằm ngay trong bảng sự kiện để gom các dòng của cùng một đơn, nhưng không cần bảng chiều riêng vì bản thân nó không có thuộc tính mô tả nào. Trong `shop.sqlite`, phần đầu đơn được tách thành bảng `orders` để không lặp ngày, kênh, khách ở từng dòng. Vì vậy `orders` là một phần của sự kiện bán hàng chứ không phải một bảng chiều; các chiều thật là ngày, kênh, khách hàng và chiến dịch mà nó trỏ tới.

View `monthly_pnl` đóng vai trò **data mart tài chính**: tổng hợp sẵn doanh thu thuần, giá vốn, lãi gộp, chi phí hoạt động, lợi nhuận trước lãi vay và thuế, số đơn, mục tiêu theo từng tháng.

*Bảng 3.4. Trích view monthly_pnl (đơn vị: đồng)*

| Tháng | Doanh thu thuần | Lãi gộp | Chi phí hoạt động | Lợi nhuận trước lãi vay, thuế | Số đơn | Mục tiêu doanh thu |
|---|---|---|---|---|---|---|
| 2025-10 | 984.310.000 | 144.706.000 | 108.627.410 | 36.078.590 | 99 | 1.323.000.000 |
| 2025-11 | 1.493.219.000 | 198.752.000 | 138.225.409 | 60.526.591 | 151 | 1.755.000.000 |
| 2026-01 | 1.077.004.000 | 126.257.000 | 127.647.044 | −1.390.044 | 126 | 1.512.000.000 |
| 2026-02 | 609.442.000 | 79.845.000 | 104.503.862 | −24.658.862 | 65 | 918.000.000 |
| Cả năm | 13.495.418.000 | 1.879.908.000 | — | — | 1.427 | — |

Một vài phát hiện đọc được ngay từ kho dữ liệu: tháng 1 và tháng 2/2026 lỗ vì lãi gộp không đủ bù chi phí hoạt động, trong đó tháng 2 có doanh thu thấp nhất năm (609.442.000 đ); laptop chiếm khoảng 67% doanh thu cả năm (9.043.111.000 đ trên 13.495.418.000 đ); ba sản phẩm doanh thu cao nhất là Apple MacBook Air (Late 2020), Acer Nitro 5 AN515-58-59JP và MSI Modern 15 B12M.

**Ví dụ câu truy vấn OLAP** (roll-up doanh thu laptop theo quý):

```sql
SELECT p.category,
       CASE WHEN substr(l.day, 6, 2) IN ('10','11','12') THEN '2025-Q4'
            WHEN substr(l.day, 6, 2) IN ('01','02','03') THEN '2026-Q1'
            WHEN substr(l.day, 6, 2) IN ('04','05','06') THEN '2026-Q2'
            ELSE '2026-Q3' END AS quy,
       SUM(l.revenue) AS doanh_thu
FROM financial_ledger l JOIN products p ON p.sku = l.sku
WHERE p.category = 'laptop'
GROUP BY 1, 2 ORDER BY 2;
-- 2025-Q4: 2.829.582.000 | 2026-Q1: 1.892.661.000
-- 2026-Q2: 1.915.700.000 | 2026-Q3: 2.405.168.000
```

## 3.4. Quy trình đưa dữ liệu vào kho (ETL)

![Hình 3.3. Đường đi của dữ liệu trong dự án](hinh/h3_4_luong_du_lieu_etl.png)

Đề tài tách ETL thành các module nhỏ, mỗi module chỉ làm một việc và **không ghi đè dữ liệu đang chạy** (Hình 3.3):

1. **Chụp bản thô (`de_snapshot`):** sao chép dữ liệu nguồn thành một phiên bản cố định, có mã băm (checksum) để phát hiện nếu file bị thay đổi. Đây là **vùng tạm**.
2. **Kiểm toán (`de_audit`):** chỉ đọc, kiểm tra bảng sổ cái: thiếu cột, sai kiểu, giá trị lạ. Không tự sửa.
3. **Đối soát (`de_reconcile`):** chạy lại toàn bộ nhập – xuất theo FIFO, so tồn kho tính ra với tồn kho ghi lại từng ngày, so phiếu nhận với đơn nhập.
4. **Tổng hợp (`de_curated`):** dựng bản tổng hợp riêng cho admin phân tích, tách khỏi dữ liệu bot đang dùng.
5. **Làm mới hằng tháng (`monthly`):** khi có tháng mới, cập nhật số liệu và tài liệu, rồi lập chỉ mục lại để tìm kiếm. **Không huấn luyện lại mô hình**: thêm tài liệu chỉ cần lập chỉ mục, không cần train.

Theo kiến trúc medallion (mục 1.2.7), bước 1 là tầng bronze, bước 2–3 là tầng silver, bước 4 cùng view `monthly_pnl` là tầng gold.

> **Điểm kỹ thuật – nguyên tắc "sai thì dừng" (fail-closed):** nếu một bước kiểm tra không đạt (ví dụ tồn kho đối soát lệch), quy trình dừng hẳn và giữ nguyên dữ liệu cũ, thay vì nạp dữ liệu có thể sai. Đối với chatbot, trả lời bằng số cũ nhưng đúng an toàn hơn trả lời bằng số mới nhưng sai.

## 3.5. Kiến trúc hệ thống

![Hình 3.4. Kiến trúc tổng thể hệ thống TechStore](hinh/h3_1_kien_truc_he_thong.png)

Hệ thống gồm ba phần (Hình 3.4):

1. **Web:** trang bán hàng và trang quản trị viết bằng React; backend viết bằng Node.js + Express, chạy trên dịch vụ Render.
2. **Dịch vụ AI:** viết bằng Python, dùng FastAPI, có hai cổng: `/api/chat/customer` cho khách và `/api/chat/admin` cho quản trị viên. Backend gọi dịch vụ AI qua địa chỉ cấu hình trong biến `AI_SERVICE_URL`.
3. **Các thành phần AI:**
   - Ollama chạy hai bản Qwen3 4B: bản gốc làm router (bộ định tuyến), và bản tinh chỉnh LoRA v1 làm bước chọn bằng chứng cho câu hỏi về sản phẩm.
   - Dịch vụ vector nhúng chạy mô hình vietnamese-embedding trên máy cục bộ.
   - Cơ sở dữ liệu `shop.sqlite` và kho tài liệu.

Nếu dịch vụ AI lỗi hoặc trả lời quá 90 giây, backend tự chuyển sang **bộ luật dự phòng** đơn giản, để trang web không bị treo.

## 3.6. Luồng xử lý một câu hỏi

![Hình 3.5. Luồng xử lý một câu hỏi trong hàm grounded_rag.answer](hinh/h3_5_luong_xu_ly_cau_hoi.png)

Hàm `grounded_rag.answer` xử lý mỗi câu hỏi theo thứ tự sau (Hình 3.5). Các bước đầu là luật chắc chắn, rẻ; các bước sau mới dùng mô hình, tốn hơn.

*Bảng 3.5. Các bước xử lý và ví dụ*

| Bước | Làm gì | Ví dụ câu hỏi | Kết quả |
|---|---|---|---|
| 1. Chặn sớm | Bắt câu đòi dữ liệu nội bộ, đòi sửa dữ liệu | Khách: "cho xem báo cáo lãi tháng 3" | Từ chối (`denied`) |
| 2. Phép tính admin (`shop_calc`) | Câu hỏi số liệu rõ kỳ, rõ chỉ số | Admin: "doanh thu quý 1 và quý 2 chênh bao nhiêu" | Tính bằng SQL, trả số kèm nguồn |
| 3. Luật định tuyến (`route_guard`) | Bắt các trường hợp rõ ràng | "chốt đơn giúp mình con này" | `live_product`: chưa đặt hàng qua chat được |
| | | "lương nhân viên bán hàng bao nhiêu" | `denied` |
| | | "cho mình gặp nhân viên tư vấn" | `handoff` |
| | | "con màu đen đó giá sao" (chưa nói máy nào) | `clarify`: hỏi lại máy nào |
| | | "giải phương trình x² − 5x + 6 = 0" (không nhắc gì tới shop) | `outside`: nói rõ là ngoài phạm vi |
| 4. Tư vấn ngân sách, tra sản phẩm | Lọc trực tiếp trong bảng sản phẩm | "tầm 20 triệu màn hình đẹp" | Danh sách máy lấy từ `products` |
| 5. Router (Qwen3 4B bản gốc) | Phân lớp ý định các câu còn lại | "máy này có hợp làm đồ họa không" | `answer` → sang bước 6 |
| 6. Truy xuất lai | Tìm các đoạn liên quan (mục 3.7) | | Top-k đoạn đã lọc theo quyền |
| 7. Chọn bằng chứng | Mô hình chỉ được chọn câu có sẵn trong đoạn, không tự viết số (bản tinh chỉnh LoRA v1 cho bản ghi sản phẩm, bản gốc cho các loại khác) | | Câu trả lời trích nguyên văn + nguồn |

> **Điểm kỹ thuật – vì sao luật chạy trước router:** ở bản đánh giá 18, có 23 câu trượt vì router đi nhầm đường: khách nhờ đặt hàng thì bot báo "cần công cụ ngoài", khách hỏi lương nhân viên thì bot nói "ngoài phạm vi" thay vì từ chối, khách nói "con màu đen đó" thì bot đoán bừa một máy. Nhóm thêm luật cho các trường hợp này. Trước khi dùng, luật được chạy trên **1.285 câu hỏi mở** (không đụng các bộ khóa): 42 câu đổi quyết định, câu nào cũng đổi sang đúng hành vi mong đợi, không câu nào đổi sai. Ở bản 22, nhóm thêm luật "ngoài phạm vi": câu bài tập, giải toán, viết code, chửi bot, vay tiền, sức khỏe, pháp lý, hỏi sàn hoặc dịch vụ khác, **mà không nhắc gì tới máy móc, mua bán hay shop**, thì trả lời ngoài phạm vi. Câu như "laptop nào viết code Python mượt" vẫn đi đường bình thường. Chạy lại trên 1.285 câu mở: đúng 17 câu đổi quyết định, đều là câu ngoài phạm vi.

## 3.7. Cài đặt truy xuất lai

![Hình 3.6. Truy xuất lai trong hàm retrieval.search](hinh/h3_6_truy_xuat_lai.png)

Hàm `retrieval.search` cài đặt đúng các thuật toán ở Chương 2:

1. **Lọc trước khi tìm:** chỉ giữ tài liệu mà vai trò người hỏi được xem, đang có hiệu lực, đúng kỳ nếu câu hỏi nhắc tháng hoặc quý ("T3" được hiểu là tháng 3, "Q2" là quý 2). Lọc trước giúp tài liệu nội bộ **không bao giờ** lọt vào danh sách ứng viên của khách.
2. **Chia đoạn theo cấu trúc (`chunking`):**
   - Cắt theo tiêu đề và đoạn văn; giữ đường dẫn tiêu đề (ví dụ "Chính sách bảo hành > Điều kiện") ở đầu mỗi đoạn.
   - Bảng thì lặp lại dòng tiêu đề cho mỗi phần.
   - Câu quá dài thì cắt theo số từ nhưng không làm mất từ nào.
   - Mỗi đoạn tối đa 100 từ khi có vector nhúng, 180 từ khi không có.
3. **Ba cách chấm điểm:**
   - **TF-IDF** n-gram 1–2 + cosine, trên văn bản đã bỏ dấu, có sửa lỗi gõ và mở rộng viết tắt.
   - **BM25** với k1 = 1,2; b = 0,75, token giữ nguyên mã có gạch ngang.
   - **Vector nhúng** vietnamese-embedding (768 chiều, đã chuẩn hóa), tính bằng tích vô hướng.
4. **Trộn RRF** với k = 60.
5. **Ngưỡng:** chỉ giữ đoạn có cosine TF-IDF > 0,08 **hoặc** cosine vector > 0,45, để loại các đoạn được xếp hạng cao chỉ vì "đứng đầu trong đám không liên quan".
6. **Lấy top-k** (k từ 1 đến 12). Nếu câu hỏi nêu đích danh một sản phẩm, mọi đoạn của sản phẩm đó được đưa lên trước.
7. **Chế độ dự phòng:** nếu dịch vụ vector không chạy, hệ thống chỉ dùng TF-IDF, không dừng hẳn.

Đoạn code BM25 trong đề tài (rút gọn) cho thấy công thức ở mục 2.5.2 được cài đặt trực tiếp:

```python
def bm25_scores(question, texts):
    tokens = lambda s: re.findall(r'\b\w[\w-]*\b', normalize(s))   # giữ "c-bts"
    corpus = [Counter(tokens(t)) for t in texts]; query = set(tokens(question))
    lengths = [sum(c.values()) for c in corpus]; average = sum(lengths) / len(lengths)
    frequency = Counter(term for c in corpus for term in c)
    result = []
    for counts, length in zip(corpus, lengths):
        score = 0.
        for term in query & counts.keys():
            idf = math.log(1 + (len(corpus) - frequency[term] + .5) / (frequency[term] + .5))
            tf = counts[term]
            score += idf * tf * 2.2 / (tf + 1.2 * (.25 + .75 * length / average))  # k1=1,2; b=0,75
        result.append(score)
    return result
```

(Trong code, `2.2` là k1 + 1, còn `.25 + .75 × length/average` là 1 − b + b × |D|/avgdl với b = 0,75.)

## 3.8. Bộ định tuyến và tinh chỉnh mô hình

![Hình 3.7. Vòng huấn luyện và đánh giá trên Kaggle](hinh/h3_7_vong_huan_luyen_danh_gia.png)

**Hiện trạng.** Đề tài dùng hai bản Qwen3 4B:

- **Router: bản gốc, chưa tinh chỉnh.** Router chạy với lời nhắc mô tả từng nhãn, temperature = 0, và đầu ra bị ràng buộc theo JSON schema (mục 2.8.3).
- **Bước chọn bằng chứng cho bản ghi sản phẩm: bản tinh chỉnh LoRA v1.** Bản gốc hay lấy thêm những dòng thông số không được hỏi; bản v1 bỏ được các dòng đó. Bản v1 chỉ dùng cho câu hỏi về sản phẩm, vì với câu hỏi chính sách hay báo cáo nó lại làm mất bằng chứng.

Nhóm đã tinh chỉnh một router riêng (**bản v5**, mô tả dưới đây), nhưng **chưa dùng**. Lúc huấn luyện, v5 chọn đúng 94,4% phần dev. Nhưng khi chạy cả hệ thống, kết quả khác hẳn. Ở bản đánh giá 7, v5 làm trượt 10 trên 31 câu của bộ chính sách, vì đẩy câu hỏi chính sách sang tài liệu giải thích thuật ngữ. Ở bản 10, sau khi đã sửa thêm, v5 vẫn làm 4 câu đang đạt chuyển thành trượt ở cả hai lần chạy. Theo quy tắc cổng (mục 3.10.1), bản có lỗi lùi không được dùng thay bản cũ. Đây là ví dụ rõ cho việc **điểm của riêng một bộ phận không đủ để quyết định**: phải đo cả hệ thống.

### 3.8.1. Dữ liệu huấn luyện

- **Cách tạo:** nhóm tự sinh câu hỏi từ đặc tả của router và từ dữ liệu trong cơ sở dữ liệu (tên sản phẩm, kỳ báo cáo, chỉ số). Nhãn lấy theo đặc tả và dữ liệu, **không lấy câu trả lời của mô hình nào làm nhãn**.
- **Chống rò rỉ:** câu hỏi của mọi bộ đánh giá đều bị loại khỏi dữ liệu huấn luyện, kể cả câu gần giống.
- **Kích thước (phiên bản v5):** 1.263 câu train, 229 câu dev. Phiên bản này thêm 48 câu viết tay, 50 câu hỏi số liệu "bẩn" (viết tắt, sai chính tả), 50 câu hỏi sản phẩm "bẩn", 28 câu hỏi hai chỉ số cùng lúc và các câu phép tính.
- **Ghi lại:** mã băm SHA-256 của file train và dev được lưu trong `DATA_CARD.json`, để biết chính xác mô hình học từ dữ liệu nào.

### 3.8.2. Cấu hình tinh chỉnh

*Bảng 3.6. Tham số tinh chỉnh Qwen3 4B (phiên bản v5)*

| Tham số | Giá trị | Giải thích |
|---|---|---|
| Mô hình gốc | Qwen3-4B-Instruct-2507 | 4 tỉ tham số, giấy phép Apache 2.0 |
| Nạp mô hình | 4 bit (thư viện Unsloth [35]) | Kiểu QLoRA, để vừa GPU T4 16 GB |
| LoRA r / α / dropout | 16 / 32 / 0 | Hạng 16, hệ số tỉ lệ α/r = 2 |
| Lớp gắn LoRA | q, k, v, o, gate, up, down | Cả phần chú ý và phần mạng truyền thẳng |
| Số tham số được học | 33.030.144 (khoảng 0,82%) | Tính từ cấu hình mô hình, xem Bảng 2.9 |
| Nhãn hiếm | Các nhóm câu mới đưa vào hai lần | Cách nhân bản mẫu để nhãn hiếm không bị lấn át (mục 2.8.1) |
| Số vòng (epoch) | 2 | Đi qua dữ liệu train 2 lần |
| Tốc độ học | 5 × 10⁻⁵, giảm theo hàm cosine, khởi động 20 bước | Học chậm để không làm hỏng kiến thức gốc |
| Batch | 1 × tích lũy 8 bước | Tương đương batch 8, tiết kiệm bộ nhớ |
| Phần cứng | GPU T4 miễn phí của Kaggle | |
| Xuất ra | GGUF, chạy bằng Ollama [36] | |

Trên phần dev lúc huấn luyện, router v5 chọn đúng **118/125 câu (94,4%)**. Đây chỉ là điểm của riêng bộ định tuyến; như đã nói ở đầu mục, khi đo cả hệ thống thì v5 chưa qua cổng nên chưa được dùng. Nhóm đang chuẩn bị bản v6 (mục 3.11).

## 3.9. Trả lời số liệu cho quản trị viên

Mô hình ngôn ngữ cỡ 4 tỉ tham số **không cộng trừ đáng tin**, và dễ nhầm các chỉ số gần nhau (lãi gộp với lợi nhuận). Vì vậy với câu hỏi số liệu, đề tài không để mô hình tính:

- Module `shop_calc` nhận diện câu hỏi có kỳ rõ ràng (tháng, quý, khoảng tháng) và chỉ số rõ ràng (doanh thu, lãi gộp, chi phí, số đơn…), cùng phép toán (tổng, chênh lệch giữa hai kỳ, phần trăm tăng giảm, so với chỉ tiêu, tỉ lệ như biên lãi gộp hay doanh thu bình quân mỗi đơn, xếp hạng các tháng).
- Mọi con số được tính bằng câu SQL có tham số (không ghép chuỗi), từ cùng một hàm phân tích `analyze_business`.
- Câu trả lời ghi rõ bảng nguồn và kỳ đã dùng.
- Câu không đủ rõ thì **không đoán**, chuyển sang hỏi lại.
- Khách thường hỏi các câu này thì bị từ chối, vì đây là số liệu nội bộ.

## 3.10. Đánh giá

### 3.10.1. Các bộ câu hỏi đánh giá

*Bảng 3.7. Các bộ đánh giá*

| Bộ | Số câu | Phần (split) | Kiểm tra gì |
|---|---|---|---|
| natural2 | 120 | development | Câu hỏi tự nhiên lượt hai, nhiều cách diễn đạt |
| natural | 120 | development | Câu hỏi tự nhiên của khách và admin |
| policy | 31 | development | Chính sách bảo hành, đổi trả, giao hàng, trả góp, khuyến mãi |
| kb3 | 600 | 479 development + 121 validation | Vòng chất lượng kho tài liệu |
| expansion | 539 | 354 development + 185 validation | Bộ mở rộng nhiều loại câu |
| ngoài phạm vi | 100 | 60 development + 40 validation | 80 câu ngoài phạm vi, 20 câu đối chứng (có ngữ cảnh lạ nhưng vẫn là việc của cửa hàng) |
| held-out | (khóa) | — | Chỉ chạy một lần khi chốt bản cuối |

Quy tắc dùng: nhóm chỉ được xem chi tiết các câu **development** để tìm lỗi và sửa. Phần **validation** chỉ xem số đếm đạt/trượt, dùng làm **cổng**: một phiên bản mới chỉ được dùng thay bản cũ nếu **không câu nào từ đạt thành trượt ở mọi lần chạy**.

Mỗi phiên bản được chạy trên Kaggle (GPU T4, khoảng 3–4 giây mỗi câu, khoảng 2,5 giờ mỗi lượt), hai lần, so với bản trước bằng script `compare_runs.py`.

### 3.10.2. Kết quả

![Hình 3.8. Kết quả bản đánh giá 19 và bản 22 trên Kaggle](hinh/h3_8_ket_qua_ban_22.png)

*Bảng 3.8. Kết quả bản đánh giá 19 và bản 22 (cùng cách chấm mới)*

| Bộ | Bản 19 | Bản 22 | Tỉ lệ bản 22 |
|---|---|---|---|
| natural2 | 101 / 120 | **117** / 120 | 97,5% |
| natural | 106 / 120 | 107 / 120 | 89,2% |
| policy | 29 / 31 | 29 / 31 | 93,5% |
| kb3 development | 425 / 479 | 425 / 479 | 88,7% |
| kb3 validation | 106 / 121 | 106 / 121 | 87,6% |
| expansion development | 326 / 354 | 333 / 354 | 94,1% |
| expansion validation | 142 / 185 | 145 / 185 | 78,4% |
| Ngoài phạm vi, 80 câu ngoài lề (development 48 + validation 32) | 57 / 80 (34 + 23) | **72** / 80 (48 + 24) | 90,0% |
| Đối chứng của bộ ngoài phạm vi (development 12 + validation 8) | 14 / 20 (9 + 5) | 17 / 20 (11 + 6) | 85,0% |

Nhận xét:

- **Bản 22 qua cổng** so với cả bản 21 và bản 19: không có câu nào trước đạt mà sau trượt, ở cả 9 phần của các bộ. Hai lượt chạy cho kết quả giống hệt nhau.
- **Cổng đã chặn được một lỗi thật.** Bản 20 thêm luật nhận diện câu đặt hàng. Điểm tăng mạnh (natural2 từ 101 lên 117), nhưng phần validation của bộ ngoài phạm vi mất 1 câu. Nhóm không mở câu đó; chỉ từ số đếm theo nhóm biết đó là câu về cửa hàng khác bị coi nhầm là đặt hàng. Luật được sửa ở bản 21 (nhờ đặt vé, phòng, đồ ăn, hay đặt trên sàn khác thì không phải đặt hàng của shop), và câu đó đúng trở lại.
- **natural2 tăng từ 101 lên 117** nhờ sửa định tuyến: câu đặt hàng, câu hỏi thông tin nội bộ, câu chỉ trỏ chưa rõ máy nào. Trong 43 câu mở bị luật mới đổi quyết định, 24 câu từ trượt thành đạt, không câu nào từ đạt thành trượt.
- **Bộ ngoài phạm vi: development tăng mạnh, validation tăng ít.** Sau khi thêm luật ngoài phạm vi (bản 22), phần development đạt 48/48, nhưng phần validation chỉ từ 23 lên 24/32. Theo số đếm theo nhóm, nhóm viết code ở validation vẫn 0/3. Luật bắt tốt kiểu câu đã thấy nhưng khái quát kém sang câu lạ. Nhóm **không** sửa luật theo phần validation, vì làm vậy thì validation không còn là phép đo khách quan nữa. Phần này để router học ở bản v6.
- **Expansion validation vẫn thấp hơn development** (78,4% so với 94,1%). Đây là điều bình thường khi chỉ sửa theo phần development: validation đo khả năng **tổng quát**. Khoảng cách này cho thấy vẫn còn lỗi chưa lộ ra ở phần development.

### 3.10.3. Phân tích lỗi và cải tiến

Nhóm phân loại mỗi câu trượt theo nguyên nhân trước khi sửa:

*Bảng 3.9. Loại lỗi và cách sửa*

| Loại lỗi | Ví dụ | Cách sửa |
|---|---|---|
| Định tuyến sai | Đặt hàng qua chat bị coi là "cần công cụ ngoài" | Thêm luật `route_guard` (bản 20, sửa ở bản 21) |
| Tìm sai tài liệu | Mã biến thể "B12M-081SG" bị lấn bởi dòng catalog "B12M" | Cho tài liệu riêng của mã biến thể cạnh tranh ngang với catalog |
| Thiếu từ khóa chính sách | "giao trong bao lâu", "trả lại hàng" không được nhận là câu chính sách | Bổ sung từ khóa |
| Chấm oan | Bot trích câu đúng nhưng khác đáp án mẫu | Cho phép đáp án thay thế (`any_of`) |
| Ngoài phạm vi chưa nói rõ | Bài tập, code, câu chửi | Thêm luật ngoài phạm vi (bản 22); câu lạ để router v6 học |
| Nhãn đề cũ | Bộ đề ghi "hẹn lại" cho câu phép tính, nhưng máy tính SQL (`shop_calc`) đã tính đúng | Cổng không tính đây là lỗi; cần sửa nhãn của bộ đề |

**Lỗi do mô hình hay do code?** Trước khi quyết định có huấn luyện lại router hay không, nhóm viết script `failure_causes.py` để gán **một** nguyên nhân cho mỗi câu trượt ở phần development, theo thứ tự: hạ tầng → luật chặn sai → router chọn sai đường → tìm kiếm không ra tài liệu đúng → chọn sai câu trích → nói sai phạm vi. Kết quả trên bản 21 (trước khi thêm luật ngoài phạm vi):

*Bảng 3.10. Nguyên nhân các câu development còn trượt ở bản 21*

| Nguyên nhân | Số câu | Thuộc về |
|---|---|---|
| Router chọn sai đường | 27 (14 ở bộ ngoài phạm vi, 11 ở expansion, 2 ở natural) | Mô hình |
| Chọn sai câu trích | 18 | Mô hình |
| Nói sai phạm vi | 2 | Mô hình |
| Tìm kiếm không ra tài liệu đúng | 8 | Code |

Đọc kỹ thì 6 trong 11 câu "router sai" của expansion thật ra là **nhãn đề cũ**: máy tính SQL đã trả lời đúng. Ba trong 8 câu "tìm kiếm" có chung một nguyên nhân trong code: khi câu hỏi gắn với một sản phẩm, bot chỉ đưa bản ghi sản phẩm mà không đưa bài kỹ thuật liên quan. Quyết định của nhóm:

1. 14 câu ngoài phạm vi: sửa bằng luật trước, vì rẻ hơn huấn luyện (bản 22).
2. Phần lỗi do mô hình còn lại (chọn câu trích, router với câu lạ): đủ nhiều để huấn luyện bản v6.

### 3.10.4. So sánh với mốc TF-IDF + hồi quy logistic

Để trả lời câu hỏi "có cần LLM không, hay một bộ phân lớp đơn giản là đủ?", nhóm dựng một mốc so sánh: TF-IDF (từ 1–2 âm tiết, cộng ký tự 2–4) + hồi quy logistic có trọng số theo lớp, học từ 640 câu của dữ liệu router v5. Hướng xử lý mong đợi được quy về 7 nhãn (`facts`, `unknown`, `semantic` → `answer`). So sánh với hướng xử lý (`basic_action`) mà **cả hệ thống** bản 22 chọn:

*Bảng 3.11. Mốc TF-IDF + hồi quy logistic so với cả hệ thống bản 22*

| Phần dữ liệu | Số câu | Mô hình | Accuracy | Macro-F1 |
|---|---|---|---|---|
| Development (natural, natural2, policy, kb3, ngoài phạm vi) | 810 | TF-IDF + hồi quy logistic | 0,863 | 0,501 |
| | | Cả hệ thống bản 22 | 0,996 | 0,949 |
| Validation (kb3, expansion, ngoài phạm vi; chỉ xem số tổng) | 329 | TF-IDF + hồi quy logistic | 0,842 | 0,626 |
| | | Cả hệ thống bản 22 | 0,930 | 0,828 |

Cách đọc bảng:

- Con số trên phần development **thiên vị hệ thống**, vì các luật được viết dựa trên chính các câu này. Phép so sánh công bằng là phần **validation**, nơi cả hai đều chưa từng nhìn thấy câu hỏi: hệ thống hơn mốc 0,20 macro-F1.
- Đây là so sánh **cả hệ thống** (luật + Qwen3 4B), không phải riêng Qwen3 4B, vì đề tài dùng chúng cùng nhau. Mốc TF-IDF + hồi quy logistic cũng có thể được ghép thêm luật; khi đó khoảng cách sẽ nhỏ hơn.
- Mốc học từ câu tự sinh, nên kém nhất ở các nhãn hiếm và ở câu ngoài phạm vi (Bảng 2.13). Đây đúng là điểm yếu của bộ phân lớp "túi từ" khi ít dữ liệu: không có từ khóa quen thì không đoán được.

Script dựng lại bảng này nằm ở `Bao_Cao/cong_cu/moc_tfidf_logistic.py`.

## 3.11. Hạn chế và hướng phát triển

**Hạn chế:**

1. **Dữ liệu kinh doanh là mô phỏng.** Kết quả cho thấy hệ thống làm đúng trên dữ liệu có cấu trúc giống thật, nhưng chưa được thử với dữ liệu và câu hỏi của khách thật.
2. **Chính sách cửa hàng là bản soạn tạm**, cần thay bằng chính sách thật.
3. **Ảnh sản phẩm chưa có quyền dùng thương mại.**
4. **Tốc độ phụ thuộc phần cứng:** trên GPU T4 mỗi câu mất 3–4 giây, nhưng trên máy cá nhân thiếu RAM có câu mất tới 20–120 giây.
5. **Câu ngoài phạm vi kiểu lạ:** phần development đạt 48/48 nhờ luật, nhưng phần validation chỉ 24/32; luật chưa khái quát được.
6. **Router đang là mô hình gốc:** bản tinh chỉnh v5 chưa qua cổng; router chưa có ngưỡng tin cậy để tự chuyển sang hỏi lại khi không chắc.
7. **Bộ xếp lại (cross-encoder)** đã huấn luyện nhưng chưa bật, vì chưa qua hết các bộ đánh giá.
8. **Một số nhãn trong bộ đề đã cũ:** 6 câu phép tính của bộ expansion ghi "hẹn lại" trong khi máy tính SQL đã tính đúng.

**Hướng phát triển:**

1. Thu thập câu hỏi thật của khách (đã ẩn danh) để đánh giá và huấn luyện; khi có dữ liệu này thì thử PhoBERT tinh chỉnh làm bộ phân lớp ý định và so với mốc ở mục 3.10.4.
2. Huấn luyện router bản v6 trên câu hỏi ngoài phạm vi viết mới (chưa từng xem bộ đánh giá), câu đối chứng và yêu cầu thao tác của admin; chỉ dùng nếu qua cổng so với bản 22.
3. Thêm ngưỡng tin cậy cho router (mục 2.7): không chắc thì hỏi lại.
4. Sửa lỗi tìm kiếm do code: khi câu hỏi gắn với một sản phẩm, vẫn cho bài kỹ thuật liên quan cạnh tranh với bản ghi sản phẩm.
5. Thử đổi mô hình vector nhúng sang loại dùng RoPE, đọc được đoạn dài hơn (bge-m3, multilingual-e5), đo lại trên các bộ câu hỏi.
6. Bật bộ xếp lại khi qua đủ cổng.
7. Mở rộng phần trả lời số liệu theo hướng Text-to-SQL có kiểm tra (mục 1.7), giữ nguyên nguyên tắc chỉ đọc.
8. Triển khai dịch vụ AI lên GPU trên cloud để web dùng ổn định.
9. Khai thác thêm kho dữ liệu cho admin: dự báo nhu cầu, phân khúc khách hàng (RFM), luật kết hợp giữa các sản phẩm hay mua cùng nhau (ví dụ laptop → chuột ở mục 1.4.1).

## Tiểu kết Chương 3

Chương 3 đã trình bày cách áp dụng lý thuyết vào chatbot TechStore:

- Dữ liệu được ghi nguồn đầy đủ và tổ chức thành một kho dữ liệu nhỏ theo lược đồ chòm sao, nạp qua quy trình ETL có kiểm tra.
- Câu hỏi đi qua luật chắc chắn trước, rồi qua router Qwen3 4B bản gốc. Tài liệu được tìm bằng truy xuất lai TF-IDF + BM25 + vector nhúng, trộn bằng RRF. Bằng chứng cho câu hỏi sản phẩm được chọn bằng bản Qwen3 4B tinh chỉnh LoRA. Số liệu admin được tính bằng SQL.
- Hệ thống được đo trên hơn 1.500 câu hỏi, tách development/validation, có cổng chống đi lùi. Bản 22 đạt 87,6–97,5% ở natural, natural2, policy, kb3 và expansion development; expansion validation đạt 78,4%; bộ ngoài phạm vi đạt 90,0% câu ngoài lề và 85,0% câu đối chứng. Trên phần validation, cả hệ thống hơn mốc TF-IDF + hồi quy logistic 0,20 macro-F1. Câu ngoài phạm vi kiểu lạ là điểm yếu còn lại, sẽ xử lý ở router v6.

# KẾT LUẬN

**Kết quả đạt được:**

1. Về lý thuyết, báo cáo đã trình bày:
   - Kho dữ liệu: định nghĩa, kiến trúc, mô hình nhiều chiều, thao tác OLAP và các kiểu máy chủ ROLAP/MOLAP/HOLAP, hai trường phái Inmon và Kimball, kiến trúc medallion.
   - Khai phá dữ liệu: khái niệm, phân loại, luật kết hợp, quy trình KDD và CRISP-DM, tiền xử lý và tiêu chí chất lượng dữ liệu, lĩnh vực ứng dụng và hướng nghiên cứu (kể cả Text-to-SQL).
   - Các thuật toán của nhánh khai phá văn bản, truy xuất thông tin và phân lớp: TF-IDF, BM25, vector nhúng, RRF, chia đoạn tài liệu, kNN, Naive Bayes, hồi quy logistic, SVM, cây quyết định, transformer và LoRA; cách xử lý nhãn lệch và ngưỡng tin cậy. Có ví dụ tính tay cho TF-IDF, BM25, cosine, RRF, Naive Bayes, entropy, luật kết hợp và các độ đo đánh giá.
2. Về ứng dụng, đề tài đã:
   - Xây dựng được chatbot TechStore có dẫn nguồn, phân quyền khách và admin, trả lời số liệu bằng SQL.
   - Tổ chức dữ liệu thành kho dữ liệu nhỏ có ghi nguồn đầy đủ.
   - Đo chất lượng bằng các bộ câu hỏi tách riêng, có quy trình chống đi lùi.

**Bài học rút ra:**

- **Dữ liệu và cách đo quan trọng không kém thuật toán.** Nhiều lần điểm tăng không phải nhờ đổi mô hình mà nhờ sửa dữ liệu, sửa luật định tuyến, hoặc sửa cách chấm.
- **Điểm của một bộ phận không thay được phép đo cả hệ thống.** Router v5 chọn đúng 94,4% phần dev nhưng làm cả hệ thống đi lùi, nên không được dùng.
- **Kết hợp nhiều phương pháp tốt hơn dựa vào một phương pháp:** luật cho ca chắc chắn, mô hình cho ca đa dạng, SQL cho con số, truy xuất lai cho tìm kiếm.
- **Không tin điểm trên dữ liệu đã nhìn.** Khoảng cách giữa development và validation nhắc nhở rằng phải giữ một phần dữ liệu không đụng tới.

**Hướng phát triển:** cải thiện nhóm câu ngoài phạm vi, thu câu hỏi thật của khách, triển khai lên GPU cloud, và khai thác kho dữ liệu cho các bài toán dự báo, phân khúc khách hàng, luật kết hợp.

# TÀI LIỆU THAM KHẢO

[1] J. Han, M. Kamber, J. Pei, *Data Mining: Concepts and Techniques*, 3rd ed., Morgan Kaufmann, 2011.

[2] U. Fayyad, G. Piatetsky-Shapiro, P. Smyth, "From Data Mining to Knowledge Discovery in Databases," *AI Magazine*, vol. 17, no. 3, pp. 37–54, 1996. doi:10.1609/aimag.v17i3.1230. [https://ojs.aaai.org/index.php/aimagazine/article/view/1230](https://ojs.aaai.org/index.php/aimagazine/article/view/1230)

[3] W. H. Inmon, *Building the Data Warehouse*, 4th ed., Wiley, 2005.

[4] R. Kimball, M. Ross, *The Data Warehouse Toolkit: The Definitive Guide to Dimensional Modeling*, 3rd ed., Wiley, 2013.

[5] R. Agrawal, R. Srikant, "Fast Algorithms for Mining Association Rules," *Proc. 20th VLDB*, pp. 487–499, 1994.

[6] X. Wu, V. Kumar, J. R. Quinlan, et al., "Top 10 algorithms in data mining," *Knowledge and Information Systems*, vol. 14, no. 1, pp. 1–37, 2008. doi:10.1007/s10115-007-0114-2.

[7] P. Chapman, J. Clinton, R. Kerber, et al., *CRISP-DM 1.0: Step-by-step data mining guide*, SPSS, 2000.

[8] P. Lewis, E. Perez, A. Piktus, et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," *NeurIPS*, 2020. [https://arxiv.org/abs/2005.11401](https://arxiv.org/abs/2005.11401)

[9] Y. Gao, Y. Xiong, X. Gao, et al., "Retrieval-Augmented Generation for Large Language Models: A Survey," 2023. [https://arxiv.org/abs/2312.10997](https://arxiv.org/abs/2312.10997)

[10] D. Q. Nguyen, A. T. Nguyen, "PhoBERT: Pre-trained language models for Vietnamese," *Findings of EMNLP*, 2020. [https://arxiv.org/abs/2003.00744](https://arxiv.org/abs/2003.00744)

[11] C. D. Manning, P. Raghavan, H. Schütze, *Introduction to Information Retrieval*, Cambridge University Press, 2008. [https://nlp.stanford.edu/IR-book/](https://nlp.stanford.edu/IR-book/)

[12] G. Salton, C. Buckley, "Term-weighting approaches in automatic text retrieval," *Information Processing & Management*, vol. 24, no. 5, pp. 513–523, 1988.

[13] S. Robertson, H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in Information Retrieval*, vol. 3, no. 4, pp. 333–389, 2009.

[14] G. V. Cormack, C. L. A. Clarke, S. Büttcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," *Proc. SIGIR*, pp. 758–759, 2009. doi:10.1145/1571941.1572114. [https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

[15] N. Reimers, I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," *EMNLP*, 2019. [https://arxiv.org/abs/1908.10084](https://arxiv.org/abs/1908.10084)

[16] J. Devlin, M.-W. Chang, K. Lee, K. Toutanova, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding," *NAACL*, 2019. [https://arxiv.org/abs/1810.04805](https://arxiv.org/abs/1810.04805)

[17] V. Karpukhin, B. Oğuz, S. Min, et al., "Dense Passage Retrieval for Open-Domain Question Answering," *EMNLP*, 2020. [https://arxiv.org/abs/2004.04906](https://arxiv.org/abs/2004.04906)

[18] R. Nogueira, K. Cho, "Passage Re-ranking with BERT," 2019. [https://arxiv.org/abs/1901.04085](https://arxiv.org/abs/1901.04085)

[19] Y. A. Malkov, D. A. Yashunin, "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs," *IEEE TPAMI*, 2018. [https://arxiv.org/abs/1603.09320](https://arxiv.org/abs/1603.09320)

[20] T. Cover, P. Hart, "Nearest neighbor pattern classification," *IEEE Transactions on Information Theory*, vol. 13, no. 1, pp. 21–27, 1967.

[21] C. Cortes, V. Vapnik, "Support-vector networks," *Machine Learning*, vol. 20, pp. 273–297, 1995.

[22] J. R. Quinlan, *C4.5: Programs for Machine Learning*, Morgan Kaufmann, 1993.

[23] L. Breiman, J. Friedman, R. Olshen, C. Stone, *Classification and Regression Trees*, Wadsworth, 1984.

[24] E. J. Hu, Y. Shen, P. Wallis, et al., "LoRA: Low-Rank Adaptation of Large Language Models," *ICLR*, 2022. [https://arxiv.org/abs/2106.09685](https://arxiv.org/abs/2106.09685)

[25] T. Dettmers, A. Pagnoni, A. Holtzman, L. Zettlemoyer, "QLoRA: Efficient Finetuning of Quantized LLMs," *NeurIPS*, 2023. [https://arxiv.org/abs/2305.14314](https://arxiv.org/abs/2305.14314)

[26] Qwen Team, "Qwen3 Technical Report," 2025. [https://arxiv.org/abs/2505.09388](https://arxiv.org/abs/2505.09388); mô hình: [https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)

[27] A. Vaswani, N. Shazeer, N. Parmar, et al., "Attention Is All You Need," *NeurIPS*, 2017. [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)

[28] K. Järvelin, J. Kekäläinen, "Cumulated gain-based evaluation of IR techniques," *ACM TOIS*, vol. 20, no. 4, pp. 422–446, 2002.

[29] A. McCallum, K. Nigam, "A Comparison of Event Models for Naive Bayes Text Classification," *AAAI Workshop on Learning for Text Categorization*, 1998.

[30] J. H. Friedman, "Greedy function approximation: A gradient boosting machine," *Annals of Statistics*, vol. 29, no. 5, pp. 1189–1232, 2001.

[31] R. J. Hyndman, G. Athanasopoulos, *Forecasting: Principles and Practice*, 3rd ed., OTexts, 2021. [https://otexts.com/fpp3/](https://otexts.com/fpp3/)

[32] dangvantuan, "vietnamese-embedding," Hugging Face, giấy phép Apache 2.0, bản `4ab46e4`. [https://huggingface.co/dangvantuan/vietnamese-embedding](https://huggingface.co/dangvantuan/vietnamese-embedding)

[33] docyx, "pc-part-dataset," GitHub, giấy phép MIT, commit `c52a04c`. [https://github.com/docyx/pc-part-dataset](https://github.com/docyx/pc-part-dataset)

[34] msjahid, "Ryans Laptop Inventory and Specifications," Kaggle, giấy phép Apache 2.0. [https://www.kaggle.com/datasets/msjahid/ryans-laptop-inventory-and-specifications](https://www.kaggle.com/datasets/msjahid/ryans-laptop-inventory-and-specifications)

[35] Unsloth AI, "Unsloth: fast LLM fine-tuning." [https://github.com/unslothai/unsloth](https://github.com/unslothai/unsloth)

[36] Ollama. [https://github.com/ollama/ollama](https://github.com/ollama/ollama)

[37] F. Pedregosa, G. Varoquaux, A. Gramfort, et al., "Scikit-learn: Machine Learning in Python," *JMLR*, vol. 12, pp. 2825–2830, 2011.

[38] M. H. Dao, T. H. Truong, D. Q. Nguyen, "Intent Detection and Slot Filling for Vietnamese," *Proc. INTERSPEECH*, 2021. [https://arxiv.org/abs/2104.02021](https://arxiv.org/abs/2104.02021); mã nguồn và bộ PhoATIS: [https://github.com/VinAIResearch/JointIDSF](https://github.com/VinAIResearch/JointIDSF)

[39] L. Pham, T. Luu, T. Vo, M. Nguyen, V. Hoang, "VN-MTEB: Vietnamese Massive Text Embedding Benchmark," 2025. [https://arxiv.org/abs/2507.21500](https://arxiv.org/abs/2507.21500)

[40] S. Bennani, C. Moslonka, "A Systematic Analysis of Chunking Strategies for Reliable Question Answering," 2026. [https://arxiv.org/abs/2601.14123](https://arxiv.org/abs/2601.14123)

[41] T. Formal, B. Piwowarski, S. Clinchant, "SPLADE: Sparse Lexical and Expansion Model for First Stage Ranking," *Proc. SIGIR*, 2021. [https://arxiv.org/abs/2107.05720](https://arxiv.org/abs/2107.05720)

[42] O. Khattab, M. Zaharia, "ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT," *Proc. SIGIR*, 2020. [https://arxiv.org/abs/2004.12832](https://arxiv.org/abs/2004.12832)

[43] J. J. Rocchio, "Relevance Feedback in Information Retrieval," in G. Salton (ed.), *The SMART Retrieval System: Experiments in Automatic Document Processing*, Prentice-Hall, pp. 313–323, 1971.

[44] T. Yu, R. Zhang, K. Yang, et al., "Spider: A Large-Scale Human-Labeled Dataset for Complex and Cross-Domain Semantic Parsing and Text-to-SQL Task," *Proc. EMNLP*, 2018. [https://arxiv.org/abs/1809.08887](https://arxiv.org/abs/1809.08887)

[45] R. Y. Wang, D. M. Strong, "Beyond Accuracy: What Data Quality Means to Data Consumers," *Journal of Management Information Systems*, vol. 12, no. 4, pp. 5–33, 1996.

[46] Databricks, "What is a medallion architecture?" [https://www.databricks.com/glossary/medallion-architecture](https://www.databricks.com/glossary/medallion-architecture)

[47] Apache Lucene, "BM25Similarity" (tài liệu API, bản 9.9). [https://lucene.apache.org/core/9_9_0/core/org/apache/lucene/search/similarities/BM25Similarity.html](https://lucene.apache.org/core/9_9_0/core/org/apache/lucene/search/similarities/BM25Similarity.html)

[48] D. Brown, "rank_bm25: A collection of BM25 algorithms in Python," GitHub. [https://github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25)

[49] dangvantuan, "vietnamese-embedding: config.json và sentence_bert_config.json," Hugging Face, bản `4ab46e4`. [https://huggingface.co/dangvantuan/vietnamese-embedding/tree/main](https://huggingface.co/dangvantuan/vietnamese-embedding/tree/main)

[50] Y. Geifman, R. El-Yaniv, "Selective Classification for Deep Neural Networks," *NeurIPS*, 2017. [https://arxiv.org/abs/1705.08500](https://arxiv.org/abs/1705.08500)

[51] J. Chen, S. Xiao, P. Zhang, et al., "BGE M3-Embedding: Multi-Lingual, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation," 2024. [https://arxiv.org/abs/2402.03216](https://arxiv.org/abs/2402.03216)

[52] L. Wang, N. Yang, X. Huang, et al., "Multilingual E5 Text Embeddings: A Technical Report," 2024. [https://arxiv.org/abs/2402.05672](https://arxiv.org/abs/2402.05672)

# PHỤ LỤC

## Phụ lục A. Nguồn dữ liệu chi tiết

### A.1. Bộ dữ liệu tham khảo cho bộ mô phỏng

Các bộ này chỉ dùng để lấy phân phối thống kê, **không đưa vào chatbot** và không phân phối lại.

*Bảng A.1. Bộ dữ liệu tham khảo*

| Bộ dữ liệu | Nơi lấy | Giấy phép |
|---|---|---|
| [abdelrahmanemad594/laptop-prices](https://www.kaggle.com/datasets/abdelrahmanemad594/laptop-prices) | Kaggle | Apache 2.0 |
| [elvinrustam/ebay-laptops-and-netbooks-sales](https://www.kaggle.com/datasets/elvinrustam/ebay-laptops-and-netbooks-sales) | Kaggle | CC0 |
| [juanmerinobermejo/laptops-price-dataset](https://www.kaggle.com/datasets/juanmerinobermejo/laptops-price-dataset) | Kaggle | Apache 2.0 |
| [mkechinov/ecommerce-behavior-data-from-multi-category-store](https://www.kaggle.com/datasets/mkechinov/ecommerce-behavior-data-from-multi-category-store) | Kaggle | Bản quyền tác giả gốc |
| [mkechinov/ecommerce-events-history-in-electronics-store](https://www.kaggle.com/datasets/mkechinov/ecommerce-events-history-in-electronics-store) | Kaggle | Bản quyền tác giả gốc |
| [mkechinov/ecommerce-purchase-history-from-electronics-store](https://www.kaggle.com/datasets/mkechinov/ecommerce-purchase-history-from-electronics-store) | Kaggle | Bản quyền tác giả gốc |
| [msjahid/ryans-laptop-inventory-and-specifications](https://www.kaggle.com/datasets/msjahid/ryans-laptop-inventory-and-specifications) | Kaggle | Apache 2.0 |
| [muhammadshahrayar/transactional-retail-dataset-of-electronics-store](https://www.kaggle.com/datasets/muhammadshahrayar/transactional-retail-dataset-of-electronics-store) | Kaggle | CC0 |
| [muhammadshahrayar/transactional-retail-of-electronics-store](https://www.kaggle.com/datasets/muhammadshahrayar/transactional-retail-of-electronics-store) | Kaggle | Chưa xác minh |
| [olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) | Kaggle | CC BY-NC-SA 4.0 (không thương mại) |
| Online Retail II | UCI Machine Learning Repository | CC BY 4.0 |

### A.2. Nguồn của 43 bài kỹ thuật

- **Intel:**
  - [RAM cho chơi game](https://www.intel.com/content/www/us/en/gaming/resources/how-much-ram-gaming.html)
  - [CPU chơi game](https://www.intel.com/content/www/us/en/gaming/resources/gaming-cpu.html)
  - [CPU và GPU](https://www.intel.com/content/www/us/en/products/docs/processors/cpu-vs-gpu.html)
  - [Chọn laptop gaming](https://www.intel.com/content/www/us/en/gaming/resources/how-to-pick-the-best-gaming-laptop.html)
  - [Thunderbolt 4 và USB-C](https://www.intel.com/content/www/us/en/architecture-and-technology/thunderbolt/thunderbolt-4-vs-usb-c.html)
  - [Thunderbolt 5](https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2023-09/thunderbolt-5-technology-brief.pdf)
  - [Băng tần Wi-Fi](https://www.intel.com/content/www/us/en/support/articles/000099711/wireless.html)
  - [Wi-Fi 7](https://www.intel.com/content/dam/www/central-libraries/us/en/documents/2022-07/wifi7-features-bandwidth-qam-infographic-nologo-1920-1080.pdf)
  - [GPU tích hợp và rời](https://www.intel.com/content/www/us/en/support/articles/000057824/graphics.html)
  - [Bộ nhớ đồ họa](https://www.intel.com/content/www/us/en/support/articles/000041253/graphics.html)
  - Tên thế hệ CPU: [000032203](https://www.intel.com/content/www/us/en/support/articles/000032203/processors/intel-core-processors.html), [000100149](https://www.intel.com/content/www/us/en/support/articles/000100149/processors/intel-core-processors.html)
- **Kingston:**
  - [M.2 và SSD](https://www.kingston.com/en/blog/pc-performance/two-types-m2-vs-ssd)
  - [DDR5](https://media.kingston.com/kingston/articles/MKF_954-DDR5-Collateral_us.pdf)
  - [Hướng dẫn bộ nhớ flash](https://media.kingston.com/pdfs/MKF_283.2_Flash_Memory_Guide_VN.pdf)
  - [NV2](https://www.kingston.com/datasheets/SNV2S_en.pdf)
  - [KC3000](https://www.kingston.com/datasheets/KC3000_en.pdf)
- **Samsung:**
  - [OLED](https://www.samsung.com/us/tvs/tv-buying-guide/why-oled-tvs-are-worth-it/)
  - [Tần số quét](https://insights.samsung.com/2026/06/17/finding-the-right-refresh-rate-know-the-best-hz-for-your-needs/)
  - Over-provisioning SSD: [white paper](https://download.semiconductor.samsung.com/resources/white-paper/S190311-SAMSUNG-Memory-Over-Provisioning-White-paper.pdf), [845DC](https://download.semiconductor.samsung.com/resources/others/Samsung_SSD_845DC_04_Over-provisioning.pdf)
- **BenQ:**
  - [Tấm nền TN/VA/IPS](https://www.benq.com/en-us/knowledge-center/knowledge/how-to-choose-between-tn-va-and-ips-panels-for-the-games-you-play/.html)
  - [Độ trễ và thời gian phản hồi](https://www.benq.com/en-us/knowledge-center/knowledge/gaming-monitor-input-lag-versus-response-time-whats-the-difference-and-why-should-i-care.html)
  - [Màn hình chỉnh ảnh](https://www.benq.com/en-us/knowledge-center/knowledge/choosing-the-right-monitor-photo-editing.html)
- **Lenovo PSREF:**
  - [LOQ 15IRH8](https://psref.lenovo.com/syspool/Sys/PDF/LOQ/LOQ_15IRH8/LOQ_15IRH8_Spec.pdf)
  - [Legion Slim 5 16IRH8](https://psref.lenovo.com/syspool/Sys/PDF/Legion/Legion_Slim_5_16IRH8/Legion_Slim_5_16IRH8_Spec.pdf)
  - [ThinkBook 15 G2 ITL](https://psref.lenovo.com/syspool/Sys/PDF/ThinkBook/ThinkBook_15_G2_ITL/ThinkBook_15_G2_ITL_Spec.pdf)
  - [IdeaPad 3 15ITL6](https://psref.lenovo.com/syspool/Sys/PDF/IdeaPad/IdeaPad_3_15ITL6/IdeaPad_3_15ITL6_Spec.pdf)
- **MSI:**
  - [Modern 15 B12M-408AU](https://storage-asset.msi.com/specSheet/au/bnp/Modern%2015%20B12M-408AU.pdf)
  - [Modern 15 B12M-081SG](https://storage-asset.msi.com/specSheet/sg/bnp/Modern%2015%20B12M-081SG.pdf)
- **Các hãng khác:**
  - [Apple MacBook Air M1](https://support.apple.com/en-us/111883)
  - [Logitech G305](https://www.logitechg.com/en-us/products/gaming-mice/g305-lightspeed-wireless-gaming-mouse.910-005280.html)
  - [AMD Ryzen 9000](https://www.amd.com/en/partner/articles/ryzen-9000-series-processors.html)
  - [NVIDIA VRAM dòng RTX 40](https://www.nvidia.com/en-in/geforce/news/rtx-40-series-vram-video-memory-explained/)
  - [Adobe Photoshop: yêu cầu cấu hình](https://helpx.adobe.com/photoshop/desktop/get-started/technical-requirements-installation/adobe-photoshop-on-desktop-technical-requirements.html)
  - [USB-IF USB PD](https://www.usb.org/usb-charger-pd)
  - [NVM Express](https://nvmexpress.org/)
  - [Crucial DDR5](https://stage.crucial.com/articles/about-memory/everything-about-ddr5-ram)
  - 80 PLUS (CLEAResult): [chương trình](https://www.clearesult.com/80plus/program-details), [hỏi đáp](https://www.clearesult.com/insights/answering-your-80-PLUS-questions)

Link Crucial trỏ vào `stage.crucial.com`, là trang thử nghiệm của Crucial; sẽ đổi sang `www.crucial.com` khi cập nhật tài liệu.

### A.3. Ảnh sản phẩm

- 37 ảnh: nguồn ghi trong `AI/data/product_images/manifest.json`, lấy từ trang của hãng (Asus, Lenovo, MSI, Acer) và nhà bán lẻ ở nhiều nước, gồm cả Việt Nam.
- 30 ảnh bổ sung ngày 3/11/2026: lấy từ trang hãng (MSI, Samsung, LG) và nhà bán lẻ (Ryans, LDLC, CellphoneS, Memoryzone, Nguyễn Công PC, Quốc Đạt…).
- Ảnh dự phòng trên web lấy từ Unsplash, theo [Unsplash License](https://unsplash.com/license).
- Trường `rights_status` của mọi ảnh sản phẩm là "chưa xác minh quyền"; `commercial_reuse_approved = false`.

## Phụ lục B. Một số câu SQL mẫu trên kho dữ liệu

**Lãi gộp và biên lãi gộp theo tháng:**

```sql
SELECT month, net_revenue, gross_profit,
       ROUND(100.0 * gross_profit / net_revenue, 1) AS bien_lai_gop_pct
FROM monthly_pnl ORDER BY month;
```

**Ba sản phẩm doanh thu cao nhất:**

```sql
SELECT p.name, SUM(l.revenue) AS doanh_thu
FROM financial_ledger l JOIN products p ON p.sku = l.sku
GROUP BY p.sku ORDER BY doanh_thu DESC LIMIT 3;
```

**Số đơn theo kênh bán (slice theo chiều kênh):**

```sql
SELECT channel, COUNT(*) AS so_don FROM orders GROUP BY channel;
-- store: 768 | website: 460 | social: 199
```

**Tồn kho cuối kỳ:**

```sql
SELECT sku, quantity, value FROM inventory_daily WHERE day = '2026-09-30';
```
