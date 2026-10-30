# Thiết kế dữ liệu, RAG và huấn luyện cho ShopBot

## Mục tiêu xuyên suốt

Một chatbot người mua và một chatbot chủ shop, dùng local Ollama; Kev giúp định
tuyến nhưng không quyết định quyền truy cập. Dùng danh mục chọn lọc, số liệu có
thể đối soát, tài liệu có nguồn/phiên bản; trả lời có số cụ thể, biểu đồ và dẫn
chứng. Cập nhật dữ liệu định kỳ khác với huấn luyện trọng số. Thử trên Streamlit
trước; tích hợp web backend, Docker và triển khai là các bước riêng chưa hoàn tất.

Đã đọc lại mục 8.4–8.6 của `documnets/ke-hoach-ba-chatbot-shop-dien-tu.md` và
phần công cụ/RAG ở chương 3–4 của `D:/Chatbot/Ai-agent-book/book-vi`.
Đặc tả gốc gợi ý 3 shop, 150–300 sản phẩm, 24 tháng mỗi shop. Theo yêu cầu mới,
phiên bản này thu gọn thành **1 shop, 67 sản phẩm, 12 tháng trọn kỳ** để kiểm tra
độ nhất quán trước. Không tuyên bố đạt quy mô đầy đủ của đặc tả gốc.

## Dữ liệu đã làm

| Gói | Đường dẫn tính từ AI | Phạm vi |
|---|---|---|
| Danh mục nguồn | `data/structured/processed/product_catalog.jsonl` | 67 sản phẩm có nguồn gốc, 19 laptop + 48 linh kiện/phụ kiện |
| SQL danh mục riêng | `data/product_sql/products.sqlite` và `.sql` | Giá thị trường chưa xác minh vẫn NULL; không trộn với giá giả lập |
| Kinh doanh mô phỏng | `data/business_sql/scenario_v1/shop.sqlite` và `.sql` | 01/10/2025–30/09/2026, cùng mã danh mục |
| Bản CSV | `data/business_sql/scenario_v1/csv/` | Đơn, chi tiết, nhập, nhận, hoàn, tồn kho, chi phí, P&L |
| Giả định | `data/business_sql/scenario_v1/assumptions.json` | Quy mô, mức cầu, giá, biên, mùa vụ, cách hạch toán |
| Đối soát | `data/business_sql/scenario_v1/validation_report.json` | Khóa ngoại, SKU, FIFO, tồn từng ngày, tiền, SQL roundtrip |
| Tài liệu shop giả lập | `data/business_sql/scenario_v1/documents/` | 22 tài liệu duyệt cho thử nghiệm + 4 bản nháp bị loại khỏi RAG |
| Đáp án ẩn | `data/business_sql/scenario_v1/evaluation_only/` | Sự kiện cài sẵn và nhu cầu không được đáp ứng; không nạp RAG hoặc train |
| Ảnh | `data/product_images/` | 37 ảnh cũ còn liên kết; 30 sản phẩm bổ sung chưa tải ảnh |

**Khóa nối duy nhất:** `record_id` nguồn = `products.product_id` ở gói danh mục
= `products.sku` ở gói kinh doanh. Tất cả chi tiết bán/nhập/hoàn/tồn tham chiếu
khóa này. Không ghép REES46 vào danh mục theo tên hãng hoặc tự đổi mã.

Gói mô phỏng có 1.427 đơn, 1.717 dòng bán, 320 đơn đặt nhập, 317 phiếu nhận,
31 lượt hoàn, 24.455 bản ghi tồn kho ngày và 99 khoản chi. Cả 67 SKU có bán.
Ba đơn đặt nhập chưa đến hạn nhận cuối kỳ là cam kết, không tính thành hàng đã nhập.

## Quy mô và tính thực tiễn của giả định

Một cửa hàng với 5 người kể cả chủ, bán tại quầy/website/social. Nhu cầu cơ sở
3,8 lượt thử mua/ngày, tăng cuối tuần và các kỳ cao điểm; có lượt không mua
được do hết hàng. 1.427 đơn/năm tương đương 3,91 đơn/ngày. Đây là kịch bản
shop nhỏ có giá trị đơn cao, không phải hàng chục nghìn đơn của chuỗi quốc gia.

