# Reviewed routing seed — development only

12 kế hoạch được chọn sau review agent_quality_20261024_r4. Input: question, principal role do server cung cấp, state trước lượt; không lấy answer hay kết quả công cụ làm input. Target được kiểm theo hợp đồng hành động/args/source/period, có evaluation/trace_id provenance.

Tất cả là exposed development seed, chưa đủ train/hiệu chuẩn Kev hoặc independent holdout. documents.answer có connection disabled, file.transform có supported=false. Đúng route không chứng nhận đã hỗ trợ nghiệp vụ. Không đưa nhãn/trace/gold vào RAG hoặc tự học từ câu trả lời sai. Khi mở rộng phải chia theo nhóm hội thoại/paraphrase trước train/dev/holdout và so baseline luật/LLM. Không ghi đè seed v1; chưa fine-tune/Colab.
