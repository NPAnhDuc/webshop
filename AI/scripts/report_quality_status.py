"""Render progress without upgrading automatic checks into semantic accuracy."""
import json,statistics
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'evaluation/quality_loop_20261021'
def read(p,default=None):return json.loads(p.read_text(encoding='utf8')) if p.exists() else default
meta=read(BASE/'metadata.json');before=read(BASE/'baseline_80/results.json',[]);after=read(BASE/'candidate_v1/results.json',[])
lookup={r['id']:r for r in after};pairs=[(r,lookup[r['id']]) for r in before if r['id'] in lookup]
def counts(rows):return dict(Counter(r['checks']['status'] for r in rows))
oldmatched=[a for a,b in pairs];newmatched=[b for a,b in pairs]
fixed=[a['id'] for a,b in pairs if a['checks']['status']=='FAIL_CHECKS' and b['checks']['status']=='PASS_CHECKS']
regressed=[a['id'] for a,b in pairs if a['checks']['status']=='PASS_CHECKS' and b['checks']['status']=='FAIL_CHECKS']
review=read(BASE/'baseline_80/human_review.json',{})
after_review=read(BASE/'candidate_v1/human_review.json',{})
status=dict(bank_turns=600,unique_question_texts=545,conversation_families=454,development=479,validation=121,
 baseline_completed=len(before),candidate_completed=len(after),matched_comparison_cases=len(pairs),baseline_matched_checks=counts(oldmatched),candidate_matched_checks=counts(newmatched),
 fixed_check_ids=fixed,regressed_check_ids=regressed,manual_review_cases=len(review),
 warning='Source/action checks only. No semantic score for600 or unseen validation. Compare only matched IDs and frozen source snapshots.')