- Doanh thu thuần sau hoàn trả: **13.495.418.000 VND/năm**, trung bình **1.124.618.167 VND/tháng**.
- Lợi nhuận gộp: **1.879.908.000 VND/năm**, biên gộp khoảng **13,93%**.
- Lợi nhuận hoạt động trước lãi vay và thuế: **487.858.402 VND/năm**.
- Tồn đầu kỳ theo giá vốn: **1.502.710.000 VND**; tồn cuối kỳ: **1.654.450.000 VND**.
- Có tháng lợi nhuận hoạt động âm; không ép simulator luôn có lời.

| Tháng | Doanh thu thuần VND | Lợi nhuận hoạt động trước lãi vay/thuế VND |
|---|---:|---:|
| 2025-10 | 984,310,000 | 36,078,590 |
| 2025-11 | 1,493,219,000 | 60,526,591 |
| 2025-12 | 1,474,785,000 | 95,154,365 |
| 2026-01 | 1,077,004,000 | -1,390,044 |
| 2026-02 | 609,442,000 | -24,658,862 |
| 2026-03 | 1,203,150,000 | 67,811,350 |
| 2026-04 | 997,980,000 | 38,254,220 |
| 2026-05 | 1,175,440,000 | 61,779,160 |
| 2026-06 | 838,580,000 | 13,557,620 |
| 2026-07 | 1,024,280,000 | 26,836,920 |
| 2026-08 | 1,427,320,000 | 45,648,480 |
| 2026-09 | 1,189,908,000 | 68,260,012 |

Giá bán là giả định trong khoảng theo nhóm; giá nguồn USD chỉ tham gia quy tắc
tham khảo với tỷ giá giả định 26.000, không phải giá bán hiện tại hoặc tỷ giá đã
kiểm chứng. Chi phí cố định gồm thuê mặt bằng 22 triệu, nhân sự kể cả chủ 52
triệu, điện nước 3,5 triệu, phần mềm 1,8 triệu, quản trị 3,5 triệu, khấu hao 3
triệu/tháng; marketing và phí giao/thu tiền tính riêng. Đây không phải báo giá
thuê hay mức lương khảo sát thị trường. Cần thay bằng thông tin địa bàn/shop thật.

Đã thống kê toàn bộ 885.129 sự kiện REES46 và mẫu đầu 200.000 dòng lịch sử mua.
Kết quả nằm trong `source_profile.json`: có 37.346 sự kiện purchase; mẫu lịch sử
có khoảng 1,83 dòng/đơn. Không coi tỷ lệ purchase/event là conversion theo khách,
không dùng 6 tháng của nguồn để suy ra mùa vụ đủ năm ở Việt Nam. Mức cầu và cơ
cấu laptop của shop vẫn là giả định chủ động, không gọi là đã khớp thống kê nguồn.

ACBS, báo cáo FRT ngày 08/05/2025, trang 2 và 5, cho bối cảnh về tăng trưởng,
biên và lỗ của FPT Shop: https://acbs.com.vn/Files/Domains/ACBS/WFL-1585/250508065942-1015-1015000001.pdf
Chỉ tham khảo cấu trúc tài chính và rủi ro; không lấy doanh thu toàn chuỗi hoặc
biên hợp nhất gồm Long Châu áp cho shop laptop này.

## Hạch toán để không matching sai

```text
Danh mục 67 SKU
  ├─ Đặt nhập → nhận hàng → lô FIFO → tồn kho theo ngày
  ├─ Đơn bán → dòng bán → xuất FIFO → doanh thu/giá vốn
  └─ Hoàn trả → hoàn tiền → nhập lại nếu bán được → đảo giá vốn tương ứng
                          ↓
                Sổ tài chính financial_ledger
                          ↓
             monthly_pnl + chi phí vận hành
```

