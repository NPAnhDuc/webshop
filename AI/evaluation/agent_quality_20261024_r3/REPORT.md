# Planner phân giai đoạn — r3 bị loại

Đã thử một thay đổi có kiểm định: StagedAdminPlanner chọn operation trước, chỉ với finance/chart/compare mới gọi bước metric/time bằng schema khóa operation. Quality/unsupported/clarify không gọi bước slot. ACL, lịch, SQL, nguồn và cấu hình mặc định giữ nguyên; chưa sửa số lượng “3 thanh RAM” vì là nguyên nhân độc lập.

Một batch local84lượt, gồm80câu/gold r2 giữ nguyên và4control mới đếm SKU so với ranking, đọc báo cáo có sẵn so với nhập/clean Excel. Integrity unchanged=true; không sửa code/data/config trong batch, không gọi thêm model batch hoặc khởi động dịch vụ. Gold correction Q12 chỉ được kế thừa từ r2, không sửa artifact cũ.

Checks18/24mới+control và57/60hồi quy; review ngữ nghĩa riêng75/84. Trên cùng80câu:73/80 so với74/80r2. Không có cải thiện đo được cho các lỗi operation cũ; thêm hồi quy A03 hỏi nối giá vốn sau so sánh bị chọn clarify dù đã có kỳ/ngữ cảnh. **accepted_for_application=false**, không promote. Tách giai đoạn tự nó chưa đủ để classifier hiểu đúng yêu cầu.

9FAIL: Q10(delete), Q14/A22(ranking), Q20/A20/Q24(clean/chuẩn hóa Excel), Q22(SKU doanh thu cao nhất), Q19(số lượng RAM), A03(hội thoại so sánh). Trừ Q19 và A03, các câu này vẫn bị gán data_quality để đọc nguồn cũ. Không có ghi dữ liệu sai; đọc an toàn không đồng nghĩa trả đúng câu hỏi.

79answer cũ không đổi sau chuẩn hóa đường dẫn artifact được so với review r2; A03 và4control được đọc riêng. Hai control mới Q21 đếm SKU và Q23 chỉ đọc báo cáo kiểm nguồn có sẵn đạt; Q22,Q24 thất bại. Các output operation sai đã hoàn tất JSON, done_reason=stop/eval_count8 ở Q10,Q20,Q22,A03; không quy lỗi này cho output truncation.

30test targetedPASS10,27s, full335testPASS111,94s; logs runtime/tests-admin-quality-r3.log và runtime/quality-data-quality-r3.log. Unit test chứng minh phân giai đoạn/khóa schema/fail-closed hoạt động, không chứng minh khả năng hiểu model. Median84lượt0,7655s/max21,156s chịu cold/warm và phân bố call; không suy nhanh hơn hoặc SLA. Summary checker kế thừa ghi chú template r2; số control đúng của r3 là4, chi tiết ở metadata/test_verification/human_review.

Bước tiếp ưu tiên xem lại thiết kế nhãn capability cụ thể (inspect_source/transform_file/rank_sales/plot/report/compare) và đầu vào ngữ cảnh tối thiểu, thay vì chỉ một nhãn unsupported bao trùm nhiều việc; đo bằng cùng câu và giữ control phủ định/câu nối. Chưa có đủ bằng chứng để train Kev hoặc thay model. Lỗi số lượng cần sửa ở parser literal riêng, không nhồi vào prompt operation. Giữ r1/r2/r3 nguyên vẹn, không mở validation RAG và không bật candidate mặc định. Không có model runner còn chạy ở cuối lượt.
