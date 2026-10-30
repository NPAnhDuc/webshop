"""Vietnamese multi-turn understanding data, split by wording family before expansion."""
from collections import Counter
import json
from pathlib import Path
import random
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
sys.path.insert(0,str(ROOT))
from shopbot.conversation import INTENTS,TIME_MODES,METRICS


def input_text(question,memory,today='2026-10-19'):
    # Keep current utterance first, avoiding truncating it behind a long history.
    recent=memory.get('history',[])[-2:]
    return ('Câu hiện tại: '+question+'\nNgày hiện tại: '+today+
            '\nNgữ cảnh đã xác nhận: '+json.dumps({k:v for k,v in memory.items() if k!='history'},ensure_ascii=False)+
            '\nHội thoại gần nhất: '+json.dumps(recent,ensure_ascii=False))


def build():
    folder=HERE/'conversation_v3';data=folder/'data';data.mkdir(parents=True,exist_ok=True)
    rng=random.Random(20261019);rows=[]
    temporal=[('tháng 9 năm 2026','explicit','month'),('tháng 12 năm 2025','explicit','month'),
              ('quý 3 năm 2026','explicit','quarter'),('năm 2025','explicit','year'),
              ('tháng trước','last_month','month'),('quý trước','last_quarter','quarter'),
              ('tháng này','current_month','month'),('năm nay','current_year','year'),
              ('quý này','current_quarter','quarter'),('năm ngoái','last_year','year')]
    templates={
        'top_products':[
            'Sản phẩm nào bán nhiều nhất trong {period}?','Cho xem mặt hàng dẫn đầu {period}.',
            'Top mã bán chạy {period} là những mã nào?','Trong {period}, shop bán chạy nhất mặt hàng gì?',
            'Xếp hạng sản phẩm theo số lượng bán {period}.','Liệt kê hàng bán tốt {period} giúp tôi.',
            'Mã hàng nào có lượng tiêu thụ cao nhất {period}?','Hàng nào khách mua nhiều nhất {period}?',
            'Tìm sản phẩm đứng đầu số lượng {period}.','Bán chạy nhất {period} là con nào?',
            'Trong kỳ {period}, mặt hàng nào được mua nhiều?','Tôi cần biết món bán chạy nhất {period}.'],
        'revenue':[
            'Doanh thu {period} bao nhiêu?','Shop thu được bao nhiêu tiền bán hàng {period}?',
            'Tổng doanh số tiền {period} là bao nhiêu?','Tính tổng doanh thu {period}.',
            'Cho số doanh thu {period}.','Kết quả thu tiền từ bán hàng {period} thế nào?',
            'Cộng doanh thu {period} giúp tôi.','Lấy số tiền doanh thu {period}.',
            'Tôi muốn tra doanh thu {period}.','Cho biết doanh thu bán hàng của {period}.',
            'Doanh thu cửa hàng {period} đạt mức nào?','Tổng doanh thu bán hàng {period}?'],
        'business_analysis':[
            'Phân tích lời lỗ {period}.','Lợi nhuận gộp {period} được bao nhiêu?',
            'Báo cáo chi phí và kết quả {period}.','Đánh giá biên lợi nhuận {period}.',
            'Giá vốn {period} hết bao nhiêu?','Vẽ biểu đồ kinh doanh {period}.',
            'Xuất ảnh báo cáo {period}.','Cho báo cáo tài chính quản trị {period}.',
            'Tính lời trước lãi vay và thuế {period}.','Vẽ sơ đồ lời lỗ {period}.',
            'Tôi muốn phân tích hoạt động {period}.','Tổng chi phí hoạt động {period} là bao nhiêu?']}
    def add(question,memory,labels,group,split):
        rows.append(dict(id=f'C3-{len(rows):05d}',text=input_text(question,memory),question=question,memory=memory,
                         today='2026-10-19',labels=labels,group_id=group,split=split,label_origin='authored_semantic_template_plus_calendar_fixture'))
    def split_of(i): return 'train' if i<8 else 'validation' if i<10 else 'test'
    for intent,patterns in templates.items():
        for i,pattern in enumerate(patterns):
            split=split_of(i)
            for phrase,mode,unit in temporal:
                metric='units' if intent=='top_products' else 'revenue' if intent=='revenue' else ('gross_profit' if i==1 else 'operating_profit' if i==8 else 'unknown')
                for prior_month in (2,7,9):
                    memory={'active_period':{'start':f'2026-{prior_month:02d}-01','end':f'2026-{prior_month+1:02d}-01','unit':'month','label':f'2026-{prior_month:02d}'},
                            'active_intent':'revenue','active_metric':'revenue',
                            'history':[{'question':f'Doanh thu tháng {prior_month} năm 2026','answer':'Đã lấy dữ liệu SQL cho kỳ này.'}]}
                    add(pattern.format(period=phrase),memory,dict(intent=intent,time_mode=mode,metric=metric,period_unit=unit),intent+':'+str(i),split)
            if intent=='top_products':
                for metric,phrase in [('revenue','doanh thu'),('gross_profit','lợi nhuận gộp')]:
                    for period,mode,unit in temporal:
                        add(f'Xếp hạng theo {phrase}: '+pattern.format(period=period),{},dict(intent=intent,time_mode=mode,metric=metric,period_unit=unit),intent+':'+str(i),split)
    followups=['Tháng đó sản phẩm nào bán chạy nhất?','Trong tháng ấy hàng nào bán tốt?',
               'Cùng kỳ đó, mã hàng nào được mua nhiều?','Ở tháng đang nói, sản phẩm nào dẫn đầu?',
               'Vậy mặt hàng bán chạy trong tháng đó?','Xem giúp món nào bán nhiều trong kỳ đó.',
               'Sản phẩm bán chạy nhất tháng đó là gì?','Ở kỳ đang xem, hàng nào bán chạy?',
               'Tìm mặt hàng bán chạy trong tháng vừa nói.','Tháng vừa xem thì sản phẩm nào bán chạy?',
               'tháng đó sản phẩm nào bán chạy nhất','Trong thời gian ấy món nào bán chạy vậy?']
    for i,q in enumerate(followups):
        for month in range(1,13):
            year=2025 if month>=10 else 2026
            end=f'{year+1}-01-01' if month==12 else f'{year}-{month+1:02d}-01'
            memory={'active_period':dict(start=f'{year}-{month:02d}-01',end=end,unit='month',label=f'{year}-{month:02d}'),
                    'active_intent':'revenue','history':[{'question':f'Doanh thu tháng {month} năm {year}','answer':'Đã xem kỳ được yêu cầu.'}]}
            add(q,memory,dict(intent='top_products',time_mode='same_period',metric='units',period_unit='month'),'followup:'+str(i),split_of(i))
        add(q,{},dict(intent='clarify',time_mode='same_period',metric='units',period_unit='month'),'followup:'+str(i),split_of(i))
    corrections=['Theo doanh thu cơ.','Không, xếp bằng doanh thu.','Đổi sang doanh thu nhé.',
                 'Lấy doanh thu thay vì số lượng.','Cho xếp theo tiền bán.','Tôi muốn xem theo doanh thu.',
                 'Sắp theo doanh thu đi.','Theo doanh thu chứ.','Còn nếu tính doanh thu?',
                 'Chuyển tiêu chí sang doanh thu.','Đang nói thứ hạng theo doanh thu nhé.','Doanh thu mới là tiêu chí tôi muốn.']
    for i,q in enumerate(corrections):
        for month in range(1,10):
            memory={'active_period':dict(start=f'2026-{month:02d}-01',end=f'2026-{month+1:02d}-01',unit='month',label=f'2026-{month:02d}'),
                    'active_intent':'top_products','active_metric':'units','history':[{'question':'Sản phẩm nào bán chạy?','answer':'Đang xếp theo số lượng bán ròng.'}]}
            add(q,memory,dict(intent='top_products',time_mode='same_period',metric='revenue',period_unit='month'),'correction:'+str(i),split_of(i))
    other={
        'products':['Laptop dưới 20 triệu màn đẹp','Con Lenovo này dùng CPU gì?','Có máy nào nhẹ để đi học?','RAM máy này bao nhiêu?',
                    'Tư vấn laptop văn phòng','Cho thông số Dell Inspiron','Giá chiếc máy đó?','Tôi cần máy cho sinh viên',
                    'Con thứ hai nặng mấy kg?','Máy vừa gợi ý còn hàng chứ?','So thông số hai laptop vừa nói','Máy đầu có màn OLED không?'],
        'documents':['Chính sách bảo hành thế nào?','Điều kiện đổi trả ra sao?','Đọc kế hoạch marketing có sẵn',
                     'Quy định giảm giá của shop','Chính sách trả góp là gì?','Cho biết quy trình nhập hàng theo tài liệu',
                     'Có được cộng dồn ưu đãi không?','Tài liệu ghi biên tối thiểu bao nhiêu?',
                     'Bản chính sách giá nào đang áp dụng?','Chính sách mới thay đổi gì?',
                     'Có quy định giảm giá sinh viên không?','Cho xem điều khoản về bảo hành.'],
        'inventory':['Tồn kho hiện tại','Còn bao nhiêu hàng trong kho?','Mã nào đang hết hàng?','Hàng nào sắp hết?',
                     'Kiểm tra số lượng tồn','Danh sách tồn theo mã','Lấy thông tin kho hiện tại','Cho tôi xem tồn kho',
                     'Bao nhiêu chiếc đang có sẵn?','Kho còn gì để bán?','Tra số tồn các mặt hàng','Kiểm kê tồn kho giúp tôi'],
        'planning':['Dựa vào tháng trước và quý trước lập kế hoạch tháng tới','Nên kinh doanh tháng tới ra sao?',
                    'Tôi cần hướng tăng doanh thu cho tháng sau','Đề xuất chiến dịch dựa trên kết quả đã xem',
                    'Lên kế hoạch bán hàng tháng tới','Gợi ý hướng đi cho cửa hàng',
                    'Làm kế hoạch marketing cho kỳ tiếp theo','Từ kết quả này nên tập trung nhóm nào?',
                    'Tháng tới nên ưu tiên gì?','Giúp tôi đưa ra hướng kinh doanh kỳ tới',
                    'Từ số liệu tháng trước, đề xuất cách bán tháng sau','Lập phương án kinh doanh tháng kế tiếp'],
        'handoff':['Gặp nhân viên','Chuyển người thật','Tôi cần tư vấn viên','Kết nối nhân viên shop',
                   'Có người hỗ trợ không?','Nhờ nhân viên tư vấn','Cho nói với người bán','Tôi muốn gặp chủ shop',
                   'Chuyển cho bộ phận hỗ trợ','Gọi người phụ trách giúp','Cho gặp người hỗ trợ trực tiếp','Tôi cần nhân viên thật'],
        'pc':['Build PC chơi game','Ghép CPU và main tương thích','Tư vấn dàn máy tự lắp','Chọn linh kiện build PC',
              'Lắp máy bàn có GPU rời','Kiểm tra socket CPU với bo mạch','Cấu hình PC 20 triệu','Nguồn có đủ cho dàn này?',
              'Giúp tôi chọn bộ máy tự ráp','RAM DDR5 có lắp main này không?','Lên cấu hình máy bàn','Kiểm tra tương thích dàn PC'],
        'clarify':['Cái đó thế nào?','Nó tốt không?','Còn cái kia?','Xem giúp tôi','Có ổn không?','Thế sao?',
                   'Cho biết đi','Làm cái đó nhé','Nó sao rồi?','Thế còn cái ấy?','Tau hỏi cái đó cơ','Tính cho tôi với']}
    for intent,patterns in other.items():
        for i,q in enumerate(patterns):
            for context_id in range(8):
                memory=({'last_product_names':['Lenovo LOQ Gaming 15IRH8','Dell Inspiron 15 3530'],
                         'history':[{'question':'Gợi ý hai laptop','answer':'1. Lenovo LOQ Gaming 15IRH8; 2. Dell Inspiron 15 3530'}]} if intent=='products' else {})
                memory['conversation_note']=f'Phiên hỗ trợ {context_id+1}; chưa có kỳ hoặc chỉ số đang xem.'
                if intent=='products': memory['budget']=[0,(15+context_id)*1000000]
                mode='next_month' if intent=='planning' else 'missing'
                unit='month' if intent=='planning' else 'none'
                add(q,memory,dict(intent=intent,time_mode=mode,metric='unknown',period_unit=unit),intent+':'+str(i),split_of(i))
    operating_templates=['Lợi nhuận hoạt động {period} bao nhiêu?','Tính lợi nhuận trước lãi vay và thuế {period}.',
        'Cho số lời sau chi phí vận hành {period}.','Báo cáo lợi nhuận hoạt động của {period}.',
        'Kỳ {period} lời hoạt động được mấy đồng?','Lấy chỉ tiêu lợi nhuận hoạt động {period}.',
        'Lời trước lãi vay và thuế của {period}?','Xem kết quả lợi nhuận hoạt động {period}.',
        'Trong {period}, lợi nhuận hoạt động đạt bao nhiêu?','Cho biết mức lời hoạt động {period}.',
        'Tra lợi nhuận hoạt động trong {period}.','Tính lời hoạt động cho kỳ {period}.']
    for i,template in enumerate(operating_templates):
        for phrase,mode,unit in temporal:
            add(template.format(period=phrase),{},dict(intent='business_analysis',time_mode=mode,metric='operating_profit',period_unit=unit),f'operating:{i}',split_of(i))
    compare_templates=['So sánh doanh thu {a} và {b}.','Doanh thu {a} so với {b} thay đổi thế nào?',
        'Chênh lệch tiền bán giữa {a} với {b}?','Đối chiếu doanh thu {a}, {b}.',
        'Tính tăng giảm doanh thu {a} so với {b}.','Giữa {a} và {b}, doanh thu chênh bao nhiêu?',
        'Hai kỳ {a} và {b} doanh thu khác nhau ra sao?','Đặt doanh thu {a} bên cạnh {b}.',
        'Đánh giá thay đổi doanh thu từ {b} sang {a}.','Đo mức tăng doanh thu {a} đối với {b}.',
        'Tôi cần so doanh thu {a} với {b}.','So doanh thu của hai kỳ: {a}; {b}.']
    for i,template in enumerate(compare_templates):
        for month in range(2,10):
            add(template.format(a=f'tháng {month} năm 2026',b=f'tháng {month-1} năm 2026'),{},
                dict(intent='compare',time_mode='explicit',metric='revenue',period_unit='month'),f'compare:{i}',split_of(i))
    # Explicitly teach clarification continuation instead of treating the date as a new topic.
    for intent in ('revenue','top_products','business_analysis'):
        for month in range(1,13):
            for style,q in enumerate([f'Tháng {month} năm 2026 nhé.',f'Xem tháng {month}/2026.',f'Là tháng {month} năm 2026 đó.']):
                memory={'pending_intent':intent,'history':[{'question':'Xem giúp chỉ số đó','answer':'Bạn muốn xem tháng nào?'}]}
                add(q,memory,dict(intent=intent,time_mode='explicit',metric='units' if intent=='top_products' else 'revenue' if intent=='revenue' else 'unknown',period_unit='month'),f'pending:{intent}:{style}',('train','validation','test')[style])
    previous_templates=['Còn kỳ trước đó?','Xem tiếp kỳ liền trước.','Lùi một kỳ giúp tôi.','Kỳ ngay trước kỳ đang xem?',
        'Tra kỳ trước kỳ ấy.','Lấy kỳ liền kề phía trước.','Chuyển về kỳ trước đó.','Xem một kỳ trước kỳ này.',
        'Lùi về kỳ ngay trước.','Thế kỳ liền trước đó thì sao?','Còn nếu xem kỳ trước kỳ ấy?','Vậy kỳ trước đó nhé.']
    for i,q in enumerate(previous_templates):
        for month in range(2,10):
            add(q,{'active_period':dict(start=f'2026-{month:02d}-01',end=f'2026-{month+1:02d}-01',unit='month',label=f'2026-{month:02d}'),
                'active_intent':'top_products','active_metric':'units'},
                dict(intent='top_products',time_mode='previous_period',metric='units',period_unit='month'),f'previous:{i}',split_of(i))
    rng.shuffle(rows)
    labels={'intent':INTENTS,'time_mode':TIME_MODES,'metric':METRICS,'period_unit':['month','quarter','year','none']}
    groups=[{r['group_id'] for r in rows if r['split']==s} for s in ('train','validation','test')]
    assert not(groups[0]&groups[1] or groups[0]&groups[2] or groups[1]&groups[2])
    texts=[{r['text'] for r in rows if r['split']==s} for s in ('train','validation','test')]
    assert not(texts[0]&texts[1] or texts[0]&texts[2] or texts[1]&texts[2])
    distributions={s:{key:dict(Counter(r['labels'][key] for r in rows if r['split']==s)) for key in labels} for s in ('train','validation','test')}
    for split,counts in distributions.items():
        for key,values in labels.items(): assert set(counts[key])==set(values),(split,key,'missing labels')
    for split in ('train','validation','test'):
        (data/(split+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows if r['split']==split),encoding='utf-8')
    (data/'labels.json').write_text(json.dumps(labels,ensure_ascii=False,indent=2),encoding='utf-8')
    manifest={'version':'conversation-v3','data_revision':2,'rows':len(rows),'splits':dict(Counter(r['split'] for r in rows)),
              'label_distributions':distributions,
              'split_by':'wording family before context/period expansion','task':'Vietnamese contextual intent/time/metric/unit understanding',
              'privacy':'Synthetic conversation only; no credentials, real customer information or financial values',
              'limitations':['Synthetic template families; not proof of open-world conversation accuracy.',
                             'Calendar computations, permissions and SQL remain validated application tools.']}
    (data/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))


if __name__=='__main__': build()