Doanh thu thuần = tiền bán sau giảm giá − hoàn tiền. Giá vốn thuần = FIFO xuất
bán − giá vốn được đảo khi hoàn nhập lại. Lợi nhuận gộp = doanh thu thuần − giá
vốn thuần. Lợi nhuận hoạt động = lợi nhuận gộp − chi phí vận hành. Tiền mua hàng
chưa bán là tồn kho, không trừ cả giá trị nhập và giá vốn lần nữa. Dòng tiền giả
định thanh toán ngay; cộng lại khấu hao không bằng tiền. Chưa mô hình hóa VAT,
lãi vay và thuế thu nhập, vì vậy không gắn nhãn lợi nhuận sau thuế.

## Mỗi loại dữ liệu huấn luyện thế nào

| Thành phần | Làm gì | Có train không? | Kiểm chứng |
|---|---|---|---|
| Danh mục, giá, tồn, đơn, nhập, hoàn, chi phí | ETL, SQL, công cụ tính chỉ số | Không train model thuộc số | Đối soát, kiểm thử phép tính, sai quyền phải chặn |
| Tài liệu chiến lược/chính sách | Chia mục/câu/bảng, metadata, embedding, truy xuất | Ban đầu index; fine-tune retriever khi đo được lỗi | Recall, nguồn đúng, phiên bản đúng, ACL, câu không đủ chứng cứ |
| Kev | Chọn ý định/công cụ public | LoRA với nhãn ý định đã kiểm tra | Accuracy/F1/confusion/calibration; không cho phép nâng quyền |
| Dự báo nhu cầu | Chuỗi số lượng bán theo ngày | Mô hình riêng; Colab so baseline với gradient boosting | MAE/WAPE trên kỳ giữ riêng; một ngày walk-forward |
| Qwen trả lời | Ghép kết quả công cụ với đoạn trích, nêu giả thuyết và giới hạn | Chưa fine-tune bằng câu trả lời tự sinh | Số đúng, dẫn nguồn, không bịa/không tiết lộ nội bộ |

Embedding được chọn làm baseline triển khai thử: **intfloat/multilingual-e5-small**,
nhẹ hơn để phù hợp RAM 8GB/RTX2060 6GB cùng Ollama/Kev. Qwen3-Embedding-0.6B là
ứng viên so sánh sau, không tự nhận tốt hơn cho bộ dữ liệu này khi chưa benchmark.
Qwen3.5-4B GGUF là model sinh câu trả lời, không mặc định dùng nó làm embedding.
Model local Ollama đang cấu hình là Qwen2.5:1.5b; không tuyên bố đã triển khai
Qwen3.5 hoặc checkpoint train mới khi chưa kiểm tra.

Chunking hiện chuyển từ cắt ký tự sang chia theo heading, đoạn và ranh giới câu;
bảng dài tách theo dòng, lặp lại header. Giữ `chunk_id`, mục, nguồn, phiên bản,
ngày hiệu lực, quyền và nhãn mô phỏng. Đây là chia có xét cấu trúc/ngữ nghĩa câu,
không giả nhận đã train một mô hình semantic segmentation. V2 embedding tối đa
512 token; cần đo truncation và retrieval trên câu hỏi thực trước khi triển khai.

## Bộ train/đánh giá v2

`training/v2/ShopBot_v2_Colab.ipynb` đóng gói riêng, không ghi đè v1:

- 102 đoạn nguồn, 824 câu truy xuất, 96 ca hỏi công cụ số liệu, 4 ca giới hạn/ACL.
- Group sản phẩm và split của v1 được giữ nguyên; không đem test v1 sang train.
- Ca tài chính: 10/2025–05/2026 train, 06–07/2026 validation, 08–09/2026 test.
- Báo cáo tháng, đáp án sự kiện cài sẵn và latent demand không vào tập retriever.
- 96 câu công cụ đã hỏi trực tiếp Engine và so với view SQL: xem `training/v2/results/tool-evaluation.json`.
- Câu truy xuất hiện vẫn chủ yếu theo khuôn; chưa đủ chứng minh hiểu câu hỏi thật,
  nhiều bước, diễn đạt mơ hồ, chống prompt injection hoặc chất lượng trả lời tự do.

