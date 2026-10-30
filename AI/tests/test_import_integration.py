import os,json
from pathlib import Path
from shopbot.store import ROOT,initialize
from shopbot.engine import Engine
from scripts.import_shop_data import import_new

def test_import_new_database(monkeypatch):
    import tempfile
    import shutil
    folder=Path(tempfile.mkdtemp(prefix='import-test-',dir=ROOT/'data'))
    try:
        source=folder/'input.json'
        source.write_text(json.dumps({'products':[{'sku':'REAL-1','name':'Shop product','price':100,'stock':1,'panel':'IPS','ram':16,'battery':50,'weight':1.4,'category':'laptop'}],'sales':[]}),encoding='utf-8')
        db=folder/'shop.db'
        result=import_new(source,db)
        monkeypatch.setenv('LLM_PROVIDER','demo')
        monkeypatch.delenv('KEV_BASE_URL',raising=False)
        engine=Engine(db)
        answer=engine.ask('laptop')
        assert [p['sku'] for p in answer['rows']]==['REAL-1']
        assert 'shop đã nhập' in answer['sources'][0]['source']
        assert 'input.json' not in answer['sources'][0]['source']
        assert result['products']==1
        assert engine.customer.mentioned_skus('REAL-1 còn hàng?')==['REAL-1']
        assert engine.customer.mentioned_skus('REAL-10 còn hàng?')==[]
    finally:
        assert folder.resolve().is_relative_to((ROOT/'data').resolve())
        shutil.rmtree(folder)