quoted_audit=read(ROOT/'evaluation/quoted_clauses_20261023_r20_v2/summary.json')
if quoted_audit:
    status['latest_qa_diagnostic']=dict(name='quoted_clause_r20_offline',summary=quoted_audit,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## R20 offline clause audit; production unchanged\n\n479development replayed without inference.28quoted questions,13titles split by current parser;27have exact-title owner in available_fields,24in final selected sources.17answers cite other titles (noise signal, not semanticFAIL count). Staged quote-aware parser only;451unquoted rows unchanged,5edge checks pass. No answer quality gain measured/no production change/no retry of deniedr19. See quoted_clauses_20261023_r20_v2/REPORT.md.\n')
quoted_candidate=read(BASE/'candidate_patch15_quoted_development/semantic_summary.json')
if quoted_candidate:
    status['active_code']='patch9_restored_after_rejected_patch15'
    status['latest_qa_diagnostic']=dict(name='patch15_quoted_rejected',summary=quoted_candidate,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch15 quote-aware parser rejected\n\nAll28focus answers manually reviewed:19→13PASS,0fixes/6regressions; candidate197units passed but semantic completeness decreased. Restored26patch9app/shopbot hashes and original tests. No old100/full479 on rejected code. Production accepted450/479and87/100unchanged; see candidate_patch15_quoted_development/REPORT.md and rollback unit log. No r19retry or knowledge/model/config revision.\n')
document_payload=read(ROOT/'evaluation/document_payload_20261023_r21/summary.json')
if document_payload:
    status['latest_qa_diagnostic']=dict(name='document_payload_r21',summary=document_payload,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## R21 unchanged production document capture\n\n12/12exact baseline answers reproduced,6PASS/6FAIL,24chat calls/integritytrue.11requested titles reach search and selector; IdeaPad/Photoshop correct facts present but wrong fragments chosen.081SGexcluded by namedSKU code-intersection filter despite exact requested article existing. Prompt1690–3007of6144tokens,allfinishstop; no truncation signal. No production gain/change; see document_payload_20261023_r21/REPORT.md.\n')
title_candidate=read(BASE/'candidate_patch16_title_development/semantic_summary.json')
if title_candidate:
    status['active_code']='patch9_restored_after_rejected_patch16'
    status['latest_qa_diagnostic']=dict(name='patch16_title_scope_rejected',summary=title_candidate,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch16 title-scoped summaries rejected\n\nAll28focus answers manually reviewed:19→17PASS,4fixes/6regressions. Correct document binding fixes KC3000/IdeaPad/Photoshop/081SG but sentence selection drops conditions/main facts on controls.208candidate units passed; restored26patch9files and removed new test after preserving artifacts. No old100/full479 on rejectedcode. Accepted450/479,87/100unchanged. See candidate_patch16_title_development/REPORT.md.\n')
paragraph_trial=read(BASE/'candidate_patch17_paragraph_development/infra_review.json')
if paragraph_trial:
    status['active_code']='patch9_restored_after_patch17_infrastructure_stop'
    status['latest_qa_diagnostic']=dict(name='patch17_paragraph_infrastructure_stop',summary=paragraph_trial,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch17 paragraph trial stopped before semantic evaluation\n\n211candidate unit tests passed.3router ConnectionError attempts/0semanticresults,25pending; stopped singlebatch and restored26patch9files.193rollback tests passed50.07s. Ollama recovered0.40.5; embedding8011launch rejected by automatic execution review (blocked by policy, no reason), no retry/bypass. No accepted quality/speed change. See candidate_patch17_paragraph_development/REPORT.md.\n')
(BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# Kiểm thử và cải thiện theo log — 21/10/2026',
 '**Ngân hàng mới:600 lượt hỏi,300 khách hàng và300 admin;545 lời văn khác nhau trong454 nhóm.** Câu nối giống nhau ở sản phẩm khác được tính đúng là các lượt theo ngữ cảnh, không giả là600 câu độc lập.',
 'Đã chốt479 lượt phát triển và121 lượt xác minh theo nhóm hội thoại. Cùng nhóm không chia sang hai tập. Hai tập vẫn đọc cùng kho tri thức; không phải bộ đánh giá của người độc lập. Bộ100 cũ giữ riêng để kiểm tra hồi quy.',
 f"**Đã hỏi{len(before)} lượt baseline mới và{len(after)}/479 lượt candidate.** Đối chiếu được{len(pairs)} lượt cùngID; đây là tiến độ, không phải đã xong600.",
 '| Trên cùng các ID đã chạy | Trước sửa | Sau sửa |','|---|---:|---:|']
for label in ['PASS_CHECKS','FAIL_CHECKS','NEEDS_REVIEW']:lines.append(f'| {label} | {counts(oldmatched).get(label,0)} | {counts(newmatched).get(label,0)} |')
lines += [
 'PASS_CHECKS chỉ xác nhận đoạn/số thuộc đúng nguồn-phiên bản hoặc action dự kiến trong kiểm tra hẹp. Chưa chứng minh đủ ý, đúng nghĩa, ngắn gọn hay không mâu thuẫn. FAIL_CHECKS cũng cần xem nguồn tương đương trước khi chốt. Không tự báo600 câu đã đạt vì có dẫn nguồn.',
 f"Các ca chuyển FAIL_CHECKS→PASS_CHECKS đã quan sát: {', '.join(fixed) or 'chưa có'}. Chuyển ngược: {', '.join(regressed) or 'chưa có'}. Chỉ tính cùng câu; không đổi tiêu chí/gold sau khi thấy câu trả lời.",
 f"Đã đọc/chấm riêng{len(review)} câu baseline bị gắn cờ hoặc cần chấm nghĩa; chưa chấm độc lập toàn80 hoặc600. [Nhận xét thủ công](baseline_80/human_review.json).",
 f"Chấm lại riêng{len(after_review)} ca đã đọc: còn{sum(v['status']=='FAIL' for v in after_review.values())} FAIL ngữ nghĩa/định tuyến trong nhóm này; không ngoại suy thành điểm toàn bộ. [Nhận xét sau sửa](candidate_v1/human_review.json).",
 '## Sửa theo lỗi thực sự trong log',
 '- Mã máy không khớp nguồn: thêm ràng buộc nhận diện mã sản phẩm, không lấy cấu hình laptop gần giống để lấp model chưa có. Còn cần kiểm thử cách gọi không có mã số và câu nhiều sản phẩm.',
 '- Từ chối nội bộ bị báo model lỗi: kiểm tra enum của kết quả model trước khi server đặt quyết định denied. Không mở rộng quyền theo lời tự xưng.',
 '- Viết tháng liền chữ số và thángISO: bổ sung phân giải phạm vi, tránh câu tháng9 bị trả báo cáo10/2025. Bảo toàn cụm lãi vay và thuế, bỏ ràng buộc không tính chênh lệch khỏi danh sách câu hỏi con.',
 '- Hai kỳ có cùng con số: bỏ gộp trùng chỉ theo văn bản; giữ riêng nguồn và phiên bản, tránh mất một tháng khi cả hai cùng có2 sản phẩm hoàn trả.',
 '- Câu độc lập có từ còn: không cho model viết lại mãSKU khi không có chủ đề trước. Kiểm tra hồi quy phát hiện trường hợp i5-14400F bị model viết ngắn sai; đã sửa và có lượt hỏi lại riêng.',
 '- Log thêm model/revision mã, kỳ, thời gian, phần chưa trả, tài liệu ứng viên và chẩn đoán. Queue tách tương tác thật, benchmark và origin chưa rõ; câu full của tương tác cũng được đưa vào kiểm tra, không chỉ các câu từ chối.',
 'Các sửa này là cải thiện mã và quan sát, không huấn luyện trọng số, không bổ sung chính sách/số thật giả để hợp đáp án. SQL và manifest tri thức vẫn giữ nguyên. Các khoảng trống thực cần xác nhận được ghi tại[KNOWLEDGE_GAPS.md](KNOWLEDGE_GAPS.md).',
 '## Kiểm chứng và chạy tiếp',
 '- Sau patch2:173 kiểm tra lõi và4 kiểm tra giao diện qua. LogAI/runtime/tests-quality-patch2-b.log vàtests-quality-patch2-ui.log. Đây là kiểm thử phần mềm, không phải điểm ngữ nghĩa chatbot.',
 '- Đã chạy20 câu hồi quy cũ trước chỉnh cuối phần viết lại truy vấn; phát hiện và sửa một ca chặn nhầmC31. Lượt hỏi lạiC31 trả đúng10nhân/boost4,7GHz, vẫn cần làm rõ phần luồng tốt hơn. C44 model giả đã báo thiếu đúng. C03,C06,A15,A39 vẫn còn lỗi; không đổi chúng thành PASS vì unit test qua.',
 f'- candidate_v1 đã chạy {len(after)}/479 lượt phát triển; kiểm tra tự động: {counts(after)}. Chỉ sửa giữa các round. Sau chốt phát triển mới hỏi121 lượt xác minh, rồi thêm ca mới từ log thực.',
 '- Đã bật tác vụ trên cuộc trò chuyện mỗi giờ để đọc kết quả, tiếp tục sửa có căn cứ và chạy vòng tiếp. Nếu batch đang chạy thì không chạy chồng hoặc đổi mã giữa lượt. Chỉ thông báo thay đổi có ý nghĩa/lỗi chặn; không nhắc lại tiến độ không đổi.',
 '- Máy và ứng dụng desktop cần mở cho công việc local; mất điện hoặc đóng máy thì không có cam kết vẫn chạy. [Hướng dẫn chính thức OpenAI](https://developers.openai.com/training/walkthroughs/scheduled-tasks).',
 '## Tệp',
 '- [Ngân hàng đã chốt](bank.json),[cấu trúc/hash và số lượng theo chủ đề](metadata.json),[nguồn chuẩn](gold_sources.json).',
 '- [Baseline80](baseline_80/CHECKS.md),[candidate đang chạy](candidate_v1/CHECKS.md),[kết quả thô](candidate_v1/results.json).',
 '- [Kế hoạch vòng lặp](LOOP_PLAN.md),[trạng thái tiếp tục](CURRENT.md),[queue log](log_review_queue.json).',
 'Bộ có nhiều câu số liệu theo tháng, không đại diện đều mọi tình huống bán hàng. Khi báo nghiệm thu phải tách theo chủ đề/nhóm và chấm nghĩa, không dùng số lượng lớn để che yếu ở tư vấn/đối chiếu.'
]
text='\n\n'.join(lines[:4])+'\n\n'+'\n'.join(lines[4:7])+'\n\n'+'\n\n'.join(lines[7:])
# Keep all markdown table rows contiguous.
import re
text=re.sub(r'(?m)^(\|.*\|)\n\n(?=\|)',r'\1\n',text)
for a,b in {'mới:600':'mới: 600',',300':', 300',';545':'; 545','trong454':'trong 454','là600':'là 600','chốt479':'chốt 479','và121':'và 121','Bộ100':'Bộ 100','và300':'và 300','cùngID':'cùng ID','xong600':'xong 600','báo600':'báo 600','toàn80':'toàn 80','hoặc600':'hoặc 600','riêng23':'riêng 23','còn7':'còn 7','quan sát:':'quan sát:','hỏi'+str(len(before)):'hỏi '+str(len(before)),'và'+str(len(after))+'/':'và '+str(len(after))+'/', 'được'+str(len(pairs)):'được '+str(len(pairs)), 'đọc/chấm riêng'+str(len(review)):'đọc/chấm riêng '+str(len(review))}.items():text=text.replace(a,b)
(BASE/'REPORT.md').write_text(text+'\n',encoding='utf8')
targeted=read(BASE/'candidate_v2_targeted/results.json',[])
if targeted:
    target_ids={r['id'] for r in targeted}
    matched_old=[r for r in after if r['id'] in target_ids]
    target_lookup={r['id']:r for r in targeted}
    target_fixed=[r['id'] for r in matched_old if r['checks']['status']=='FAIL_CHECKS' and target_lookup[r['id']]['checks']['status']=='PASS_CHECKS']
    target_regressed=[r['id'] for r in matched_old if r['checks']['status']=='PASS_CHECKS' and target_lookup[r['id']]['checks']['status']=='FAIL_CHECKS']
    status['patch2_targeted']=dict(completed=len(targeted),planned=89,before=counts(matched_old),after=counts(targeted),fixed_check_ids=target_fixed,regressed_check_ids=target_regressed,integrity=read(BASE/'candidate_v2_targeted/integrity.json'))
    status['candidate_manual_review']=dict(cases=len(after_review),statuses=dict(Counter(v['status'] for v in after_review.values())),warning='Purposefully selected flagged cases and topic samples, not a representative accuracy estimate.')
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch2: ngữ cảnh sản phẩm và thuộc tính\n\n')
        f.write('Giữ mã sản phẩm được khách nhắc đến riêng với tiêu đề bài tham khảo; giữ nguyên thuộc tính trong câu hỏi thay vì dùng câu viết lại làm mất ý. Phân biệt VRAM/RAM, bố trí bộ RAM/tốc độ và độ trễ đầu tiên/CAS bằng nhãn trường nguồn. Không thêm đáp án hoặc ID benchmark vào mã. SQL, tri thức và trọng số không thay đổi.\n\n')
        f.write(f"Đã chạy {len(targeted)}/89 lượt development có đủ lịch sử hội thoại, gồm các lỗi đã quan sát và đối chứng. Trên cùng {len(targeted)} ID: trước {counts(matched_old)}, sau {counts(targeted)}. Sửa được kiểm tra nguồn/action: {target_fixed}; suy giảm kiểm tra: {target_regressed}. Không coi đây là điểm toàn 479 hoặc điểm ngữ nghĩa.\n\n")
        f.write('Xem [báo cáo patch2](PATCH2_REPORT.md). Chưa chạy lại toàn 479 bằng patch2, chưa chạy lại đầy đủ 100 hồi quy cũ và chưa mở 121 validation.\n')
experiment=read(BASE/'candidate_v3_targeted/decision.json')
if experiment:
    trial=read(BASE/'candidate_v3_targeted/results.json',[])
    status['patch3_experiment']=dict(decision=experiment,completed=len(trial),checks=counts(trial))
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch3 thử nghiệm — không áp dụng\n\n')
        f.write(f"Đã kiểm lại {len(trial)}/89 lượt cùng câu: {counts(trial)}. Sửa Q0396 nhưng làm hỏng Q0473; không có cải thiện ròng. Đã phục hồi mã đúng hash patch2, giữ nguyên kết quả thử và nguồn. 179 test qua thuộc bản thử bị loại; mã đang dùng có 177 test qua ở patch2. [Chi tiết và quyết định](PATCH3_REPORT.md). Validation chưa mở.\n")
memory_trial=read(BASE/'candidate_v4_targeted/results.json',[])
if memory_trial:
    previous={r['id']:r for r in targeted}
    matched=[previous[r['id']] for r in memory_trial]
    memory_fixed=[r['id'] for r in memory_trial if previous[r['id']]['checks']['status']=='FAIL_CHECKS' and r['checks']['status']=='PASS_CHECKS']
    memory_regressed=[r['id'] for r in memory_trial if previous[r['id']]['checks']['status']=='PASS_CHECKS' and r['checks']['status']=='FAIL_CHECKS']
    memory_review=read(BASE/'candidate_v4_targeted/human_review.json',{})
    status['patch4_memory']=dict(completed=len(memory_trial),planned=89,before=counts(matched),after=counts(memory_trial),
        fixed_check_ids=memory_fixed,regressed_check_ids=memory_regressed,decision=read(BASE/'candidate_v4_targeted/decision.json'),
        review_cases=len(memory_review),review_statuses=dict(Counter(v['status'] for v in memory_review.values())),
        roles={role:dict(turns=sum(r['role']==role for r in memory_trial),checks=counts([r for r in memory_trial if r['role']==role])) for role in ['customer','admin']})
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch4: lịch sử để nhớ đối tượng, nguồn để xác nhận dữ kiện\n\n')
        f.write(f"Đã chạy {len(memory_trial)}/89 lượt cùng ID với patch2: trước {counts(matched)}, sau {counts(memory_trial)}. FAIL_CHECKS→PASS_CHECKS: {memory_fixed}; chiều ngược: {memory_regressed}. Đây chỉ là kiểm tra nguồn/action. Quyết định và chấm nghĩa phải xem [PATCH4_REPORT.md](PATCH4_REPORT.md).\n\n")
        f.write('Với sản phẩm đã xác định, router/selector nhận câu hỏi trước và chủ đề đã xác nhận, không nhận câu trả lời cũ do bot sinh làm bằng chứng. History người dùng trong profile vẫn nguyên vẹn. Không đổi nguồn/gold/model, không mở validation. 179 test phần mềm qua (AI/runtime/tests-quality-patch4.log).\n')
        memory_decision=status['patch4_memory']['decision']
        if memory_decision and not memory_decision['promoted']:
            f.write('\n**Đã loại patch4 và phục hồi mã đúng hash patch2:** sửa Q0301 nhưng làm hỏng Q0300/Q0373/Q0446/Q0478. Không dùng bản thử làm mã hiện tại. 179 test thuộc bản bị loại; mã hiện tại có 177 test đã qua ở patch2.\n')
fifth=read(BASE/'candidate_v5_development/comparison.json')
if fifth:
    status['patch5_development']=fifth
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch5 — toàn 479 development đã hoàn tất\n\n'+fifth['markdown_summary']+'\n')
old100=read(BASE/'old100_patch5_retry1/summary.json')
if old100:
    status['old100_patch5']=old100
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Hồi quy100 trên patch5 đã chấm\n\n')
        f.write(f"Theo cùng rubric v7: {old100['semantic_pass']}/100 PASS, khách47/50 và admin40/50; v7 là85/100. Sửa C06/C44, không có hồi quy từ PASS.87 câu trả lời/trích dẫn giống hệt nên kế thừa review,13 thay đổi được đọc lại. Không là điểm validation hoặc độ chính xác thực tế. [Chi tiết](old100_patch5_retry1/REPORT.md).\n")
sixth=read(BASE/'old100_patch6/decision.json')
if sixth:
    status['patch6']=dict(decision=sixth,summary=read(BASE/'old100_patch6/summary.json'))
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch6 đã loại\n\nBản thử mở rộng ứng viên giảm87→76/100,11hồi quy. Đã phục hồi đúng hash patch5;182 test thuộc bản bị loại,181 test của mã đang dùng. [Chi tiết](PATCH6_REPORT.md).\n')
assessment=read(BASE/'BASELINE_600_SUMMARY.json')
if assessment:
    status['assessment_600']=assessment
    status['validation']=assessment['validation']
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Hoàn tất479 development và121 validation trên mã đóng băng\n\n')
        f.write('Validation được đọc/chấm đủ121:112PASS/9FAIL, khách49/52,admin63/69; nhóm lập luận kinh doanh chỉ2/7. Tổng600 có524PASS_CHECKS/8FAIL_CHECKS/68NEEDS_REVIEW, không phải điểm đúng ngữ nghĩa. Development mới chấm112ca chọn, không ngoại suy toàn479/600. Chưa nghiệm thu; validation đã mở, sửa tiếp cần nhóm holdout mới. [Báo cáo đầy đủ và giới hạn](BASELINE_600_REPORT.md).\n')
(BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
context_root=ROOT/'evaluation/context_revision_20261021_r3'
context_baseline=read(context_root/'baseline_regraded/summary.json')
if context_baseline:
    status['context_revision']=dict(revision=str(context_root),state='baseline_complete_no_bot_change',summary=context_baseline,reserved_opened=False)
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Baseline ngữ cảnh revision3 — bot chưa đổi\n\n')
        f.write('24development tập trung có12PASS/12FAIL nghĩa.4cờ lỗi giả của r2 do gold span quá dài được sửa bằng revision mới từ nguồn gốc; r2 giữ nguyên. R3 regrade cùng24outputs, không inference mới hay cải thiện chatbot.24reserved chưa được hỏi. [Chi tiết/provenance](../context_revision_20261021_r3/REPORT.md).\n')
context_candidate=read(context_root/'context_r3_candidate1/summary.json')
if context_candidate:
    status['context_revision']=dict(revision=str(context_root),state='candidate_pending_old100_regression',baseline=context_baseline,summary=context_candidate,decision=read(context_root/'context_r3_candidate1/decision.json'),reserved_opened=False)
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch7 — candidate ngữ cảnh, chưa chốt hồi quy\n\n')
        f.write('Phân giải tháng/quý trước guard mơ hồ, vẫn hỏi khi chưa biết máy/bộ/tài liệu. Cùng24development:12→17PASS nghĩa,7FAIL còn lại,không cóPASS→FAIL trong24. Checks16PASS/3FAIL/5REVIEW. Chưa hồi quy100 trênpatch7; điểm87/100 cũ thuộcpatch5.24reserved chưa mở. [Chi tiết](../context_revision_20261021_r3/context_r3_candidate1/REPORT.md).\n')
seventh_regression=read(BASE/'old100_patch7/summary.json')
if seventh_regression:
    status['old100_patch7']=seventh_regression
    status['context_revision']['state']='old100_regression_passed_continue_development'
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch7 — hồi quy100 đã hoàn tất\n\n')
        f.write('Giữ87PASS/13FAIL,khách47/50,admin40/50,0PASS→FAIL so patch5.99answer/action/sources giống hệt; A17chỉ đổi thứ tự nguồn đã đọc lại;13FAILđãđọc lại.213quotes/0integrityissues. Giữcandidateđểdevelopment,chưa nghiệm thu,chưa rerun479/chưa mở24reserved. Không tuyên bố cải thiện tốc độ do cache. [Báo cáo](old100_patch7/REPORT.md).\n')
context_second=read(context_root/'context_r3_candidate2/summary.json')
if context_second:
    status['context_revision']=dict(revision=str(context_root),state='patch8_pending_old100_regression',baseline=context_baseline,summary=context_second,decision=read(context_root/'context_r3_candidate2/decision.json'),reserved_opened=False)
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch8 — candidate định tuyến, cần hồi quy100\n\n')
        f.write('Cùng24 development:17→18PASS nghĩa,6FAIL; sửa yêu cầu thực hiện cập nhật giá thành deferred,0PASS→FAIL trong24. Checks17/2/5 riêng. Đã khóa cùng đồng hồ xóa/as_of trong test sau khi máy sang22/10;187test qua. Chưa hồi quy100 trênpatch8,87/100 thuộcpatch7.24reserved chưa mở. [Chi tiết](../context_revision_20261021_r3/context_r3_candidate2/REPORT.md).\n')
eighth_decision=read(BASE/'old100_patch8/decision.json')
if eighth_decision:
    status['patch8_experiment']=dict(decision=eighth_decision,summary=read(BASE/'old100_patch8/summary.json'))
    status['context_revision']['state']='patch8_rejected_active_patch7'
    status['context_revision']['active_summary']=context_candidate
    status['context_revision']['rejected_summary']=context_second
    status['context_revision']['summary']=context_candidate
    status['context_revision']['rejected_decision']=read(context_root/'context_r3_candidate2/decision.json')
    status['context_revision']['decision']=read(context_root/'context_r3_candidate1/decision.json')
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch8 đã loại sau hồi quy100\n\n')
        f.write('Bản thử87→88PASS nhưng làm hỏngA36(C-TET có dữ liệu lại báo thiếu),A35mất chủđềchiếndịch. Đãphục hồi đúng hashpatch7,187testqua,giữ fixture cùngclock. Active17/24developmentvà87/100;18/24và88/100thuộcbản bịloại.24reserved chưa mở. [Quyết định và bằng chứng](old100_patch8/REPORT.md).\n')
context_third=read(context_root/'context_r3_candidate3/summary.json')
if context_third:
    status['context_revision']=dict(revision=str(context_root),state='patch9_pending_old100_regression',baseline=context_baseline,summary=context_third,decision=read(context_root/'context_r3_candidate3/decision.json'),reserved_opened=False)
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch9 — candidate ràng buộc sản phẩm, cần hồi quy100\n\n')
        f.write('Cùng24 development:17→18PASS nghĩa,6FAIL; sửaD10 từ trả thuật ngữ sang hỏi model khi chưa có đối tượng,0PASS→FAIL trong24. Khách8/8,admin10/16;checks17/2/5 riêng.193test qua, không đổi nguồn/model/gold.87/100 đã đo thuộcpatch7, chưa đo patch9.24reserved chưa mở; patch8 vẫn bị loại. [Chi tiết](../context_revision_20261021_r3/context_r3_candidate3/REPORT.md).\n')
ninth_regression=read(BASE/'old100_patch9/summary.json')
if ninth_regression:
    status['old100_patch9']=ninth_regression
    status['context_revision']['state']='patch9_old100_passed_broader_development_needed'
    status['context_revision']['decision']=read(context_root/'context_r3_candidate3/decision.json')
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch9: hồi quy100 hoàn tất, cần đánh giá rộng\n\n')
        f.write('87PASS/13FAIL giữ nguyên so patch7;98answer/action/sources giống hệt,2thayđổiA16/A17đọc lại vẫn đúng.210quotes/0integrityissues.193test đã qua,24targeted18PASS/6FAIL,không là điểm toàn hệ thống. Giữ mã để đánh giá lại479development;24reserved chưa mở. [Chi tiết](old100_patch9/REPORT.md), [kế hoạch coverage](candidate_v9_development/REVIEW_PLAN.md).\n')
ninth_development=read(BASE/'candidate_v9_development/comparison.json')
if ninth_development:
    status['patch9_development']=ninth_development
    status['context_revision']['state']='patch9_full479_semantic_review_complete' if ninth_development['semantic_coverage']['unreviewed']==0 else 'patch9_full479_semantic_review_in_progress'
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    coverage=ninth_development['semantic_coverage']
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch9: đủ479, chấm nghĩa còn dang dở\n\n')
        f.write(f"Checks422/4/53 giữ nguyên so patch5,15case đổi sourceobjects đã đọc đúng;914quotes/0quoteissues/0privateleaks. Coverage{coverage['reviewed']}/479: {coverage['inherited']}kế thừa,{coverage['fresh']}đọc mới; tập đã chấm{coverage['reviewed_subset']},còn{coverage['unreviewed']}chưa đọc. Không có điểm nghĩa toàn479/600,không coi coverage tăng là bot tiến bộ. Chưa mở24reserved/chưa nghiệmthu. [Chi tiết](candidate_v9_development/REPORT.md).\n")
ninth_semantics=read(BASE/'candidate_v9_development/semantic_summary.json')
if ninth_semantics:
    status['patch9_semantic_development']=ninth_semantics
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch9 đã chấm nghĩa đủ479\n\n450PASS/29FAIL theo rubric nội dung chính,112kếthừa+367đọc mới. Khách231/248,admin219/231;330/358nhómđạt mọi lượt.53câu có secondaryissue. Nhóm kinhdoanh6/17,côngnghệ19/28; nhiều câu số liệu lặp, không coi là độ đúng ngoài thực tế hoặc nghiệmthu. Không cộng với validationpatch5 thành điểm600cho patch9. [Phân bố vàgiới hạn](candidate_v9_development/semantic_summary.json).\n')
tenth_progress=read(BASE/'candidate_v10_development/progress.json')
if tenth_progress:
    status['patch10_development']=dict(progress=tenth_progress,integrity=read(BASE/'candidate_v10_development/integrity.json'),state='recorded_pending_semantic_review' if (BASE/'candidate_v10_development/integrity.json').exists() else 'running_or_incomplete',production_accepted=False,reserved_opened=False)
    status['context_revision']['state']='patch10_development_in_progress_or_pending_review'
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
tenth_decision=read(BASE/'candidate_v10_development/decision.json')
if tenth_decision:
    status['patch10_development']['decision']=tenth_decision
    status['patch10_development']['summary']=read(BASE/'candidate_v10_development/summary.json')
    status['patch10_development']['state']=tenth_decision['state']
    if tenth_decision['state']=='rejected_restore_patch9':status['context_revision']['state']='patch10_rejected_active_patch9'
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch10 đã loại: bốn sửa, hai câu nối hồi quy\n\n450→452/479nghĩa,noise53→30,nhưngQ0300/Q0478mất trả lời đúng dù biếtmodel. Phục hồi đúngpatch9,giữtrial/gold/raw.201testthuộcbảnthử,activepatch9cósuite193. Không áp parser riêng lẻ trước xử lý phụ thuộc lời đáp cũ. [Chi tiết](candidate_v10_development/REPORT.md).\n')
history_probe=read(ROOT/'evaluation/history_binding_20261022_r1/summary.json')
if history_probe:
    status['history_binding_probe_r1']=history_probe
    (BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Chẩn đoán history trên cùngpatch9\n\n6kịch bản/2caseđãmở:historygốc2/2,historyngắn0/2,historyngắn+câunêumodelrõ2/2. Chưa triển khai resolver tự động,khônggọilàproductionimprovement; cần baseline rộng hơn và hồi quy. Inputs modelanswer chỉ là hội thoại test,không xuất bản knowledge/training. [Chi tiết](../history_binding_20261022_r1/REPORT.md).\n')
# Later controlled history experiments are development diagnostics, not production scores.
history_rounds={
    'r2_baseline':'history_binding_20261022_r2',
    'patch11_rejected':'history_binding_20261022_r2_candidate_p11',
    'r3_explicit_original':'history_binding_20261022_r3_original_explicit',
    'patch12_rejected':'history_attribute_20261022_r4_candidate_p12',
    'patch13_rejected':'history_source_20261022_r5_candidate_p13',
    'r6_payload_observation':'history_payload_20261022_r6',
    'patch14_focused_pending_regression':'history_staged_20261022_r7_candidate_p14',
    'r8_relevance_feasibility':'relevance_probe_20261022_r8',
    'r10_part_relevance_feasibility':'part_relevance_20261022_r10',
    'r11_candidate_answer_support':'answer_support_20261022_r11',
    'r12_broader_answer_support':'answer_support_20261022_r12',
    'r13_candidate_coverage':'coverage_20261022_r13',
    'r14_product_coverage_confirmation':'coverage_20261022_r14',
    'r15_requested_field_intent':'field_intent_20261023_r15',
    'r16_per_part_field_intent':'field_intent_20261023_r16',
    'r17_qwen35_compatibility_failure':'field_intent_20261023_r17_qwen35',
    'r18_decoder_compatibility':'decoding_compat_20261023_r18',
    'r19_prepared_execution_rejected':'runtime_canary_20261023_r19',
}
status['history_diagnostics']={name:dict(summary=read(ROOT/'evaluation'/folder/'summary.json'),decision=read(ROOT/'evaluation'/folder/'decision.json'),report=str(ROOT/'evaluation'/folder/'REPORT.md')) for name,folder in history_rounds.items() if (ROOT/'evaluation'/folder/'summary.json').exists()}
patch12_decision=read(ROOT/'evaluation/history_attribute_20261022_r4_candidate_p12/decision.json')
if patch12_decision and patch12_decision.get('state')=='rejected_restore_patch9':
    status['active_code']='patch9_restored_after_rejected_patch12'
    status['active_unit_tests']=193
    status['context_revision']['state']='patch9_full479_semantic_review_complete'
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## History diagnostics: patches11 and12 rejected\n\n')
        f.write('Last accepted patch9 remains450/479 development and87/100 legacy regression. Four-condition baseline217/224 comes from correlated r2+r3 scenarios, not224 independent questions. Patch11 fixed5 but regressed2; patch12 fixed3 but regressed9 and was restored. Explicit naming alone and attribute-only ranking do not ensure applicable evidence. General technical advice still substitutes for known SKU facts. Prior model answers remain untrusted input, never knowledge/training. No source/model/data changes or new validation. See CURRENT.md and individual diagnostic reports.\n')
patch13_decision=read(ROOT/'evaluation/history_source_20261022_r5_candidate_p13/decision.json')
if patch13_decision and patch13_decision.get('state')=='rejected_restore_patch9':
    status['active_code']='patch9_restored_after_rejected_patch13'
    status['active_unit_tests']=193
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch13 rejected; raw model-call diagnosis\n\n')
        f.write('Source-envelope trial206/224 versus217/224,1fix/12regressions, restoredpatch9. Diagnostic6known controls:4PASS/2FAIL, all6 outputs identical to baseline. All requested kit facts and legal IDs are present in selector requests, but two choose general advice with missing=[]. Prompt tokens1507–3262 under6144, all12 calls stop normally; no context/output exhaustion observed in these calls, no cache bug established. Activepatch9 scores unchanged; details in history_payload_20261022_r6/REPORT.md.\n')
patch14_summary=read(ROOT/'evaluation/history_staged_20261022_r7_candidate_p14/summary.json')
if patch14_summary:
    status['current_candidate']=dict(name='patch14',state='focused_pass_pending_old100_and_full479',summary=patch14_summary,production_accepted=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch14 focused trial; broader regression pending\n\n')
        f.write('Staged product evidence reading:217→221PASS/224 same-input diagnostic scenarios,4fixes/0regressions, secondary cases28→8. This is68questiontexts/178question-profileinputs, not independent accuracy. No fallback was needed among149product-first reads, so caveat/missing-attribute risk remains.198tests passed. Old100 then full479 required on same code before acceptance. Last acceptedpatch9 scores remain450/479 and87/100.\n')
patch14_regression=read(BASE/'old100_patch14/summary.json')
patch14_decision=read(BASE/'old100_patch14/decision.json')
if patch14_decision and patch14_decision.get('state')=='rejected_restore_patch9':
    status['active_code']='patch9_restored_after_rejected_patch14'
    status['active_unit_tests']=193
    status['patch14_regression']=patch14_regression
    status['current_candidate']=dict(name='patch14',state='rejected_restore_patch9',production_accepted=False,decision=patch14_decision)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Patch14 rejected after old100; judge probe insufficient\n\n')
        f.write('Legacy10087→85, C31unknown thread-count answer and C34regional soldered-RAM scope regress. Focused224 gain did not survive; restoredpatch9 with193tests passed. No full479 on rejected code. Whole-answer relevance judge agrees5/6 on selected controls but falsely accepts missing-thread answer; no production verifier installed. Last accepted scores450/479 and87/100 unchanged. See old100_patch14/REPORT.md and relevance_probe_20261022_r8/REPORT.md.\n')
part_probe=read(ROOT/'evaluation/part_relevance_20261022_r10/summary.json')
if part_probe:
    status['latest_qa_diagnostic']=dict(name='part_relevance_r10',summary=part_probe,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Required part-level judge: still insufficient\n\n')
        f.write('31development/constructed scenarios,57manually labeled parts:50/57part agreement and26/31exact cases. Six false-accepted parts/four cases and one false-rejected valid unknown. Model often treats a fact available in source as if candidate answer said it. No production verifier installed or gold changed after inference; acceptedpatch9 scores unchanged. R9 prepared/unqueried, r10corrects two part phrasings before inference. See part_relevance_20261022_r10/REPORT.md.\n')
answer_support=read(ROOT/'evaluation/answer_support_20261022_r11/summary.json')
if answer_support:
    status['latest_qa_diagnostic']=dict(name='answer_support_r11',summary=answer_support,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Candidate-answer quote diagnostic r11; production unchanged\n\nSame31r10 inputs/gold,57parts. Raw51/57 and27/31exact cases; membership-guarded56/57 and30/31. Guard catches6source-only false approvals, but rejects one acceptable ECC answer because the judge quotes only its source. Generic-but-literal MacBook quotes and numeric-prefix quote show membership is not semantic sufficiency. No production verifier installed; broader frozen confirmation required. Total126.732s/median3.515s versus r10 96.822s/2.546s, no controlled speed claim. Acceptedpatch9 still450/479 and87/100. See answer_support_20261022_r11/REPORT.md.\n')
broader_support=read(ROOT/'evaluation/answer_support_20261022_r12/summary.json')
if broader_support:
    status['latest_qa_diagnostic']=dict(name='answer_support_r12',summary=broader_support,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Broader r12 confirmation: combined judge rejected\n\n44new scenarios/22texts/68parts: raw45/68,20falseaccept/3falsereject; candidatequote-membership guard53/68,3falseaccept/12falsereject. Guard removes17bad approvals but introduces9false rejections. Literal-but-insufficient OLED clause and swapped plan/actual values survive. Fiveof8validunknownparts rejected; correct table/implicit/typography also fail. No production gate installed or gold changed. Acceptedpatch9 unchanged450/479,87/100,193tests. Details answer_support_20261022_r12/REPORT.md.\n')
coverage_probe=read(ROOT/'evaluation/coverage_20261022_r13/summary.json')
if coverage_probe:
    status['latest_qa_diagnostic']=dict(name='coverage_r13',summary=coverage_probe,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Candidate-only coverage r13; still no production gate\n\nSame44r12candidates, new coverage labels distinct from source-support correctness. Raw45/68three-state, guarded56/68and35/44exact. Sevenfalsecovered from generic answers mislabeled explicitunknown and2missedcovered from missing IDs for realunknowns. IDs all exist but do not establish relevance. No factual verification or accepted chatbot gain; patch9 still450/479,87/100,193tests lastpassed. Details coverage_20261022_r13/REPORT.md.\n')
product_coverage=read(ROOT/'evaluation/coverage_20261022_r14/summary.json')
if product_coverage:
    status['latest_qa_diagnostic']=dict(name='coverage_r14',summary=product_coverage,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## R14 product confirmation rejects answered-only gate\n\n112distinctpayloads/56profiles/12questiontexts. Substantivecoverage54correctanswered/36correctnotanswered/22falseanswered/0missedanswered; no sourcebodies and allfalseapprovedIDsvalid. CPUmodel/corecount andwatts/efficiency mismatchpersists. Preregisteredthreshold failed broaderconfirmation; no productiongate installed, patch9unchanged450/479,87/100,193tests lastpassed. Details coverage_20261022_r14/REPORT.md.\n')
field_intent=read(ROOT/'evaluation/field_intent_20261023_r15/summary.json')
if field_intent:
    status['latest_qa_diagnostic']=dict(name='field_intent_r15',summary=field_intent,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Requested-field intent r15; no productionshortcut\n\nRegistry62actualcatalogkeys, no candidate/sourcevalues. Exactintent68/91,17/17CPUcoreintentsright but11invalidcontracts,4unsafe shortcuts and fieldmismatches/extras. Product40/56,fallback25/30,compound3/5. Scope/unknown risks prevent integration; acceptedpatch9unchanged450/479,87/100,193tests lastpassed. See field_intent_20261023_r15/REPORT.md.\n')
part_field_intent=read(ROOT/'evaluation/field_intent_20261023_r16/summary.json')
if part_field_intent:
    status['latest_qa_diagnostic']=dict(name='field_intent_r16',summary=part_field_intent,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## R16 per-part intent: scope regressions prevent acceptance\n\nSame91gold68→79exact,16fixes/5regressions; invalidcontracts11→0 butunsafe4→7. Product52/56,fallback23/30,compound4/5. Requiredpartkeys stillmisbindthreads/USB-C/regionandnowprinciples. No productionshortcut; acceptedpatch9unchanged450/479,87/100,193tests lastpassed. Read-onlyexistingnominal4BQwen3.5alias inventory recorded, no modelchange/inference. See field_intent_20261023_r16/REPORT.md.\n')
model_comparison=read(ROOT/'evaluation/field_intent_20261023_r17_qwen35/summary.json')
if model_comparison:
    status['latest_qa_diagnostic']=dict(name='field_intent_r17_qwen35',summary=model_comparison,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## Qwen3.5 comparison blocked by runtimegrammar\n\n91planned,3HTTP500attempts,88pending,0semanticresults; runnerstopped. Actualqwen35loadedctx6144, runtime Unexpectedemptygrammarstack error observed. Do notscoreinfra asFAIL orresume unchanged; minimaldecodingcompatibilityprobe needed. Productioncode/configunchanged, lastacceptedpatch9results450/479,87/100,193tests. See field_intent_20261023_r17_qwen35/REPORT.md.\n')
decoder_compat=read(ROOT/'evaluation/decoding_compat_20261023_r18/summary.json')
if decoder_compat:
    status['latest_qa_diagnostic']=dict(name='decoder_compat_r18',summary=decoder_compat,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## R18 decoder probe: no safe schema-bypass workaround\n\nSchema500,JSONobject500,noformat200but300repeated8digits/lengthstop;0validcontracts,0semanticresults. RawHTTPerrorbodies preserved; cachedrunnerconfound/rootcauseunresolved. No productionconfig/codechange, lastaccepted450/479,87/100,193tests. Nextfreshstate/backend/samplingcanary,notfull91. See decoding_compat_20261023_r18/REPORT.md.\n')
canary_prepared=read(ROOT/'evaluation/runtime_canary_20261023_r19/summary.json')
if canary_prepared:
    status['latest_qa_diagnostic']=dict(name='runtime_canary_r19_prepared',summary=canary_prepared,production_installed=False)
    with (BASE/'REPORT.md').open('a',encoding='utf8') as f:
        f.write('\n## R19 prepared; automatic execution review rejected launch\n\nThree bounded canaries frozen/offlinechecked, attempted0. Combined command containing checks/docs/backgroundlaunch rejected with blocked by policy, no specific reason. No retry/split to bypass review; no model unload/inference/config change. Productionpatch9 unchanged450/479,87/100,193tests lastpassed. See runtime_canary_20261023_r19/REPORT.md.\n')
(BASE/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in status.items() if k not in ['patch2_targeted','assessment_600']},ensure_ascii=False))