Colab huấn luyện embedding E5 rồi chạy dự báo riêng. Chỉ chọn trọng số embedding
nếu validation cải thiện; hòa thì giữ baseline. Dự báo chỉ chọn gradient boosting
nếu thắng naive theo tuần trên validation. Test chạy sau khi cố định lựa chọn.
Một năm giả lập không chứng minh deep learning dự báo đúng; chưa dùng dự báo để
ra quyết định nhập hàng hoặc tự thực hiện giao dịch.

Kết quả Colab đã xác minh ngày 19/10/2026:

- E5 v2 đã train 3 epoch trên Tesla T4, 569 mẫu supported thuộc 53 nhóm nguồn.
  Recall@1 validation trước/sau đều 1,0 trên 94 câu khuôn mẫu; test 94 câu đạt
  1,0. Chọn epoch 0 (baseline), không nhận checkpoint mới là cải tiến.
- Dự báo v2 chọn HistGradientBoosting bằng validation. Test một ngày walk-forward:
  MAE 2,51 sản phẩm/ngày, WAPE 43,68%; naive theo tuần MAE 3,43 và WAPE 59,54%.
  Sai số còn lớn và dữ liệu giả lập nên chưa duyệt triển khai dự báo.
- Kev v1 đã xác minh train xong 2 epoch/294 records seen, 38 optimizer steps;
  adapter đã tải về. Test pilot 36 câu: accuracy baseline 97,22%, sau train 100%.
  Đây là tập nhỏ theo khuôn; chưa tự thay endpoint hoặc hạ ngưỡng an toàn.
- Gói báo cáo/adapter tải từ Colab đã đối chiếu SHA256, lưu tại
  `training/colab_artifacts/20261019/`. Báo cáo gốc v2 ở
  `v2/retriever/training-summary.json` và `v2/forecast/report.json` bên trong đó.
- Checkpoint E5 v2 `last-trained/model.safetensors` đã tải về và đối chiếu checksum;
  chưa được chọn thay baseline. Sau rà soát giá giả lập theo cấu hình laptop,
  `training-input-verification.json` xác nhận corpus, QA, routing và chuỗi số lượng
  dùng để train trên Colab vẫn giống từng byte; chỉ số liệu tiền và đáp án công cụ
  được tính lại, kiểm thử lại. Không cần train lại model để cập nhật giá/doanh thu.

## Vòng gia sư một-một và cập nhật

1. Hỏi câu kiểm thử: số liệu, nhập/xuất, mục tiêu, phiên bản cũ/mới, thiếu dữ liệu,
   câu cần kết hợp SQL+tài liệu, câu vượt quyền. Lưu câu, tool, bằng chứng và kết quả.
2. Phân loại lỗi: dữ liệu sai, join sai, công thức sai, chọn tool sai, truy xuất
   sai, chọn phiên bản sai hay diễn giải quá chứng cứ.
3. Sửa đúng tầng; không thêm một đáp án bịa vào kho để che lỗi SQL hoặc dữ liệu.
4. Mẫu cần huấn luyện phải có nguồn hoặc kết quả công cụ chuẩn; review trước khi
   nhập train. Lỗi test giữ để báo cáo, không đưa lại vào train của cùng benchmark.
5. Train phiên mới trên Colab; so baseline, validation và test riêng. Chỉ cập nhật
   model local sau khi kiểm tra artifact, phân quyền và hồi quy. Giữ khả năng quay lui.

Đã có pipeline cập nhật tháng cho định dạng đơn giản trước đây và worker tham
khảo SBA. Gói sổ FIFO mới là fixture cố định; UI không cho đổ JSON bán hàng đơn
giản vào nó vì sẽ phá đối soát nhập/hoàn/tồn. Khi nhận dữ liệu thật cần ETL đầy
đủ vào schema này, staging → validate → publish phiên bản; tải tài liệu thì index
phiên bản mới. Chưa có lịch tự cào mọi nguồn hàng tuần/tháng hoặc tích hợp upload
frontend hiện tại vào AI; không gọi nhãn “đã lập chỉ mục” của frontend là RAG thật.

