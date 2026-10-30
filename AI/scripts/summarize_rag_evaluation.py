"""Transparent before/after report; raw failed and interrupted trials preserved."""
from pathlib import Path
import json
import hashlib
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.evaluate_rag import evaluate

ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'evaluation/rag_v1'


def read(name):return json.loads((folder/name).read_text(encoding='utf8'))


def main():
    cases={c['id']:c for c in read('bank.json')};errata=read('errata.json')['changes']
    baseline=[json.loads(s) for s in (folder/'baseline_dev/results.jsonl').read_text(encoding='utf8').splitlines()]
    reviewed=[]
    for r in baseline:
        case=dict(cases[r['id']],**{k:v for k,v in errata.get(r['id'],{}).items() if k!='reason'})
        score=evaluate(case,r['sources'],dict(answer=r['answer'],rag=r.get('score',{}).get('synthesis',{})))
        reviewed.append(dict(r,score=score))
    target=folder/'baseline_reviewed';target.mkdir(exist_ok=True)
    (target/'results.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in reviewed),encoding='utf8')
    scored=[r['score'] for r in reviewed];required=sum(s['required_passages'] for s in scored)
    before=dict(cases=len(reviewed),answer_pass=sum(s['answer_pass'] for s in scored),
        passage_recall=sum(s['passages_found'] for s in scored)/required,average_answer_words=sum(s['words'] for s in scored)/len(scored),
        note='Same question bank. Errata credits equivalent anti-stacking evidence; original raw run preserved. No answer relabeling to favor the candidate.')
    (target/'summary.json').write_text(json.dumps(before,indent=2),encoding='utf8')
    dev=read('extractive_dev_v6/summary.json');holdout=read('final_holdout_v6/summary.json');conversation=read('conversation_v7/summary.json')
    # Independent audit against saved source chunks, not only the renderer.
    spans=0;invalid=[]
    for name in ('extractive_dev_v6','final_holdout_v6'):
        for line in (folder/name/'results.jsonl').read_text(encoding='utf8').splitlines():
            row=json.loads(line);sources={s['chunk_id']:s for s in row.get('sources',[])}
            for claim in row.get('score',{}).get('synthesis',{}).get('claims',[]):
                for evidence in claim['evidence']:
                    source=sources.get(evidence.get('chunk_id'))
                    for quote in evidence.get('quotes',[]):
                        spans+=1
                        if source is None or quote not in source['text']:invalid.append(dict(id=row['id'],quote=quote))
    core=None
    corepath=folder/'core_regressions_v7/summary.json'
    if corepath.exists() and json.loads(corepath.read_text(encoding='utf8')).get('completed')==json.loads(corepath.read_text(encoding='utf8')).get('planned_questions'):
        core=json.loads(corepath.read_text(encoding='utf8'))
        oldpath=ROOT/'training/conversation_v3/audit_improved_20261019_verified_v2/results.jsonl'
        original={(r['group'],r['question']):r for r in (json.loads(s) for s in oldpath.read_text(encoding='utf8').splitlines())}
        new=[json.loads(s) for s in (folder/'core_regressions_v7/results.jsonl').read_text(encoding='utf8').splitlines()]
        core['regressions']=[r['question'] for r in new if original[(r['group'],r['question'])]['status']=='PASS' and r['status']=='FAIL']
    source_names=['retrieval.py','dense_retrieval.py','chunking.py','rag_answer.py','engine.py','conversation.py','business_review.py']
    verification=dict(baseline=before,dev=dev,holdout=holdout,conversation=conversation,
        span_audit=dict(checked=spans,invalid=invalid,scope='Exact stored source spans; does not prove relevance, completeness or real-world truth.'),
        core=core,database_sha256=hashlib.sha256((ROOT/'data/business_sql/scenario_v1/shop.sqlite').read_bytes()).hexdigest(),
        corpus_correction=read('corpus-correction.json'),selected_mode='extractive',reranker_active=False,
        code_sha256={name:hashlib.sha256((ROOT/'shopbot'/name).read_bytes()).hexdigest() for name in source_names})
    (folder/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf8')
    lines=['# Cải thiện RAG cơ bản — 20/10/2026','',
      'Phạm vi: RAG tài liệu và luồng admin SQL + tài liệu. Không fine-tune mới, không chuyển sang agentic RAG.',
      '', '## Kết quả', '', '| Kiểm tra | Trước | Sau |','|---|---:|---:|',
      f"| Trả lời đúng phần được hỏi, dev | {before['answer_pass']}/32 | {dev['answer_pass']}/32 |",
      f"| Tìm được đoạn chuẩn, dev | {before['passage_recall']:.1%} | {dev['passage_recall']:.1%} |",
      f"| Độ dài trung bình câu trả lời, dev | {before['average_answer_words']:.0f} từ | {dev['average_answer_words']:.0f} từ |",
      f"| 16 ca giữ riêng | Chưa đo baseline | {holdout['answer_pass']}/16 |",
      f"| Hội thoại nhiều lượt / quyền / đối chiếu kế hoạch | — | {conversation['passed']}/{conversation['cases']} |",'',
      'Bộ nhỏ được viết từ tài liệu shop mô phỏng: 48 ca, có các biến thể cùng họ câu. Không phải độ chính xác production. 16 ca giữ riêng không được dùng để sửa. Bộ chấm kiểm tra con số/từ khóa cần thiết và thừa nhận phần thiếu; kiểm tra thủ công vẫn cần cho câu trả lời tự do.',
      '', '## Đã sửa','',
      '- BM25 giữ mã chiến dịch kết hợp TF-IDF và embedding tiếng Việt bằng RRF; nhận Q3/2026, tăng số bằng chứng để ghép nhiều nguồn.',
      '- Chunk theo heading kể cả thiếu dòng trống, giữ tiêu đề bảng/đơn vị; bỏ nhãn mô phỏng lặp khỏi văn bản nhúng nhưng giữ nguyên trong nguồn và metadata.',
      '- Model chọn câu/dòng bảng có sẵn và phần câu hỏi chưa được giải đáp; renderer ghép bằng chứng ngắn, dẫn mục/phiên bản. Không ghép nguyên các chunk dài như trước.',
      '- Cung cấp ngày hiệu lực cho bộ chọn bằng chứng. Các bước lọc quyền, bản nháp và phiên bản vẫn thực hiện trước tìm kiếm.',
      '- Viết lại câu nối bằng câu hỏi tài liệu trước và kỳ server đã xác nhận; giữ bộ nhớ theo vai trò. Tăng giới hạn đầu ra riêng bước viết lại để tránh JSON bị cắt.',
      '- Làm rõ SUP-LAP/SUP-PC từ bảng suppliers, lưu procurement v2 và provenance; giữ v1, không thay số kinh doanh.',
      '- Admin có đối chiếu mục tiêu/thực hiện, bảng nhóm hàng, SKU ưu tiên kiểm tra và tồn lịch sử. Tháng 9 thiếu 349.092.000 đồng; không quy hụt kế hoạch cho ngành hàng khi thiếu mục tiêu ngành hàng.',
      '', '## Kiểm chứng và các bản không chọn','',
      f'- Kiểm tra độc lập {spans} trích đoạn đã hiển thị: {len(invalid)} không khớp nguồn. Đây chỉ là kiểm tra nguồn, không bảo đảm hiểu đúng toàn bộ câu hỏi.',
      '- 111 unit/integration tests qua; kiểm tra mục tiêu sau sửa cuối cũng qua. Tính tiền lấy từ SQL, không dùng model viết SQL/Python.',
      '- Reranker bằng model từng làm rơi nguồn đúng; không bật mặc định. Các thử nghiệm diễn giải tự do trả lời thiếu/lặp nên không triển khai. Giữ raw logs của các bản dừng hoặc bị loại.',
      '- Hiệu chỉnh bộ chấm: quy tắc không cộng dồn có thể nằm ở cả chính sách giá và lịch marketing; một câu về quyền thay ngân sách chỉ có bằng chứng một phần. Lưu errata riêng, không ghi đè bank/raw run.',
      '', '## Còn hạn chế','',
      '- Hai ca giữ riêng chưa đạt: cách nói “quá ba tháng” chưa nối đúng ngưỡng 90 ngày; câu vừa hỏi xả kho vừa hỏi quyền thay ngân sách chưa nói rõ phần ngân sách còn thiếu.',
      '- Bản chọn dùng tổng hợp trích xuất nhiều nguồn, chưa có diễn giải tự do đủ tin cậy. Không gọi nó là RAG hoàn hảo.',
      '- Chưa có reranker được chứng minh tốt hơn, chưa đánh giá production, chưa tăng chất lượng tư vấn mua hàng sâu ở lượt này.',
      '- Dữ liệu vẫn mô phỏng. Điều khoản shop chưa có vẫn phải thiếu; không tự chế chính sách/thuế/dự báo hoặc kết luận nhân quả.',
      '', '## Tệp bằng chứng','',
      '- `bank.json`, `manifest.json`, `errata.json`: câu hỏi và nguồn chuẩn.',
      '- `baseline_dev/`, `baseline_reviewed/`, `extractive_dev_v6/`, `final_holdout_v6/`: raw results và số đo.',
      '- `conversation_v7/`: kiểm thử model thật nối câu và luồng admin.',
      '- `core_regressions_v7/`: hồi quy số liệu/sản phẩm/quyền; không trộn bộ chấm tài liệu cũ yêu cầu chép nguyên chunk vào điểm RAG mới.',
      '- `verification.json`, `corpus-correction.json`: hash và đối soát nguồn/dữ liệu.']
    if core:
        lines.insert(lines.index('## Còn hạn chế')-1,f"- Hồi quy ngoài tài liệu: {core['passed']}/{core['completed']} PASS; {len(core['regressions'])} câu vốn đúng bị sai. Các tác vụ thiếu dữ liệu/chưa hỗ trợ vẫn được ghi FAIL.")
    (folder/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(before=before,after=dev['answer_pass'],holdout=holdout['answer_pass'],span_checks=spans,invalid_spans=len(invalid),core_complete=core.get('completed') if core else None),ensure_ascii=True))


if __name__=='__main__':main()
