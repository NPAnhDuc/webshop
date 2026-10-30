from datetime import date
from shopbot.grounded_rag import answer
from test_grounded_rag import source


def test_swapped_month_evidence_is_bound_to_user_part_before_render(monkeypatch):
 docs=[]
 for month,value in [('2026-05',1175440000),('2026-08',1427320000)]:
  d=source(f'Doanh thu thuần: {value} VND.')
  d.update(document_id='monthly-report-'+month,source='monthly-report-'+month+'-v1.md',title='Báo cáo tháng '+month,chunk_id='chunk-'+month,doc_type='monthly_report',audience='admin',authority='synthetic_shop_document')
  docs.append(d)
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:docs)
 def swapped(system,payload,schema):
  may=next(f['id'] for f in payload['fragments'] if '1175440000' in f['text'])
  aug=next(f['id'] for f in payload['fragments'] if '1427320000' in f['text'])
  return dict(action='answer',answers={'P1':[aug],'P2':[may]},missing=[],negative=[])
 r=answer('Đặt cạnh nhau doanh thu thuần trong báo cáo tháng 5/2026 và tháng 8/2026, không tính chênh lệch.','admin',{},'unused',date(2026,10,24),model=swapped)
 mapping={f['id']:f['document_id'] for f in r['rag']['available_fields']}
 assert [mapping[i] for i in r['rag']['part_evidence']['P1']]==['monthly-report-2026-05']
 assert [mapping[i] for i in r['rag']['part_evidence']['P2']]==['monthly-report-2026-08']
 assert r['rag']['answerability']=='full' and len(r['rag']['claims'])==2


def test_identical_values_from_distinct_periods_remain_two_claims(monkeypatch):
 docs=[]
 for month in ['2026-05','2026-08']:
  d=source('Doanh thu thuần: 100 VND.')
  d.update(document_id='monthly-report-'+month,source='monthly-report-'+month+'-v1.md',title='Báo cáo tháng '+month,chunk_id='chunk-'+month,doc_type='monthly_report',audience='admin',authority='synthetic_shop_document')
  docs.append(d)
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:docs)
 def both(system,payload,schema):
  ids=[f['id'] for f in payload['fragments'] if 'Doanh thu thuần:' in f['text']]
  return dict(action='answer',answers={k:ids for k in payload['parts']},missing=[],negative=[])
 r=answer('Đặt cạnh nhau doanh thu thuần trong báo cáo tháng 5/2026 và tháng 8/2026, không tính chênh lệch.','admin',{},'unused',date(2026,10,24),model=both)
 assert len(r['rag']['claims'])==2 and len(r['sources'])==2
 assert len(r['rag']['part_evidence']['P1'])==len(r['rag']['part_evidence']['P2'])==1
