# Mixed catalog + knowledge — r10/r11

Làm lại phần r9 bị loại theo hướng khác: **không đổi prompt/enum router** (byte-identical r8). Tách câu bằng luật cố định sau khi route (`split_mixed` trong `catalog_planner.py`): chỉ tách tại liên từ rõ ràng (và/rồi/đồng thời/kèm theo/ngoài ra/dấu phẩy không nằm giữa hai chữ số), hai phần là span nguyên văn, phần catalog phải có thao tác/toán hạng (tìm/lọc/so máy/dưới N/N thanh...) và không có dấu hiệu kiến thức, phần kiến thức không có toán hạng catalog. Mơ hồ (hai yêu cầu catalog, không có liên từ, chính sách có số lượng mua) → trả None, giữ luồng một ý định cũ. Không gọi thêm model, không có splitter LLM tự bịa câu hỏi con.

Áp dụng khi router chọn search/compare/documents (r10) và thêm clarify (r11). **Không ghi đè admin** vì "so sánh" còn dùng cho so kỳ tài chính. Phần catalog chạy như cũ trên span catalog; phần kiến thức gọi `documents.answer` (hiện registered-disabled) và câu trả lời nêu rõ phần đó chưa kết nối, `partial=true`, `components` ghi trạng thái từng phần, kể cả khi phần catalog phải hỏi lại. Kèm hai sửa nhỏ: đếm số lượng nhận "monitor", ordinal nhận "thứ2" viết liền số.

## Kết quả (cùng118 lượt/gold r9, ngày server đóng băng23/10/2026)

| | r8 | r9 (loại) | r10 | r11 |
|---|---|---|---|---|
| 106 cũ: đổi answer/toolargs so r8 | — | 4 đổi, 3 hồi quy | 0 | 0 |
| 106 semantic | 103/106 | 100/106 | 103/106 (kế thừa) | 103/106 (kế thừa) |
| 12 mixed (checks độc lập r9) | — | 7/12 | 9/12 | **11/12** |

- integrity unchanged=true cả hai lượt; r11 median 0,844s, max 2,0s.
- r10 sai Q48/Q52 (router trả clarify) và Q58. r11 sửa Q48/Q52.
- Còn **Q58** (admin, "So máy thứ1 với thứ2 và giải thích RAM là gì"): router chọn admin → hiểu thành so hai kỳ. Chưa sửa; cần phân biệt so sản phẩm/so kỳ trong nhánh admin mà không phá câu so kỳ.
- Q29/Q30/Q41 vẫn FAIL do viết dính — tính năng typo vẫn hoãn theo yêu cầu người dùng; splitter cố ý không tách "Tìm3thanhRAMdưới3triệu".
- 106 semantic là kế thừa review r8 sau khi xác minh answer (normalize revision) và tool/args giống hệt; 12 mixed là mechanical checks, chưa human review văn phong.

Tests: `tests/test_mixed_requests.py` 32 ca; toàn bộ **455 PASS** 138,6s (`runtime/tests-mixed-r11-full.log`). Code snapshot trong `code_snapshot/`, runner `scripts/run_quality_data_quality_r10.py`/`_r11.py`, log `runtime/quality-agent-r10.log`/`r11.log`.

Đây là development đã lộ, không phải independent validation. Default `basic_rag`/config/model/data không đổi; chưa promote/frontend/deploy/train. Đề xuất: r11 thay r8 làm checkpoint hồi quy. Bước sau: chạy bộ 300 buyer (`buyer_expansion_20261024_r2`), rồi Q58/nhánh tài liệu khi worker 8011 được sửa.
