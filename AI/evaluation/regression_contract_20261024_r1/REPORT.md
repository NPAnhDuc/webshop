# Hồi quy trước sửa và trace

Đã chụp baseline_code/manifest và9lỗi ngữ nghĩa r3 trước thay đổi, giữ source results/review hash.9countcases viết trước sửa:2/9PASS; sau sửa9/9 cùngcasehash. Parser đọc thanh/bộ/ổ; runtime kiểm requested/returned/available/uniqueIDs, thiếu hàng thì báo thiếu, không bịa đủ.

Engine(trace_directory=...) bật structured traces opt-in do server chọn đường dẫn: question/role/date/plans/calls với args/output/status, state trước/sau, result/error/time/parentid. ContextVar tách capture scope; rolefolders không thay ACL HTTP/filesystem. Không tự đưa trace vào RAG/train. Lỗi ghi trace được audit và không thay answer hợp lệ.

conversation_cases_r2.json có22lượt/6hội thoại: finance/so sánh/đổi metric, đổi nhóm catalog, quality không bịa kỳ, phủ định/unsupported, documents-only/mixed và đổi role. Đây là hợp đồng development chờ model evaluation, không claim22lượtPASS. SQLoracle trực tiếp3kỳ lưu query/param/hash, không dùng analyze_business làm đáp án chuẩn.

Fixture trace đầu dùng category memory/internal-hard-drive sai taxonomy backendram/ssd. Giữ originalbank và3failedtrace, thêm errata.json/conversation_cases_r2.json. smoke_r2 có3lượt linked trace với parser/toolthật và plannerinjected đạt, không phải LLM. Không sửa taxonomynguồn để làm fixture saiPASS.

36targetedPASS5,50s trướcparentlink; codecuối full350PASS128,12s. Một batchmodel thật cùng84câu r3 ở agent_quality_20261024_r4:76/84ngữ nghĩa so75/84, chỉQ19answerđổi vàđúng3RAM;84trace links verified. Còn8lỗi, chưapromote. Kế hoạch10bổsung ở design/reliability_20261024/PLAN.md. Bước tiếp registry/state/documents, devCompose sớm; Excelunit/date/version/rollback vàseasonal-naive/backtest còn trong kế hoạch.
