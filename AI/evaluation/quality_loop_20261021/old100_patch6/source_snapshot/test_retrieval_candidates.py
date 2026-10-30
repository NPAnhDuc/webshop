from datetime import date
import numpy as np

from shopbot.knowledge import KnowledgeStore
from shopbot.retrieval import search
from shopbot.store import initialize


def test_sparse_identifier_survives_low_dense_scores_without_bypassing_access(tmp_path,monkeypatch):
    db=tmp_path/'shop.sqlite'
    initialize(db)
    monkeypatch.setattr('shopbot.knowledge.ROOT',tmp_path)
    monkeypatch.setattr('shopbot.retrieval.ROOT',tmp_path)
    kb=KnowledgeStore(db,root=tmp_path)
    common=dict(role='admin',doc_type='policy',audience='admin',effective_from='2025-01-01')
    kb.save('identifier-rule','Quy trình mã ZX91 được lưu tại đây.',title='Quy trình',approved=True,**common)
    kb.save('unrelated-rule','Điều kiện khác không chứa mã yêu cầu.',title='Điều kiện',approved=True,**common)
    kb.save('draft-rule','ZX91 nội dung chưa duyệt.',title='Bản nháp',approved=False,**common)
    monkeypatch.setattr('sklearn.metrics.pairwise.cosine_similarity',lambda left,right:np.zeros((1,right.shape[0])))
    monkeypatch.setattr('shopbot.dense_retrieval.dense_scores',lambda question,chunks:([0.]*len(chunks),'fixture',[False]*len(chunks)))
    args=dict(db_path=db,as_of=date(2026,10,21),doc_types=['policy'],scope={},top_k=3)
    docs=search('ZX91','admin',**args)
    assert {d['document_id'] for d in docs}=={'identifier-rule'}
    assert all(d['bm25_score']>0 and d['dense_score']==0 for d in docs)
    assert search('ZX91','customer',**args)==[]
