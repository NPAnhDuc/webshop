import json
import sqlite3
import pytest
from shopbot.de_reconcile import SCHEMA,reconcile_database,reconcile_revision
from shopbot.de_snapshot import capture_raw,stage_audit


@pytest.fixture
def source(tmp_path):
    path=tmp_path/'ledger.sqlite'
    # A three-day fixture proves the generic reconciliation does not require
    # the old generator's 365-day period or full-refund/window policy.
    with sqlite3.connect(path) as con:
        for table,fields in SCHEMA.items():
            extras={'products':{},'returns':{'item_id':'text','refund':'int'},
                    'order_items':{'list_price':'int','discount':'int','revenue':'int'},
                    'financial_ledger':{'day':'date','quantity':'int','revenue':'int','kind':'text'},
                    'operating_expenses':{}}
            columns=dict(fields,**extras.get(table,{}))
            con.execute('CREATE TABLE "'+table+'" ('+','.join('"'+k+'" '+('INTEGER' if t=='int' else 'TEXT') for k,t in columns.items())+')')
        con.execute('CREATE TABLE operating_expenses(id TEXT,day TEXT,amount INTEGER)')
        con.executemany('INSERT INTO metadata VALUES (?,?)',[('source','demo'),('period_start','2026-01-01'),('period_end','2026-01-03')])
        con.execute("INSERT INTO products VALUES ('p1',5)")
        con.execute("INSERT INTO purchase_orders VALUES ('po1','2026-01-02')")
        con.execute("INSERT INTO purchase_lines VALUES ('pl1','po1','p1',2,70)")
        con.execute("INSERT INTO receipts VALUES ('rc1','pl1','2026-01-03','p1',2,70)")
        con.execute("INSERT INTO orders VALUES ('o1','2026-01-02')")
        con.execute("INSERT INTO order_items VALUES ('i1','o1','p1',1,60,100,0,100)")
        con.execute("INSERT INTO returns VALUES ('r1','2026-01-03','p1',1,60,1,'i1',100)")
        con.executemany('INSERT INTO inventory_moves VALUES (?,?,?,?,?,?,?)',[
            (1,'2026-01-01','p1',3,180,'opening','p1'),
            (2,'2026-01-02','p1',-1,-60,'sale','i1'),
            (3,'2026-01-03','p1',2,140,'receipt','rc1'),
            (4,'2026-01-03','p1',1,60,'return','r1')])
        con.executemany('INSERT INTO inventory_daily VALUES (?,?,?,?)',[
            ('2026-01-01','p1',3,180),('2026-01-02','p1',2,120),('2026-01-03','p1',5,320)])
        con.executemany('INSERT INTO financial_ledger VALUES (?,?,?,?,?,?,?)',[
            ('i1','p1',60,'2026-01-02',1,100,'sale'),('r1','p1',-60,'2026-01-03',-1,-100,'return')])
    return path


def failures(report):return {c['check'] for c in report['checks'] if not c['passed']}


def test_receipt_return_fifo_daily_snapshots_and_value_conservation(source):
    before=source.read_bytes();r=reconcile_database(source)
    assert r['passed'] and source.read_bytes()==before
    assert r['totals']==dict(opening_inventory_value=180,purchases_received=140,net_cogs=0,
        closing_inventory_value=320,closing_units=5,inventory_rows=3,movement_rows=4,
        declared_period=dict(start='2026-01-01',end='2026-01-03',days=3))
    assert not r['curated_published']


@pytest.mark.parametrize('sql,expected',[
    ("UPDATE receipts SET unit_cost=71",'receipts_match_purchase_lines'),
    ("UPDATE purchase_lines SET quantity=1",'receipts_do_not_exceed_order'),
    ("DELETE FROM inventory_moves WHERE kind='receipt'",'receipt_movement_matches_source'),
    ("DELETE FROM inventory_daily WHERE day='2026-01-02'",'daily_snapshot_coverage'),
    ("UPDATE inventory_daily SET value=value+1 WHERE day='2026-01-03'",'daily_snapshots_match_movements'),
    ("UPDATE inventory_moves SET delta=-4 WHERE kind='sale'",'no_negative_intraday_inventory'),
    ("UPDATE inventory_moves SET cost_delta=-61 WHERE kind='sale'",'independent_fifo_replay'),
    ("UPDATE products SET stock=999",'current_stock_matches_replay'),
    ("UPDATE receipts SET day='2026-02-30'",'typed_values:receipts'),
    ("INSERT INTO receipts SELECT * FROM receipts",'unique_identity:receipts'),
])
def test_corruption_is_detected_and_source_not_repaired(source,sql,expected):
    with sqlite3.connect(source) as con:con.execute(sql)
    before=source.read_bytes();r=reconcile_database(source)
    assert not r['passed'] and expected in failures(r) and source.read_bytes()==before


def test_fifo_detects_wrong_unit_cost_even_when_book_conservation_matches(source):
    with sqlite3.connect(source) as con:
        con.execute('UPDATE order_items SET cost=61')
        con.execute("UPDATE financial_ledger SET cost=61 WHERE kind='sale'")
        con.execute("UPDATE inventory_moves SET cost_delta=-61 WHERE kind='sale'")
        con.execute("UPDATE inventory_daily SET value=value-1 WHERE day>'2026-01-01'")
    r=reconcile_database(source)
    assert 'independent_fifo_replay' in failures(r)
    assert 'inventory_cost_conservation' not in failures(r)


def test_non_restock_return_keeps_cogs_and_does_not_add_stock(source):
    with sqlite3.connect(source) as con:
        con.execute('UPDATE returns SET restock=0,cost_reversal=0')
        con.execute("UPDATE financial_ledger SET cost=0 WHERE kind='return'")
        con.execute("DELETE FROM inventory_moves WHERE kind='return'")
        con.execute("UPDATE inventory_daily SET quantity=4,value=260 WHERE day='2026-01-03'")
        con.execute('UPDATE products SET stock=4')
    r=reconcile_database(source)
    assert r['passed'] and r['totals']['net_cogs']==60 and r['totals']['closing_inventory_value']==260


def test_late_unexplained_stock_cannot_be_relabelled_as_opening_balance(source):
    with sqlite3.connect(source) as con:
        con.execute("UPDATE inventory_moves SET day='2026-01-02' WHERE kind='opening'")
        con.execute("UPDATE inventory_daily SET quantity=0,value=0 WHERE day='2026-01-01'")
    r=reconcile_database(source)
    assert failures(r)=={'opening_moves_at_period_start'}


def test_revision_gate_uses_existing_raw_and_does_not_overwrite(source,tmp_path):
    catalog=tmp_path/'catalog.json';catalog.write_text(json.dumps(dict(schema='agent-catalog-v1',products=[dict(id='p1')])),encoding='utf-8')
    raw=tmp_path/'raw_revision';capture_raw(source,catalog,raw,'fixture');stage_audit(raw)
    out=tmp_path/'reconciled';r=reconcile_revision(raw,out)
    assert r['passed'] and json.loads((out/'manifest.json').read_text(encoding='utf-8'))['status']=='reconciled_pending_curated_design'
    with pytest.raises(ValueError,match='exists'):reconcile_revision(raw,out)
    with (raw/'staging/audit.json').open('a',encoding='utf-8') as f:f.write(' ')
    with pytest.raises(ValueError,match='changed'):reconcile_revision(raw,tmp_path/'other')
