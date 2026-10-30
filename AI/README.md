# Shop AI · chatbot local cho cửa hàng điện tử

Mở http://127.0.0.1:8501. Chạy lại: `D:\Chatbot\chatbotshop\AI\start-local.ps1`.

**Cập nhật 25/10/2026:** RAG nâng cấp — số liệu admin theo kỳ trả bằng SQL khớp database, cách ly bằng chứng theo sản phẩm/tài liệu, reranker tiếng Việt đã fine-tune (`RAG_EVIDENCE_RERANK=1`), thêm 5 tài liệu kỹ thuật nguồn chính thức và handbook admin đã đối chiếu SQL; bộ 479 450→462, câu hỏi theo kỳ 3/14→14/14. Worker embedding hết rò bộ nhớ. Chi tiết: [RAG_UPGRADE_20261025.md](evaluation/RAG_UPGRADE_20261025.md).

**Phạm vi đang chạy: RAG cơ bản** (`CHATBOT_MODE=basic_rag`): đọc tài liệu có nguồn, hỏi lại/từ chối khi thiếu; không tính KPI, vẽ biểu đồ hoặc khẳng định giá/tồn kho tức thời. Admin Streamlit có quản lý tài liệu độc lập với sổ giao dịch. [Tiêu chí và giới hạn](BASIC_RAG_REQUIREMENTS.md), [kết quả kiểm tra](evaluation/basic_rag_v1/REPORT.md). Các chức năng SQL/sales mô tả ở phần cũ bên dưới thuộc `CHATBOT_MODE=tools`, được giữ để đối chiếu.

**Kiểm thử theo log:** activepatch9,193testqua;chấm đủ479development:450PASS/29FAIL,khách231/248/admin219/231,hồi quy100giữ87PASS. Bộ có nhiều câu số liệu lặp,kinhdoanhchỉ6/17,khônglàđộđúngkháchthật. Patch10thửđạt452/479nhưnglàmhỏng2câunốinênđãloạivàphụchồi. Đang chẩn đoán phụthuộc lời đáp trước,chưanghiệmthu.24reservedchưahỏi,121validationcũđãmởvà112/121thuộcpatch5,khônggộpđiểmkhácmãthành600. [Baselinepatch9](evaluation/quality_loop_20261021/candidate_v9_development/REPORT.md), [quyết định loại patch10](evaluation/quality_loop_20261021/candidate_v10_development/REPORT.md), [chẩn đoán hội thoại](evaluation/history_binding_20261022_r1/REPORT.md).

**Chẩn đoán hội thoại 22/10:** đã kiểm tra thêm bốn điều kiện hỏi nối/hỏi rõ tên sản phẩm với hai lịch sử đã ghi. Bản thử giải tham chiếu (patch11) và đổi thứ tự bằng chứng (patch12) đều bị loại do làm hỏng câu từng trả lời đúng; đã phục hồi patch9. Các lỗi còn lại nằm ở chọn đúng bằng chứng theo SKU, dù thông số đã có. Không lấy câu trả lời sai của bot làm dữ liệu học. [Trạng thái hiện tại](evaluation/quality_loop_20261021/CURRENT.md), [báo cáo patch12](evaluation/history_attribute_20261022_r4_candidate_p12/REPORT.md).

**Kiểm tra rộng 22/10:** bản thử đọc thông số trước rồi tham khảo sau (patch14) cải thiện bộ hội thoại nhỏ nhưng làm sai hai câu về thông số chưa biết và mã vùng trong bộ100; đã loại và phục hồi patch9. Bộ chấm bằng model cũng bỏ sót một lỗi trong6ca, nên chưa được cài vào chatbot. [Kết quả hồi quy](evaluation/quality_loop_20261021/old100_patch14/REPORT.md), [thử bộ kiểm tra tính liên quan](evaluation/relevance_probe_20261022_r8/REPORT.md).

**Cập nhật RAG21/10/2026:** mặc định `RAG_PIPELINE=grounded`, hai bước hiểu yêu cầu rồi chọn bằng chứng cho từng ý; giữ phạm vi thời gian/chủ đề qua lượt hỏi, giới hạn tìm nguồn theo miền và cache vector theo nội dung/model revision. Đối chiếu bằng `RAG_PIPELINE=legacy`. Cùng bộ100 câu phát triển: **67→85 đạt** (khách42→45/50; admin25→40/50), trung vị quan sát7,88→5,38giây. Còn15 câu FAIL, gồm4 câu thoái lui; chưa phải tỷ lệ đúng ngoài thực tế hoặc nghiệm thu độc lập. [Báo cáo trước/sau, lỗi còn lại và đáp án](evaluation/grounded_rag_20261021/REPORT.md); [159 kiểm tra tự động](evaluation/grounded_rag_20261021/VALIDATION.md). Không huấn luyện trọng số hoặc thay dữ liệu tài chính trong lượt này.

