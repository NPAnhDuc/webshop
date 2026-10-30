from datetime import date
import pytest
from shopbot.grounded_rag import answer
from test_grounded_rag import source

HEADER='| Mã | Chiến dịch | Bắt đầu | Kết thúc | Ngân sách (VND) | Giảm giá (basis points) |'
ROW='| C-BTS | Tựu trường laptop văn phòng | 2026-08-01 | 2026-08-31 | 28000000 | 600 |'
TABLE=HEADER+'\n|---|---|---|---|---:|---:|\n'+ROW

def run(monkeypatch,question,table=TABLE):
 d=source(table);d.update(document_id='marketing-calendar',source='marketing-calendar-v1.md',title='Lịch marketing và cách đo',heading_path='Lịch marketing và cách đo > Lịch chiến dịch',version=1,doc_type='marketing',audience='admin',authority='synthetic_shop_document')
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[d])
 def advisory(system,payload,schema):
  ids=[v['id'] for v in payload['fragments']]
  return dict(action='answer',answers={k:ids[:1] for k in payload['parts']},missing=[],negative=[])
 return answer(question,'admin',{},'unused',date(2026,10,24),model=advisory)

@pytest.mark.parametrize('question',[
 'Lịch C-BTS áp dụng cho cả laptop gaming hay chỉ nhóm cụ thể?',
 'Chiến dịch này áp dụng cho tất cả sản phẩm không?',
 'Chương trình này có điều kiện nhóm hàng nào?',
])
def test_campaign_title_alone_does_not_prove_product_eligibility(monkeypatch,question):
 r=run(monkeypatch,question)
 assert r['rag']['answerability']=='partial'
 assert r['rag']['unanswered']
 assert 'Tựu trường laptop văn phòng' in r['answer']
 assert 'dữ liệu mô phỏng' in r['answer']

@pytest.mark.parametrize('question',[
 'Lịch C-BTS bắt đầu và kết thúc khi nào?',
 'Ngân sách của chiến dịch C-BTS bao nhiêu?',
 'Chiến dịch C-BTS tên là gì?',
])
def test_schedule_budget_and_name_remain_supported(monkeypatch,question):
 r=run(monkeypatch,question)
 assert r['rag']['answerability']=='full'

@pytest.mark.parametrize('table',[
 '| Mã | Nhóm hàng áp dụng |\n|---|---|\n| C-BTS | Laptop văn phòng |',
 '| Mã | Điều kiện |\n|---|---|\n| C-BTS | Chỉ laptop văn phòng, không áp dụng gaming |',
 'C-BTS chỉ áp dụng cho laptop văn phòng, không áp dụng laptop gaming.',
])
def test_explicit_eligibility_evidence_is_not_blanket_rejected(monkeypatch,table):
 r=run(monkeypatch,'Chiến dịch C-BTS áp dụng cho laptop gaming không?',table)
 assert r['rag']['answerability']=='full'
