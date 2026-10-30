# Hội thoại kiểm tra dữ liệu — candidate r1 chưa nghiệm thu

Đã nối operation data_quality vào planner admin và nhánh trả lời có nguồn từ admin.data_quality. Hỏi nguồn, số SKU/dòng sổ, đối soát và độ phủ có thể gọi reader đã pin thay vì hỏi kỳ tài chính. Bộ nhớ giữ chủ đề quality cùng kỳ/metric tài chính trước đó; chuyển lại doanh thu tháng9/2026 vẫn gọi finance đúng kỳ. Nhánh quality công bố phạm vi toàn revision, dữ liệu mô phỏng và chưa xác nhận đủ doanh số, không đếm dòng sổ thành số đơn.

Một batch local Qwen3 hiện có:74 lượt gồm14mới và60hồi quy bank/gold copy nguyên byte từ admin r4. Không sửa code/data/model/config lúc batch chạy; integrity unchanged=true. Không fine-tune, embedding hoặc dịch vụ mới. Bank là development đã lộ, không phải validation độc lập.

Checks cơ học:11/14mới,58/60hồi quy. Review ngữ nghĩa riêng69/74:7/7ca kiểm nguồn/coverage đi đúng reader và giữ giới hạn; hai ca số liệu mới đúng1.189.908.000VND và131đơn tháng9/2026. Khách tự xưng admin bị chặn, không thực thi ghi dữ liệu. Tuy nhiên có5FAIL, vì vậy **accepted_for_application=false**, không bật mặc định.

Lỗi cần sửa ở round sau:

- Q10,Q11,A20: planner hiểu yêu cầu xóa/clean/ghi đè Excel thành đọc chất lượng nguồn cũ. Tool chỉ đọc nên không ghi sai dữ liệu, nhưng câu trả lời sai ý định. Cần tách thao tác kiểm nguồn với nhập/biến đổi/ghi dữ liệu chưa hỗ trợ.
- A04: câu vẽ biểu đồ giá vốn bị chọn finance; số đúng nhưng không có ảnh. Đây là hồi quy so với r4.
- Q12: câu thông số RAM bị chọn search rồi hỏi ngân sách. Gold gốc ghi deferred chưa đúng hợp đồng route documents; giữ nguyên gold, ghi gold_audit trong human_review và phát hành sửa nhãn ở revision sau. Actual clarify/ngân sách vẫn FAIL theo cả hai cách chấm.

60ca hồi quy giảm từ60/60r4 xuống58/60ở candidate này;36buyer controls cũ vẫn đạt, hai lỗi ở admin. Checker cũ crash KeyError khi gặp call data_quality không có start/end; đã giữ nguyên checker cũ và tạo bản copy trong revision mới, đổi phép đọc args thành get để ghi FAIL đúng thay vì crash. Không chỉnh gold/raw hoặc biến call sai thành PASS.

Trung vị74lượt0,937s, lượt lớn nhất23,953s; không phải SLA hay bằng chứng nhanh hơn baseline. 22test hội thoại targetedPASS12,20s trước di chuyển guard ngày; full code cuối327testPASS131,83s. Log runtime/tests-admin-quality-r1.log và runtime/quality-data-quality-r1.log. UnitPASS không thay điểm ngữ nghĩa.

App mặc định, config, frontend/auth và nguồn cũ không thay; candidate chỉ opt-in, cần inject curated_reader ở server. Giữ nguyên toàn bộ artifact/source/bank/gold/candidate cũ. Chưa có Excel mapping, DS/backtest, train Kev/Colab hoặc HyDE. Bước kế tiếp ưu tiên sửa ranh giới operation có control, khôi phục chart và route thuật ngữ trong revision mới, rồi so cùng câu và hồi quy; không mở validation RAG cũ hoặc chạy batch thứ hai trong heartbeat này.