**Mốc kiểm thử trước khi nạp gói công nghệ, bằng 50 câu người dùng gửi:** 11 đạt, 39 chưa đạt đầy đủ; 19 lỗi trả lời/định tuyến/làm rõ, 19 thiếu dữ liệu chính và 1 chưa hỗ trợ đối chiếu lịch sử. Có lỗi sai kỳ/phạm vi dù dẫn đúng văn bản. Xem [báo cáo từng câu và đáp án nguyên văn](evaluation/user_bank_20261020/REPORT.md). Không dùng điểm 37+13 của bộ phát triển trước để thay cho bộ nghiệm thu này.

**Đã nạp gói công nghệ 20/10/2026:** 34 tài liệu kỹ thuật mới và 67 hồ sơ sản phẩm được cập nhật theo đúng SKU; luồng, model, prompt và SQL không đổi. [Nguồn dữ liệu và trạng thái phát hành](data/unstructured/technology_20261020/README.md), [biên nhận](data/unstructured/technology_20261020/publication.json). Lượt chạy lại 50 câu sau khi gộp trùng thông số được lưu riêng tại `evaluation/user_bank_20261020/technology_run_v2/`; số kiểm tra tính đúng nguồn không được coi là điểm nghiệm thu chức năng.

Script khởi chạy Ollama, worker tiếng Việt và Streamlit; Kev chỉ bật khi thêm `-EnableKev`. Worker cập nhật tháng phụ thuộc cấu hình và loại database. Mật khẩu chủ shop nằm trong `AI/.env`, biến `ADMIN_PASSWORD`. Đổi mật khẩu rồi khởi động lại web. Dịch vụ chỉ lắng nghe loopback.

## Hai miền dữ liệu

- `data/structured/`: số liệu có cấu trúc; database shop, giao dịch, giá/tồn kho, nguồn UCI, lô theo tháng, snapshot và seed định tuyến.
- `data/unstructured/`: tài liệu chính sách/chiến lược, phiên bản theo tháng, báo cáo dẫn xuất và tài liệu tham khảo bên ngoài.

Chi tiết cách chuẩn bị và cập nhật: [DATA_MONTHLY.md](DATA_MONTHLY.md). Các thư mục `data/raw` và `data/documents` cũ hiện trống; nội dung đã chuyển sang hai miền trên.

**Nguồn tải về**: UCI Online Retail II (45.622.418 byte, CC BY 4.0, DOI 10.24432/C5CG6D); ba bài hướng dẫn SBA về kế hoạch kinh doanh, marketing/bán hàng và nghiên cứu thị trường. Giữ URL, thời gian tải, hash và file gốc. UCI là benchmark bán lẻ hàng quà tặng ở Anh; tài liệu SBA là tham khảo phương pháp. Chúng không phải số liệu, giá hay chính sách của shop.

Database đang chọn là **mô phỏng 67 SKU**, tại `data/business_sql/scenario_v1/shop.sqlite`, giai đoạn 2025-10-01 đến 2026-09-30. Nhập, bán, hoàn trả và tồn cùng SKU, kiểm tra FIFO. Database demo cũ vẫn được giữ riêng; chưa có dữ liệu thật của shop. Bộ FIFO này không cho worker tháng chèn theo định dạng demo cũ.

## Cập nhật dữ liệu và tri thức theo tháng

Worker kiểm tra mỗi 60 giây khi hệ thống chạy. Mặc định nạp số liệu tháng đã chốt; tài liệu đã duyệt được kích hoạt theo ngày hiệu lực. Có thể nạp tháng hiện tại bằng tùy chọn rõ ràng, báo cáo ghi dữ liệu chưa đầy đủ.

- Kiểm tra SKU, ID dòng bán, ngày, số âm và kiểu dữ liệu. Không trộn dữ liệu demo với dữ liệu thật.
- ID đã có + nội dung giống nhau: bỏ qua. ID đã có + nội dung khác: từ chối cả lô.
- Dữ liệu lịch sử không ghi đè snapshot tồn kho mới hơn. Nếu ngày snapshot ban đầu không rõ, không tự thay giá/tồn từ lô lịch sử.
- Tạo snapshot SQLite, báo cáo số liệu tháng và chỉ mục tài liệu có nguồn. Công cụ đọc SQL lấy số liệu mới ngay; RAG đọc chỉ mục mới ngay.
- Tài liệu có mã ổn định, version, quyền đọc, trạng thái duyệt và ngày hiệu lực. Bản nháp/tương lai/hết hạn không dùng; không phục hồi bản cũ khi bản mới hết hạn.
- Có khóa chống chạy đồng thời và log các lô bị từ chối. Khi máy tắt, worker ngừng; khi khởi chạy lại sẽ kiểm tra các tháng còn thiếu.