## Flow chatbot và các giới hạn còn lại

```text
Câu hỏi → xác thực vai trò → định tuyến bằng luật/Kev
   ├─ Thông số/giá/tồn → SQL/API danh mục
   ├─ Doanh thu/lời/lỗ → SQL + công cụ phân tích → bảng/biểu đồ
   ├─ Chính sách/kế hoạch → lọc quyền + hiệu lực → chunk retrieval
   └─ So kế hoạch → kết quả SQL + kế hoạch đúng kỳ → dẫn chứng + đề xuất có điều kiện
                                  ↓
             Qwen chọn/diễn giải từ chứng cứ → kiểm tra số và nguồn → trả lời
                                  ↓
                       log lỗi → vòng gia sư → benchmark
```

Đã chạy trong Streamlit: truy vấn catalog SQL, phân tích số, biểu đồ, so với mục
tiêu SQL và trích đoạn kế hoạch liên quan. Bộ tìm kiếm live vẫn là TF-IDF với
chunking mới, **chưa thay bằng checkpoint embedding v2**, chưa reranker/hybrid
dense-sparse. Qwen hiện chỉ chọn chứng cứ, chưa là agent phân tích tự do.
Phần lập kế hoạch chiến dịch/giải thích nguyên nhân đa bước đầy đủ vẫn cần phát
triển và đánh giá; không tự khẳng định nguyên nhân chỉ vì thấy tương quan.

Đã thêm công cụ xuất PNG báo cáo tổng quan và sơ đồ lời/lỗ, có nhận xét từ cùng
report SQL, kỳ, nguồn và nhãn mô phỏng. Xem `reports/README.md`; hỏi “Vẽ sơ đồ
lợi nhuận quý 3 năm 2026 và phân tích”. Chức năng vẽ không cần train model riêng.

## Vì sao điều chỉnh hướng ban đầu

- Tăng danh mục lên 67 giúp kiểm tra nghiệp vụ, nhưng tăng số dòng giả lập hay
  epoch không tự tạo trí thông minh. Thiếu thông tin thực phải giữ là thiếu.
- Không dùng deep learning để cộng trừ hoặc để nhớ doanh thu; SQL chính xác,
  cập nhật ngay và truy vết tốt hơn. Deep learning chỉ đáng dùng cho dự báo sau
  khi thắng baseline trên dữ liệu giữ riêng, tốt nhất là dữ liệu thật nhiều năm.
- Không nạp hết kho báo cáo vào RAG mà bỏ quyền/phiên bản. Mục tiêu chuỗi lớn
  khác shop; bản nháp khác bản duyệt; báo cáo tương lai không được rò vào quá khứ.
- Không “tự học” từ mọi câu model tự trả lời. Gia sư phải dựa trên bằng chứng và
  chỉ sửa lỗi đã xác định; nếu không, model có thể củng cố chính đáp án sai của nó.
- Chưa Docker/deploy ngay vì frontend đang là luồng riêng và dense retrieval
  chưa được nối. Đóng gói trước lúc kiểm chứng sẽ chỉ đóng gói cả các điểm sai.

## Tái tạo

Chạy bằng `AI/.venv/Scripts/python.exe` từ thư mục gốc dự án:

```text
AI/scripts/prepare_research_data.py
AI/scripts/export_catalog_sql.py
AI/scripts/build_simulated_shop.py
AI/scripts/profile_retail_sources.py
AI/scripts/validate_simulated_shop.py
AI/scripts/build_scenario_documents.py
AI/training/build_v2_pack.py
AI/training/make_v2_notebook.py
AI/training/evaluate_v2_tools.py
```

Không chạy lại generator vào database có giao dịch thật; đầu ra là fixture mô phỏng
có phiên bản. Mọi chỉnh sửa giả định cần tạo phiên bản scenario mới và kiểm tra lại.
