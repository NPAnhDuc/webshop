import hashlib
import json
import sqlite3
import pytest
from shopbot.de_audit import audit_database,FIELDS


@pytest.fixture
def source(tmp_path):
    path=tmp_path/'ledger.sqlite'
    with sqlite3.connect(path) as con:
        for table,fields in FIELDS.items():
            columns=','.join('"'+k+'" '+('INTEGER' if t=='int' else 'TEXT') for k,t in fields.items())
            con.execute('CREATE TABLE "'+table+'" ('+columns+')')
        con.execute('CREATE TABLE metadata(key TEXT,value TEXT)')
        con.execute("INSERT INTO metadata VALUES ('source','demo')")
        con.execute("INSERT INTO products VALUES ('p1')")
        con.execute("INSERT INTO orders VALUES ('o1','2026-01-01')")
        con.execute("INSERT INTO order_items VALUES ('i1','o1','p1',2,100,10,190,120)")
        con.execute("INSERT INTO returns VALUES ('r1','i1','2026-01-03','p1',1,95,60,1)")
        con.execute("INSERT INTO financial_ledger VALUES ('i1','2026-01-01','p1',2,190,120,'sale')")
        con.execute("INSERT INTO financial_ledger VALUES ('r1','2026-01-03','p1',-1,-95,-60,'return')")
        con.execute("INSERT INTO operating_expenses VALUES ('e1','2026-01-02',10)")
    catalog=tmp_path/'catalog.json'
    catalog.write_text(json.dumps(dict(schema='agent-catalog-v1',products=[{'id':'p1'}])),encoding='utf-8')
    return path,catalog


def failed(report):return {c['check'] for c in report['checks'] if not c['passed']}


def test_readonly_audit_reports_source_hash_observed_coverage_and_exact_money(source):
    db,catalog=source;before=db.read_bytes();r=audit_database(db,catalog)
    assert r['passed'] and db.read_bytes()==before
    assert r['source']['sha256']==hashlib.sha256(before).hexdigest()
    assert r['source']['data_kind']=='simulation'
    assert r['observed_totals']==dict(rows=2,net_units=1,net_revenue=95,net_cogs=60,gross_profit=35)
    assert r['profiles']['financial_ledger']['first_observed_day']=='2026-01-01'
    assert r['profiles']['financial_ledger']['last_observed_day']=='2026-01-03'
    assert not r['curated_published'] and not r['source_modified']


@pytest.mark.parametrize('sql,check',[
    ("UPDATE orders SET day='2026-02-30'",'typed_values:orders'),
    ("UPDATE order_items SET cost=NULL",'typed_values:order_items'),
    ("UPDATE order_items SET quantity=1.5",'typed_values:order_items'),
    ("UPDATE order_items SET revenue=revenue+1",'line_arithmetic'),
    ("UPDATE financial_ledger SET revenue=revenue+1 WHERE kind='sale'",'sale_matches_source'),
    ("UPDATE returns SET sku='unknown'",'known_sku:returns'),
    ("UPDATE order_items SET order_id='missing'",'sale_matches_source'),
    ("INSERT INTO products VALUES ('p1')",'unique_identity:products'),
])
def test_bad_records_are_flagged_without_silently_repairing_source(source,sql,check):
    db,catalog=source
    with sqlite3.connect(db) as con:con.execute(sql)
    before=db.read_bytes();r=audit_database(db,catalog,sample_limit=2)
    assert not r['passed'] and check in failed(r)
    assert len(r['quarantine_samples'])<=2 and db.read_bytes()==before
    if check.startswith('typed_values:'):assert r['observed_totals'] is None


def test_schema_failure_with_catalog_still_returns_an_audit_not_a_crash(source):
    db,catalog=source
    with sqlite3.connect(db) as con:con.execute('DROP TABLE returns')
    r=audit_database(db,catalog)
    assert not r['passed'] and 'schema:returns' in failed(r)
    assert r['source']['catalog']['sha256']


def test_catalog_identity_is_checked_without_merging_sources(source):
    db,catalog=source
    catalog.write_text(json.dumps(dict(schema='agent-catalog-v1',products=[{'id':'other'}])),encoding='utf-8')
    r=audit_database(db,catalog)
    assert 'exact_catalog_sku_identity' in failed(r)
    with sqlite3.connect(db) as con:assert con.execute('SELECT sku FROM products').fetchall()==[('p1',)]


def test_multiple_individually_valid_returns_cannot_over_refund_one_sale(source):
    db,catalog=source
    with sqlite3.connect(db) as con:
        for identifier in ('r2','r3'):
            con.execute("INSERT INTO returns VALUES (?, 'i1','2026-01-04','p1',1,95,60,1)",(identifier,))
            con.execute("INSERT INTO financial_ledger VALUES (?,'2026-01-04','p1',-1,-95,-60,'return')",(identifier,))
    r=audit_database(db,catalog)
    assert 'return_totals_within_sale' in failed(r)


def test_active_wal_is_rejected_instead_of_mislabelled_as_a_stable_snapshot(source):
    db,catalog=source
    con=sqlite3.connect(db);con.execute('PRAGMA journal_mode=WAL');con.execute("INSERT INTO products VALUES ('p2')");con.commit()
    try:
        with pytest.raises(ValueError,match='stable'):audit_database(db,catalog)
    finally:con.close()
