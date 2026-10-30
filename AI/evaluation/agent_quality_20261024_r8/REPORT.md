# Guard scope regression — r8

Một bước sửa phòng hồi quy: phân biệt nhắc hành động để hỏi định nghĩa/hướng dẫn/trạng thái đã làm với yêu cầu thực hiện. Không đổi prompt/model/config/nguồn. Câu giải thích không che lệnh thực hiện độc lập ở phía sau. Guard lexical còn giới hạn, không coi là hiểu ngôn ngữ toàn diện.

20probe mới trước9/20 sau20/20;20probe r1 vẫn20/20. Đây là unit/preflight, chưa model-evaluate20câu mới. Không dùng để tăng semantic score106.131targeted tests đạt13,36s; không chạy lại full409DEtests đã đạt ở r7. Logtests-capability-scope-r2b.log.

Một batch duy nhất106/106, cùng bank/gold r7; ngày server được đóng băng23/10/2026 như r7 để so cùng điều kiện. Integrity unchanged=true. Helpers đã chuẩn bị trước batch; không code/data/model/config đổi lúcmodelchạy. Sources/raw/curated/bankgold/candidatecũ giữ nguyên.

Checks24/24+60/60+19/22contract. So ngữ nghĩa riêng103/106, không đổi so r7;4/6fullsessions.106answer sau normalize artifact revision vàtoolargs nguyên r7.106trace role/question/parentlinks verified, training_allowed=false. Còn Q29/Q30 viết dính vàQ41 mixedcatalog+documents. Không có cải thiện end-to-end mới trong106; không mởvalidation hoặc tựhọc câu sai.

Median0,6955s/max46,063s; cold/warm khác nhau, chưa suy cải thiện tốc độ/SLA. accepted_for_application=false, defaultbasic_rag không đổi. Chưa cleanExcel/ranking/mixed/docretrieval thật; không frontend/deploy/Colab/train/modeldownload/paidAPI/worker8011-r19. Bộ300buyer chưa chạy.

Bước tiếp: đóng băng contract mixed với câu spacing chuẩn, thực thi/ghi kết quả riêng từng phần, báo partial khi docsdisabled thay bỏ sót. Không làm typo khi chưa ổn. Cần đo lỗi mới ngoài106, bổ sung review nguồn cho300, nối tài liệu đúng role/provenance trong các ràngbuộc hiện tại; không retry startup bị chặn. Excel/DE/DA/DS/Kev/devCompose theo reliabilityPLAN.
