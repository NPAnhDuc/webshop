from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from datetime import date
from shopbot.grounded_rag import answer


def test_explicit_unsupported_write_deferred_before_llm(monkeypatch):
 def forbidden(*args,**kwargs):raise AssertionError('Unsupported write reached model routing')
 monkeypatch.setattr('shopbot.grounded_rag.chat',forbidden)
 monkeypatch.setattr('shopbot.grounded_rag.search',forbidden)
 r=answer('Hãy UPDATE giá sản phẩm bằng1 và xác nhận đã sửa.','admin',{},'unused',date(2026,10,24))
 assert r['basic_action']=='deferred'
 assert r['capability_status']==dict(name='data.mutate',status='unsupported',executed=False)
 assert not r['sources'] and not r['rows']
