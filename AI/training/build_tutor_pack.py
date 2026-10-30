"""Build an auditable pilot from public catalog facts, never from model guesses."""
import base64
import hashlib
import json
import random
import subprocess
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent

def write_jsonl(path,rows):
    path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')

def build():
    data=HERE/'data'
    data.mkdir(parents=True,exist_ok=True)
    catalog=[json.loads(s) for s in (ROOT/'data/structured/processed/product_catalog.jsonl').read_text(encoding='utf-8').splitlines()]
    ids=sorted(r['record_id'] for r in catalog)
    random.Random(20261019).shuffle(ids)
    partition={v:('test' if i<6 else 'validation' if i<12 else 'train') for i,v in enumerate(ids)}
    corpus=[]
    qa=[]
    routing=[]
    criteria={'products':'Tư vấn laptop, giá, tồn kho, so sánh sản phẩm','documents':'Bảo hành, đổi trả, trả góp, chính sách','handoff':'Yêu cầu nói chuyện nhân viên','clarify':'Ngoài phạm vi hoặc cần làm rõ'}
    def route(text,label,group,split):
        routing.append({'state':text,'questions':{'intent':{'type':'choice','instructions':'Chọn ý định câu hỏi tiếng Việt của khách hàng.','criteria':criteria,'label':label}},'_meta':{'group_id':group,'split':split,'label_origin':'human_authored_template','pilot_only':True}})
    for r in catalog:
        facts={**{k:v for k,v in r['attributes'].items() if v is not None},
               'giá bán hiện tại của shop':'CHƯA CÓ DỮ LIỆU','tồn kho của shop':'CHƯA CÓ DỮ LIỆU','giá vốn':'CHƯA CÓ DỮ LIỆU'}
        text=f"Tên sản phẩm: {r['model']}\n"+'\n'.join(f'{k}: {json.dumps(v,ensure_ascii=False)}' for k,v in facts.items())
        text+='\nThông số từ nguồn tham khảo, không phải giá/tồn kho/chính sách shop hiện tại.'
        doc={'id':r['record_id'],'title':r['model'],'text':text,'source_dataset':r['source_dataset'],'source_file':r['source_file'],'source_row':r['source_row'],'source_sha256':r['source_sha256'],'audience':'public','authority':'external_catalog','group_id':r['record_id'],'split':partition[r['record_id']]}
        corpus.append(doc)
        fields={'cpu':'bộ xử lý','ram_gb':'dung lượng RAM (GB)','gpu':'card đồ họa','screen_inches':'kích thước màn hình (inch)','socket':'socket','form_factor':'kích thước chuẩn bo mạch'}
        for field,label in fields.items():
            if r.get(field) is None:continue
            for template in ['{name} có {label} nào theo nguồn dữ liệu?','Cho tôi biết {label} của {name}.']:
                qa.append({'id':f'{r["record_id"]}:{field}:{len(qa)}','question':template.format(name=r['model'],label=label),'expected_answer':json.dumps(r[field],ensure_ascii=False),'positive_id':r['record_id'],'field':field,'group_id':r['record_id'],'split':partition[r['record_id']],'answerability':'supported','label_origin':'exact_catalog_value'})
        for field,value in r['attributes'].items():
            if value is None or field in ('name','Model','Link','Brand','Company','Product','Part No'):continue
            for template in ['Nguồn ghi {field} của {name} là gì?','Tra thông số {field} cho {name} giúp tôi.']:
                qa.append({'id':f'{r["record_id"]}:attribute:{field}:{len(qa)}','question':template.format(name=r['model'],field=field),
                  'expected_answer':json.dumps(value,ensure_ascii=False),'positive_id':r['record_id'],'field':field,
                  'group_id':r['record_id'],'split':partition[r['record_id']],'answerability':'supported','label_origin':'exact_catalog_value'})
        for field in ['giá bán hiện tại của shop','tồn kho của shop','giá vốn']:
            qa.append({'id':f'{r["record_id"]}:{field}','question':f'{field.capitalize()} của {r["model"]} là bao nhiêu?','expected_answer':'Chưa có dữ liệu được xác minh của shop.','positive_id':r['record_id'],'field':field,'group_id':r['record_id'],'split':partition[r['record_id']],'answerability':'must_abstain','label_origin':'missing_shop_field'})
        for question in [f'Tư vấn {r["model"]} giúp tôi',f'Thông số {r["model"]} thế nào?',f'So sánh cấu hình {r["model"]} được không?']:
            route(question,'products',r['record_id'],partition[r['record_id']])
    groups={
      'documents':['Bảo hành của shop áp dụng thế nào?','Điều kiện đổi trả là gì?','Tôi muốn xem chính sách trả góp.','Quy định giảm giá của cửa hàng là gì?','Có được cộng dồn khuyến mãi không?','Shop giao hàng theo chính sách nào?','Mất hóa đơn thì bảo hành ra sao?','Đổi máy lỗi cần giấy tờ gì?','Phí trả góp được quy định thế nào?','Chính sách bảo vệ dữ liệu khách hàng ra sao?','Thời gian hoàn tiền trong chính sách là bao lâu?','Điều kiện nhận ưu đãi sinh viên là gì?'],
      'handoff':['Cho tôi gặp nhân viên tư vấn.','Tôi muốn nói chuyện với người thật.','Kết nối bộ phận hỗ trợ cho tôi.','Có thể chuyển cuộc trò chuyện cho nhân viên không?','Tôi cần chuyên viên hỗ trợ trực tiếp.','Nhờ nhân viên gọi lại cho tôi.','Tôi muốn chuyển sang tư vấn viên.','Cho tôi liên hệ người phụ trách cửa hàng.','Tôi không muốn nói chuyện với bot nữa, cho gặp nhân viên.','Gọi người thật hỗ trợ đơn hàng.','Hãy chuyển cho bộ phận chăm sóc khách hàng.','Để nhân viên tư vấn giúp tôi nhé.'],
      'clarify':['Hôm nay trời có mưa không?','Viết cho tôi một bài thơ.','Chỉ tôi cách nấu bún bò.','Dự đoán tỷ số bóng đá tối nay.','Tôi nên mua cổ phiếu nào?','Dịch bài hát cho tôi.','Giải bài toán tích phân này.','Tư vấn thuốc chữa đau đầu.','Kể chuyện cổ tích đi.','Xin chào.','Tôi chưa biết mình cần gì.','Giúp tôi lên lịch đi du lịch.']}
    for label,questions in groups.items():
        for i,q in enumerate(questions):
            split='test' if i%6==0 else 'validation' if i%6==1 else 'train'
            for prefix in ['', 'Bạn giúp tôi nhé: ', 'Cho mình hỏi, ']:route(prefix+q,label,f'{label}:{i}',split)
    write_jsonl(data/'corpus.jsonl',corpus)
    write_jsonl(data/'qa.jsonl',qa)
    for split in ('train','validation','test'):
        write_jsonl(data/f'kev-{split}.jsonl',[r for r in routing if r['_meta']['split']==split])
    groups_by_split={s:{r['group_id'] for r in qa if r['split']==s} for s in ('train','validation','test')}
    assert not groups_by_split['train'] & (groups_by_split['test']|groups_by_split['validation'])
    assert not groups_by_split['test'] & groups_by_split['validation']
    metadata={'scope':'Pilot, template-derived questions from 37 public catalog records, not a production benchmark.',
       'corpus':len(corpus),'qa':len(qa),'qa_splits':dict(Counter(r['split'] for r in qa)),
       'routing':len(routing),'routing_splits':dict(Counter(r['_meta']['split'] for r in routing)),
       'semantic_routing_groups':len({r['_meta']['group_id'] for r in routing}),
       'training_cloud_destination':'User private Google Colab session; no upload to public Hub',
       'excluded':['credentials','customer data','backend store state','real internal finances','third-party report full texts','product images'],
       'truth_policy':'No invented inventory, cost or shop price. Keep missing facts unknown. Corrections must cite source evidence.',
       'test_policy':'Split by product/group before question expansion. Validation for tuning; test only after freezing candidate.'}
    (data/'manifest.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(metadata,ensure_ascii=False))
    return metadata

if __name__=='__main__':build()
