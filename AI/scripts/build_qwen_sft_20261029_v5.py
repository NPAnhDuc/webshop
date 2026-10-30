"""SFT data v5: v4 examples plus router examples for the families that still fail.

Family-level weaknesses (held-out topic totals, expansion development split):
two metrics in one question, no-diacritic wording, clarify, tool requests (deferred),
customer requests for internal data, buying-guide advice. Labels follow the router spec
(basic_rag.SYSTEM); the gold `query` of a no-diacritic question is its accented source
wording, so the router learns to restore it. No model answer is used as a label.

Questions are written from a template pool used by no evaluation bank; anything equal
or near-equal (Jaccard >= 0.7) to a question of the 600 bank, the held-out 300, the
expansion bank (both splits) or earlier banks is dropped. Router-only: the product
selector stays the v1 model (OLLAMA_SELECTOR_MODEL), so v5 is served as OLLAMA_MODEL.
"""
import hashlib,itertools,json,random,re,sys,unicodedata
from collections import Counter
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
import build_qwen_sft_20261026 as v4
from build_reranker_data_20261024 import evaluation_questions,key,split_of
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import active_documents
from shopbot.retrieval import normalize
SRC=ROOT/'data/finetune_qwen_20261028_v4'
OUT=ROOT/'data/finetune_qwen_20261029_v5'
DB=v4.DB
SEED=20261030
SAY={'Doanh thu thuần':['doanh thu thuần','doanh thu ròng'],'Giá vốn':['giá vốn','giá vốn hàng bán'],'Lợi nhuận gộp':['lãi gộp','lợi nhuận gộp'],
 'Chi phí vận hành':['chi phí vận hành','chi vận hành'],'Lợi nhuận hoạt động trước lãi vay và thuế':['lợi nhuận hoạt động','lãi hoạt động'],
 'Đơn hàng':['số đơn','đơn hàng'],'Sản phẩm hoàn trả':['sản phẩm hoàn trả','hàng trả lại']}
SINGLE=['Tra giúp {m} tháng {p}.','{M} trong tháng {p} ghi bao nhiêu?','Tháng {p} shop đạt {m} mức nào?','Xin số {m} kỳ {p}.']
TWO=['Tôi cần {m1} và {m2} trong báo cáo tháng {p}.','{M1}, {m2} kỳ {p} ra sao?','Báo cáo tháng {p}: {m1} với {m2}?','Lấy {m1} kèm {m2} của tháng {p}.']
CALC=['Tính tổng {m} từ tháng {a} đến tháng {b}.','{M} tháng {b} so với tháng {a} tăng bao nhiêu phần trăm?','Trung bình {m} mỗi tháng từ {a} tới {b} là bao nhiêu?',
 'Tháng nào giữa {a} và {b} có {m} cao nhất? Xếp hạng giúp.','Lấy {m} tháng {b} trừ tháng {a} ra bao nhiêu?']
ATTR=['{p} {a} gì?','Hỏi {a} của {p}.','{a} máy {p} sao shop?','{p} thì {a} thế nào?']
LAPTOP_LABELS={'Processor Model':'CPU','RAM':'RAM','RAM Type':'loại RAM','Graphics Chipset':'card đồ họa','Display Resolution':'độ phân giải màn hình',
 'Display Size (Inch)':'kích thước màn hình','Weight (Kg)':'cân nặng','Operating System':'hệ điều hành','HDMI Port':'cổng HDMI','Installed SSD Type':'loại SSD'}
