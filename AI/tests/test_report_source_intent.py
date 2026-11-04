from datetime import date
from pathlib import Path
import json
import pytest
from shopbot.rag_metrics import metric_request
from shopbot.rag_scope import resolve_scope
C=json.loads((Path(__file__).resolve().parents[1]/'evaluation/report_source_intent_20261025_r1/contract.json').read_text(encoding='utf-8'))

@pytest.mark.parametrize('question',C['report_questions'])
def test_explicit_report_reading_stays_on_document_path(question):
 assert metric_request(question,'admin',resolve_scope(question,date(2026,10,24))) is None

@pytest.mark.parametrize('question',C['sql_questions'])
def test_direct_kpi_remains_on_sql_path(question):
 assert metric_request(question,'admin',resolve_scope(question,date(2026,10,24))) is not None


@pytest.mark.parametrize('question,previous,expected',[
 ('Còn giá vốn cùng tháng đó?','document','document'),
 ('Còn tháng 8/2026?','document','document'),
 ('Doanh thu tháng 9/2026 là bao nhiêu?','document','sql'),
 ('Còn laptop RAM16GB thì sao?','document','sql'),
 ('Từ dữ liệu gốc, doanh thu tháng 9/2026 bao nhiêu?','document','sql'),
 ('Theo báo cáo tháng 9/2026, giá vốn bao nhiêu?','sql','document'),
 ('Còn chính sách giao hàng?','document','sql'),
 ('Báo cáo 12/2025 ghi giá vốn thế nào?','sql','document'),
 ('Giá vốn tháng 10/2025 và tháng 3/2026 mỗi tháng bao nhiêu? Chỉ đọc số, không tính.','sql','sql'),
])
def test_source_preference_keep_reset_and_override(question,previous,expected):
 from shopbot.rag_metrics import metric_source
 assert metric_source(question,previous)==expected


@pytest.mark.parametrize('question,keys',[
 ('ky 1/2026 so hang bi tra ve la bn',['return_units']),
 ('Số sản phẩm hoàn trả tháng 10/2025 và tháng 9/2026 mỗi tháng bao nhiêu?',['return_units']),
 ('ky 3/2026 dt sau tra hang la bn',['revenue']),
 ('Kỳ 1/2026: cho tôi tiền vốn hàng bán cùng lượng đơn.',['cost','orders']),
 ('Tháng 7/2026 doanh thu sau trả hàng và lợi nhuận trước lãi vay và thuế là bao nhiêu?',['operating_profit','revenue']),
])
def test_everyday_metric_wording_reaches_sql(question,keys):
 asked,_=metric_request(question,'admin',resolve_scope(question,date(2026,10,24)))
 assert [m[0] for m in asked]==keys


def test_product_breakdown_stays_on_documents():
 assert metric_request('Doanh thu sản phẩm laptop tháng 9/2026 là bao nhiêu?','admin',resolve_scope('tháng 9/2026',date(2026,10,24))) is None


def test_two_turn_report_metric_keeps_source_and_period(monkeypatch):
 from shopbot.grounded_rag import answer
 from test_grounded_rag import source
 d=source('Doanh thu thuần: 1189908000 VND. Giá vốn: 1010759000 VND.')
 d.update(document_id='monthly-report-2026-09',source='monthly-report-2026-09-v1.md',title='Báo cáo tháng 2026-09',doc_type='monthly_report',audience='admin',authority='synthetic_shop_document')
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[d])
 monkeypatch.setattr('shopbot.rag_metrics.answer_metrics',lambda *a,**k:pytest.fail('Explicit report source must not become SQL'))
 def advisory(system,payload,schema):
  target='Giá vốn' if any('giá vốn' in part.lower() for part in payload['parts'].values()) else 'Doanh thu thuần'
  ids=[f['id'] for f in payload['fragments'] if target in f['text']]
  return dict(action='answer',answers={k:ids[:1] for k in payload['parts']},missing=[],negative=[])
 first=answer('Đọc báo cáo tháng 9/2026, doanh thu thuần được ghi bao nhiêu?','admin',{},'unused',date(2026,10,24),model=advisory)
 assert first['profile']['rag_metric_source']=='document'
 second=answer('Còn giá vốn cùng tháng đó?','admin',first['profile'],'unused',date(2026,10,24),model=advisory)
 assert second['profile']['rag_metric_source']=='document'
 assert second['profile']['rag_scope']['months']==['2026-09']
 assert '1010759000' in second['answer']
 assert '1189908000' not in second['answer']
 assert second['sources'][0]['source']=='monthly-report-2026-09-v1.md'
 assert not any('sql-financial'==s['document_id'] for s in second['sources'])
