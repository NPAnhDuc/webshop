# Patch10 bị loại: bớt lạc nguồn nhưng làm hỏng hai câu nối

Đã hoàn tất479lượt, integrity unchanged=true. So cùng479và cùng rubric với baselinepatch9đã chấm đầy đủ: **450→452PASS nghĩa**,29→27FAIL. SửaQ0154/Q0193/Q0228(claim phụ sai sản phẩm) vàQ0191(số nhânCPUtrong câu nối). Nhưng **Q0300/Q0478từPASS→FAIL**: hỏi model dù đã biếtDeepcoolCH160; hỏi bố tríRAMkitG.Skilllại trảDDR5/Photoshop thay2thanh×32GB.

75answer/action/source objects thay đổi được đọc mới đủ ba panel25câu, có câu trước trong hội thoại và nguồn đúngSKU/kỳ.404case còn lại kế thừa exact reviewpatch9cóprovenance. Khách233/248,admin219/231. Secondaryissuecases giảm53→30; đáp án nhiều câu gọn hơn, nhưng vẫn còn thông tin phụ. Checks riêng lại giảm422→421PASS,4→5FAIL,53REVIEW giữ nguyên: không dùng tổng checks thay điểm nghĩa.

**Quyết định: không áp dụng patch10 riêng lẻ, phục hồi đúng mã và testpatch9.** Các câu nối về sản phẩm đã xác định là chức năng cần giữ; tổng tăng2và giảmnoise không đủ để chốt khi hai câu đang trả được bị hỏng. Snapshot trial tại `source_snapshot/`,baseline trước sửa tại `../patch10_before_code/`. Giữ tất cảraw/bank/gold/review cũ.201test thuộc bản thử; sau phục hồi chạy lại suite193tại `AI/runtime/tests-quality-p10-rollback.log`.

Nguyên nhân phần dẫn nguồn tạoP1ảo được xác nhận: ba claim phụ sai phạm vi đều hết sau sửa. Tuy nhiên câu trả lời ở lượt đầu ngắn hơn làm thay đổi hành vi lượt sau. Cùng `rag_product_subject` đúng và cùng câu hỏi nhưng router/selector phụ thuộc câu trả lời cũ do bot sinh:

- Q0300: trước đó lịch sử chứa cả vật liệu hông; khi chỉ còn loạiMiniITXDesktop, router hỏi lại dù `confirmed_subject` vẫnDeepcoolCH160.
- Q0478: candidate list vẫn có `ram_modules_1` đúngG.Skill, nhưng selector chọnram_typevàhướng dẫnPhotoshop. Lịch sử lượt đầu chỉ cònDDR5/6400, thay vìCAS32kèmDDR5nhưbaseline.

Đây không phải thiếu dữ liệu hoặc mất tên model. Không nạp đáp án sai vào tri thức. Việc bỏ toàn bộ câu trả lời khỏi history đã thử ởpatch4và làm hỏng các ca tương tự; không lặp nguyên phương án đó hoặc chỉ viết thêm prompt dài.

818trích đoạn đúng nguồn/phiên bản đã chốt,0quoteissues/0privateleaks. Trung vị4.360giây,tổng2180.794giâyso4.422/2264.654củapatch9. Prompt ngắn hơn và bớt trích đoạn phù hợp giả thuyết giảm tải, nhưng cache/warmupkhôngkiểmsoát; không quy chênh lệch cho riêng parser hoặc tuyên bố cải thiện tốc độ sản phẩm.

Active sau phục hồi làpatch9: **450/479development và87/100hồi quy**,24targeted18/24;452/479thuộc bản bị loại. Các bộ đều có giới hạn, không phải độ đúng ngoài thực tế; businessreasoningpatch9chỉ6/17.24reserved chưa hỏi,121validation cũ đã mở và thuộcpatch5. Không cần chạy thêm100trên bản đã loại.

Bước tiếp theo nên tập trung ràng buộc đối tượng trong câu nối, trước khi thử lại việc rút gọn đáp án. Một hướng cần kiểm là dựng câu hỏi độc lập từ đối tượng đã xác minh, giữ câu gốc và lịch sử cho hội thoại, không dùng lời đáp cũ làm bằng chứng. Phải xử lý model mới/đổi chủ đề, so hai máy, tên chưa rõ, không tự ghi đèclarifyhaynạp đáp án. Chọn một bước có baseline và phản chứng, dùng bộdevelopmentđã mở; không dùngreserved để vá. Không áp lại parserpatch10riêng lẻ khi chưa giải quyết hồi quy.
