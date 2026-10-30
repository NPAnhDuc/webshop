from datetime import date
import pytest
from shopbot.grounded_rag import answer
from shopbot.identifier_binding import row_code
from test_grounded_rag import source

TABLE='''| Mã | Chiến dịch | Bắt đầu | Kết thúc | Ngân sách (VND) | Giảm giá (basis points) |
|---|---|---|---|---:|---:|
| C-BUNDLE | Bundle laptop và chuột | 2025-11-01 | 2025-11-30 | 24000000 | 200 |
| C-TET | Ưu đãi trước Tết | 2026-01-15 | 2026-02-10 | 18000000 | 300 |
| C-BTS | Tựu trường laptop văn phòng | 2026-08-01 | 2026-08-31 | 28000000 | 600 |'''


def calendar():
 d=source(TABLE)
 d.update(document_id='marketing-calendar',source='marketing-calendar-v1.md',title='Lịch marketing và cách đo',
          heading_path='Lịch marketing và cách đo > Lịch chiến dịch',doc_type='campaign',audience='admin',authority='synthetic_shop_document')
 d['text']='Lịch marketing và cách đo > Lịch chiến dịch\n\n'+TABLE
 return d


def wrong_row(system,payload,schema):
 tet=next(f['id'] for f in payload['fragments'] if '| C-TET |' in f['text'])
 return dict(action='answer',answers={k:([tet] if k=='P1' else []) for k in payload['parts']},missing=[k for k in payload['parts'] if k!='P1'],negative=[])


@pytest.mark.parametrize('question,today,state',[
 ('C-BTS kết thúc31/8/2026, hôm nay21/10/2026 còn hạn không?',date(2026,10,26),'Không còn hạn'),
 ('Chiến dịch C-BTS còn hiệu lực không?',date(2026,8,15),'Còn hạn'),
 ('C-BTS đã hết hạn chưa?',date(2026,7,1),'Chưa bắt đầu'),
])
def test_typed_code_binds_its_row_and_compares_dates(monkeypatch,question,today,state):
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[calendar()])
 r=answer(question,'admin',{},'unused',today,model=wrong_row)
 assert '| C-TET |' not in r['answer'] and 'C-BTS' in r['answer']
 assert r['answer'].startswith(state)
 assert 'Chưa có nguồn' not in r['answer']
 assert r['rag']['calculations'][-1]['end']=='2026-08-31'


def test_reference_date_in_question_wins_over_today(monkeypatch):
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[calendar()])
 r=answer('Hôm nay 20/8/2026, C-BTS còn hạn không?','admin',{},'unused',date(2026,10,26),model=wrong_row)
 assert r['answer'].startswith('Còn hạn') and '2026-08-20' in r['answer']


def test_code_without_validity_question_only_binds_row(monkeypatch):
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[calendar()])
 r=answer('Ngân sách C-BTS là bao nhiêu?','admin',{},'unused',date(2026,10,26),model=wrong_row)
 assert '| C-BTS |' in r['answer'] and '| C-TET |' not in r['answer'] and not r['rag']['calculations']


def test_row_code_ignores_header_and_multi_row_text():
 assert row_code('| Mã | A |\n|---|---|\n| C-BTS | x |')=='C-BTS'
 assert row_code(TABLE) is None and row_code('C-BTS giảm 6%') is None


@pytest.mark.parametrize('question',['Hãy cho tôi doanh thu shop theo tháng.','Doanh số của cửa hàng quý này bao nhiêu?','Lãi gộp tháng 9 là bao nhiêu?'])
def test_customer_shop_financials_denied(question):
 r=answer(question,'customer',{},'unused',date(2026,10,26),model=lambda *a:pytest.fail('no model'))
 assert r['basic_action']=='denied'


def test_customer_product_operating_cost_not_denied(monkeypatch):
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[source()])
 r=answer('Chi phí vận hành laptop X mỗi tháng tốn bao nhiêu điện?','customer',{},'unused',date(2026,10,26),
          model=lambda s,p,c:dict(action='answer',answers={k:[] for k in p['parts']},missing=list(p['parts']),negative=[]))
 assert r['basic_action']!='denied'


