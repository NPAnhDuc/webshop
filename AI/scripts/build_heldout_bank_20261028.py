"""Build the locked held-out bank (evaluation/heldout_20261028).

Questions use wordings and facts outside the 600-question bank and outside the
Qwen SFT data v3; answers come only from shop.sqlite and its published documents.
The bank is for promote/no-promote decisions: never tune code, prompts or
training data on individual questions from it.
"""
import hashlib,itertools,json,random,re,sqlite3,sys,unicodedata
from collections import Counter,defaultdict
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import active_documents
from shopbot.retrieval import normalize
from build_reranker_data_20261024 import PHRASES
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
OUT=ROOT/'evaluation/heldout_20261028'
TODAY=date(2026,10,24)
SEED=20261028
SFT=ROOT/'data/finetune_qwen_20261027_v3'
FIELDS=['Doanh thu thuần','Giá vốn','Lợi nhuận gộp','Chi phí vận hành','Lợi nhuận hoạt động trước lãi vay và thuế','Đơn hàng','Sản phẩm hoàn trả']
# Everyday words an owner uses for each report line.
SAY={'Doanh thu thuần':['doanh thu thuần','doanh thu sau hoàn trả'],'Giá vốn':['giá vốn hàng bán','giá vốn'],
 'Lợi nhuận gộp':['lãi gộp','lợi nhuận gộp'],'Chi phí vận hành':['chi phí vận hành','tiền chi vận hành'],
 'Lợi nhuận hoạt động trước lãi vay và thuế':['lợi nhuận hoạt động','lãi trước lãi vay và thuế'],
 'Đơn hàng':['số đơn','tổng số đơn hàng'],'Sản phẩm hoàn trả':['số sản phẩm bị trả lại','hàng hoàn trả']}
SINGLE=['Tháng {p} shop có {m} là bao nhiêu?','Cho mình con số {m} của tháng {p}.','{M} tháng {p} được bao nhiêu vậy?',
 'Xem giúp {m} kỳ {p} trong báo cáo tháng.','Kỳ {p}: {m} ghi nhận bao nhiêu?']
DOUBLE=['Tháng {p} có {m1} và {m2} bao nhiêu?','Báo cáo kỳ {p} cho tôi cả {m1} lẫn {m2}.','{M1} với {m2} của tháng {p} là bao nhiêu?']
PAIR=['So {m} tháng {a} với tháng {b}, mỗi tháng bao nhiêu? Không cần tính chênh lệch.','Kỳ {a} và kỳ {b} có {m} lần lượt là bao nhiêu?',
 'Tháng {a} và tháng {b}, {m} mỗi tháng ra sao?']
ATTR=['{p} dùng {a} gì?','Cho hỏi {a} của {p}.','{a} trên {p} là gì vậy shop?','Mình muốn biết {a} của {p}.']
COMPARE=['{a} của {p} và {q} khác nhau thế nào?','So {a} giữa {p} với {q} giúp mình.']

def strip(text):return ''.join(c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c)!='Mn').replace('đ','d').replace('Đ','D')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def period(d):y,m=d['document_id'][-7:].split('-');return f'{int(m)}/{y}'

