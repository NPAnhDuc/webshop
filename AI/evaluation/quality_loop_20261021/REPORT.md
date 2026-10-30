# Kiểm thử và cải thiện theo log — 21/10/2026

**Ngân hàng mới: 600 lượt hỏi, 300 khách hàng và 300 admin; 545 lời văn khác nhau trong 454 nhóm.** Câu nối giống nhau ở sản phẩm khác được tính đúng là các lượt theo ngữ cảnh, không giả là 600 câu độc lập.

Đã chốt 479 lượt phát triển và 121 lượt xác minh theo nhóm hội thoại. Cùng nhóm không chia sang hai tập. Hai tập vẫn đọc cùng kho tri thức; không phải bộ đánh giá của người độc lập. Bộ 100 cũ giữ riêng để kiểm tra hồi quy.

**Đã hỏi 80 lượt baseline mới và 479/479 lượt candidate.** Đối chiếu được 80 lượt cùng ID; đây là tiến độ, không phải đã xong 600.

| Trên cùng các ID đã chạy | Trước sửa | Sau sửa |
|---|---:|---:|
| PASS_CHECKS | 57 | 66 |
| FAIL_CHECKS | 10 | 1 |
| NEEDS_REVIEW | 13 | 13 |

PASS_CHECKS chỉ xác nhận đoạn/số thuộc đúng nguồn-phiên bản hoặc action dự kiến trong kiểm tra hẹp. Chưa chứng minh đủ ý, đúng nghĩa, ngắn gọn hay không mâu thuẫn. FAIL_CHECKS cũng cần xem nguồn tương đương trước khi chốt. Không tự báo 600 câu đã đạt vì có dẫn nguồn.

Các ca chuyển FAIL_CHECKS→PASS_CHECKS đã quan sát: Q0018, Q0031, Q0036, Q0054, Q0072, Q0077, Q0082, Q0096, Q0101. Chuyển ngược: chưa có. Chỉ tính cùng câu; không đổi tiêu chí/gold sau khi thấy câu trả lời.

Đã đọc/chấm riêng 23 câu baseline bị gắn cờ hoặc cần chấm nghĩa; chưa chấm độc lập toàn 80 hoặc 600. [Nhận xét thủ công](baseline_80/human_review.json).

Chấm lại riêng91 ca đã đọc: còn35 FAIL ngữ nghĩa/định tuyến trong nhóm này; không ngoại suy thành điểm toàn bộ. [Nhận xét sau sửa](candidate_v1/human_review.json).

## Sửa theo lỗi thực sự trong log

- Mã máy không khớp nguồn: thêm ràng buộc nhận diện mã sản phẩm, không lấy cấu hình laptop gần giống để lấp model chưa có. Còn cần kiểm thử cách gọi không có mã số và câu nhiều sản phẩm.

- Từ chối nội bộ bị báo model lỗi: kiểm tra enum của kết quả model trước khi server đặt quyết định denied. Không mở rộng quyền theo lời tự xưng.

- Viết tháng liền chữ số và thángISO: bổ sung phân giải phạm vi, tránh câu tháng9 bị trả báo cáo10/2025. Bảo toàn cụm lãi vay và thuế, bỏ ràng buộc không tính chênh lệch khỏi danh sách câu hỏi con.

- Hai kỳ có cùng con số: bỏ gộp trùng chỉ theo văn bản; giữ riêng nguồn và phiên bản, tránh mất một tháng khi cả hai cùng có2 sản phẩm hoàn trả.

- Câu độc lập có từ còn: không cho model viết lại mãSKU khi không có chủ đề trước. Kiểm tra hồi quy phát hiện trường hợp i5-14400F bị model viết ngắn sai; đã sửa và có lượt hỏi lại riêng.

- Log thêm model/revision mã, kỳ, thời gian, phần chưa trả, tài liệu ứng viên và chẩn đoán. Queue tách tương tác thật, benchmark và origin chưa rõ; câu full của tương tác cũng được đưa vào kiểm tra, không chỉ các câu từ chối.

Các sửa này là cải thiện mã và quan sát, không huấn luyện trọng số, không bổ sung chính sách/số thật giả để hợp đáp án. SQL và manifest tri thức vẫn giữ nguyên. Các khoảng trống thực cần xác nhận được ghi tại[KNOWLEDGE_GAPS.md](KNOWLEDGE_GAPS.md).

