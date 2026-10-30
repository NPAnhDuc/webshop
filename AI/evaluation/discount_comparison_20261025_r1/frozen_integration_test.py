from datetime import date
import pytest
from shopbot.grounded_rag import answer
from test_grounded_rag import source


def test_current_cap_comparison_does_not_invent_approver(monkeypatch):
 d=source('Mức giảm tối đa 6%; không cộng dồn.')
 d.update(document_id='pricing-policy',source='pricing-policy-v2.md',title='Quy định giá và biên gộp',doc_type='policy',audience='admin',authority='synthetic_shop_document',status='approved',effective_from='2026-04-01',effective_to=None)
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[d])
 def advisory(system,payload,schema):
  ids=[x['id'] for x in payload['fragments']]
  return dict(action='answer',answers={k:(ids[:1] if k=='P1' else []) for k in payload['parts']},missing=[k for k in payload['parts'] if k!='P1'],negative=[])
 r=answer('Tôi muốn giảm7%, đối chiếu trần giảm giá và người duyệt giúp tôi.','admin',{},'unused',date(2026,10,24),model=advisory)
 assert '1 điểm phần trăm' in r['answer']
 assert r['rag']['answerability']=='partial'
 assert r['rag']['unanswered']==['người duyệt giúp tôi.']
 assert r['rag']['calculations'][0]['relation']=='above'
 assert r['rag']['calculations'][0]['approval_granted'] is False