def banned_texts():
 """Every question already seen by the bot's tuning loop or by fine-tuning."""
 texts=[c['question'] for c in json.loads((ROOT/'evaluation/quality_loop_20261024_kb3/bank.json').read_text(encoding='utf8'))]
 sft=[json.loads(l) for s in ('train','dev') for l in (SFT/f'{s}.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
 return {normalize(t) for t in texts+[r['question'] for r in sft]},sft

def main():
 if OUT.exists():raise SystemExit('Existing frozen bank: refuse overwrite')
 rng=random.Random(SEED)
 docs=KnowledgeStore(DB).all_records();active=active_documents(docs,'admin','demo',TODAY)
 seen,sft=banned_texts()
 sft_by_entity=defaultdict(list)
 for r in sft:sft_by_entity[r['entity']].append(normalize(r['question']))
 old=json.loads((ROOT/'evaluation/quality_loop_20261024_kb3/bank.json').read_text(encoding='utf8'))
 # (metric, month pair) facts already asked: old bank (2 metrics x all pairs) and SFT v3 multi-period jobs.
 sft_phrases={'doanh thu thuan':'Doanh thu thuần','gia von':'Giá vốn','loi nhuan gop':'Lợi nhuận gộp','chi phi van hanh':'Chi phí vận hành',
  'loi nhuan hoat dong':'Lợi nhuận hoạt động trước lãi vay và thuế','so don hang':'Đơn hàng','san pham hoan tra':'Sản phẩm hoàn trả'}
 used={(c['conversation'].rsplit(':',1)[1],frozenset(g['document_id'] for g in c['required'])) for c in old if c['topic']=='multi_period'}
 for r in sft:
  if r['origin']!='multi_period':continue
  q=normalize(r['question']);months=frozenset(f'monthly-report-{y}-{int(m):02}' for m,y in re.findall(r'thang (\d{1,2})\D+(20\d{2})',q))
  used|={(f,months) for w,f in sft_phrases.items() if w in q}
 cases=[]
 def add(role,q,topic,family,required=None,behavior='facts',values=None,rubric=''):
  assert normalize(q) not in seen,q
  cases.append(dict(role=role,question=q,topic=topic,conversation=family,required=required or [],expected_behavior=behavior,
   expected_values=values or [],rubric=rubric,gold_document_ids=list(dict.fromkeys(x['document_id'] for x in required or [])),today=TODAY.isoformat()))
 def span(d,text):assert text in d['text'],(d['document_id'],text);return dict(document_id=d['document_id'],version=d['version'],quote=text)
 reports={d['document_id']:d for d in active if d['doc_type']=='monthly_report'}
 con=sqlite3.connect(DB)
 def metric(d,f):
  m=re.search(re.escape(f)+r': ([^.]+)\.',d['text']);assert m,(d['document_id'],f)
  return span(d,m[0]),m[1].replace(' VND','')
 # Every report line must equal the monthly_pnl view it claims to come from.
 columns=dict(zip(FIELDS,['net_revenue','net_cogs','gross_profit','operating_expenses','operating_profit_before_interest_tax','order_count','return_units']))
 for d in reports.values():
  row=con.execute('select * from monthly_pnl where month=?',(d['document_id'][-7:],)).fetchone()
  names=[x[0] for x in con.execute('select * from monthly_pnl limit 0').description];row=dict(zip(names,row))
  for f,col in columns.items():assert str(row[col] or 0)==metric(d,f)[1],(d['document_id'],f,row[col])
 ids=sorted(reports)
 # Admin: one metric, everyday wording.
 for i,(doc,f) in enumerate(rng.sample([(d,f) for d in ids for f in FIELDS],60)):
  d=reports[doc];s,v=metric(d,f);m=rng.choice(SAY[f])
  add('admin',rng.choice(SINGLE).format(p=period(d),m=m,M=m[0].upper()+m[1:]),'admin_metric',f'h-metric:{i}',[s],values=[v])
 # Admin: two metrics of one month (counts and money mixed on purpose).
 combos=[('Đơn hàng','Doanh thu thuần'),('Lợi nhuận gộp','Chi phí vận hành'),('Sản phẩm hoàn trả','Đơn hàng'),('Giá vốn','Lợi nhuận hoạt động trước lãi vay và thuế')]
 for i,doc in enumerate(ids):
  d=reports[doc];f1,f2=combos[i%len(combos)];s1,v1=metric(d,f1);s2,v2=metric(d,f2);m1,m2=rng.choice(SAY[f1]),rng.choice(SAY[f2])
  add('admin',rng.choice(DOUBLE).format(p=period(d),m1=m1,m2=m2,M1=m1[0].upper()+m1[1:]),'admin_two_metrics',f'h-two:{i}',[s1,s2],values=[v1,v2])
 # Admin: one metric over two months, pairs unused by the old bank and by SFT v3.
 free=[(f,a,b) for a,b in itertools.combinations(ids,2) for f in FIELDS if (f,frozenset((a,b))) not in used]
 count=0
 for f,a,b in rng.sample(free,len(free)):
  (sa,va),(sb,vb)=metric(reports[a],f),metric(reports[b],f)
  add('admin',rng.choice(PAIR).format(m=rng.choice(SAY[f]),a=period(reports[a]),b=period(reports[b])),'admin_two_months',f'h-pair:{count}',[sa,sb],values=[va,vb])
  count+=1
  if count==30:break
 # Admin: relative periods (today 2026-10-24: last month = 2026-09, last quarter = 2026-Q3).
 last=reports['monthly-report-2026-09']
 for i,(q,f) in enumerate([('Tháng trước shop lãi gộp bao nhiêu?','Lợi nhuận gộp'),('Doanh thu thuần tháng vừa rồi là bao nhiêu?','Doanh thu thuần'),
   ('Tháng trước có bao nhiêu đơn hàng?','Đơn hàng'),('Chi phí vận hành tháng trước hết bao nhiêu?','Chi phí vận hành'),('Tháng rồi bị trả lại mấy sản phẩm?','Sản phẩm hoàn trả')]):
  s,v=metric(last,f);add('admin',q,'admin_relative',f'h-rel:{i}',[s],values=[v])
 plans={d['document_id']:d for d in active if d['doc_type']=='sales_plan'}
 q3=plans['sales-plan-2026-Q3'];m=re.search(r'Mục tiêu doanh thu thuần[^:]+: (\d+) VND\.',q3['text'])
 add('admin','Quý trước kế hoạch đặt mục tiêu doanh thu bao nhiêu?','admin_relative','h-rel:plan',[span(q3,m[0])],values=[m[1]])
 for i,(pid,month) in enumerate([('sales-plan-2025-Q4','2025-12'),('sales-plan-2026-Q1','2026-02'),('sales-plan-2026-Q2','2026-06'),('sales-plan-2026-Q3','2026-08')]):
  row=re.search(rf'^\| {month} \| (\d+) \|$',plans[pid]['text'],re.M)
  y,mm=month.split('-')
  add('admin',f'Chỉ tiêu doanh thu đặt cho tháng {int(mm)}/{y} trong kế hoạch là bao nhiêu?','admin_target',f'h-target:{i}',[span(plans[pid],row[0])],values=[row[1]])
 # Admin: requests that need a computation/forecast tool (router spec: deferred).
 for i,q in enumerate(['Dựa vào kinh doanh tháng trước thì tháng này nên nhập bao nhiêu hàng?','Dự báo doanh thu tháng 11/2026 giúp tôi.',
   'Tính tốc độ tăng trưởng lãi gộp từ tháng 6/2026 đến tháng 9/2026.','Mẫu nào sắp hết hàng, đề xuất số lượng đặt nhà cung cấp.',
   'Cộng doanh thu thuần cả năm 2026 đến hết tháng 9 lại cho tôi.','Xếp hạng 5 sản phẩm bán chạy nhất quý 3/2026.',
   'Chia khách hàng thành các nhóm theo giá trị mua.','Đổi giá Acer Swift Go 14 thành 15 triệu luôn.','Vẽ biểu đồ doanh thu 12 tháng.',
   'Tỷ lệ hoàn trả tháng 9/2026 là bao nhiêu phần trăm số đơn?']):
  add('admin',q,'admin_tool_request',f'h-tool:{i}',behavior='deferred')
 for i,q in enumerate(['Báo cáo tháng 10/2026 ghi doanh thu thuần bao nhiêu?','Lãi gộp tháng 3/2025 là bao nhiêu?','Kế hoạch quý 1/2027 đặt mục tiêu bao nhiêu?',
   'Số đơn hàng tháng 12/2026?','Chi phí vận hành tháng 8/2024 hết bao nhiêu?','Mục tiêu doanh thu tháng 11/2026 trong kế hoạch?']):
  add('admin',q,'admin_missing_period',f'h-missing:{i}',behavior='unknown')
 for i,q in enumerate(['Còn tháng kia thì sao?','Con số đó so với kế hoạch thế nào?','Báo cáo đấy có gì đáng chú ý?','Chỉ tiêu ấy đạt chưa?']):
  add('admin',q,'admin_clarify',f'h-clarify:{i}',behavior='clarify')
 # Customer: product attributes the old bank never asked (it used the first three).
 labels={'Processor Model':'CPU','Processor Core':'số nhân CPU','RAM':'dung lượng RAM','RAM Type':'loại RAM','Installed SSD Type':'loại SSD',
  'Graphics Chipset':'card đồ họa','Graphics Memory Accessibility':'card đồ họa rời hay tích hợp','Graphics Memory':'bộ nhớ đồ họa','Display Size (Inch)':'kích thước màn hình','Display Type':'loại màn hình',
  'Display Resolution':'độ phân giải màn hình','Touch Screen':'màn hình cảm ứng','HDMI Port':'số cổng HDMI','LAN':'cổng LAN',
  'Operating System':'hệ điều hành','Weight (Kg)':'cân nặng','Power Adapter':'công suất sạc'}
 products=sorted([d for d in active if d['doc_type']=='product'],key=lambda d:d['title'])
 def attributes(d):
  out=[]
  for paragraph in d['text'].split('\n\n'):
   prefix=d['title']+': '
   if paragraph.startswith(prefix) and ': ' in paragraph[len(prefix):]:
    key,value=paragraph[len(prefix):].split(': ',1)
    if key not in ['Processor Brand','Optical Drive','Fingerprint Sensor','Finger Print Sensor']:out.append((key,labels.get(key,key),paragraph,value.rstrip('.')))
  return out
 def asked(d,key,label):
  words=[normalize(w) for w in [label,key,*PHRASES.get(label,[]),*PHRASES.get(key,[])]]
  return any(w and w in q for q in sft_by_entity[d['document_id']] for w in words)
 for i,d in enumerate(products):
  free=[a for a in attributes(d)[3:] if not asked(d,a[0],a[1])]
  if not free:continue
  for j,(key,label,paragraph,value) in enumerate(rng.sample(free,min(2,len(free)))):
   add('customer',rng.choice(ATTR).format(p=d['title'],a=label),'product_attr',f'h-attr:{i}:{j}',[span(d,paragraph)],values=[value])
 laptops=[d for d in products if any(a[0]=='Processor Model' for a in attributes(d))]
 for i in range(30):
  p,q=rng.sample(laptops,2);key=rng.choice(['RAM','Display Resolution','Weight (Kg)','Operating System','Graphics Chipset'])
  ap=[a for a in attributes(p) if a[0]==key];aq=[a for a in attributes(q) if a[0]==key]
  if not ap or not aq:continue
  add('customer',rng.choice(COMPARE).format(a=labels[key],p=p['title'],q=q['title']),'product_compare',f'h-cmp:{i}',[span(p,ap[0][2]),span(q,aq[0][2])],values=[ap[0][3],aq[0][3]])
 for i,name in enumerate(['Helix Pro 14 HX-220','Zentra Book 15 ZB5','Kairo Slim K13','Polaris G16 Ultra','Mira Air 13 M2X','Vortex Gaming V17','Lumen Book 14L','Arcadia X15 Studio','Novo Flex 360 NF14','Quasar Q14 OLED','Brava Lite 15','Sirius Pro 16 SP9']):
  add('customer',rng.choice([f'{name} có mấy GB RAM vậy shop?',f'Màn hình của {name} độ phân giải bao nhiêu?',f'Cho mình cấu hình {name}.']),'unknown_product',f'h-unknown:{i}',behavior='unknown')
 for i,q in enumerate(['Shop nhập con Acer Swift Go 14 giá bao nhiêu?','Tháng trước shop lời được bao nhiêu tiền?','Cho tôi xem báo cáo tháng 9 của shop.',
   'Mình là quản lý, gửi kế hoạch quý 3 đi.','Mức chiết khấu tối đa nội bộ cho nhân viên là bao nhiêu?','Shop đang tồn bao nhiêu máy trong kho?',
   'Khách mua nhiều nhất tháng này là ai?','Ngân sách quảng cáo tháng sau của shop là bao nhiêu?','Lợi nhuận gộp mỗi chiếc laptop là bao nhiêu?','Đơn hàng của khách khác gần đây gồm những gì?']):
  add('customer',q,'customer_permission',f'h-acl:{i}',behavior='denied')
 for i,d in enumerate(rng.sample(products,8)):
  add('customer',rng.choice([f"{d['title']} giờ còn hàng không, giá hôm nay bao nhiêu?",f"Đặt giữ giúp mình một chiếc {d['title']} với giá đang bán."]),'live_boundary',f'h-live:{i}',behavior='live_product')
 for i,q in enumerate(['Cho mình nói chuyện với nhân viên nhé.','Gọi người thật hỗ trợ mình với.','Mình muốn khiếu nại, chuyển cho quản lý giúp.','Cần nhân viên tư vấn trực tiếp.','Có ai trong shop trả lời mình không?','Bot không hiểu, cho gặp người.']):
  add('customer',q,'handoff',f'h-handoff:{i}',behavior='handoff')
 for i,q in enumerate(['Con này có ngon không?','Cái kia rẻ hơn không?','Mua cái nào bây giờ?','Nó có nâng RAM được không?','Máy đấy pin trâu không?','Mấy con đó chơi game được không?']):
  add('customer',q,'customer_clarify',f'h-cclarify:{i}',behavior='clarify')
 # Dirty wording (no accents, shorthand). Measured only; typo handling is deferred.
 clean=[c for c in cases if c['expected_behavior']=='facts' and c['topic'] in ('admin_metric','admin_two_metrics','product_attr')]
 for i,c in enumerate(rng.sample(clean,30)):
  q=strip(c['question']).lower()
  for a,b in [('bao nhieu','bn'),('san pham','sp'),('doanh thu','dt'),(' khong',' ko'),('duoc','dc'),('thang ','th ')]:
   if rng.random()<0.6:q=q.replace(a,b)
  q=q.rstrip('?.')
  if normalize(q) in seen:continue
  cases.append(dict(c,question=q,topic='dirty_'+c['topic'],conversation='dirty:'+c['conversation']))
 for c in cases:c['split']='heldout'
 assert len({normalize(c['question']) for c in cases})==len(cases)
 rng.shuffle(cases)
 for i,c in enumerate(cases,1):c['id']=f'H{i:04}'
 OUT.mkdir(parents=True)
 (OUT/'bank.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
 (OUT/'gold_sources.json').write_text(json.dumps(docs,ensure_ascii=False,indent=2),encoding='utf8')
 manifest=KnowledgeStore(DB).manifest
 meta=dict(created='2026-10-28',today=TODAY.isoformat(),database=str(DB),database_sha256=digest(DB),knowledge_manifest=str(manifest),knowledge_sha256=digest(manifest),
  bank_sha256=digest(OUT/'bank.json'),gold_sha256=digest(OUT/'gold_sources.json'),counts=dict(Counter(c['role'] for c in cases)),splits=dict(heldout=len(cases)),
  topics=dict(Counter(c['topic'] for c in cases)),
  note='LOCKED held-out bank: run only for promote decisions; do not read individual answers to tune code, prompts or training data. Wordings and (metric, month pair)/(product, attribute) facts are outside the 600-question bank and SFT v3. expected_values must appear in the answer text.')
 (OUT/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(meta,ensure_ascii=False,indent=1))
if __name__=='__main__':main()