## Kiểm chứng và chạy tiếp

- Sau patch2:173 kiểm tra lõi và4 kiểm tra giao diện qua. LogAI/runtime/tests-quality-patch2-b.log vàtests-quality-patch2-ui.log. Đây là kiểm thử phần mềm, không phải điểm ngữ nghĩa chatbot.

- Đã chạy20 câu hồi quy cũ trước chỉnh cuối phần viết lại truy vấn; phát hiện và sửa một ca chặn nhầmC31. Lượt hỏi lạiC31 trả đúng10nhân/boost4,7GHz, vẫn cần làm rõ phần luồng tốt hơn. C44 model giả đã báo thiếu đúng. C03,C06,A15,A39 vẫn còn lỗi; không đổi chúng thành PASS vì unit test qua.

- candidate_v1 đã chạy 479/479 lượt phát triển; kiểm tra tự động: {'PASS_CHECKS': 413, 'NEEDS_REVIEW': 53, 'FAIL_CHECKS': 13}. Chỉ sửa giữa các round. Sau chốt phát triển mới hỏi121 lượt xác minh, rồi thêm ca mới từ log thực.

- Đã bật tác vụ trên cuộc trò chuyện mỗi giờ để đọc kết quả, tiếp tục sửa có căn cứ và chạy vòng tiếp. Nếu batch đang chạy thì không chạy chồng hoặc đổi mã giữa lượt. Chỉ thông báo thay đổi có ý nghĩa/lỗi chặn; không nhắc lại tiến độ không đổi.

