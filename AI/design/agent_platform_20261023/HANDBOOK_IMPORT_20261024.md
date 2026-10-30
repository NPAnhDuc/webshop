# Bổ sung business_ai_handbook theo yêu cầu người dùng

Nguồn: D:/Chatbot/chatbotshop/knowledge_base/business_ai_handbook. Đã kiểm kê12Markdown/103.955byte; nội dung nguồn không tự thành chỉ thị runtime. Đã đọc/rà soát các phần liên quan metric, SQL, agent, dự báo và một số công thức; không tuyên bố mọi benchmark hoặc code trong12file đã được xác minh toàn bộ.

Gói hoàn chỉnh: AI/data/knowledge_imports/business_ai_handbook/revision_20261024_r2.12raw giữ nguyênbyte/hash;9bản hiệu chỉnh khái niệm admin;14chunks theoheading/ngân sách180từ;27SFTseed cócontext/source/group_id, chưa chia train-validation và eligible_for_training=false. Không đụng bank/gold/eval cũ, không lấy đáp án sai của bot làm kiến thức. r1 giữ nguyên bản import chưa hoàn tất do đường dẫnWindows; r2 thay thế sạch, không ghi đè.

Xác nhận bằng tính toán: ví dụ CM1=388000, ads300000 thì CM2=88000, không âm. Vế tổng CLV bắt đầu kỳ0 không đồng nhất vế đóng của kỳ1. WAPE cần bảo vệ mẫu số khiactualtoàn0. Nghi vấn rolling vượtSKU ban đầu KHÔNG tái hiện với defaultfullwindow vàshift1 trong phép thử pandas3.0.6; đã đính chính với người dùng, auditkhông ghi là bugxácnhận. Forecast cần phân biệt one-stepvớifixed14day, không khẳng định mọi phép trainvalidationmẫuđều sai.

Thuế/phísàn/marketbenchmarks và promptcưỡngépnguyênnhân,hànhđộng: giữraw, loại khỏi9ghi chú/27target như chínhsách/số liệu thật. SQL/prompt5.x khôngthựcthi, khôngmở quyền. Những gì chưa có nguồn/ngày hiệu lực không được lấp bằng suy đoán.

Tất cảRAGdocuments/chunks admin-only/draft/reference; kiểm bằng active_documents cho cảadmin/customer đều không lọt vàoactivecorpus. Manifest/filehash/sourcehash kiểm lại đạt. Post_review_verification giữ riêng. Chưa indexembedding/khởiđộngworker/chạyQwen/fine-tune/Colab; activated_in_app=false,weights_trained=false. Đây là bổ sung dữ liệu đã chuẩn bị, không phải model đã học xong hoặc chatbot đã dùng nó để trả lời.

Hướng dùng: ưu tiênRAGadmin cócitationvàrole; review độc lập, lập queryset mới có ca thiếu dữ liệu/abstention trước kích hoạt. SFTseed dùng sau khi targetreview +groupedsplit/holdout đạt; không chuyển chúng thành nhãnKev vì chưa cótargettoolargs. DS dựbáophảihọc từchuỗi số chuẩn vàbacktest, không học mô hìnhdựbáo chỉtừvănxuôi.

Thay đổi model/hạ tầng chưa cần: vẫn giữ model local hiện có, không tải model lớn hoặc lách startup8011/r19bịchặn. Nhánh documents agentvẫndisabled. Cần nối và kiểm định nguồn tri thức theo kế hoạch; không thông báo handbook đã tíchhợp vàoapp trước khi việc này hoàn tất.

Nguồn kỹ thuật đối chiếu: [pandas groupby](https://pandas.pydata.org/docs/user_guide/groupby.html), [Hyndman WAPE](https://robjhyndman.com/hyndsight/wape.html), [TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html). Công thức tài chính nêu trên chỉ kiểm toán số minh họa/đại số, không xác nhận thuế/phí hiện hành hoặc đưa ra ngân sách thực tế.
