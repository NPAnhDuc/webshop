"""Frozen source-field binding probes; injected wrong evidence, no model calls."""
import json,sys
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import shopbot.grounded_rag as rag

def doc(text,kind='procedure',authority='shop_policy'):
 return dict(document_id='fixture',title='Nguồn thử',source='fixture.md',version=1,section=1,chunk_id='fixture',
  text='Nguồn thử\n\n'+text,audience='admin',data_kind='demo',doc_type=kind,authority=authority,status='approved',effective_from='2026-01-01',effective_to=None)

CASES=[
 ('MOQ nhà cung cấp là bao nhiêu?','Nhà cung cấp có lead time 4 ngày.',False),
 ('Số lượng đặt hàng tối thiểu nhà cung cấp là bao nhiêu?','Nhà cung cấp có lead time 9 ngày.',False),
 ('MOQ nhà cung cấp là bao nhiêu?','Bảo hành cần liên hệ nhân viên.',False),
 ('Lead time nhà cung cấp bao lâu?','MOQ nhà cung cấp là 10 sản phẩm.',False),
 ('Thời gian giao hàng của nhà cung cấp là bao lâu?','Bảo hành là 12 tháng.',False),
 ('MOQ nhà cung cấp là bao nhiêu?','MOQ nhà cung cấp là 10 sản phẩm.',True),
 ('Số lượng đặt tối thiểu của nhà cung cấp là bao nhiêu?','Số lượng đặt tối thiểu là 7 sản phẩm.',True),
 ('Lead time nhà cung cấp bao lâu?','Thời gian giao hàng của nhà cung cấp là 6 ngày.',True),
]
rows=[]
for question,text,expect_claim in CASES:
 d=doc(text);rag.search=lambda *a,**k:[d]
 def wrong(system,payload,schema):return dict(action='answer',answers={k:[payload['fragments'][0]['id']] for k in payload['parts']},missing=[],negative=[])
 r=rag.answer(question,'admin',{},'unused',date(2026,10,24),model=wrong)
 actual=bool(r['rag']['claims'])
 rows.append(dict(question=question,source=text,expected_claim=expect_claim,actual_claim=actual,answer=r['answer'],passed=actual==expect_claim))
with (Path(__file__).parent/sys.argv[1]).open('x',encoding='utf-8') as f:json.dump(dict(passed=sum(x['passed'] for x in rows),total=len(rows),model_calls=0,cases=rows),f,ensure_ascii=False,indent=2)
print(sum(x['passed'] for x in rows),len(rows))