- Máy và ứng dụng desktop cần mở cho công việc local; mất điện hoặc đóng máy thì không có cam kết vẫn chạy. [Hướng dẫn chính thức OpenAI](https://developers.openai.com/training/walkthroughs/scheduled-tasks).

## Tệp

- [Ngân hàng đã chốt](bank.json),[cấu trúc/hash và số lượng theo chủ đề](metadata.json),[nguồn chuẩn](gold_sources.json).

- [Baseline80](baseline_80/CHECKS.md),[candidate đang chạy](candidate_v1/CHECKS.md),[kết quả thô](candidate_v1/results.json).

- [Kế hoạch vòng lặp](LOOP_PLAN.md),[trạng thái tiếp tục](CURRENT.md),[queue log](log_review_queue.json).

Bộ có nhiều câu số liệu theo tháng, không đại diện đều mọi tình huống bán hàng. Khi báo nghiệm thu phải tách theo chủ đề/nhóm và chấm nghĩa, không dùng số lượng lớn để che yếu ở tư vấn/đối chiếu.

## Patch2: ngữ cảnh sản phẩm và thuộc tính

Giữ mã sản phẩm được khách nhắc đến riêng với tiêu đề bài tham khảo; giữ nguyên thuộc tính trong câu hỏi thay vì dùng câu viết lại làm mất ý. Phân biệt VRAM/RAM, bố trí bộ RAM/tốc độ và độ trễ đầu tiên/CAS bằng nhãn trường nguồn. Không thêm đáp án hoặc ID benchmark vào mã. SQL, tri thức và trọng số không thay đổi.

Đã chạy 89/89 lượt development có đủ lịch sử hội thoại, gồm các lỗi đã quan sát và đối chứng. Trên cùng 89 ID: trước {'PASS_CHECKS': 69, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 13}, sau {'PASS_CHECKS': 77, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 5}. Sửa được kiểm tra nguồn/action: ['Q0125', 'Q0164', 'Q0210', 'Q0247', 'Q0300', 'Q0373', 'Q0411', 'Q0446', 'Q0467']; suy giảm kiểm tra: ['Q0396']. Không coi đây là điểm toàn 479 hoặc điểm ngữ nghĩa.

Xem [báo cáo patch2](PATCH2_REPORT.md). Chưa chạy lại toàn 479 bằng patch2, chưa chạy lại đầy đủ 100 hồi quy cũ và chưa mở 121 validation.

## Patch3 thử nghiệm — không áp dụng

Đã kiểm lại 89/89 lượt cùng câu: {'PASS_CHECKS': 77, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 5}. Sửa Q0396 nhưng làm hỏng Q0473; không có cải thiện ròng. Đã phục hồi mã đúng hash patch2, giữ nguyên kết quả thử và nguồn. 179 test qua thuộc bản thử bị loại; mã đang dùng có 177 test qua ở patch2. [Chi tiết và quyết định](PATCH3_REPORT.md). Validation chưa mở.

## Patch4: lịch sử để nhớ đối tượng, nguồn để xác nhận dữ kiện

Đã chạy 89/89 lượt cùng ID với patch2: trước {'PASS_CHECKS': 77, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 5}, sau {'PASS_CHECKS': 74, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 8}. FAIL_CHECKS→PASS_CHECKS: ['Q0301']; chiều ngược: ['Q0300', 'Q0373', 'Q0446', 'Q0478']. Đây chỉ là kiểm tra nguồn/action. Quyết định và chấm nghĩa phải xem [PATCH4_REPORT.md](PATCH4_REPORT.md).

Với sản phẩm đã xác định, router/selector nhận câu hỏi trước và chủ đề đã xác nhận, không nhận câu trả lời cũ do bot sinh làm bằng chứng. History người dùng trong profile vẫn nguyên vẹn. Không đổi nguồn/gold/model, không mở validation. 179 test phần mềm qua (AI/runtime/tests-quality-patch4.log).

**Đã loại patch4 và phục hồi mã đúng hash patch2:** sửa Q0301 nhưng làm hỏng Q0300/Q0373/Q0446/Q0478. Không dùng bản thử làm mã hiện tại. 179 test thuộc bản bị loại; mã hiện tại có 177 test đã qua ở patch2.

## Patch5 — toàn 479 development đã hoàn tất

Toàn479 cùng ID: trước {'PASS_CHECKS': 413, 'NEEDS_REVIEW': 53, 'FAIL_CHECKS': 13}, sau {'PASS_CHECKS': 422, 'NEEDS_REVIEW': 53, 'FAIL_CHECKS': 4}.11 lỗi kiểm tra được sửa,2 suy giảm Q0191/Q0396 so v1 (tác động kết hợp patch2+5). Riêng89 đã có patch2: {'PASS_CHECKS': 77, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 5} → {'PASS_CHECKS': 79, 'NEEDS_REVIEW': 7, 'FAIL_CHECKS': 3}; Q0267/Q0352 sửa được, không có chuyển PASS_CHECKS→FAIL_CHECKS trong89. Còn4 lỗi Q0055/Q0191/Q0301/Q0396. Không gọi các số này là độ đúng ngữ nghĩa.181 test mã qua; chưa nghiệm thu, chưa mở121 validation. [Chi tiết](PATCH5_REPORT.md).

## Hồi quy100 trên patch5 đã chấm

Theo cùng rubric v7: 87/100 PASS, khách47/50 và admin40/50; v7 là85/100. Sửa C06/C44, không có hồi quy từ PASS.87 câu trả lời/trích dẫn giống hệt nên kế thừa review,13 thay đổi được đọc lại. Không là điểm validation hoặc độ chính xác thực tế. [Chi tiết](old100_patch5_retry1/REPORT.md).

## Patch6 đã loại

Bản thử mở rộng ứng viên giảm87→76/100,11hồi quy. Đã phục hồi đúng hash patch5;182 test thuộc bản bị loại,181 test của mã đang dùng. [Chi tiết](PATCH6_REPORT.md).

## Hoàn tất479 development và121 validation trên mã đóng băng

Validation được đọc/chấm đủ121:112PASS/9FAIL, khách49/52,admin63/69; nhóm lập luận kinh doanh chỉ2/7. Tổng600 có524PASS_CHECKS/8FAIL_CHECKS/68NEEDS_REVIEW, không phải điểm đúng ngữ nghĩa. Development mới chấm112ca chọn, không ngoại suy toàn479/600. Chưa nghiệm thu; validation đã mở, sửa tiếp cần nhóm holdout mới. [Báo cáo đầy đủ và giới hạn](BASELINE_600_REPORT.md).

## Baseline ngữ cảnh revision3 — bot chưa đổi

24development tập trung có12PASS/12FAIL nghĩa.4cờ lỗi giả của r2 do gold span quá dài được sửa bằng revision mới từ nguồn gốc; r2 giữ nguyên. R3 regrade cùng24outputs, không inference mới hay cải thiện chatbot.24reserved chưa được hỏi. [Chi tiết/provenance](../context_revision_20261021_r3/REPORT.md).

## Patch7 — candidate ngữ cảnh, chưa chốt hồi quy

Phân giải tháng/quý trước guard mơ hồ, vẫn hỏi khi chưa biết máy/bộ/tài liệu. Cùng24development:12→17PASS nghĩa,7FAIL còn lại,không cóPASS→FAIL trong24. Checks16PASS/3FAIL/5REVIEW. Chưa hồi quy100 trênpatch7; điểm87/100 cũ thuộcpatch5.24reserved chưa mở. [Chi tiết](../context_revision_20261021_r3/context_r3_candidate1/REPORT.md).

## Patch7 — hồi quy100 đã hoàn tất

Giữ87PASS/13FAIL,khách47/50,admin40/50,0PASS→FAIL so patch5.99answer/action/sources giống hệt; A17chỉ đổi thứ tự nguồn đã đọc lại;13FAILđãđọc lại.213quotes/0integrityissues. Giữcandidateđểdevelopment,chưa nghiệm thu,chưa rerun479/chưa mở24reserved. Không tuyên bố cải thiện tốc độ do cache. [Báo cáo](old100_patch7/REPORT.md).

## Patch8 — candidate định tuyến, cần hồi quy100

Cùng24 development:17→18PASS nghĩa,6FAIL; sửa yêu cầu thực hiện cập nhật giá thành deferred,0PASS→FAIL trong24. Checks17/2/5 riêng. Đã khóa cùng đồng hồ xóa/as_of trong test sau khi máy sang22/10;187test qua. Chưa hồi quy100 trênpatch8,87/100 thuộcpatch7.24reserved chưa mở. [Chi tiết](../context_revision_20261021_r3/context_r3_candidate2/REPORT.md).

## Patch8 đã loại sau hồi quy100

Bản thử87→88PASS nhưng làm hỏngA36(C-TET có dữ liệu lại báo thiếu),A35mất chủđềchiếndịch. Đãphục hồi đúng hashpatch7,187testqua,giữ fixture cùngclock. Active17/24developmentvà87/100;18/24và88/100thuộcbản bịloại.24reserved chưa mở. [Quyết định và bằng chứng](old100_patch8/REPORT.md).

## Patch9 — candidate ràng buộc sản phẩm, cần hồi quy100

Cùng24 development:17→18PASS nghĩa,6FAIL; sửaD10 từ trả thuật ngữ sang hỏi model khi chưa có đối tượng,0PASS→FAIL trong24. Khách8/8,admin10/16;checks17/2/5 riêng.193test qua, không đổi nguồn/model/gold.87/100 đã đo thuộcpatch7, chưa đo patch9.24reserved chưa mở; patch8 vẫn bị loại. [Chi tiết](../context_revision_20261021_r3/context_r3_candidate3/REPORT.md).

## Patch9: hồi quy100 hoàn tất, cần đánh giá rộng

87PASS/13FAIL giữ nguyên so patch7;98answer/action/sources giống hệt,2thayđổiA16/A17đọc lại vẫn đúng.210quotes/0integrityissues.193test đã qua,24targeted18PASS/6FAIL,không là điểm toàn hệ thống. Giữ mã để đánh giá lại479development;24reserved chưa mở. [Chi tiết](old100_patch9/REPORT.md), [kế hoạch coverage](candidate_v9_development/REVIEW_PLAN.md).

## Patch9: đủ479, chấm nghĩa còn dang dở

Checks422/4/53 giữ nguyên so patch5,15case đổi sourceobjects đã đọc đúng;914quotes/0quoteissues/0privateleaks. Coverage479/479: 112kế thừa,367đọc mới; tập đã chấm{'FAIL': 29, 'PASS': 450},còn0chưa đọc. Không có điểm nghĩa toàn479/600,không coi coverage tăng là bot tiến bộ. Chưa mở24reserved/chưa nghiệmthu. [Chi tiết](candidate_v9_development/REPORT.md).

## Patch9 đã chấm nghĩa đủ479

450PASS/29FAIL theo rubric nội dung chính,112kếthừa+367đọc mới. Khách231/248,admin219/231;330/358nhómđạt mọi lượt.53câu có secondaryissue. Nhóm kinhdoanh6/17,côngnghệ19/28; nhiều câu số liệu lặp, không coi là độ đúng ngoài thực tế hoặc nghiệmthu. Không cộng với validationpatch5 thành điểm600cho patch9. [Phân bố vàgiới hạn](candidate_v9_development/semantic_summary.json).

## Patch10 đã loại: bốn sửa, hai câu nối hồi quy

450→452/479nghĩa,noise53→30,nhưngQ0300/Q0478mất trả lời đúng dù biếtmodel. Phục hồi đúngpatch9,giữtrial/gold/raw.201testthuộcbảnthử,activepatch9cósuite193. Không áp parser riêng lẻ trước xử lý phụ thuộc lời đáp cũ. [Chi tiết](candidate_v10_development/REPORT.md).

## Chẩn đoán history trên cùngpatch9

6kịch bản/2caseđãmở:historygốc2/2,historyngắn0/2,historyngắn+câunêumodelrõ2/2. Chưa triển khai resolver tự động,khônggọilàproductionimprovement; cần baseline rộng hơn và hồi quy. Inputs modelanswer chỉ là hội thoại test,không xuất bản knowledge/training. [Chi tiết](../history_binding_20261022_r1/REPORT.md).

## History diagnostics: patches11 and12 rejected

Last accepted patch9 remains450/479 development and87/100 legacy regression. Four-condition baseline217/224 comes from correlated r2+r3 scenarios, not224 independent questions. Patch11 fixed5 but regressed2; patch12 fixed3 but regressed9 and was restored. Explicit naming alone and attribute-only ranking do not ensure applicable evidence. General technical advice still substitutes for known SKU facts. Prior model answers remain untrusted input, never knowledge/training. No source/model/data changes or new validation. See CURRENT.md and individual diagnostic reports.

## Patch13 rejected; raw model-call diagnosis

Source-envelope trial206/224 versus217/224,1fix/12regressions, restoredpatch9. Diagnostic6known controls:4PASS/2FAIL, all6 outputs identical to baseline. All requested kit facts and legal IDs are present in selector requests, but two choose general advice with missing=[]. Prompt tokens1507–3262 under6144, all12 calls stop normally; no context/output exhaustion observed in these calls, no cache bug established. Activepatch9 scores unchanged; details in history_payload_20261022_r6/REPORT.md.

## Patch14 focused trial; broader regression pending

Staged product evidence reading:217→221PASS/224 same-input diagnostic scenarios,4fixes/0regressions, secondary cases28→8. This is68questiontexts/178question-profileinputs, not independent accuracy. No fallback was needed among149product-first reads, so caveat/missing-attribute risk remains.198tests passed. Old100 then full479 required on same code before acceptance. Last acceptedpatch9 scores remain450/479 and87/100.

## Patch14 rejected after old100; judge probe insufficient

Legacy10087→85, C31unknown thread-count answer and C34regional soldered-RAM scope regress. Focused224 gain did not survive; restoredpatch9 with193tests passed. No full479 on rejected code. Whole-answer relevance judge agrees5/6 on selected controls but falsely accepts missing-thread answer; no production verifier installed. Last accepted scores450/479 and87/100 unchanged. See old100_patch14/REPORT.md and relevance_probe_20261022_r8/REPORT.md.

## Required part-level judge: still insufficient

31development/constructed scenarios,57manually labeled parts:50/57part agreement and26/31exact cases. Six false-accepted parts/four cases and one false-rejected valid unknown. Model often treats a fact available in source as if candidate answer said it. No production verifier installed or gold changed after inference; acceptedpatch9 scores unchanged. R9 prepared/unqueried, r10corrects two part phrasings before inference. See part_relevance_20261022_r10/REPORT.md.

## Candidate-answer quote diagnostic r11; production unchanged

Same31r10 inputs/gold,57parts. Raw51/57 and27/31exact cases; membership-guarded56/57 and30/31. Guard catches6source-only false approvals, but rejects one acceptable ECC answer because the judge quotes only its source. Generic-but-literal MacBook quotes and numeric-prefix quote show membership is not semantic sufficiency. No production verifier installed; broader frozen confirmation required. Total126.732s/median3.515s versus r10 96.822s/2.546s, no controlled speed claim. Acceptedpatch9 still450/479 and87/100. See answer_support_20261022_r11/REPORT.md.

## Broader r12 confirmation: combined judge rejected

44new scenarios/22texts/68parts: raw45/68,20falseaccept/3falsereject; candidatequote-membership guard53/68,3falseaccept/12falsereject. Guard removes17bad approvals but introduces9false rejections. Literal-but-insufficient OLED clause and swapped plan/actual values survive. Fiveof8validunknownparts rejected; correct table/implicit/typography also fail. No production gate installed or gold changed. Acceptedpatch9 unchanged450/479,87/100,193tests. Details answer_support_20261022_r12/REPORT.md.

## Candidate-only coverage r13; still no production gate

Same44r12candidates, new coverage labels distinct from source-support correctness. Raw45/68three-state, guarded56/68and35/44exact. Sevenfalsecovered from generic answers mislabeled explicitunknown and2missedcovered from missing IDs for realunknowns. IDs all exist but do not establish relevance. No factual verification or accepted chatbot gain; patch9 still450/479,87/100,193tests lastpassed. Details coverage_20261022_r13/REPORT.md.

## R14 product confirmation rejects answered-only gate

112distinctpayloads/56profiles/12questiontexts. Substantivecoverage54correctanswered/36correctnotanswered/22falseanswered/0missedanswered; no sourcebodies and allfalseapprovedIDsvalid. CPUmodel/corecount andwatts/efficiency mismatchpersists. Preregisteredthreshold failed broaderconfirmation; no productiongate installed, patch9unchanged450/479,87/100,193tests lastpassed. Details coverage_20261022_r14/REPORT.md.

## Requested-field intent r15; no productionshortcut

Registry62actualcatalogkeys, no candidate/sourcevalues. Exactintent68/91,17/17CPUcoreintentsright but11invalidcontracts,4unsafe shortcuts and fieldmismatches/extras. Product40/56,fallback25/30,compound3/5. Scope/unknown risks prevent integration; acceptedpatch9unchanged450/479,87/100,193tests lastpassed. See field_intent_20261023_r15/REPORT.md.

## R16 per-part intent: scope regressions prevent acceptance

Same91gold68→79exact,16fixes/5regressions; invalidcontracts11→0 butunsafe4→7. Product52/56,fallback23/30,compound4/5. Requiredpartkeys stillmisbindthreads/USB-C/regionandnowprinciples. No productionshortcut; acceptedpatch9unchanged450/479,87/100,193tests lastpassed. Read-onlyexistingnominal4BQwen3.5alias inventory recorded, no modelchange/inference. See field_intent_20261023_r16/REPORT.md.

## Qwen3.5 comparison blocked by runtimegrammar

91planned,3HTTP500attempts,88pending,0semanticresults; runnerstopped. Actualqwen35loadedctx6144, runtime Unexpectedemptygrammarstack error observed. Do notscoreinfra asFAIL orresume unchanged; minimaldecodingcompatibilityprobe needed. Productioncode/configunchanged, lastacceptedpatch9results450/479,87/100,193tests. See field_intent_20261023_r17_qwen35/REPORT.md.

## R18 decoder probe: no safe schema-bypass workaround

Schema500,JSONobject500,noformat200but300repeated8digits/lengthstop;0validcontracts,0semanticresults. RawHTTPerrorbodies preserved; cachedrunnerconfound/rootcauseunresolved. No productionconfig/codechange, lastaccepted450/479,87/100,193tests. Nextfreshstate/backend/samplingcanary,notfull91. See decoding_compat_20261023_r18/REPORT.md.

## R19 prepared; automatic execution review rejected launch

Three bounded canaries frozen/offlinechecked, attempted0. Combined command containing checks/docs/backgroundlaunch rejected with blocked by policy, no specific reason. No retry/split to bypass review; no model unload/inference/config change. Productionpatch9 unchanged450/479,87/100,193tests lastpassed. See runtime_canary_20261023_r19/REPORT.md.
