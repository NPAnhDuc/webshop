import json
import sqlite3
import pytest
from shopbot.de_audit import FIELDS
from shopbot.de_snapshot import capture_raw,verify_raw,stage_audit,digest


@pytest.fixture
def source(tmp_path):
    db=tmp_path/'source.sqlite';catalog=tmp_path/'catalog.json'
    with sqlite3.connect(db) as con:
        for table,fields in FIELDS.items():
            cols=','.join('"'+k+'" '+('INTEGER' if t=='int' else 'TEXT') for k,t in fields.items())
            con.execute('CREATE TABLE "'+table+'" ('+cols+')')
        con.execute('CREATE TABLE metadata(key TEXT,value TEXT)')
        con.execute("INSERT INTO metadata VALUES ('source','demo')")
        con.execute("INSERT INTO products VALUES ('p1')")
        con.execute("INSERT INTO orders VALUES ('o1','2026-01-01')")
        con.execute("INSERT INTO order_items VALUES ('i1','o1','p1',1,100,0,100,60)")
        con.execute("INSERT INTO financial_ledger VALUES ('i1','2026-01-01','p1',1,100,60,'sale')")
    catalog.write_text(json.dumps(dict(schema='agent-catalog-v1',products=[{'id':'p1'}])),encoding='utf-8')
    return db,catalog,tmp_path/'revision'


def test_exact_raw_copy_and_source_provenance_without_recursive_folder_copy(source):
    db,catalog,out=source;before=db.read_bytes();other=db.parent/'evaluation_gold.txt';other.write_text('do not capture')
    manifest=capture_raw(db,catalog,out,'source-a')
    assert verify_raw(out)==manifest and db.read_bytes()==before==(out/'raw/ledger.sqlite').read_bytes()
    assert manifest['artifacts']['ledger.sqlite']['sha256']==digest(db)
    assert manifest['data_kind']=='simulation' and manifest['source_id']=='source-a'
    assert set(p.name for p in (out/'raw').iterdir())=={'ledger.sqlite','catalog_public.json'}
    assert not manifest['curated_published']


def test_staging_uses_captured_bytes_not_later_live_source_changes(source):
    db,catalog,out=source;capture_raw(db,catalog,out,'source-a')
    with sqlite3.connect(db) as con:con.execute('UPDATE financial_ledger SET revenue=999')
    result=stage_audit(out)
    report=json.loads((out/'staging/audit.json').read_text(encoding='utf-8'))
    assert result['status']=='audit_passed_pending_reconciliation'
    assert report['observed_totals']['net_revenue']==100 and not result['curated_published']


def test_invalid_raw_is_preserved_and_staging_quarantined_not_published(source):
    db,catalog,out=source
    with sqlite3.connect(db) as con:con.execute('UPDATE order_items SET cost=NULL')
    original=db.read_bytes();capture_raw(db,catalog,out,'source-a')
    result=stage_audit(out)
    assert result['status']=='quarantined' and not result['curated_published']
    assert db.read_bytes()==original==(out/'raw/ledger.sqlite').read_bytes()
    assert json.loads((out/'staging/quarantine.json').read_text(encoding='utf-8'))


def test_existing_raw_and_staging_revisions_are_never_overwritten(source):
    db,catalog,out=source;capture_raw(db,catalog,out,'source-a');stage_audit(out)
    before=(out/'staging/audit.json').read_bytes()
    with pytest.raises(ValueError,match='exists'):capture_raw(db,catalog,out,'source-a')
    with pytest.raises(ValueError,match='exists'):stage_audit(out)
    assert (out/'staging/audit.json').read_bytes()==before


def test_tampered_artifact_cannot_enter_staging(source):
    db,catalog,out=source;capture_raw(db,catalog,out,'source-a')
    with (out/'raw/ledger.sqlite').open('ab') as stream:stream.write(b'tampered')
    with pytest.raises(ValueError,match='hash/size'):stage_audit(out)
    assert not (out/'staging').exists()


def test_manifest_cannot_redirect_reader_outside_revision(source):
    db,catalog,out=source;capture_raw(db,catalog,out,'source-a')
    path=out/'manifest.json';manifest=json.loads(path.read_text(encoding='utf-8'))
    manifest['artifacts']['ledger.sqlite']['path']='../../source.sqlite'
    path.write_text(json.dumps(manifest),encoding='utf-8')
    with pytest.raises(ValueError,match='path'):verify_raw(out)


def test_source_change_during_capture_leaves_failure_marker_not_completion(source,monkeypatch):
    import shopbot.de_snapshot as module
    db,catalog,out=source;original=module.shutil.copyfileobj
    def copy_then_modify(src,dst,*args):
        original(src,dst,*args)
        if src.name==str(db):
            with db.open('ab') as stream:stream.write(b'changed')
    monkeypatch.setattr(module.shutil,'copyfileobj',copy_then_modify)
    with pytest.raises(RuntimeError,match='changed'):capture_raw(db,catalog,out,'source-a')
    assert (out/'capture.failed.json').exists() and not (out/'manifest.json').exists()


def test_active_wal_is_not_copied_as_if_database_file_were_complete(source):
    db,catalog,out=source;con=sqlite3.connect(db)
    con.execute('PRAGMA journal_mode=WAL');con.execute("INSERT INTO products VALUES ('p2')");con.commit()
    try:
        with pytest.raises(ValueError,match='stable'):capture_raw(db,catalog,out,'source-a')
        assert not out.exists()
    finally:con.close()
