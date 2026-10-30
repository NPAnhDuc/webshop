"""Render completed manual source-based review; never infer PASS from keywords."""
import hashlib,json,statistics
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'evaluation/adversarial_100_20261020'
def read(name):return json.loads((OUT/name).read_text(encoding='utf8'))


def main():
    bank=read('bank.json');rows=read('results.json');review=read('review.json');meta=read('metadata.json')
    integrity=read('integrity.json')
    assert len(bank)==len(rows)==len(review)==100
    assert [c['id'] for c in bank]==[r['id'] for r in rows]
    assert set(review)=={c['id'] for c in bank}
    assert integrity['unchanged']
    assert hashlib.sha256((OUT/'bank.json').read_text(encoding='utf8').encode()).hexdigest()==meta['bank_sha256']
    merged=[];quote_count=0;quote_errors=[];private_leaks=[]
    for case,row in zip(bank,rows):
        judgement=review[case['id']]
        assert judgement['status'] in ['PASS','FAIL'] and judgement['reason']
        result=row['result'];sources={s['chunk_id']:s for s in result.get('sources',[])}
        if row['role']=='customer' and any(s.get('audience')=='admin' for s in sources.values()):private_leaks.append(row['id'])
        for claim in result.get('rag',{}).get('claims',[]):
            for evidence in claim.get('evidence',[]):
                for quote in evidence.get('quotes',[]):
                    quote_count+=1
                    if evidence.get('chunk_id') not in sources or quote not in sources[evidence['chunk_id']]['text']:quote_errors.append(row['id'])
        merged.append(dict(**case,**judgement,result=row))
    def stats(items):return dict(total=len(items),passed=sum(x['status']=='PASS' for x in items),failed=sum(x['status']=='FAIL' for x in items))
    summary=dict(overall=stats(merged),roles={r:stats([x for x in merged if x['role']==r]) for r in ['customer','admin']},
                 content=stats([x for x in merged if x['expected_behavior'] in ['answer','partial']]),
                 boundaries=stats([x for x in merged if x['expected_behavior'] not in ['answer','partial']]),
                 by_behavior={b:stats([x for x in merged if x['expected_behavior']==b]) for b in sorted({x['expected_behavior'] for x in merged})},
                 failure_causes=dict(Counter(x['cause'] for x in merged if x['status']=='FAIL')),
                 failed_ids=[x['id'] for x in merged if x['status']=='FAIL'],
                 fail_but_self_full=[x['id'] for x in merged if x['status']=='FAIL' and x['result']['result'].get('rag',{}).get('answerability')=='full'],
                 exact_quotes_checked=quote_count,quote_errors=quote_errors,customer_private_source_leaks=private_leaks,
                 exceptions=[r['id'] for r in rows if not r['result']],
                 seconds_total=round(sum(r['seconds'] for r in rows),2),seconds_median=round(statistics.median(r['seconds'] for r in rows),2),
                 seconds_max=max(r['seconds'] for r in rows),integrity_unchanged=True,
                 scope='Authored weakness-focused stress set, manually scored by Codex against frozen rubrics and source snapshots; not real-traffic accuracy or independent human evaluation.')
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    lines=['# Kiểm thử 100 câu tập trung điểm yếu — 20/10/2026',
           f"**Khách hàng: {summary['roles']['customer']['passed']}/50 PASS; admin: {summary['roles']['admin']['passed']}/50 PASS. Tổng {summary['overall']['passed']} PASS, {summary['overall']['failed']} FAIL.**",
           'Bộ câu hỏi và tiêu chí được chốt trước khi hỏi. Chỉ câu hỏi, vai trò và lịch sử cùng nhóm được đưa vào bot; không đưa đáp án/tiêu chí. Không thay model, prompt, thuật toán, tài liệu hoặc SQL trong lượt chạy. Mốc thời gian20/10/2026, basic_rag đang dùng.',
           'Đây là bộ thử chủ đích tập trung điểm yếu, không đại diện tỷ lệ chính xác ngoài thực tế. Codex tự soạn và chấm từng câu theo tiêu chí/nguồn, không phải đánh giá độc lập của con người. Chấp nhận cách diễn đạt/nguồn tương đương và không bắt khớp từ khóa máy móc. Nhãn full/partial của bot không quyết định điểm; thiếu ý trọng tâm, sai kỳ hoặc sai phạm vi vẫn FAIL dù dẫn đúng nguồn.',
           f"Trong **67 câu trả lời kiến thức hoặc phần đã biết**: {summary['content']['passed']} PASS, {summary['content']['failed']} FAIL. Trong **33 câu hỏi lại/báo thiếu/giới hạn chức năng/quyền**: {summary['boundaries']['passed']} PASS, {summary['boundaries']['failed']} FAIL. Từ chối đúng ở nhóm thứ hai không có nghĩa đã có đủ dữ liệu/chức năng kinh doanh.",
           f"Kiểm tra {quote_count} đoạn trích nguyên văn: {len(quote_errors)} lỗi đoạn không có trong nguồn; {len(private_leaks)} trường hợp nguồn admin lọt sang khách; {len(summary['exceptions'])} ngoại lệ không có kết quả. Đây là kiểm tra trên các ca cụ thể, không chứng minh an toàn mọi tình huống. Câu chỉ thị trích trong câu hỏi không phải payload được cài vào tài liệu RAG; không có bộ PII thật để thử toàn diện.",
           f"Có {len(summary['fail_but_self_full'])} câu FAIL nhưng bot tự gắn full: {', '.join(summary['fail_but_self_full']) or 'không có'}. Tổng thời gian các câu {summary['seconds_total']} giây; trung vị {summary['seconds_median']} giây; tối đa {summary['seconds_max']} giây. Bao gồm tải model/tạo cache, không phải SLA.",
           '## Nhóm lỗi chính', '\n'.join(f'- {cause}: {count} câu.' for cause,count in summary['failure_causes'].items()),
           '## Chấm từng câu','| ID | Vai trò | Kết quả | Chủ đề | Nhận xét |','|---|---|---|---|---|']
    for x in merged:lines.append(f"| {x['id']} | {x['role']} | **{x['status']}** | {x['topic']} | {x['reason'].replace('|','/')} |")
    lines += ['## Tệp đối chiếu',
              '- [QUESTIONS.md](QUESTIONS.md): đủ100 câu và tiêu chí chốt trước.\n- [ANSWERS.md](ANSWERS.md): câu trả lời nguyên văn, nhãn và nhận xét.\n- [results.json](results.json): nguồn, truy vấn, profile và kết quả thô.\n- [gold_sources.json](gold_sources.json): snapshot nguồn độc lập với câu trả lời.\n- [metadata.json](metadata.json), [integrity.json](integrity.json): hash đóng băng và kiểm tra trước/sau.\n- [review.json](review.json): quyết định chấm thủ công.']
    (OUT/'REPORT.md').write_text('\n\n'.join(lines)+'\n',encoding='utf8')
    answers=['# Đủ 100 câu và câu trả lời nguyên văn']
    for x in merged:
        row=x['result'];r=row['result']
        answers += [f"## {x['id']} — {x['status']} — {x['role']}",x['question'],
                    'Tiêu chí đã chốt: '+x['rubric'],r.get('answer','ERROR'),
                    f"Hành động: {r.get('basic_action')}; tự đánh giá: {r.get('rag',{}).get('answerability')}; {row['seconds']} giây.",
                    'Chấm: '+x['reason']]
    (OUT/'ANSWERS.md').write_text('\n\n'.join(answers)+'\n',encoding='utf8')
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
