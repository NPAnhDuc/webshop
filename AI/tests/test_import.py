from scripts.import_shop_data import validate
import pytest

def product():
    return dict(sku='real-1',name='Laptop',price=100,stock=1,panel='IPS',ram=16,battery=50,weight=1.4,category='laptop')

def test_import_rejects_unknown_sku():
    with pytest.raises(ValueError,match='Unknown SKU'):
        validate({'products':[product()],'sales':[dict(id='a',day='2026-09-01',sku='missing',quantity=1,revenue=100,cost=80)]})

def test_import_rejects_bad_values_and_duplicate_ids():
    p=product();p['stock']=-1
    with pytest.raises(ValueError): validate({'products':[p]})
    s=dict(id='a',day='2026-09-01',sku='real-1',quantity=1,revenue=100,cost=80)
    with pytest.raises(ValueError,match='duplicate'): validate({'products':[product()],'sales':[s,s]})

def test_import_valid():
    p,s=validate({'products':[product()],'sales':[]})
    assert len(p)==1 and s==[]
