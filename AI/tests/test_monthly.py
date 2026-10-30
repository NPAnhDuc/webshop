from datetime import date
import json
from pathlib import Path
import pytest
from shopbot.store import initialize,connect
from shopbot.monthly import MonthlyUpdater,atomic_json,active_documents,read_json


@pytest.fixture
def updater(tmp_path):
    db=tmp_path/'data/structured/shop.db'
    initialize(db)
    return MonthlyUpdater(db,root=tmp_path,today=date(2026,10,16))


def batch(updater,month='2026-09',sales=None):
    with connect(updater.db,readonly=True) as con:
        products=[dict(r) for r in con.execute('SELECT * FROM products')]
    value={'ready':True,'complete':month<updater.today.strftime('%Y-%m'),'month':month,'data_kind':'demo','inventory_as_of':month+'-01','products':products,
           'sales':sales if sales is not None else [dict(id='new-1',day=month+'-03',sku='DEMO-A',quantity=1,revenue=100,cost=80)]}
    path=updater.structured/'monthly'/month/'shop.json'
    atomic_json(path,value)
    return path,value


def document(updater,version=1,body='Bảo hành 24 tháng.',audience='customer',effective='2026-09-01',until=None,status='approved',identifier='policy'):
    folder=updater.unstructured/'monthly/2026-09'
    folder.mkdir(parents=True,exist_ok=True)
    file=folder/f'{identifier}-{version}.md'
    file.write_text(body,encoding='utf-8')
    manifest=folder/'manifest.json'
    payload=read_json(manifest,{'ready':True,'data_kind':'demo','documents':[]})
    entry=dict(file=file.name,document_id=identifier,version=version,audience=audience,effective_from=effective,effective_to=until,status=status)
    payload['documents']=[d for d in payload['documents'] if (d['document_id'],d['version'])!=(identifier,version)]+[entry]
    atomic_json(manifest,payload)
    return file


def scalar(updater,query):
    with connect(updater.db,readonly=True) as con:return con.execute(query).fetchone()[0]


def test_monthly_exact_idempotent_and_snapshot(updater):
    original=scalar(updater,'SELECT SUM(revenue) FROM sales')
    batch(updater)
    result=updater.process('2026-09')
    assert result['inserted']==1
    assert scalar(updater,'SELECT SUM(revenue) FROM sales')==original+100
    assert (updater.root/result['snapshot']).is_file()
    assert updater.process('2026-09')['status']=='unchanged'
    assert scalar(updater,'SELECT SUM(revenue) FROM sales')==original+100
    assert list((updater.unstructured/'generated/2026-09').glob('*.md'))


def test_conflicting_ids_rollback_all(updater):
    path,value=batch(updater)
    updater.process('2026-09')
    original=scalar(updater,'SELECT SUM(revenue) FROM sales')
    value['sales']=[dict(id='new-2',day='2026-09-04',sku='DEMO-A',quantity=1,revenue=999,cost=80),dict(value['sales'][0],revenue=777)]
    value['products'][0]['stock']=999
    atomic_json(path,value)
    with pytest.raises(ValueError,match='Conflicting'):updater.process('2026-09')
    assert scalar(updater,'SELECT SUM(revenue) FROM sales')==original
    assert scalar(updater,"SELECT stock FROM products WHERE sku='DEMO-A'")!=999


def test_historical_inventory_does_not_replace_current(updater):
    path,value=batch(updater)
    value['products'][0]['stock']=999
    atomic_json(path,value)
    result=updater.process('2026-09')
    assert not result['catalog_updated']
    assert scalar(updater,"SELECT stock FROM products WHERE sku='DEMO-A'")==12


def test_current_sales_deferred_then_closed(updater):
    batch(updater,'2026-10')
    before=scalar(updater,'SELECT COUNT(*) FROM sales')
    assert updater.process('2026-10')['sales_deferred']
    assert scalar(updater,'SELECT COUNT(*) FROM sales')==before
    updater.today=date(2026,11,1)
    assert updater.process('2026-10')['inserted']==1
    assert scalar(updater,'SELECT COUNT(*) FROM sales')==before+1


def test_current_month_can_be_explicitly_loaded(updater):
    batch(updater,'2026-10')
    assert updater.process('2026-10',allow_current=True)['inserted']==1
    # A later automatic pass must not undo the manual update.
    assert updater.process('2026-10')['status']=='unchanged'


def test_calendar_rollover_does_not_claim_data_complete(updater):
    path,value=batch(updater,'2026-10')
    assert not updater.process('2026-10',allow_current=True)['complete']
    updater.today=date(2026,11,1)
    result=updater.process('2026-10')
    assert result['status']=='updated' and not result['complete']
    value['complete']=True;atomic_json(path,value)
    assert updater.process('2026-10')['complete']