Đây là cập nhật dữ liệu/tri thức, **không huấn luyện lại trọng số Kev/Qwen**, theo lựa chọn của chủ shop. Không tự tạo số bán hàng hay chính sách thật khi chưa có đầu vào.

## Tính năng hỏi đáp

Tư vấn người mua đã bổ sung hồ sơ nhu cầu qua nhiều lượt: ngân sách, hãng, RAM, cân nặng, màn hình và mục đích dùng. Model chọn SKU từ danh sách đã kiểm tra; giá/tồn/thông số do SQLite cung cấp. Hỗ trợ sửa/bỏ điều kiện, so sánh mẫu vừa xem, chọn theo giá và báo khi chưa có hàng đáp ứng. Mặc định bật với Ollama (`SALES_ADVISOR=0` để đối chiếu bản cũ). Kết quả và giới hạn: [báo cáo tư vấn](evaluation/sales_v1/REPORT.md). Chưa nối luồng này sang endpoint chat demo của Express/React.

Streamlit gồm luồng người mua và chủ shop có mật khẩu; lịch sử tách theo vai trò, có đăng xuất. LangGraph điều phối planner Qwen → công cụ chỉ đọc → câu trả lời có nguồn. Hỗ trợ lọc laptop theo ngân sách/màn hình/pin, kiểm tra tồn, so sánh, chính sách có trích nguồn; admin xem doanh thu/lợi nhuận theo tháng/quý/năm, so sánh hai kỳ, biểu đồ và báo cáo tháng. Không chạy SQL/Python do model sinh. Chưa kết nối chuyển nhân viên thực tế hoặc đặt hàng.

Truy xuất kết hợp embedding tiếng Việt PhoBERT, TF-IDF và BM25 bằng RRF, lọc quyền/hiệu lực/phiên bản trước khi tìm. Qwen3 hiểu yêu cầu và ngữ cảnh; encoder phân loại đã train trên Colab được giữ để đối chiếu, mặc định không gọi (`VI_CLASSIFIER_SHADOW=1` mới chạy kiểm tra), không đưa dự đoán hẹp của nó vào quyết định planner; công cụ kiểm tra quyền, tính lịch và truy vấn SQL. Số liệu và trích đoạn giữ từ nguồn; chưa có reranker được chứng minh tốt hơn hoặc tư vấn kinh doanh tự do đã được đánh giá.

## Model local

- Ollama portable v0.40.5: cổng 11435, cloud tắt; Qwen3-4B-Instruct-2507 Q4_K_M trên RTX 2060 qua Vulkan. Model trong `models/ollama`; Qwen2.5:1.5b được giữ để đối chiếu.
- `dangvantuan/vietnamese-embedding`: worker CPU cổng 8011, PyVi tách từ, 768 chiều, giới hạn thực tế 256 token. Dùng môi trường `.venv-kev` với `requirements-vietnamese.txt`.
- Adapter hiểu hội thoại v3: train 4 lớp cuối PhoBERT + 4 đầu phân loại trên T4; hiện giữ để đối chiếu, mặc định không gọi; không đưa kết quả phân loại vào prompt planner vì chưa bao phủ đủ tác vụ tài chính và bộ lọc; không tự thay quyền công cụ. Chia sẻ 8 lớp đóng băng với encoder tìm tài liệu, giữ riêng 4 lớp đã train để không thay embedding gốc.
- Kev-0.8B: giữ thí nghiệm cũ, chỉ khởi động khi thêm `-EnableKev`; không nạp cùng lúc theo mặc định trên máy 8 GB RAM.
- GGUF Qwen3.5-4B ở `D:/tool/models/Qwen3.5-4B-GGUF` đã thử nhưng trả từ lặp trên CPU/Vulkan, nên chưa dùng mặc định. File gốc được giữ nguyên.
- Kev repo SHA `1f04cfa28e6a708485b28a9585010b9e436b776e`, Apache-2.0; LangGraph tham khảo SHA `e77a5cb08c1f3ff306d997dd76fc7169afdab5ea`. Repo trong `references/`. Không dùng `pip install kev` vì trùng tên package khác.
- Kev checkpoint revision `bf75a6a8848ea6960ff2ed108d9ed44c2941174f`; base revision `dc7cdfe2ee4154fa7e30f5b51ca41bfa40174e68`. Base đã kiểm tra SHA256 `c2b1e5a17d9c1e27685d92ed9b382911ebb99955ecd89052d1721241adfbab6c`.

