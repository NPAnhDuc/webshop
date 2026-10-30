"""Build a reviewable report from completed raw results, without model grading."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.knowledge import KnowledgeStore


def main():
    folder=ROOT/'evaluation/basic_rag_v1'
    live=json.loads((folder/'live_v4/summary.json').read_text(encoding='utf8'))
    fixtures=json.loads((folder/'fixtures_v3/summary.json').read_text(encoding='utf8'))
    results=json.loads((folder/'live_v4/results.json').read_text(encoding='utf8'))
    tests=json.loads((folder/'fixtures_v3/results.json').read_text(encoding='utf8'))
    if len(results)!=37 or len(tests)!=13:raise ValueError('Evaluation incomplete')
    quotes=0;mismatches=0
    for row in results+tests:
        result=row['result'];lookup={d['chunk_id']:d for d in result['sources']}
        for claim in result.get('rag',{}).get('claims',[]):
            for evidence in claim.get('evidence',[]):
                source=lookup.get(evidence['chunk_id'])
                for quote in evidence.get('quotes',[]):
                    quotes+=1
                    if not source or quote not in source['text']:mismatches+=1
    comparison=next(r['result'] for r in results if r['case']['id']=='B08')
    fixture_conflict=tests[-1]['result'].get('rag',{}).get('potential_conflict')
    db=ROOT/'data/business_sql/scenario_v1/shop.sqlite';store=KnowledgeStore(db)
    if any(d['document_id'].startswith('test-') for d in store.records()):raise ValueError('Test fixtures contaminated live knowledge')
    from dotenv import dotenv_values
    config=dotenv_values(ROOT/'.env')
    verification=dict(live=live,fixtures=fixtures,quotes_checked=quotes,quote_mismatches=mismatches,
        comparison_between_quarters_flagged_as_conflict=comparison.get('rag',{}).get('potential_conflict'),
        conflicting_fixture_flagged=fixture_conflict,fixture_documents_in_live_store=False,
        configured_mode=config.get('CHATBOT_MODE'),database_sha256=hashlib.sha256(db.read_bytes()).hexdigest(),
        code_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in (
            'shopbot/basic_rag.py','shopbot/knowledge.py','shopbot/knowledge_ui.py','shopbot/retrieval.py',
            'shopbot/rag_answer.py','shopbot/engine.py','shopbot/monthly.py','app.py')},
        test_runs=['144 passed: full regression suite before the last three added tests',
                   '27 passed: basic RAG, citation and Streamlit checks after the three added tests',
                   '18 passed: latest basic RAG checks after canonical MD persistence/promotion expiry validation'],
        limitations='Authored development cases, with repeated tuning. Not blind, production accuracy, human relevance judgment, a formal contradiction proof or weight training.')
    (folder/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf8')
    report=f'''# Kết quả RAG cơ bản — 20/10/2026

Đã chọn `CHATBOT_MODE=basic_rag` cho Python/Streamlit. Luồng này chỉ đọc tài liệu có nguồn; các công cụ SQL, giá/tồn kho, xếp hạng theo ngân sách, biểu đồ và Build PC không được gọi. React/Express chưa nối sang luồng này. Không fine-tune model hoặc chạy thêm Colab trong đợt này.

## Kết quả kiểm tra

| Kiểm tra | Kết quả |
|---|---:|
| Câu hỏi trên kho hiện tại, live_v4 | {live['passed']}/{live['cases']} |
| Chính sách/hướng dẫn/thông tin shop giả lập cách ly, fixtures_v3 | {fixtures['passed']}/{fixtures['cases']} |
| Tìm đúng tài liệu trong top 8 | {live['source_recall_at_8']:.0%} |
| Tìm đúng đoạn chuẩn trong top 8 | {live['passage_recall_at_8']:.0%}, {live['expected_passages']} đoạn cần tìm |
| Từ chối đúng khi thiếu thông tin | {live['correct_missing']}/{live['expected_missing']} |
| Từ chối nhầm trên các câu có đáp án trong bộ | {live['false_refusals_on_supported']} |
| Lộ tài liệu admin cho người mua | {live['private_source_leaks']} |
| Trích đoạn được kiểm tra độc lập với nguồn trả về | {quotes} |
| Trích đoạn không nằm trong nguồn | {mismatches} |

**Các số trên là kết quả tập phát triển đã được dùng sửa lỗi, không phải độ chính xác thực tế hay bộ kiểm tra mù.** Đáp án số liệu/thuật ngữ được kiểm bằng từ khóa và nguồn chuẩn; không dùng các chỉ số này thay đánh giá chất lượng diễn giải hoặc độ đầy đủ của người bán. Trích nguyên văn đúng không chứng minh đã chọn đúng ý trong mọi câu.

Kiểm tra phần mềm: 144 tests trong bộ hồi quy đầy đủ đạt. Sau khi thêm ba tests, 27 tests RAG/trích dẫn/Streamlit đạt; sau sửa lưu MD và bắt buộc ngày hết khuyến mãi, 18 tests RAG mới nhất đạt. Các tests cũ được chạy với `CHATBOT_MODE=tools` để kiểm tra không làm hỏng luồng cũ; các tests RAG đặt mode riêng rõ ràng. Không gọi những tests công cụ cũ là bằng chứng RAG tự tính số liệu.

## Đã thay đổi

- Tách luồng hỏi đáp tài liệu khỏi luồng công cụ, không để câu hỏi mua hàng tự trả giá/tồn mô phỏng. Giá/tồn quay về trang sản phẩm; chưa có URL shop được xác minh nên không tạo link giả.
- Tạo 67 bản thông số tham khảo, không có giá/tồn/giá vốn. Thông tin còn thiếu phải báo thiếu; bảo hành của nhà bán lẻ nước ngoài không trở thành cam kết của shop Việt Nam.
- Thêm bốn mục giải thích kỹ thuật từ nguồn chính thức: [OLED — Samsung](https://www.samsung.com/us/tvs/tv-buying-guide/why-oled-tvs-are-worth-it/), [tần số quét — Samsung](https://insights.samsung.com/2026/06/17/finding-the-right-refresh-rate-know-the-best-hz-for-your-needs/), [NVMe — NVM Express](https://nvmexpress.org/), [DDR5 — Crucial](https://stage.crucial.com/articles/about-memory/everything-about-ddr5-ram). Các mục này là tài liệu kỹ thuật tham khảo, không phải chính sách riêng của shop.
- Tìm kết hợp embedding tiếng Việt, TF-IDF và BM25; xử lý một số viết tắt/lỗi gõ nhẹ. Giữ bộ lọc quyền/ngày/phiên bản bắt buộc. Dự đoán loại tài liệu của model là ưu tiên mềm, tránh loại mất đoạn cần; người dùng yêu cầu lọc cứng thì vẫn giữ lọc cứng.
- Giới hạn các mẩu bằng chứng theo mức liên quan trước khi model chọn câu, để giảm chọn thông số không được hỏi. Câu trả lời giữ văn bản nguồn và dẫn tên/mục/đoạn/phiên bản. Có bộ nhớ sáu lượt theo vai trò và truy vấn trước.
- Admin Streamlit tải, sửa thành phiên bản mới và gỡ tài liệu. Có thể cập nhật cả tài liệu nền bằng phiên bản phủ mới, không đổi file nền hoặc sổ giao dịch. Nháp/tương lai/hết hạn không dùng; gỡ không làm bản cũ hồi sinh. Khuyến mãi được duyệt cần ngày kết thúc. PDF scan chưa OCR không được coi là đã đọc được.
- Manifest được đọc ở lượt hỏi tiếp theo, độc lập lịch nhập dữ liệu tháng. Cache vector phụ thuộc nội dung/model. Tests xác nhận nạp/sửa/gỡ hiển thị ở truy vấn kế tiếp; chưa đo SLA với tài liệu lớn và tải đồng thời.
- Log câu hỏi/câu trả lời/trạng thái/nguồn, có xoay vòng và che một số trường theo mẫu. Admin xem câu thiếu dữ liệu. Che theo mẫu chưa bảo đảm loại mọi thông tin nhạy cảm.
- Kiểm tra dấu hiệu mâu thuẫn qua hai nguồn có dẫn chứng: hai điều khoản giả lập 7 và 14 ngày được đánh dấu. Hai mục tiêu khác quý được kiểm riêng để tránh gọi khác biệt thời gian là mâu thuẫn. Bước này vẫn có thể sai vì dùng model, chưa phải kiểm chứng logic tổng quát.

## Dữ liệu và giới hạn

Kho hiện có 98 phiên bản, 92 tài liệu đã duyệt đang hiệu lực: 67 thông số, 4 mục thuật ngữ và 21 tài liệu chiến lược/chính sách/báo cáo mô phỏng. Chưa có chính sách thật đủ điều kiện đổi trả/bảo hành/giao hàng/hóa đơn/trả góp; chương trình ưu đãi thật; địa chỉ/giờ/liên hệ; bài hướng dẫn chọn máy; hướng dẫn mua hàng của shop. Tám câu thiếu thông tin được từ chối đúng, không được xem là đã có các dữ liệu này.

13 tình huống dùng chính sách và địa chỉ GIẢ LẬP chỉ nằm trong thư mục kiểm thử riêng; không được xuất bản vào kho phục vụ người dùng. Các mẫu để chủ shop bổ sung nằm trong `data/unstructured/drafts/basic_rag/`, chưa lập chỉ mục. Kênh gặp nhân viên thật chưa được kết nối; bot chỉ nhận biết yêu cầu và nói rõ chưa gửi.

Kiểm tra hiệu lực hiện ở độ chính xác theo ngày, chưa xử lý hết hạn trong giờ. Chưa có bộ câu hỏi độc lập của nhân viên bán hàng, kiểm thử đồng thời, đo thời gian phản hồi diện rộng, hoặc đảm bảo hiểu mọi cách viết sai/viết tắt. Bộ nhớ chưa xuyên thiết bị. Không tự học trọng số từ log; log dùng tìm tài liệu còn thiếu.

Database tài chính giữ nguyên SHA256 `{verification['database_sha256']}`. Streamlit health đã trả HTTP 200; quản lý tài liệu được kiểm tra bằng Streamlit AppTest, không kiểm tra bằng browser thật trong lượt này.

## Bằng chứng

- `live_v4/bank.json`, `results.json`, `summary.json`: 37 câu trên kho đang chọn.
- `fixtures_v3/fixtures.json`, `results.json`, `summary.json`: 13 tình huống dữ liệu giả lập cách ly.
- `verification.json`: kiểm tra trích đoạn, hash mã và database, cấu hình mode, dấu hiệu mâu thuẫn.
- Các lần `live_v1..v3`, `fixtures_v1..v2` và `ERRATA.md` được giữ nguyên. Lần đầu 25/37; các lỗi gồm chọn sai nhóm dữ liệu, hỏi lại câu đã rõ, chọn sai thông số và bó hẹp loại tài liệu. Có sửa đáp án đánh giá được ghi riêng, nên không dùng chênh lệch tỷ lệ như một phép đo độc lập.
- Phạm vi đầy đủ: `BASIC_RAG_REQUIREMENTS.md`.
'''
    (folder/'REPORT.md').write_text(report,encoding='utf8')
    print(json.dumps(dict(live=live['passed'],fixtures=fixtures['passed'],quotes=quotes,mismatches=mismatches,
        quarter_conflict=verification['comparison_between_quarters_flagged_as_conflict'],fixture_conflict=fixture_conflict,mode=verification['configured_mode'])))


if __name__=='__main__':main()
