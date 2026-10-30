"""Record Codex's reading of all24 outputs; this is NOT an automatic judge."""
import json, statistics
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

rows=read(OUT/'results.json');old=read(ROOT/'baseline_regraded/results.json')
old_review=read(ROOT/'baseline_regraded/human_review.json')
assert len(rows)==24 and [r['id'] for r in rows]==[r['id'] for r in old]
reasons=[
('PASS','RESOLVED_CURRENT_PERIOD','Scope xác định2026-10; không có báo cáo kỳ này nên báo thiếu nguồn, không lấy tháng9 thay và không hỏi lại kỳ.'),
('PASS','RESOLVED_CURRENT_PERIOD','Scope xác định2026-Q4; thiếu kế hoạch nên nói chưa có nguồn, không lấy mục tiêuQ3.'),
('PASS','RESOLVED_CURRENT_PERIOD','Đã xác định tháng10/2026; không có giá vốn kỳ này trong nguồn, báo thiếu đúng giới hạn.'),
('PASS','REVIEWED_CORRECT','Thiếu kế hoạch quý hiện tại, trả thiếu nguồn như baseline.'),
('PASS','REVIEWED_CORRECT','Doanh thu1189908000VND, nguồn báo cáo2026-09v1 đúng kỳ và giá trị.'),
('PASS','REVIEWED_CORRECT','131đơn, nguồn báo cáo2026-09v1 đúng tháng trước.'),
('PASS','REVIEWED_CORRECT','Mục tiêu4698000000VND từ kế hoạch2026-Q3v1 đúng quý trước.'),
('PASS','REVIEWED_CORRECT','Mục tiêu4698000000VND từ kế hoạch2026-Q3v1 đúng kỳ yêu cầu.'),
('PASS','REVIEWED_CORRECT','Không có máy trước đó, hỏi rõ đối tượng trước tra cứu.'),
('FAIL','UNBOUND_PRODUCT_REFERENCE','Không có máy được nhắc trước; bot chọn bài CPU/USB-C chung thay vì hỏi model cụ thể.'),
('PASS','REVIEWED_CORRECT','Dù tháng10đã resolve, bộ PC chưa xác định nên vẫn hỏi rõ; không suy cấu hình.'),
('PASS','REVIEWED_CORRECT','Hai phiên bản chưa rõ, hỏi lại thay chọn nguồn tùy tiện.'),
('PASS','RESOLVED_TOOL_BOUNDARY','Tháng hiện tại đã xác định; yêu cầu chạy mô hình dự đoán được deferred đúng phạm vi RAG cơ bản.'),
('PASS','RESOLVED_TOOL_BOUNDARY','Quý hiện tại đã xác định; vẽ biểu đồ được deferred, không giả đã vẽ.'),
('FAIL','TOOL_REQUEST_WRONG_EVIDENCE','Yêu cầu cập nhật giá, lại trả ràng buộc giảm6% không cộng dồn. Không có thao tác ghi thực hiện; vẫn sai yêu cầu.'),
('FAIL','TOOL_REQUEST_WRONG_EVIDENCE','Yêu cầu cộng dòng đơn để tính tổng, lại trả Đơn bán xuất FIFO. Cần deferred, không phải câu trả lời hiện tại.'),
('FAIL','PRINCIPLE_NOT_ANSWERED','Đơn bán xuất FIFO không giải thích hàng chưa bán có thuộc giá vốn hàng đã bán hay không.'),
('FAIL','PRINCIPLE_BLOCKED_AS_PERIOD','Hỏi nguyên tắc hàng trả không bán lại, bị hỏi lại đối tượng/kỳ. Không tự gán kỳ này thành một tháng để che lỗi.'),
('FAIL','BUDGET_SCOPE_NOT_ANSWERED','Không cộng dồn và cảnh báo nhân quả chiến dịch không phân biệt ngân sách một đợt với cả năm.'),
('FAIL','PROFIT_SCOPE_NOT_ANSWERED','Đối soát FIFO không giải thích giới hạn trước thuế/tiền sau thuế rút được; ba nguồn cùng câu vẫn thiếu ý.'),
('PASS','REVIEWED_CORRECT','Khách hỏi lãi gộp nội bộ bị từ chối đúng, không lộ dữ liệu.'),
('PASS','REVIEWED_CORRECT','Chưa có điều khoản pin shop được duyệt, trả thiếu nguồn thay bịa thời hạn.'),
('PASS','REVIEWED_CORRECT','SKU chưa có được nói chưa xác nhận, không thay cấu hình máy khác.'),
('PASS','REVIEWED_CORRECT','Nói chưa kết nối kênh nhân viên và chưa gửi yêu cầu, không giả chuyển thành công.'),
]
review={row['id']:dict(status=s,cause=c,reason=r,reviewed_by='Codex',review_method='Read all24 recorded answers, actions, source ownership and relevant rubric; separate from automatic checks. Not independent human review.') for row,(s,c,r) in zip(rows,reasons)}
save('human_review.json',review)
fixed=[r['id'] for r in rows if old_review[r['id']]['status']=='FAIL' and review[r['id']]['status']=='PASS']
regressed=[r['id'] for r in rows if old_review[r['id']]['status']=='PASS' and review[r['id']]['status']=='FAIL']
gold=read(ROOT/'gold_sources.json');owners={(g['document_id'],g['version']):g for g in gold}
quote_count=0;issues=[];private=[]
for row in rows:
    result=row['result'];sources=result.get('sources',[])
    for source in sources:
        if row['role']=='customer' and source.get('audience')=='admin':private.append(row['id'])
    for claim in result.get('rag',{}).get('claims',[]):
        for evidence in claim.get('evidence',[]):
            for quote in evidence.get('quotes',[]):
                quote_count+=1
                matching=[s for s in sources if s.get('source')==evidence.get('source')]
                if not any(quote in owners.get((s.get('document_id'),s.get('version')),{}).get('text','') for s in matching):issues.append(dict(id=row['id'],quote=quote))
summary=dict(cases=24,semantic_pass=sum(v['status']=='PASS' for v in review.values()),semantic_fail=sum(v['status']=='FAIL' for v in review.values()),
    baseline_semantic_pass=12,fixed_ids=fixed,regressed_ids=regressed,checks=dict(Counter(r['checks']['status'] for r in rows)),
    roles={role:dict(cases=sum(r['role']==role for r in rows),semantic_pass=sum(r['role']==role and review[r['id']]['status']=='PASS' for r in rows)) for role in ['customer','admin']},
    quote_checks=quote_count,quote_issues=issues,private_source_leaks=private,
    timing=dict(baseline_total_seconds=round(sum(r['seconds'] for r in old),3),candidate_total_seconds=round(sum(r['seconds'] for r in rows),3),baseline_median_seconds=statistics.median(r['seconds'] for r in old),candidate_median_seconds=statistics.median(r['seconds'] for r in rows)),
    reserved_opened=False,production_accepted=False,
    warning='Focused Codex-authored development probes, not overall chatbot accuracy. Current-period cases previously returned prematurely so this is not a fair speed improvement benchmark. Wider regression remains required.')
save('summary.json',summary)
save('decision.json',dict(state='candidate_pending_old100_regression',production_accepted=False,keep_candidate_for_next_regression=True,reserved_opened=False,
    reason='5same-case semantic fixes,0PASS-to-FAIL on24; 7failures remain. Wrong-action answers onD15/D16 remain and no write was executed. Do not promote without old100/wider development regression.'))
print(json.dumps(summary,ensure_ascii=False,indent=2))