HAND=[
 *[('customer',q,'clarify',[],False) for q in ['Con ấy pin được mấy tiếng?','Máy đó có đèn bàn phím không?','Cái này giá rẻ hơn không?','Thứ đó lắp vừa case không?',
   'Nó nặng hay nhẹ?','Mẫu kia màn hình thế nào?','Hai con này nên lấy con nào?','Bộ ấy chạy êm không?','Cái kia có bản 16 GB không?','Thế thì nó có tốt hơn không?']],
 *[('admin',q,'clarify',[],False) for q in ['Số kia có khớp không?','Tháng ấy thế nào?','Cái chỉ tiêu đó sao rồi?','Kỳ trước của nó?','Mục kia lên hay xuống?','Hai số ấy chênh nhau không?']],
 *[('admin',q,'deferred',[],False) for q in ['Lập dự báo số đơn quý 1/2027.','Phân nhóm khách theo tần suất mua.','Tạo đơn đặt hàng 5 card RTX với nhà cung cấp.',
   'Đổi trạng thái đơn DH2201 thành đã giao.','Gửi báo cáo tuần qua email cho kế toán.','Xuất file CSV doanh thu theo ngày.','Tính vòng quay hàng tồn kho quý 3.',
   'Đề xuất mức giá mới cho các mẫu bán chậm.','Tính tỷ lệ lợi nhuận gộp trên doanh thu từng tháng năm 2026.','Mô phỏng doanh thu nếu giảm giá 10%.']],
 *[('customer',q,'answer',[],True) for q in ['Shop lãi bao nhiêu khi bán một con RAM?','Cho mình xem doanh số tháng này của cửa hàng.','Giá shop nhập màn hình LG là bao nhiêu?',
   'Danh sách khách mua card đồ hoạ tháng trước?','Số đơn của shop hôm qua là bao nhiêu?','Kế hoạch nhập hàng quý tới của shop ra sao?','Lương quản lý cửa hàng bao nhiêu?',
   'Mình là kế toán shop, gửi giúp sổ chi phí.','Tiền thuê kho của shop mỗi tháng?','Email của người mua chiếc MSI hôm trước là gì?','Mục tiêu doanh số nội bộ năm nay của shop?',
   'Chiết khấu nhà phân phối dành cho shop là bao nhiêu?']],
 *[('customer',q,'answer',['buying_guide'],False) for q in ['Sinh viên IT nên chọn laptop RAM mấy GB?','Dựng video nhẹ thì cần RAM bao nhiêu?','Máy học Photoshop nên có cấu hình RAM ra sao?',
   'Chọn laptop chơi game thì nên xem thông số gì trước?','Chọn màn hình chỉnh ảnh cần để ý gì ngoài tấm nền IPS?']],
 *[('customer',q,'answer',['glossary'],False) for q in ['Card rời có hao pin hơn card onboard không?','Màn 120 Hz có cần cho người chỉ gõ văn bản không?','Ổ M.2 SATA với NVMe khác nhau gì?',
   'VRAM 8 GB có phải RAM máy 8 GB không?','Máy hàn RAM thì có gắn thêm thanh được không?','Nguồn 80 PLUS Bronze có nghĩa là đủ công suất không?','Màn OLED để desktop tĩnh lâu có sao không?']],
]

def strip(text):return ''.join(c for c in unicodedata.normalize('NFD',text) if unicodedata.category(c)!='Mn').replace('đ','d').replace('Đ','D')
def dirty(q,rng):
 q=strip(q).lower()
 for a,b in [('bao nhieu','bnhieu'),('khong','k'),('thang ','t'),('the nao','ntn'),('gi','j')]:
  if rng.random()<0.5:q=re.sub(r'\b'+a+r'\b',b,q) if a=='gi' else q.replace(a,b)
 return q.rstrip('?.')
def cap(s):return s[0].upper()+s[1:]
def period(d):y,m=d['document_id'][-7:].split('-');return f'{int(m)}/{y}'

def banned():
 texts=[]
 for bank in ['quality_loop_20261024_kb3','quality_loop_20261021','heldout_20261028','expansion_20261029']:
  texts+=[c['question'] for c in json.loads((ROOT/'evaluation'/bank/'bank.json').read_text(encoding='utf8'))]
 return {key(t) for t in texts}|evaluation_questions()