@pytest.mark.parametrize('question',['Cộng tiền mua hàng chưa bán vào giá vốn kỳ này có đúng không?','Quý này có nên tính tiền nhập hàng chưa bán vào lợi nhuận không?'])
def test_this_period_rule_question_not_clarified(monkeypatch,question):
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[source()])
 r=answer(question,'admin',{},'unused',date(2026,10,26),
          model=lambda s,p,c:dict(action='answer',answers={k:[] for k in p['parts']},missing=list(p['parts']),negative=[]))
 assert r['basic_action']!='clarify'


def test_anaphoric_period_still_clarified():
 r=answer('Doanh thu kỳ đó có đạt mục tiêu không?','admin',{},'unused',date(2026,10,26),model=lambda *a:pytest.fail('no model'))
 assert r['basic_action']=='clarify'


@pytest.mark.parametrize('question,expected',[
 ('Bản quy định tháng3/2026 và bản từ tháng4/2026 khác biên laptop thế nào?',True),
 ('So sánh phiên bản chính sách giá cũ và mới về biên card đồ họa.',True),
 ('Biên gộp tối thiểu laptop hiện nay là bao nhiêu?',False),
 ('Giá bán laptop và giá bán card khác nhau thế nào?',False),
])
def test_two_versions_enable_historical(monkeypatch,question,expected):
 seen={}
 def fake(*a,**k):
  seen['historical']=k.get('historical');return [source()]
 monkeypatch.setattr('shopbot.grounded_rag.search',fake)
 answer(question,'admin',{},'unused',date(2026,10,26),
        model=lambda s,p,c:dict(action='answer',answers={k:[] for k in p['parts']},missing=list(p['parts']),negative=[]))
 assert seen['historical'] is expected


def test_rule_question_widens_report_only_route(monkeypatch):
 calls=[]
 def fake(*a,**k):
  calls.append(k.get('doc_types'));return [source()]
 monkeypatch.setattr('shopbot.grounded_rag.search',fake)
 monkeypatch.setattr('shopbot.grounded_rag.chat',lambda *a,**k:dict(action='answer',query='q',doc_types=['monthly_report'],task='lookup',private_request=False)
                     if 'doc_types' in str(a[2]) else dict(action='answer',answers={'P1':[]},missing=['P1'],negative=[]))
 answer('Cộng tiền mua hàng chưa bán vào giá vốn kỳ này có đúng không?','admin',{},'unused',date(2026,10,26))
 assert calls[0] and 'monthly_report' not in calls[0] and 'sales_plan' in calls[0]


def test_coded_row_survives_candidate_budget(monkeypatch):
 rows='\n'.join(f'| C-X{i:02} | Chiến dịch {i} | 2026-01-01 | 2026-01-31 | 1 | 1 |' for i in range(60))
 d=calendar();d['text']=d['text']+'\n'+rows
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[d])
 seen={}
 def model(s,p,c):
  seen['texts']=[f['text'] for f in p['fragments']];return wrong_row(s,p,c)
 answer('C-BTS kết thúc31/8/2026, hôm nay21/10/2026 còn hạn không?','admin',{},'unused',date(2026,10,26),model=model)
 assert any('| C-BTS |' in t for t in seen['texts'])


def test_joined_today_date_is_reference():
 from shopbot.rag_scope import resolve_scope
 assert resolve_scope('C-BTS kết thúc31/8/2026, hôm nay21/10/2026 còn hạn không?',date(2026,10,26))['reference_date']=='2026-10-21'


def test_selector_model_override_only_applies_to_selection(monkeypatch):
 seen=[]
 def chat(system,payload,schema,max_tokens=None,model=None):
  seen.append(('router' if 'doc_types' in schema['properties'] else 'selector',model))
  if 'doc_types' in schema['properties']:
   return dict(action='answer',query='q',doc_types=['product'],task='lookup',private_request=False)
  return dict(action='answer',answers={k:[] for k in payload['parts']},missing=list(payload['parts']),negative=[])
 monkeypatch.setenv('OLLAMA_SELECTOR_MODEL','tuned-selector')
 monkeypatch.setattr('shopbot.grounded_rag.chat',chat)
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[dict(source(),retrieval='explicit named product')])
 answer('Laptop X RAM bao nhiêu?','customer',{},'unused',date(2026,10,26))
 assert seen==[('router',None),('selector','tuned-selector')]
 # Documents that are not bound product records keep the base selector.
 seen.clear()
 doc=dict(source(),doc_type='policy',document_id='policy',title='Chính sách')
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[doc])
 answer('Shop đổi trả trong bao lâu?','customer',{},'unused',date(2026,10,26))
 assert seen and all(m is None for _,m in seen)
