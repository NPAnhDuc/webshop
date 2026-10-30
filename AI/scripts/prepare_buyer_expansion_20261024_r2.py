"""Freeze 300 buyer development turns; no model calls, ingestion or training."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'data/agent_platform_20261023/catalog_v1/catalog_public.json'
OUT=ROOT/'evaluation/buyer_expansion_20261024_r2'


def main():
    catalog=json.loads(SOURCE.read_text(encoding='utf-8'));products=catalog['products']
    assert len(products)==67
    OUT.mkdir(exist_ok=False)
    rows=[]
    def add(question,group,family,expected,**extra):
        rows.append(dict(id=f'BUY-{len(rows)+1:03}',conversation=group,role='customer',
            question=question,family=family,expected=expected,**extra))
    labels={'laptop':'laptop','cpu':'CPU','ssd':'ổ SSD','mainboard':'mainboard','ram':'thanh RAM',
        'accessories':'phụ kiện','case':'case máy tính','monitor':'màn hình','psu':'bộ nguồn','vga':'card đồ họa'}
    fields={'laptop':[('ram_gb','RAM bao nhiêu GB'),('battery_wh','dung lượng pin bao nhiêu Wh')],
        'cpu':[('cores','có bao nhiêu nhân CPU'),('socket','dùng socket nào')],
        'ssd':[('storage_gb','dung lượng bao nhiêu GB'),('storage_type','dùng chuẩn ổ lưu trữ gì')],
        'mainboard':[('socket','dùng socket nào'),('ram_type','hỗ trợ loại RAM nào')],
        'ram':[('ram_gb','dung lượng RAM bao nhiêu GB'),('ram_type','là loại RAM nào')],
        'accessories':[('connection','kết nối theo chuẩn nào'),('warranty_months','bảo hành bao nhiêu tháng theo bản ghi')],
        'case':[('supported_form_factors','hỗ trợ những chuẩn mainboard nào'),('max_gpu_length_mm','lắp card đồ họa dài tối đa bao nhiêu mm')],
        'monitor':[('refresh_hz','tần số quét bao nhiêu Hz'),('panel','dùng tấm nền gì')],
        'psu':[('psu_watt','công suất bao nhiêu W'),('certification','đạt chuẩn hiệu suất nào')],
        'vga':[('vram_gb','VRAM bao nhiêu GB'),('recommended_psu_w','cần nguồn công suất bao nhiêu W')]}
    # 134 exact-product fact probes. Missing catalog fields deliberately test abstention.
    for p in products:
        for field,phrase in fields[p['category']]:
            value=p['specs'].get(field)
            add(f"Theo bản thông tin đang có, {p['name']} {phrase}?",'product-'+p['id'],
                'product_fact',dict(product_id=p['id'],field=field,catalog_value=value,
                    missing=value is None,must_not_invent_missing=True,oracle='captured catalog only; not manufacturer verification',
                    gold_status='catalog_field_oracle_needs_semantic_review'))

    def search_expected(category,budget,limit,inclusive=False):
        matches=[]
        for p in products:
            if p['category']!=category or p['status']!='active':continue
            variants=[v for v in p['variants'] if v['status']=='active' and v.get('available_qty',0)>0
                and (0<v['price']<=budget if inclusive else 0<v['price']<budget)]
            if variants:
                v=min(variants,key=lambda x:(x['price'],x['id']))
                matches.append((v['price'],p['id'],v['id']))
        matches.sort()
        return dict(capability='catalog.search',category=category,budget_vnd=budget,inclusive=inclusive,
            requested_count=limit,total_matching=len(matches),expected_product_ids=[p[1] for p in matches[:limit]],
            expected_variant_ids=[p[2] for p in matches[:limit]],shortage=len(matches)<limit,
            data_kind='simulation',oracle='independent catalog filtering, not CatalogTools.search')
    # 40 searches: strict boundary, just above boundary, inclusive and insufficient availability.
    for category,label in labels.items():
        minimum=min(v['price'] for p in products if p['category']==category for v in p['variants'])
        for j,(budget,limit,inclusive) in enumerate([(minimum,3,False),(minimum+1,2,False),
                (minimum,1,True),(minimum*2,5,False)]):
            bound='tối đa' if inclusive else 'dưới'
            add(f"Trong danh mục hiện có, lấy {limit} {label} giá {bound} {budget} đồng giúp mình.",
                f'search-{category}-{j}','catalog_search',search_expected(category,budget,limit,inclusive))
    # 20 comparisons with exact model identities; no inferred benchmark/winner.
    laptops=[p for p in products if p['category']=='laptop']
    comparison_fields=['ram_gb','cpu_model','gpu_model','storage_gb','panel','refresh_hz','weight_kg','battery_wh']
    for i in range(20):
        a=laptops[i%19];b=laptops[(i+1 if i<19 else i+7)%19]
        add(f"Đối chiếu {a['name']} với {b['name']}: điểm khác về cấu hình là gì, thông số thiếu thì nói rõ.",
            f'compare-{i}','product_comparison',dict(capability='catalog.compare',product_ids=[a['id'],b['id']],
                fields={f:[a['specs'].get(f),b['specs'].get(f)] for f in comparison_fields},
                must_not_infer_benchmarks_or_universal_winner=True,gold_status='catalog_oracle_needs_semantic_review'))
    docs=[
        'RAM DDR4 và DDR5 khác nhau thế nào với người dùng văn phòng?',
        'SSD NVMe khác SSD SATA ở điểm nào khi mở máy và chép tệp?',
        'OLED và IPS có ưu nhược điểm gì khi học online lâu?',
        'Màn hình 120 Hz có làm mọi trò chơi chạy 120 FPS không?',
        'Độ phủ màu sRGB và độ sáng màn hình nói lên điều gì?',
        'GPU tích hợp có phải lúc nào cũng yếu hơn GPU rời không?',
        'TDP có phải chính là điện năng máy luôn tiêu thụ không?',
        'Pin 56 Wh có thể suy ra chính xác dùng được mấy giờ không?',
        'USB-C có đảm bảo máy nào cũng sạc và xuất hình được không?',
        'Thunderbolt và USB-C có phải cùng một thứ không?',
        'Hai CPU cùng tên i5 có chắc hiệu năng ngang nhau không?',
        'Dung lượng VRAM khác RAM máy tính ở đâu?',
        'Nguồn 80 Plus có tự chứng minh đủ công suất cho mọi bộ PC không?',
        'RAM dual-channel là gì, khi nào có lợi?',
        'Ổ SSD gần đầy có thể ảnh hưởng hiệu năng như thế nào?',
        'Shop cho đổi máy do không thích màu trong bao lâu?',
        'Mua online phát hiện điểm chết màn hình thì shop xử lý thế nào?',
        'Bảo hành pin khác bảo hành toàn máy ở điểm nào theo chính sách shop?',
        'Hóa đơn VAT của shop được xuất khi nào và cần thông tin gì?',
        'Điều kiện trả góp của shop có bắt buộc dùng thẻ tín dụng không?',
        'Hộp đã mở có còn được trả hàng theo chính sách shop không?',
        'Shop có nhận bảo hành nếu khách tự nâng RAM không?',
        'Hàng trưng bày có chính sách riêng nào tại shop?',
        'Giao đến tỉnh khác mất bao lâu theo chính sách hiện hành?',
        'Shop có thu phí giao máy và lắp đặt không?',
        'Muốn hủy đơn trước lúc giao thì làm theo bước nào?',
        'Mã giảm giá có dùng cùng chương trình trả góp không?',
        'Chi nhánh shop ở đâu và giờ mở cửa hôm nay thế nào?',
        'Làm sao liên hệ nhân viên thật của shop để xác nhận thông số?',
        'Nếu thông tin hai tài liệu bảo hành khác nhau thì ưu tiên bản nào?']
    for i,q in enumerate(docs):
        add(q,f'doc-{i}','knowledge_policy',dict(capability='documents.answer',
            gold_status='needs_verified_official_or_shop_source',must_not_invent_shop_policy=True,
            current_agent_connection='registered_disabled; route success is not knowledge-answer success'))
    workloads=[
        'Mình học kế toán, khoảng 18 triệu, dùng Excel lớn thì cần hỏi thêm gì để chọn máy?',
        'Lập trình Android và chạy máy ảo thì ưu tiên RAM hay GPU?',
        'Sinh viên kiến trúc dùngRevit với ngân sách 25 triệu nên cân nhắc gì?',
        'Chỉ làm Word và họp video, mình có cần mua laptop gaming không?',
        'Muốn chơi Black Myth Wukong, chưa biết độ phân giải thì có thể cam kếtFPS chưa?',
        'Dựng video 4K thường xuyên, ngân sách 20 triệu có đánh đổi nào cần nói trước?',
        'Mình mang máy đi học cả ngày, có thể chỉ nhìn Wh để chốt máy pin tốt không?',
        'Máy học tập cho con nhỏ nên cân nhắc độ bền và bảo hành như thế nào?',
        'Tôi thích máy ít ồn hơn cấu hình cao, bot cần hỏi thêm điều gì?',
        'Muốn chỉnh ảnh màu chính xác thì màn hình cần thông số và kiểm chứng nào?',
        'Có laptop nào dưới 15 triệu chắc chắn không nóng khi chơi game không?',
        'Làm AI local có bắt buộc dùng GPU rời, cần hỏi quy mô mô hình thế nào?',
        'Mình đã có màn hình ngoài, có cần ưu tiên màn hình laptop đắt hơn không?',
        'Chọn máy cho người lớn tuổi chỉ gọi video và đọc báo nên chú ý gì?',
        'Muốn nâng máy cũ nhưng chưa biết model, có thể mua RAM bất kỳ không?',
        'Build PC 20 triệu bao gồm cả màn hình, đã đủ thông tin để chốt 8 linh kiện chưa?',
        'Dùng Linux là chính thì có thể cam kết mọi laptop đều tương thích không?',
        'Cùng giá nhưng một máy 16 GB và một máy 8 GB GPU mạnh hơn, nên hỏi nhu cầu gì?',
        'Có nên khuyên khách vượt ngân sách chỉ vì máy đắt hơn không?',
        'Mình muốn máy vừa nhẹ vừa chạy game nặng vừa rẻ, bot nên trình bày đánh đổi ra sao?']
    for i,q in enumerate(workloads):
        add(q,f'workload-{i}','consultation',dict(gold_status='needs_reviewed_advice_sources_and_scope',
            must_not_invent_fps_runtime_compatibility=True,must_respect_budget_and_ask_missing_constraints=True))
    # 14 independent4-turn sessions:56 turns with state changes and ordinal references.
    setups=[('laptop',24000000,18000000,'ram'),('cpu',10000000,7000000,'ssd'),
        ('ram',4000000,3000000,'monitor'),('ssd',5000000,2500000,'cpu'),
        ('monitor',7000000,5000000,'laptop'),('vga',15000000,12000000,'psu'),
        ('mainboard',7000000,5000000,'ram'),('psu',4000000,3000000,'case'),
        ('case',3000000,2000000,'mainboard'),('accessories',2000000,1500000,'ssd'),
        ('laptop',30000000,22000000,'monitor'),('cpu',8000000,6000000,'vga'),
        ('ram',6000000,3500000,'psu'),('ssd',4000000,2000000,'case')]
    compare_phrases=['So sánh món đầu và món thứ hai trong danh sách mới.',
        'Hai sản phẩm đầu của lượt vừa rồi khác nhau ở đâu?',
        'Đặt sản phẩm số một cạnh số hai giúp mình.',
        'Cho mình bảng đối chiếu hai món đứng đầu danh sách đó.',
        'So cấu hình món thứ hai với món đầu tiên nhé.',
        'Lấy hai lựa chọn đầu vừa tìm để so, thiếu thông số thì ghi thiếu.',
        'Mình muốn đối chiếu số một và số hai của kết quả gần nhất.',
        'Hai món đầu lần này khác thông số nào?',
        'So sánh lựa chọn thứ nhất với lựa chọn thứ hai vừa hiển thị.',
        'Món đầu so với món kế tiếp có chênh lệch gì?',
        'Xin bảng thông số của hai sản phẩm đầu ở kết quả mới.',
        'Trong lượt tìm cuối, so hai sản phẩm đứng đầu giúp tôi.',
        'So hai món đầu tiên, đừng dùng danh sách ở lượt trước nữa.',
        'Mình đang cân nhắc hai lựa chọn đầu của danh sách mới nhất, so giúp nhé.']
    for i,(category,budget,newbudget,next_category) in enumerate(setups):
        session=f'multi-{i+1:02}'
        first=search_expected(category,budget,4)
        second=search_expected(category,newbudget,2)
        add(f"Mình muốn xem 4 {labels[category]} dưới {budget} đồng.",session,'multi_turn',first,turn=1)
        add(f"Vẫn loại vừa rồi, hạ trần xuống {newbudget} đồng và lấy 2 món nhé.",session,'multi_turn',
            dict(**second,keep_category=True,replace_selection=True),turn=2)
        add(compare_phrases[i],session,'multi_turn',dict(capability='catalog.compare',
            product_ids=second['expected_product_ids'][:2],clarify_if_fewer_than_two=len(second['expected_product_ids'])<2,
            source_selection='immediately_previous_successful_search'),turn=3)
        add(f"Bỏ lựa chọn cũ, chuyển sang {labels[next_category]}, lấy 3 món dưới {budget} đồng.",session,'multi_turn',
            dict(**search_expected(next_category,budget,3),clear_old_category_selection=True),turn=4)
    assert len(rows)==300
    assert len({r['id'] for r in rows})==300
    with (OUT/'bank.jsonl').open('x',encoding='utf-8') as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    families={family:sum(r['family']==family for r in rows) for family in sorted({r['family'] for r in rows})}
    manifest=dict(schema='buyer-expansion-v1',turns=300,unique_questions=len({r['question'] for r in rows}),
        multi_turn_sessions=14,multi_turn_turns=56,families=families,source_catalog_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        bank_sha256=hashlib.sha256((OUT/'bank.jsonl').read_bytes()).hexdigest(),data_kind='simulation',
        development_only=True,independent_validation=False,model_calls=0,training_performed=False,
        typo_understanding_feature_implemented=False,gold_policy='Catalog oracles separate from source-dependent questions needing review. Do not treat routing/deferred as answered knowledge.',
        ingestion_allowed=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))


if __name__=='__main__':main()