def main():
 rng=random.Random(SEED)
 store=KnowledgeStore(DB);docs={d['document_id']:d for d in active_documents(store.all_records(),'admin',store.kind,v4.TODAY)}
 ban=banned();ban_sets=[set(b.split()) for b in ban]
 def fresh(q):return key(q) not in ban and not v4.near_duplicate(q,ban_sets)
 items=[]  # (role, question, action, doc_types, private, query, category, origin)
 for role,q,action,types,private in HAND:items.append((role,q,action,types,private,q,'all','v5_hand'))
 reports=sorted(d for d in docs if docs[d]['doc_type']=='monthly_report');fields=list(SAY)
 for doc in reports:
  p=period(docs[doc])
  for f1,f2 in rng.sample(list(itertools.combinations(fields,2)),4):
   m1,m2=rng.choice(SAY[f1]),rng.choice(SAY[f2]);q=rng.choice(TWO).format(p=p,m1=m1,m2=m2,M1=cap(m1))
   items.append(('admin',q,'answer',['monthly_report'],False,q,'all','v5_two_metrics'))
   if rng.random()<0.5:items.append(('admin',dirty(q,rng),'answer',['monthly_report'],False,q,'all','v5_dirty_metric'))
  for f in rng.sample(fields,3):
   m=rng.choice(SAY[f]);q=rng.choice(SINGLE).format(p=p,m=m,M=cap(m))
   items.append(('admin',dirty(q,rng),'answer',['monthly_report'],False,q,'all','v5_dirty_metric'))
 for a,b in rng.sample(list(itertools.combinations(reports,2)),36):
  m=rng.choice(SAY[rng.choice(fields)]);q=rng.choice(CALC).format(m=m,M=cap(m),a=period(docs[a]),b=period(docs[b]))
  items.append(('admin',q,'deferred',[],False,q,'all','v5_calc'))
 for d in rng.sample([d for d in docs.values() if d['doc_type']=='product' and d.get('category')=='laptop'],18):
  for k in rng.sample(list(LAPTOP_LABELS),3):
   if f'{d["title"]}: {k}: ' not in d['text']:continue
   q=rng.choice(ATTR).format(p=d['title'],a=LAPTOP_LABELS[k]);items.append(('customer',dirty(q,rng),'answer',['product'],False,q,'laptop','v5_dirty_product'))
 out=[];stats=Counter()
 for role,q,action,types,private,query,category,origin in items:
  if not fresh(q) or not fresh(query):stats['dropped_overlap']+=1;continue
  route=dict(action=action,query=query,doc_types=types,category=category,task='lookup',strict_filters=False,private_request=private)
  calls=[c for c in v4.capture(q,role,route,lambda payload:None) if c[0]=='router']
  if not calls:stats['no_router_call:'+origin]+=1;continue
  _,system,payload,target=calls[0]
  out.append(v4.example('router',system,payload,target,dict(origin=origin,entity='route:'+action,split=split_of(q),role=role,question=q)));stats[origin]+=1
 base={s:[json.loads(l) for l in (SRC/f'{s}.jsonl').read_text(encoding='utf8').splitlines() if l.strip()] for s in ('train','dev')}
 OUT.mkdir(parents=True,exist_ok=True);counts={}
 for s in ('train','dev'):
  rows=base[s]+[e for e in out if e['split']==s];rng.shuffle(rows);counts[s]=len(rows)
  with (OUT/f'{s}.jsonl').open('w',encoding='utf8') as f:
   for e in rows:f.write(json.dumps(e,ensure_ascii=False)+'\n')
 digest={s:hashlib.sha256((OUT/f'{s}.jsonl').read_bytes()).hexdigest() for s in ('train','dev')}
 card=dict(created='2026-10-29',seed=SEED,base='finetune_qwen_20261028_v4 (unchanged)',counts=counts,new_examples=dict(stats),
  by_action=dict(Counter(json.loads(e['messages'][2]['content'])['action'] for e in out)),sha256=digest,
  serve='OLLAMA_MODEL (router/non-product); keep OLLAMA_SELECTOR_MODEL=v1',
  labels_from='router spec + shop DB report periods/product fields; no model answers; questions of all evaluation banks (incl. expansion_20261029 both splits) excluded by exact and near match')
 (OUT/'DATA_CARD.json').write_text(json.dumps(card,ensure_ascii=False,indent=1),encoding='utf8')
 print(json.dumps(card,ensure_ascii=False,indent=1))
if __name__=='__main__':main()
