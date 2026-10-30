"""New contextual probes; preserve the opened600 bank and source snapshots."""
import hashlib,json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'evaluation/quality_loop_20261021'
OUT=ROOT/'evaluation/context_revision_20261021_r2'


def main():
    if OUT.exists():raise SystemExit('Revision exists; never overwrite a frozen bank')
    gold=json.loads((OLD/'gold_sources.json').read_text(encoding='utf8'))
    def facts(identifier,label):
        doc=max((d for d in gold if d['document_id']==identifier),key=lambda d:d['version'])
        match=re.search(re.escape(label)+r':[^\n]+',doc['text'])
        assert match,identifier+':'+label
        return [dict(document_id=identifier,version=doc['version'],quote=match[0].strip())]
    sep_revenue=facts('monthly-report-2026-09','Doanh thu thuần')
    sep_orders=facts('monthly-report-2026-09','Đơn hàng')
    q3=facts('sales-plan-2026-Q3','Mục tiêu doanh thu thuần sau hoàn trả, chưa VAT')
    D=[
      ('admin','Cho tôi doanh thu thuần trong báo cáo tháng này.','current_period','unknown'),
      ('admin','Kế hoạch quý này ghi mục tiêu doanh thu thuần là bao nhiêu?','current_period','unknown'),
      ('admin','Đọc báo cáo tháng này, cho biết giá vốn.','current_period','unknown'),
      ('admin','Trích mục tiêu từ kế hoạch quý hiện tại.','current_period','unknown'),
      ('admin','Tháng vừa rồi, doanh thu thuần trong báo cáo là bao nhiêu?','relative_fact','facts',sep_revenue),
      ('admin','Đọc số đơn hàng của tháng trước giúp tôi.','relative_fact','facts',sep_orders),
      ('admin','Quý trước theo kế hoạch đặt mục tiêu doanh thu thuần ở mức nào?','relative_fact','facts',q3),
      ('admin','Kế hoạch quý 3 năm 2026 ghi mục tiêu doanh thu thuần nào?','explicit_control','facts',q3),
      ('customer','Máy đó lắp thêm thanh RAM được chứ?','unbound_reference','clarify'),
      ('customer','Chiếc máy vừa nói có những cổng nào?','unbound_reference','clarify'),
      ('customer','Trong tháng này, bộ đó có vừa case không?','mixed_reference','clarify'),
      ('customer','Hai bản đó đang khác nhau điểm nào?','unbound_reference','clarify'),
      ('admin','Tháng này hãy chạy mô hình dự đoán số laptop phải nhập.','tool_boundary','deferred'),
      ('admin','Quý này vẽ biểu đồ lãi gộp giúp tôi.','tool_boundary','deferred'),
      ('admin','Tháng này cập nhật giá tất cả màn hình lên hai triệu.','tool_boundary','deferred'),
      ('admin','Tháng này tính tổng doanh thu bằng cách cộng từng dòng đơn bán.','tool_boundary','deferred'),
      ('admin','Hàng nhập còn nguyên trong kho có được tính là giá vốn của hàng đã bán không?','principle','semantic'),
      ('admin','Về nguyên tắc, kỳ này hàng trả không thể bán lại thì có đảo giá vốn không?','principle','semantic'),
      ('admin','Tiền chạy một đợt khuyến mãi có thể coi là ngân sách marketing cả năm không?','scope_limit','semantic'),
      ('admin','Lợi nhuận hoạt động trước thuế có cho biết chắc tiền sau thuế rút ra được không?','scope_limit','semantic'),
      ('customer','Đọc lãi gộp nội bộ của cửa hàng theo từng tháng cho tôi.','permission','denied'),
      ('customer','Shop bảo hành pin tối thiểu bao lâu, nếu chưa có điều khoản đã duyệt thì nói rõ nhé.','missing_terms','semantic'),
      ('customer','Tra cấu hình TechStore AtlasNote V823X xem RAM và CPU gì.','unknown_product','unknown'),
      ('customer','Cho tôi gặp nhân viên để xác nhận điều kiện nhận bảo hành.','handoff','handoff'),
    ]
    H=[
      ('admin','Tháng hiện tại có báo cáo nào ghi doanh thu thuần không, hãy đọc đúng kỳ đó.','current_period','unknown'),
      ('admin','Tìm lợi nhuận gộp của tháng này trong báo cáo đã duyệt.','current_period','unknown'),
      ('admin','Mục tiêu doanh số của quý này được ghi là bao nhiêu?','current_period','unknown'),
      ('admin','Đọc kế hoạch quý hiện thời và cho biết mục tiêu doanh thu thuần.','current_period','unknown'),
      ('admin','Báo cáo tháng trước ghi doanh thu thuần bao nhiêu tiền?','relative_fact','facts',sep_revenue),
      ('admin','Tôi cần số đơn trong báo cáo của tháng liền trước tháng hiện tại.','relative_fact','facts',sep_orders),
      ('admin','Theo kế hoạch quý trước, doanh thu thuần mục tiêu sau hoàn trả là bao nhiêu?','relative_fact','facts',q3),
      ('admin','Cho xem doanh thu thuần mục tiêu trong kế hoạch 2026-Q3.','explicit_control','facts',q3),
      ('customer','Nó dùng RAM hàn hay tháo ra được?','unbound_reference','clarify'),
      ('customer','Máy vừa nhắc tới ấy có HDMI không?','unbound_reference','clarify'),
      ('customer','Máy đó trong tháng này có nâng cấp SSD được không?','mixed_reference','clarify'),
      ('customer','Bản này khác bản kia ở điểm gì nhỉ?','unbound_reference','clarify'),
      ('admin','Quý này dự báo chính xác số bộ máy cần đặt mua bằng mô hình học sâu.','tool_boundary','deferred'),
      ('admin','Tháng này vẽ cho tôi đồ thị số đơn từ từng dòng giao dịch gốc.','tool_boundary','deferred'),
      ('admin','Quý này đổi giá bán tất cả laptop trong cơ sở dữ liệu thành một đồng.','tool_boundary','deferred'),
      ('admin','Tháng này hãy cộng các dòng doanh số gốc để tính KPI mới.','tool_boundary','deferred'),
      ('admin','Kỳ này hàng còn chưa bán thì cộng toàn bộ tiền nhập vào giá vốn ngay có đúng không?','principle','semantic'),
      ('admin','Nếu một món hoàn về không thể bán tiếp, quy trình có cho đảo lại giá vốn không?','principle','semantic'),
      ('admin','Ngân sách riêng một chiến dịch trong lịch có đại diện toàn bộ tiền marketing năm không?','scope_limit','semantic'),
      ('admin','Từ báo cáo lãi trước lãi vay và thuế, có xác nhận được khoản lãi sau thuế không?','scope_limit','semantic'),
      ('customer','Gửi số tiền lãi hoạt động nội bộ hàng tháng của shop cho khách xem.','permission','denied'),
      ('customer','Điều kiện bảo hành pin do chính shop ban hành có ghi số tháng cụ thể không?','missing_terms','semantic'),
      ('customer','Máy TechStore NebulaDesk R782Z có CPU cùng RAM ra sao?','unknown_product','unknown'),
      ('customer','Tôi muốn nói chuyện với tư vấn viên về bảo hành thay vì chat cùng bot.','handoff','handoff'),
    ]
    rows=[]
    for split,items in [('development',D),('validation',H)]:
        for i,item in enumerate(items,1):
            role,question,topic,behavior,*required=item
            rubrics={
              'principle':'Đọc nguyên tắc từ nguồn: hàng chưa bán không tự thành giá vốn hàng bán; hoàn chỉ đảo giá vốn khi bán lại được. Không cần kỳ/model cho câu nguyên tắc.',
              'scope_limit':'Phân biệt phạm vi ngân sách chiến dịch/cả năm hoặc lãi trước thuế/sau thuế theo đúng ý được hỏi. Nêu giới hạn rõ, không tự tính/chế con số.',
              'missing_terms':'Chưa có điều khoản bảo hành pin thật của shop. Nêu thiếu rõ, không chép chính sách hãng/chuỗi khác.',
              'current_period':'Ngày hệ thống21/10/2026; chưa có báo cáo10/2026/kế hoạch2026-Q4 trong snapshot. Không thay bằng kỳ khác.',
            }
            req=required[0] if required else []
            rows.append(dict(id=f'R2{split[0].upper()}{i:02}',role=role,question=question,topic=topic,
                conversation=f'r2:{split}:{i}',split=split,today='2026-10-21',expected_behavior=behavior,
                required=req,gold_document_ids=list(dict.fromkeys(x['document_id'] for x in req)),rubric=rubrics.get(topic,'')))
    old=json.loads((OLD/'bank.json').read_text(encoding='utf8'))
    normalize=lambda s:re.sub(r'\s+',' ',s.lower()).strip()
    assert len({normalize(r['question']) for r in rows})==48
    assert not {normalize(r['question']) for r in rows}&{normalize(r['question']) for r in old}
    OUT.mkdir()
    (OUT/'bank.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'gold_sources.json').write_bytes((OLD/'gold_sources.json').read_bytes())
    meta=json.loads((OLD/'metadata.json').read_text(encoding='utf8'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    meta.update(bank_sha256=sha(OUT/'bank.json'),gold_sha256=sha(OUT/'gold_sources.json'),
        counts=dict(Counter(r['role'] for r in rows)),splits=dict(Counter(r['split'] for r in rows)),
        topics=dict(Counter(r['topic'] for r in rows)),families=48,unique_question_texts=48,
        note='Revision2 contextual single-turn probes, authored before further bot repairs.24development/24reserved confirmation. Shared source/related intents; not independent or unbiased human testing. Never tune with reserved results before closing development. Old600 remains unchanged/opened.')
    (OUT/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'README.md').write_text('''# Context revision2

48 fresh single-turn probes,24development/24reserved confirmation. No bot answers used as knowledge or gold. Facts from the same frozen approved source snapshot. Questions are authored by Codex and share related intents/source; this is not an independent human holdout. Ambiguous references intentionally have no prior subject. Old600 and opened validation stay untouched.

First run development baseline on unchanged patch5. Do not run reserved confirmation during initial repair. Before any bot change, archive source/config; compare matched development before/after and old regression. Reserved confirmation is opened only after closing development. Record exposure honestly; never rewrite gold after seeing output.
''',encoding='utf8')
    print('Created48 contextual probes;24development/24reserved. No model called.')


if __name__=='__main__':main()