Luồng v3 mặc định dùng model hiểu hội thoại, giữ kỳ/ý định/tiêu chí và 6 lượt gần nhất, tách theo vai trò. Nút cuộc trò chuyện mới xóa trạng thái. `CONVERSATION_MODE=legacy` chỉ dành đối chiếu bản luật cũ. Bộ nhớ chưa xuyên thiết bị hoặc phiên đăng nhập.

Kết quả và giới hạn v3: `training/conversation_v3/README.md`. Train Colab: 2.676 mẫu tổng hợp, 4 epochs, 440 bước, 135,9 giây; validation 93,53%, test tổng hợp 464/464. Pilot kết hợp local 15/15 lượt; đây không phải độ chính xác trên hội thoại khách thật. Số kinh doanh tính từ SQL, không ghi nhớ doanh thu vào trọng số.

## Kiểm tra

```powershell
cd D:\Chatbot\chatbotshop\AI
.\.venv\Scripts\python.exe scripts\health.py
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp runtime\tests-new-run
```

Bộ kiểm thử hiện gồm 111 ca, có phân quyền, Streamlit, SQL, nhập dữ liệu, cập nhật tháng, ngày hiệu lực, biểu đồ, bộ nhớ nhiều lượt, kiểm chứng trích đoạn và lịch. Kiểm tra model thật v3 trong `training/conversation_v3/results`; test có mock không thay thế pilot gọi model thật.

Yêu cầu gốc: `../documnets/ke-hoach-ba-chatbot-shop-dien-tu.md`, đặc biệt mục 8–10. Áp dụng ý tưởng bộ nhớ/truy xuất và công cụ từ chương 3–4 của `D:/Chatbot/Ai-agent-book`.

Chưa hoàn thành toàn bộ kế hoạch BA: còn reranker/đánh giá hội thoại độc lập, finetune model sinh, dự báo thực tế/RFM/phân tích nguyên nhân, đề xuất có duyệt và đo kết quả, Build PC, storefront/tích hợp backend. Docker và triển khai công khai ở bước sau.

## Sửa lỗi hội thoại 19/10/2026

Sửa Q4/2025 bị hiểu thành tháng 4; thêm lọc ngành hàng trong SQL, thông số CPU/GPU từ nguồn và phân biệt tiền nhập/hoàn/đếm đơn/doanh thu từng kênh. Lượt nối câu dùng các trường thay đổi để giữ kỳ, tiêu chí, số mã và nhóm; giữ yêu cầu đang chờ làm rõ. Tìm tài liệu dùng ngày của phiên hỏi. OLED không có phải nêu rõ lựa chọn thay thế. Đây là sửa planner/công cụ, không phải một lượt finetune trọng số mới.

Bộ đánh giá cũ giữ nguyên tại `training/conversation_v3/audit_extended_20261019_v1`; các lượt sửa lưu thư mục riêng. Câu không thực hiện được vẫn FAIL, kể cả thiếu chính sách thật, dự báo có khoảng tin cậy, thuế, Excel/RFM hoặc Build PC. Không dùng điểm trên dữ liệu tổng hợp làm độ chính xác production.

Báo cáo sửa và đối chiếu: [IMPROVEMENT_REPORT.md](training/conversation_v3/IMPROVEMENT_REPORT.md).

## Rà và cải thiện RAG cơ bản — 20/10/2026

Xem [báo cáo và bằng chứng](evaluation/rag_v1/REPORT.md). Bộ chuyên biệt gồm 32 ca phát triển và 16 ca giữ riêng, không gộp điểm SQL vào điểm RAG. Bản chọn đạt 32/32 dev, 14/16 giữ riêng; truy xuất đoạn chuẩn dev 87,9% → 97,0%. Đây là benchmark nhỏ từ shop mô phỏng, không phải độ chính xác production.

`RAG_SYNTHESIS=1`, `RAG_ANSWER_MODE=extractive`: model chọn câu/dòng bảng trực tiếp từ nhiều nguồn; renderer giữ nguyên bằng chứng và dẫn mục/phiên bản, trả rõ phần thiếu. Câu nối được viết lại bằng chủ đề tài liệu và kỳ đã xác nhận. Bản diễn giải tự do (`generative`) còn yếu nên không chọn; reranker thử nghiệm làm rơi nguồn đúng nên `RAG_RERANK=0`.

Admin có bảng đối chiếu kế hoạch/thực hiện, nhóm hàng và ưu tiên kiểm tra SKU/tồn kho. Chưa có mục tiêu nhóm thì không quy hụt kế hoạch cho nhóm; không suy ra nhân quả quảng cáo. `procurement` v2 làm rõ tên nhà cung cấp từ bảng SQL, giữ bản v1 và provenance, không thay số liệu kinh doanh. Hai ca giữ riêng vẫn FAIL về diễn đạt thời gian và bỏ sót vế hỏi ngân sách.
