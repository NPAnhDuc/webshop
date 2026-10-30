"""Compare fixed-bank functional audits without rewriting either run."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'training/conversation_v3'

def read_rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf8').splitlines()]

def main():
    old=BASE/'audit_extended_20261019_v1/reviewed'
    new=BASE/'audit_improved_20261019_verified_v2'
    extra=BASE/'audit_new_wording_20261019_v2'
    before=read_rows(old/'results.jsonl');after=read_rows(new/'results.jsonl')
    independent=read_rows(extra/'results.jsonl')
    metadata=json.loads((new/'run-metadata.json').read_text(encoding='utf8'))
    extra_metadata=json.loads((extra/'run-metadata.json').read_text(encoding='utf8'))
    assert len(before)==len(after)==106 and len(independent)==12
    assert [(r['id'],r['question']) for r in before]==[(r['id'],r['question']) for r in after]
    assert json.loads((BASE/'audit_extended_20261019_v1/question-bank.json').read_text(encoding='utf8'))==json.loads((new/'question-bank.json').read_text(encoding='utf8'))
    source_checks={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest for name,digest in metadata['frozen_sources'].items()}
    dataset_digest=hashlib.sha256((ROOT/'data/business_sql/scenario_v1/shop.sqlite').read_bytes()).hexdigest()
    assert all(source_checks.values()) and dataset_digest==metadata['dataset_sha256']
    assert metadata['frozen_sources']==extra_metadata['frozen_sources']
    assert json.loads((BASE/'audit_new_wording_20261019_v1/question-bank.json').read_text(encoding='utf8'))==json.loads((extra/'question-bank.json').read_text(encoding='utf8'))
    assert dataset_digest==json.loads((old/'summary.json').read_text(encoding='utf8'))['dataset_sha256']
    repaired=[b['id'] for a,b in zip(before,after) if a['status']=='FAIL' and b['status']=='PASS']
    regressed=[b['id'] for a,b in zip(before,after) if a['status']=='PASS' and b['status']=='FAIL']
    errors=[r['id'] for r in after+independent if any(v['code']=='execution_error' for v in r['failures'])]
    passed=lambda rows:sum(r['status']=='PASS' for r in rows)
    candidate=read_rows(BASE/'audit_improved_20261019_verified_v3/results.jsonl')
    candidate_extra=read_rows(BASE/'audit_new_wording_20261019_v4/results.jsonl')
    candidate_regressions=[b['id'] for a,b in zip(after,candidate) if a['status']=='PASS' and b['status']=='FAIL']
    verification=dict(completed=106,new_wording_completed=12,old_passed=passed(before),passed=passed(after),failed=106-passed(after),new_wording_passed=passed(independent),repaired=repaired,regressed=regressed,execution_errors=errors,source_checks=source_checks,dataset_sha256=dataset_digest,unchanged_question_bank=True,
        rejected_candidate=dict(passed=passed(candidate),new_wording_passed=passed(candidate_extra),regressions=candidate_regressions),
        selection_reason='Restored exact source of stable 93/106 run; few-shot candidate regressed a previously correct topic-switch case.')
    (new/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf8')
    queue=[]
    historical=read_rows(BASE/'audit_new_wording_20261019_v2/results.jsonl')
    current_by_id={r['id']:r for r in independent}
    for row in historical:
        if row['status']=='PASS': continue
        dependent=row['id']=='Q007'
        queue.append(dict(id=row['id'],question=row['question'],observed_input_memory=row['input_memory'],
            observed_plan=row.get('plan'),expected=row['expected'],sql_evidence=row['grading_evidence'],
            dataset_sha256=dataset_digest,source_run='training/conversation_v3/audit_new_wording_20261019_v2',
            replay_status=current_by_id[row['id']]['status'],
            training_eligible=False,label_review_required=True,
            review_reason=('Dependent turn inherited the wrong initial metric correctly; repair the first turn and rebuild gold memory before any training.' if dependent else
                'Review the ambiguous Vietnamese term doanh so and document the monetary-unit convention or clarification policy.'),
            purpose='Tutor review/replay only. Do not put financial amounts into model weights or claim this bank remains unseen after tuning.'))
    (BASE/'tutor-review-queue.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in queue),encoding='utf8')
    lines=['# Cải thiện hội thoại — 19/10/2026','',f'Bộ cũ cùng 106 câu: **{passed(before)} PASS / {106-passed(before)} FAIL → {passed(after)} PASS / {106-passed(after)} FAIL**.',f'12 câu diễn đạt bổ sung: **{passed(independent)} PASS / {12-passed(independent)} FAIL**.','',
        'Cùng database mô phỏng, cùng câu hỏi và đáp án SQL. Không sửa nhãn để nâng điểm. Mốc trước là bản đã rà soát thủ công: hai từ chối quyền đúng được PASS. Các lượt thử dừng giữa chừng giữ riêng, không dùng làm điểm cuối. Đây là bộ kiểm thử phát triển, không phải ước lượng chất lượng trên khách thật.','',
        '## Đã thay đổi','',
        '- Sửa phân tích Q4/2025 và ký hiệu tháng/quý; lịch vẫn do code kiểm tra.',
        '- Model chọn thay đổi của lượt nối; server giữ kỳ, tiêu chí, số kết quả và nhóm khi không đổi. Công cụ mới không bị ép về ý định cũ.',
        '- SQL lọc laptop/chuột/GPU/các nhóm linh kiện trước xếp hạng, giữ đồng hạng cao nhất.',
        '- Trả CPU/GPU từ product_facts bằng danh sách trường công khai; không đưa bản ghi thô vào câu trả lời.',
        '- Phân biệt tiền hoàn, tiền nhập, số đơn, doanh thu theo kênh; số tính từ sổ SQL.',
        '- Tìm tài liệu theo ngày của phiên hỏi, quyền và hiệu lực; không khẳng định có OLED khi không có.',
        '- Đồng nhất cửa sổ ngữ cảnh 6144 ở hai bước gọi Ollama để tránh nạp lại model.',
        '- Encoder phân loại tổng hợp giữ để đối chiếu, mặc định không gọi; embedding tiếng Việt tìm tài liệu vẫn hoạt động.',
        '', '12 câu bổ sung lần đầu đạt 9/12, bản được chọn đạt 10/12. Thử thêm ví dụ JSON đạt 12/12 câu này nhưng bộ chính giảm từ 93 xuống 92/106, hồi quy Q054 (đổi chủ đề). Đã lưu thử nghiệm và khôi phục nguyên source bản 93/106, xác nhận bằng SHA256. Không coi các bộ đã dùng để sửa là test mù.',
        '', 'Đợt này sửa planner, bộ nhớ và công cụ; không có lượt finetune trọng số mới. Dữ liệu doanh thu vẫn là mô phỏng, không trở thành dữ liệu shop thật sau sửa.',
        '', '## Kiểm chứng','',
        '91 unit/integration tests qua. `verification.json` xác nhận cùng ngân hàng câu hỏi, cùng SHA256 database, source lúc chạy khớp source hiện tại; kiểm tra thêm 12 câu bằng cùng đáp án SQL độc lập.',
        '',f'Lỗi thực thi: {len(errors)}. Ca hồi quy so với bản trước: '+(', '.join(regressed) or 'không có')+'.',
        '', '## Câu vẫn FAIL','', '| Mã | Hỏi | Lý do |','|---|---|---|']
    for row in after:
        if row['status']=='FAIL': lines.append('| '+row['id']+' | '+row['question'].replace('|','/')+' | '+'; '.join(v['detail'] for v in row['failures']).replace('|','/')+' |')
    lines+=['','## Các câu bổ sung còn FAIL','']
    for row in independent:
        if row['status']=='FAIL': lines.append('- '+row['id']+': '+row['question']+' — '+'; '.join(v['detail'] for v in row['failures']))
    lines+=['','Chuỗi doanh số từng chọn nhầm đơn vị ở câu đầu rồi kế thừa sai sang câu sau. Đây là một lỗi gốc ảnh hưởng hai lượt. Hàng đợi `tutor-review-queue.jsonl` giữ lỗi trước sửa, trạng thái chạy lại và đáp án SQL; chưa tự cho vào train. Cần rà nghĩa từ/đơn vị và dựng lại ngữ cảnh chuẩn cho câu nối trước khi gán nhãn huấn luyện.','',
        'Các yêu cầu thiếu dữ liệu/chức năng vẫn FAIL dù trả lời giới hạn đúng. Không tự tạo thuế/chính sách, dự báo có độ tin cậy, bằng chứng nhân quả hoặc tương thích linh kiện để biến thành PASS.','',
        '- Chi tiết 106 câu được chọn: `audit_improved_20261019_verified_v2/REPORT.md`.',
        '- Chi tiết 12 câu bổ sung được chọn: `audit_new_wording_20261019_v2/REPORT.md`.',
        '- Thử nghiệm không kích hoạt: `audit_improved_20261019_verified_v3/REPORT.md` và `audit_new_wording_20261019_v4/REPORT.md`.',
        '- Bản trước giữ nguyên: `audit_extended_20261019_v1/reviewed/REPORT.md`.']
    (BASE/'IMPROVEMENT_REPORT.md').write_text('\n'.join(lines),encoding='utf8')
    print(json.dumps(verification,ensure_ascii=True))

if __name__=='__main__':main()
