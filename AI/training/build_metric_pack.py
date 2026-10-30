"""Metric tutoring data: disjoint wording families, counterfactual context, no money."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.metric_contract import LABELS,metric_text,BASE_MODEL,BASE_REVISION,CONTRACT_VERSION

FRAMES={
 'train':[
  'Xếp hạng {cat} theo {term} {period}.',
  'Top 3 {cat} tính theo {term} trong {period}.',
  '{cat} nào có {term} cao nhất {period}?',
  'Sắp các mã {cat} theo {term}, kỳ {period}.',
  'Lấy ba {cat} dẫn đầu về {term} {period}.',
  'Đánh giá nhóm {cat} bằng {term} {period}.',
  'Bảng {cat} {period}, chỉ tiêu cần xem là {term}.',
  'Cho tôi thứ hạng {cat} dựa trên {term} {period}.'],
 'validation':[
  'Nếu lấy {term} làm thước đo, {cat} nào đứng đầu {period}?',
  'Tìm nhóm {cat} nổi bật về {term} ở {period}.',
  'Kết quả của {cat} xét riêng {term} cho {period} ra sao?'],
 'test':[
  'Mức {term} của {cat} trong {period}, mã nào dẫn bảng?',
  'Tau muốn lấy {term} để phân thứ tự {cat} cho {period}.',
  'Trong đợt {period}, xét {term} thì {cat} nào hơn các mã khác?']}

TERMS={
 'revenue':{
  'train':['doanh thu','doanh số','tiền bán hàng','giá trị bán ra','tổng tiền thu từ bán hàng','doanh số tính bằng tiền','doanh thu thuần','số tiền khách trả'],
  'validation':['doanh số bằng VND','tiền hàng bán được','tiền thu bán hàng'],
  'test':['doanh số tiền','số đồng thu về từ hàng bán','giá trị doanh thu sau hoàn trả']},
 'units':{
  'train':['số lượng','số chiếc bán được','lượng hàng bán ròng','số món đã bán','số sản phẩm được mua','doanh số tính theo số chiếc','lượng tiêu thụ tính bằng cái','số đơn vị hàng bán'],
  'validation':['số cái bán ra','doanh số đo bằng chiếc','lượng sản phẩm tiêu thụ'],
  'test':['số lượng bán sau hoàn hàng','bao nhiêu chiếc được bán','lượng món hàng khách đã mua']},
 'gross_profit':{
  'train':['lợi nhuận gộp','lãi gộp','tiền lãi trước chi phí vận hành','doanh thu trừ giá vốn','lãi bán hàng trước chi phí hoạt động','số tiền lợi nhuận gộp','lãi gộp sau hoàn trả','chênh lệch doanh thu và giá vốn'],
  'validation':['phần doanh thu còn lại sau giá vốn','tiền lời gộp','lợi nhuận trước trừ chi phí hoạt động'],
  'test':['số lãi gộp tính bằng đồng','tiền bán trừ chi phí vốn hàng đã bán','lời gộp trước phí vận hành']},
 'operating_profit':{
  'train':['lợi nhuận hoạt động trước lãi vay và thuế','lãi sau giá vốn và chi phí vận hành, trước thuế và lãi vay','lợi nhuận sau chi phí hoạt động nhưng chưa tính lãi vay hay thuế','lãi hoạt động chưa trừ thuế và lãi vay','doanh thu trừ giá vốn và chi phí vận hành trước lãi vay, thuế','kết quả hoạt động kinh doanh trước lãi vay và thuế','lợi nhuận vận hành trước lãi vay và thuế','tiền lời sau phí vận hành nhưng trước thuế và lãi vay'],
  'validation':['lời sau vận hành nhưng chưa tính thuế và lãi vay','lợi nhuận đã trừ phí hoạt động, chưa trừ lãi vay và thuế','tiền lãi trước thuế và lãi vay nhưng đã trừ chi phí hoạt động'],
  'test':['lợi nhuận hoạt động đã trừ giá vốn và vận hành, chưa tính lãi vay hoặc thuế','tiền còn sau giá vốn, phí vận hành, trước thuế và lãi vay','lời vận hành chưa khấu trừ lãi vay, thuế']}}

FOLLOW={
 'train':['Giữ tiêu chí ấy, lùi một tháng.','Cùng bảng đó nhưng tháng 6/2026.','Vẫn như vừa rồi, chuyển sang quý trước.','Không đổi cách xếp, chỉ xem tháng 5/2026.','Lấy kỳ trước đó và giữ nguyên chỉ số.','Còn tháng 8 thì sao, vẫn cùng tiêu chí?','Dùng đúng tiêu chí cũ cho kỳ mới.','Bảng như trên, đổi kỳ thôi.','Giữ cách tính ấy giúp tau.','Lùi lại một quý, không đổi tiêu chí.'],
 'validation':['Tương tự kết quả vừa xem, chỉ chuyển kỳ.','Đừng thay thước đo, lấy tháng 7 nhé.','Tiếp tục dùng cách xếp ban nãy.'],
 'test':['Y chang bảng mới rồi nhưng cho kỳ liền trước.','Thước đo đã chọn giữ y nguyên, đổi sang tháng 4.','Vẫn đo như lúc trước, chỉ cần lùi thời gian.']}

NEGATIVES={
 'train':['Laptop này dùng CPU nào?','Màn hình OLED có đẹp không?','Giá bán máy này bao nhiêu?','Chính sách bảo hành thế nào?','Giá vốn sản phẩm này là gì?','Đếm số đơn hàng của cả shop.','Tổng tiền hoàn cho khách.','Biên lợi nhuận gộp bao nhiêu phần trăm?','Tính lãi ròng sau thuế.','Ngân sách marketing của quý này.','Phí giao hàng mấy đồng?','Chọn máy RAM 16 GB.','Top 3 mặt hàng giúp tôi.','So sánh hai kỳ giúp tôi.','Tôi cần một bảng xếp hạng.','Vẽ sơ đồ báo cáo.'],
 'validation':['Máy có nặng hai ký không?','Quy định trả góp áp dụng thế nào?','Xếp hàng trong tháng này cho tôi.','Tỉ lệ lãi gộp trên doanh thu là mấy phần trăm?','Tiền mua hàng nhập kho là bao nhiêu?'],
 'test':['Bộ xử lý con máy đó là dòng gì?','Kho còn bao nhiêu chiếc?','Cho tôi bảng hạng trong quý ấy.','Điều kiện đổi hàng ra sao?','Hỏi lợi nhuận ròng sau tất cả thuế và lãi vay.']}

AMBIGUOUS={
 'train':['Xếp theo doanh thu hay số lượng nhỉ?','Doanh thu với lãi gộp, lấy cái nào để xếp?','Tôi chưa chọn được chỉ tiêu để so sánh.','Xếp theo tiền hay theo số chiếc cũng được, chưa chốt.','Cho kết quả theo chỉ tiêu đó ấy.','Cách tính thứ nhất hay thứ hai, chưa rõ.'],
 'validation':['Lấy doanh số tiền hay số cái bán ra?','Giữa lãi gộp và tiền bán, tôi chưa chốt tiêu chí.'],
 'test':['Xếp theo tiền thu hoặc số món, chọn cách nào?','Doanh thu với số chiếc, tau chưa biết lấy chỉ số nào.']}

CORRECTIONS={
 'train':['Đừng dùng {old} nữa; chuyển tiêu chí sang {new}.','Tôi sửa chỉ số: {new}, thay vì {old}.','Không phải {old}; bảng này phải dựa vào {new}.','Ý tau là {new}, không phải {old}.'],
 'validation':['Thước đo cần sửa từ {old} qua {new}.','Cái cần là {new}; bỏ tiêu chí {old}.'],
 'test':['Tau nói lại: xét {new} chứ đừng xét {old}.','Đính chính bảng hạng: lấy {new}, loại cách tính theo {old}.']}

def build():
    out=ROOT/'training/metric_v4';data=out/'data';data.mkdir(parents=True,exist_ok=True)
    rng=random.Random(202610194);rows=[];seen={}
    def add(question,label,split,family,has_metric=False,intent='top_products'):
        memory={'active_intent':intent,'active_metric':'revenue' if has_metric else 'unknown'}
        text=metric_text(question,memory,intent)
        key=hashlib.sha256(text.encode()).hexdigest()
        if key in seen:
            prior=seen[key]
            assert prior['label']==label and prior['split']==split,('Conflicting/overlapping normalized feature text',question)
            return
        row=dict(id=f'M4-{len(rows):05d}',question=question,memory=memory,intent=intent,text=text,label=label,
                 split=split,group_id=split+':'+family,label_origin='authored_metric_semantics_and_explicit_context_contract')
        rows.append(row);seen[key]=row
    for split in FRAMES:
        cats=['laptop','chuột','linh kiện'] if split=='train' else ['màn hình','SSD']
        periods=['tháng 7/2026','quý 2 năm 2026']
        for metric,terms in TERMS.items():
            for fi,frame in enumerate(FRAMES[split]):
                for ti,term in enumerate(terms[split]):
                    for cat in cats:
                        for period in periods:
                            for has_metric in (False,True):
                                add(frame.format(cat=cat,term=term,period=period),metric,split,f'frame-{fi}:term-{metric}-{ti}',has_metric)
            for fi,frame in enumerate(CORRECTIONS[split]):
                for other in TERMS:
                    if other==metric: continue
                    for ti,term in enumerate(terms[split]):
                        old=TERMS[other][split][ti%len(TERMS[other][split])]
                        add(frame.format(old=old,new=term),metric,split,f'correction-{fi}:term-{metric}-{ti}',True)
        for i,q in enumerate(FOLLOW[split]):
            add(q,'inherit',split,'follow-'+str(i),True)
            add(q,'clarify',split,'follow-'+str(i),False)
        for i,q in enumerate(NEGATIVES[split]):
            for known in (False,True): add(q,'unspecified',split,'negative-'+str(i),known)
        for i,q in enumerate(AMBIGUOUS[split]):
            for known in (False,True): add(q,'clarify',split,'ambiguous-'+str(i),known)
    # Every representation is unique across all splits, not just raw questions.
    assert len({r['text'] for r in rows})==len(rows)
    for split in FRAMES:
        subset=[r for r in rows if r['split']==split];rng.shuffle(subset)
        assert set(r['label'] for r in subset)==set(LABELS)
        (data/f'{split}.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in subset),encoding='utf8')
    manifest=dict(version=CONTRACT_VERSION,base_model=BASE_MODEL,base_revision=BASE_REVISION,labels=LABELS,
        samples=len(rows),splits=dict(Counter(r['split'] for r in rows)),
        per_split_labels={s:dict(Counter(r['label'] for r in rows if r['split']==s)) for s in FRAMES},
        family_counts={s:len({r['group_id'] for r in rows if r['split']==s}) for s in FRAMES},
        input_contract_sha256=hashlib.sha256((ROOT/'shopbot/metric_contract.py').read_bytes()).hexdigest(),
        monetary_convention='Doanh so means money unless an explicit unit such as chiec/cai overrides it.',
        training_scope='Metric decision only. No intent routing, SQL, product facts or monetary totals in weights.',
        split_policy='Separate frames, term phrases and correction wording before expansion. No normalized feature text overlaps.',
        limitations=['Synthetic authored data; family expansion is not independent customer conversations.',
                    'Old 106 and added 12 are development regression banks already seen; require additional unseen wording evaluation.',
                    'Ambiguous financial definitions must be reviewed, not converted into fabricated labels from failed model replies.'])
    (data/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(manifest,ensure_ascii=True))

if __name__=='__main__':build()