def test_kind_and_future_date_rejected(updater):
    path,value=batch(updater)
    value['data_kind']='shop';atomic_json(path,value)
    with pytest.raises(ValueError,match='never mix'):updater.process('2026-09')
    value['data_kind']='demo';value['sales'][0]['day']='2026-10-17';atomic_json(path,value)
    with pytest.raises(ValueError,match='outside'):updater.process('2026-09')


def test_document_versions_acl_drafts_expiry(updater):
    document(updater)
    document(updater,2,'Bảo hành 36 tháng.',effective='2026-10-20',until='2026-10-25')
    document(updater,1,'Nội bộ mã SECRET.',audience='admin',identifier='private')
    document(updater,1,'Bản nháp 99 tháng.',status='draft',identifier='draft')
    updater.process('2026-09')
    docs=read_json(updater.index_path)['documents']
    a=active_documents(docs,'customer','demo',date(2026,10,16))
    assert len(a)==1 and '24' in a[0]['text']
    b=active_documents(docs,'customer','demo',date(2026,10,21))
    assert len(b)==1 and '36' in b[0]['text']
    assert active_documents(docs,'customer','demo',date(2026,10,26))==[]
    assert not any(d['document_id']=='draft' for d in docs)


def test_same_document_version_cannot_change(updater):
    file=document(updater)
    updater.process('2026-09')
    before=updater.index_path.read_bytes()
    file.write_text('Bảo hành 99 tháng.',encoding='utf-8')
    with pytest.raises(ValueError,match='version bump'):updater.process('2026-09')
    assert updater.index_path.read_bytes()==before


def test_monthly_retrieval_uses_updated_policy(updater,monkeypatch):
    import shopbot.retrieval as retrieval
    monkeypatch.setattr(retrieval,'ROOT',updater.root)
    folder=updater.unstructured/'public';folder.mkdir(parents=True)
    (folder/'chinh-sach-mau.md').write_text('Bảo hành cũ 24 tháng.',encoding='utf-8')
    document(updater,2,'Bảo hành mới 36 tháng.',identifier='chinh-sach-mau')
    document(updater,1,'Bí mật ALPHAPRIVATE.',audience='admin',identifier='private')
    updater.process('2026-09')
    result=retrieval.search('Bảo hành','customer',db_path=updater.db,as_of=updater.today)
    assert any('36' in r['text'] for r in result)
    assert not any('24' in r['text'] or 'ALPHAPRIVATE' in r['text'] for r in result)
    assert not retrieval.search('ALPHAPRIVATE','customer',db_path=updater.db,as_of=updater.today)


def test_expired_policy_does_not_revive_static_policy(updater,monkeypatch):
    import shopbot.retrieval as retrieval
    monkeypatch.setattr(retrieval,'ROOT',updater.root)
    folder=updater.unstructured/'public';folder.mkdir(parents=True)
    (folder/'policy.md').write_text('Bảo hành cũ 24 tháng.',encoding='utf-8')
    document(updater,2,'Bảo hành 36 tháng.',until='2026-10-10')
    updater.process('2026-09')
    assert retrieval.search('Bảo hành','customer',db_path=updater.db,as_of=updater.today)==[]


def test_sale_ids_from_seed_are_not_recounted(updater):
    with connect(updater.db,readonly=True) as con:
        row=dict(con.execute("SELECT * FROM sales WHERE day='2026-09-01' AND sku='DEMO-A'").fetchone())
    row['id']='demo:2026-09-01:DEMO-A'
    batch(updater,sales=[row])
    assert updater.process('2026-09')['duplicates']==1


def test_monthly_report_is_searchable_and_private(updater,monkeypatch):
    import shopbot.retrieval as retrieval
    monkeypatch.setattr(retrieval,'ROOT',updater.root)
    batch(updater)
    updater.process('2026-09')
    question='Báo cáo tháng 9 năm 2026'
    assert any(d.get('doc_type')=='monthly_report' for d in retrieval.search(question,'admin',db_path=updater.db,as_of=updater.today))
    assert not any(d.get('doc_type')=='monthly_report' for d in retrieval.search(question,'customer',db_path=updater.db,as_of=updater.today))


def test_bad_month_quarantined_and_future_skipped(updater):
    path,value=batch(updater);value['sales'][0]['quantity']=-1;atomic_json(path,value)
    (updater.structured/'monthly/2030-01').mkdir(parents=True)
    result=updater.run_pending()
    assert len(result)==1 and result[0]['status']=='rejected'
    assert list((updater.runtime/'errors').glob('*.json'))


def test_bad_document_month_does_not_block_other_months(updater):
    folder=updater.unstructured/'monthly/2026-08';folder.mkdir(parents=True)
    atomic_json(folder/'manifest.json',{'ready':True,'data_kind':'demo','documents':[{'status':'approved'}]})
    batch(updater)
    results={r['month']:r for r in updater.run_pending()}
    assert results['2026-08']['status']=='rejected'
    assert results['2026-09']['status']=='updated'


def test_non_object_batch_is_quarantined(updater):
    path,_=batch(updater);atomic_json(path,[])
    assert updater.run_pending()[0]['status']=='rejected'
