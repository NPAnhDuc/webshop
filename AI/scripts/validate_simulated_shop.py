"""Independent reconciliation of generated tables and executable SQL export."""
from collections import defaultdict, deque
from datetime import date
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/business_sql/scenario_v1'


def validate(folder=OUT):
    folder = Path(folder)
    db = sqlite3.connect(f'file:{(folder/"shop.sqlite").as_posix()}?mode=ro',uri=True)
    db.row_factory = sqlite3.Row
    failures=[]
    checks=[]
    def check(name, condition):
        checks.append(name)
        if not condition: failures.append(name)
    def zero(name, sql): check(name,db.execute(sql).fetchone()[0]==0)
    check('sqlite_integrity',db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
    check('foreign_keys',not db.execute('PRAGMA foreign_key_check').fetchall())
    source=[json.loads(s) for s in (ROOT/'data/structured/processed/product_catalog.jsonl').read_text(encoding='utf-8').splitlines()]
    ids={r['record_id'] for r in source}
    actual={r[0] for r in db.execute('SELECT sku FROM products')}
    check('exact_catalog_identity',ids==actual and len(ids)>=60)
    stored={r['sku']:json.loads(r['record_json']) for r in db.execute('SELECT * FROM product_facts')}
    check('source_facts_unchanged',all(stored[r['record_id']]==r for r in source))
    zero('line_revenue_arithmetic','SELECT COUNT(*) FROM order_items WHERE revenue<>quantity*list_price-discount OR discount<0')
    zero('sale_ledger_matches_items','''SELECT COUNT(*) FROM order_items i JOIN orders o ON o.id=i.order_id
        LEFT JOIN financial_ledger l ON l.id=i.id WHERE l.id IS NULL OR l.kind<>'sale'
        OR l.sku<>i.sku OR l.day<>o.day OR l.quantity<>i.quantity OR l.revenue<>i.revenue OR l.cost<>i.cost''')
    zero('return_ledger_matches_returns','''SELECT COUNT(*) FROM returns r LEFT JOIN financial_ledger l ON l.id=r.id
        WHERE l.id IS NULL OR l.kind<>'return' OR l.sku<>r.sku OR l.day<>r.day
        OR l.quantity<>-r.quantity OR l.revenue<>-r.refund OR l.cost<>-r.cost_reversal''')
    check('no_unexplained_ledger_rows',db.execute('SELECT COUNT(*) FROM financial_ledger').fetchone()[0]==
          db.execute('SELECT (SELECT COUNT(*) FROM order_items)+(SELECT COUNT(*) FROM returns)').fetchone()[0])
    zero('return_line_identity_and_timing','''SELECT COUNT(*) FROM returns r JOIN order_items i ON i.id=r.item_id
        JOIN orders o ON o.id=i.order_id WHERE r.sku<>i.sku OR r.quantity<>i.quantity OR r.refund<>i.revenue
        OR r.day<=o.day OR julianday(r.day)-julianday(o.day)>14
        OR r.cost_reversal<>CASE WHEN r.restock=1 THEN i.cost ELSE 0 END''')
    zero('purchase_receipt_identity_and_timing','''SELECT COUNT(*) FROM receipts r JOIN purchase_lines l ON l.id=r.line_id
        JOIN purchase_orders p ON p.id=l.po_id WHERE r.sku<>l.sku OR r.quantity<>l.quantity
        OR r.unit_cost<>l.unit_cost OR r.day<>p.due_day OR r.day<p.ordered_day''')
    zero('sale_movement_matches_line','''SELECT COUNT(*) FROM order_items i LEFT JOIN inventory_moves m
        ON m.source_id=i.id AND m.kind='sale' WHERE m.id IS NULL OR m.sku<>i.sku
        OR m.delta<>-i.quantity OR m.cost_delta<>-i.cost''')
    check('sale_movement_cardinality',db.execute("SELECT COUNT(*) FROM inventory_moves WHERE kind='sale'").fetchone()[0]==db.execute('SELECT COUNT(*) FROM order_items').fetchone()[0])
    lots=defaultdict(deque);fifo_valid=True
    for move in db.execute('SELECT * FROM inventory_moves ORDER BY day,id'):
        sku=move['sku'];qty=move['delta'];amount=move['cost_delta']
        if qty>0:
            if amount%qty: fifo_valid=False
            lots[sku].append([qty,amount//qty])
        elif qty<0:
            expected=0;need=-qty
            while need and lots[sku]:
                lot=lots[sku][0];take=min(need,lot[0]);expected+=take*lot[1]
                lot[0]-=take;need-=take
                if not lot[0]: lots[sku].popleft()
            if need or expected!=-amount: fifo_valid=False
    check('independent_fifo_replay',fifo_valid)
    quantity=defaultdict(int);value=defaultdict(int);daily={}
    for move in db.execute('SELECT * FROM inventory_moves ORDER BY day,id'):
        sku=move['sku'];quantity[sku]+=move['delta'];value[sku]+=move['cost_delta']
        if quantity[sku]<0 or value[sku]<0: failures.append('negative_intraday_inventory:'+sku)
        daily[(move['day'],sku)]=(quantity[sku],value[sku])
    running={s:(0,0) for s in ids}
    valid_snapshots=True
    for snap in db.execute('SELECT * FROM inventory_daily ORDER BY day,sku'):
        key=(snap['day'],snap['sku'])
        if key in daily: running[snap['sku']]=daily[key]
        if running[snap['sku']]!=(snap['quantity'],snap['value']): valid_snapshots=False
    check('every_daily_stock_and_valuation_reconciles',valid_snapshots)
    period=dict(db.execute("SELECT key,value FROM metadata WHERE key IN ('period_start','period_end')"))
    days=(date.fromisoformat(period['period_end'])-date.fromisoformat(period['period_start'])).days+1
    check('one_complete_year_daily_snapshots',days>=365 and db.execute('SELECT COUNT(*) FROM inventory_daily').fetchone()[0]==days*len(ids))
    check('current_stock_matches_final_snapshot',all(p['stock']==quantity[p['sku']] for p in db.execute('SELECT sku,stock FROM products')))
    opening=db.execute("SELECT COALESCE(SUM(cost_delta),0) FROM inventory_moves WHERE kind='opening'").fetchone()[0]
    purchases=db.execute('SELECT COALESCE(SUM(quantity*unit_cost),0) FROM receipts').fetchone()[0]
    cogs=db.execute('SELECT SUM(cost) FROM financial_ledger').fetchone()[0]
    check('fifo_inventory_cost_conservation',opening+purchases-cogs==sum(value.values()))
    pnl=list(db.execute('SELECT * FROM monthly_pnl ORDER BY month'))
    check('twelve_closed_months',len(pnl)==12)
    check('pnl_exact_revenue',sum(r['net_revenue'] for r in pnl)==db.execute('SELECT SUM(revenue) FROM financial_ledger').fetchone()[0])
    check('pnl_exact_profit',all(r['gross_profit']==r['net_revenue']-r['net_cogs'] and
          r['operating_profit_before_interest_tax']==r['gross_profit']-r['operating_expenses'] for r in pnl))
    check('purchases_not_double_counted_as_expense',not db.execute("SELECT 1 FROM operating_expenses WHERE category IN ('purchase','cogs')").fetchone())
    check('cash_flow_adds_back_non_cash_depreciation',all(r['operating_cash_flow_assuming_cash_settlement']==
          r['net_revenue']-r['purchases_received']-r['operating_expenses']+db.execute(
              "SELECT COALESCE(SUM(amount),0) FROM operating_expenses WHERE substr(day,1,7)=? AND category='depreciation'",(r['month'],)).fetchone()[0] for r in pnl))
    check('all_trade_dates_within_scenario',all(period['period_start']<=r[0]<=period['period_end'] for r in db.execute('SELECT day FROM financial_ledger')))
    replica=sqlite3.connect(':memory:')
    replica.executescript((folder/'shop.sqlite.sql').read_text(encoding='utf-8'))
    check('sql_dump_executes_with_valid_foreign_keys',not replica.execute('PRAGMA foreign_key_check').fetchall())
    for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        check('sql_roundtrip_'+name,[tuple(r) for r in db.execute(f'SELECT * FROM {name} ORDER BY rowid')]==replica.execute(f'SELECT * FROM {name} ORDER BY rowid').fetchall())
    replica.close()
    coverage=db.execute('SELECT COUNT(DISTINCT sku) FROM order_items').fetchone()[0]
    report={'passed':not failures,'checks':len(checks),'failures':failures,'products':len(ids),
            'products_with_sales':coverage,'unknown_product_ids':0 if ids==actual else None,
            'period_days':days,'opening_inventory_value':opening,'purchases_received':purchases,
            'net_cogs':cogs,'closing_inventory_value':sum(value.values()),
            'synthetic':True,'not_evidence_of_real_market_accuracy':True}
    (folder/'validation_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    db.close()
    if failures: raise AssertionError(report)
    return report


if __name__=='__main__': print(json.dumps(validate(),ensure_ascii=False))
