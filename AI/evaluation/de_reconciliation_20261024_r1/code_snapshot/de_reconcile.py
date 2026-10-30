"""Reconcile captured receipts, movements, FIFO and daily inventory without writes.

FIFO replay adapts the existing validate_simulated_shop.py algorithm; no fixed
14-day returns policy or one-year requirement is carried into this gate.
"""
from collections import defaultdict,deque
from contextlib import closing
from datetime import date
import json
from pathlib import Path
import sqlite3
from .de_snapshot import digest,stable_sqlite,verify_raw,write_new

SCHEMA={
    'products':{'sku':'text','stock':'int'},
    'purchase_orders':{'id':'text','ordered_day':'date'},
    'purchase_lines':{'id':'text','po_id':'text','sku':'text','quantity':'int','unit_cost':'int'},
    'receipts':{'id':'text','line_id':'text','day':'date','sku':'text','quantity':'int','unit_cost':'int'},
    'returns':{'id':'text','day':'date','sku':'text','quantity':'int','cost_reversal':'int','restock':'int'},
    'order_items':{'id':'text','order_id':'text','sku':'text','quantity':'int','cost':'int'},
    'orders':{'id':'text','day':'date'},
    'financial_ledger':{'id':'text','sku':'text','cost':'int'},
    'inventory_moves':{'id':'int','day':'date','sku':'text','delta':'int','cost_delta':'int','kind':'text','source_id':'text'},
    'inventory_daily':{'day':'date','sku':'text','quantity':'int','value':'int'},
    'metadata':{'key':'text','value':'text'},
}


def reconcile_database(path):
    path=Path(path).resolve(strict=True);stable_sqlite(path);before=digest(path)
    checks=[];samples=[];totals={}
    def record(name,violations,items=()):
        checks.append(dict(check=name,passed=violations==0,violations=violations))
        for item in items:
            if len(samples)<25:samples.append(dict(check=name,**item))
    with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as con:
        con.row_factory=sqlite3.Row;con.execute('PRAGMA query_only=ON');con.execute('BEGIN')
        valid=True
        for table,fields in SCHEMA.items():
            columns={r['name'] for r in con.execute(f'PRAGMA table_info("{table}")')}
            missing=set(fields)-columns;record('schema:'+table,len(missing));valid &= not missing
        if valid:
            rows={table:con.execute('SELECT '+','.join('"'+k+'"' for k in fields)+f' FROM "{table}"').fetchall() for table,fields in SCHEMA.items()}
            for table,fields in SCHEMA.items():
                bad=[]
                for i,row in enumerate(rows[table]):
                    for key,kind in fields.items():
                        v=row[key];ok=type(v) is int if kind=='int' else isinstance(v,str) and bool(v.strip())
                        if kind=='date' and ok:
                            try:ok=date.fromisoformat(v).isoformat()==v
                            except ValueError:ok=False
                        if not ok:bad.append(dict(table=table,row=i,column=key))
                record('typed_values:'+table,len(bad),bad);valid &= not bad
        if valid:
            def sql_check(name,sql):
                failed=con.execute(sql).fetchall();record(name,len(failed),[dict(r) for r in failed[:25]])
            for table,fields in SCHEMA.items():
                keys=['id'] if 'id' in fields else (['sku'] if table=='products' else ['key'] if table=='metadata' else ['day','sku'])
                columns=','.join('"'+key+'"' for key in keys)
                sql_check('unique_identity:'+table,f'SELECT {columns} FROM "{table}" GROUP BY {columns} HAVING COUNT(*)>1')
            for table in ['purchase_lines','receipts','returns','order_items','inventory_moves','inventory_daily']:
                sql_check('known_sku:'+table,f'''SELECT x.sku FROM {table} x LEFT JOIN products p ON p.sku=x.sku WHERE p.sku IS NULL''')
            sql_check('purchase_lines_valid','''SELECT l.id FROM purchase_lines l LEFT JOIN purchase_orders p ON p.id=l.po_id
                WHERE p.id IS NULL OR l.quantity<=0 OR l.unit_cost<=0''')
            sql_check('receipts_match_purchase_lines','''SELECT r.id FROM receipts r LEFT JOIN purchase_lines l ON l.id=r.line_id
                LEFT JOIN purchase_orders p ON p.id=l.po_id WHERE l.id IS NULL OR p.id IS NULL OR r.sku<>l.sku
                OR r.quantity<=0 OR r.unit_cost<=0 OR r.unit_cost<>l.unit_cost OR r.day<p.ordered_day''')
            sql_check('receipts_do_not_exceed_order','''SELECT l.id FROM purchase_lines l JOIN receipts r ON r.line_id=l.id
                GROUP BY l.id,l.quantity HAVING SUM(r.quantity)>l.quantity''')
            sql_check('sale_movement_matches_source','''SELECT i.id FROM order_items i LEFT JOIN orders o ON o.id=i.order_id
                LEFT JOIN inventory_moves m ON m.kind='sale' AND m.source_id=i.id WHERE o.id IS NULL OR m.id IS NULL
                OR m.sku<>i.sku OR m.day<>o.day OR m.delta<>-i.quantity OR m.cost_delta<>-i.cost''')
            sql_check('receipt_movement_matches_source','''SELECT r.id FROM receipts r LEFT JOIN inventory_moves m
                ON m.kind='receipt' AND m.source_id=r.id WHERE m.id IS NULL OR m.sku<>r.sku OR m.day<>r.day
                OR m.delta<>r.quantity OR m.cost_delta<>r.quantity*r.unit_cost''')
            sql_check('return_movement_matches_source','''SELECT r.id FROM returns r LEFT JOIN inventory_moves m
                ON m.kind='return' AND m.source_id=r.id WHERE (r.restock=1 AND (m.id IS NULL OR m.sku<>r.sku
                OR m.day<>r.day OR m.delta<>r.quantity OR m.cost_delta<>r.cost_reversal))
                OR (r.restock=0 AND m.id IS NOT NULL) OR r.restock NOT IN (0,1)''')
            sql_check('one_movement_per_source','''SELECT kind,source_id FROM inventory_moves WHERE kind<>'opening'
                GROUP BY kind,source_id HAVING COUNT(*)<>1''')
            sql_check('explained_movements','''SELECT m.id FROM inventory_moves m
                LEFT JOIN order_items i ON m.kind='sale' AND i.id=m.source_id
                LEFT JOIN receipts r ON m.kind='receipt' AND r.id=m.source_id
                LEFT JOIN returns t ON m.kind='return' AND t.id=m.source_id AND t.restock=1
                WHERE m.kind NOT IN ('opening','sale','receipt','return')
                OR (m.kind<>'opening' AND i.id IS NULL AND r.id IS NULL AND t.id IS NULL)''')
            moves=sorted(rows['inventory_moves'],key=lambda r:(r['day'],r['id']))
            products={r['sku']:r['stock'] for r in rows['products']}
            lots=defaultdict(deque);quantity=defaultdict(int);value=defaultdict(int);daily={}
            fifo_bad=[];sign_bad=[];negative=[]
            for m in moves:
                sku=m['sku'];qty=m['delta'];amount=m['cost_delta'];kind=m['kind']
                if not ((kind in ('opening','receipt','return') and qty>0 and amount>=0)
                        or (kind=='sale' and qty<0 and amount<=0)):
                    sign_bad.append(dict(id=m['id']))
                if qty>0:
                    if amount<0 or amount%qty:fifo_bad.append(dict(id=m['id'],reason='invalid_incoming_unit_cost'))
                    else:lots[sku].append([qty,amount//qty])
                elif qty<0:
                    expected=0;need=-qty
                    while need and lots[sku]:
                        lot=lots[sku][0];take=min(need,lot[0]);expected+=take*lot[1]
                        lot[0]-=take;need-=take
                        if not lot[0]:lots[sku].popleft()
                    if need or expected!=-amount:fifo_bad.append(dict(id=m['id'],reason='shortage_or_cost_mismatch'))
                quantity[sku]+=qty;value[sku]+=amount
                if quantity[sku]<0 or value[sku]<0:negative.append(dict(id=m['id']))
                daily[(m['day'],sku)]=(quantity[sku],value[sku])
            record('movement_signs',len(sign_bad),sign_bad)
            record('independent_fifo_replay',len(fifo_bad),fifo_bad)
            record('no_negative_intraday_inventory',len(negative),negative)
            events=sorted(daily.items());position=0;running={sku:(0,0) for sku in products};bad=[]
            snaps=sorted(rows['inventory_daily'],key=lambda r:(r['day'],r['sku']))
            for snap in snaps:
                while position<len(events) and events[position][0][0]<=snap['day']:
                    (_,sku),state=events[position];running[sku]=state;position+=1
                if running.get(snap['sku'])!=(snap['quantity'],snap['value']):bad.append(dict(day=snap['day'],sku=snap['sku']))
            record('daily_snapshots_match_movements',len(bad),bad)
            record('current_stock_matches_replay',sum(stock!=quantity[sku] for sku,stock in products.items()))
            metadata={r['key']:r['value'] for r in rows['metadata']}
            period=None
            try:
                start=date.fromisoformat(metadata['period_start']);end=date.fromisoformat(metadata['period_end'])
                if start>end or start.isoformat()!=metadata['period_start'] or end.isoformat()!=metadata['period_end']:
                    raise ValueError('Invalid declared period')
                period=dict(start=start.isoformat(),end=end.isoformat(),days=(end-start).days+1)
            except (ValueError,KeyError):pass
            record('declared_inventory_period',int(period is None))
            if period:
                keys={(r['day'],r['sku']) for r in snaps}
                record('unique_daily_snapshots',len(snaps)-len(keys))
                record('daily_snapshot_coverage',int(len(keys)!=period['days']*len(products)))
                record('inventory_dates_within_period',sum(not period['start']<=r['day']<=period['end'] for r in [*moves,*snaps]))
            opening=sum(m['cost_delta'] for m in moves if m['kind']=='opening')
            purchases=sum(r['quantity']*r['unit_cost'] for r in rows['receipts'])
            cogs=sum(r['cost'] for r in rows['financial_ledger']);closing_value=sum(value.values())
            record('inventory_cost_conservation',int(opening+purchases-cogs!=closing_value))
            totals=dict(opening_inventory_value=opening,purchases_received=purchases,net_cogs=cogs,
                closing_inventory_value=closing_value,closing_units=sum(quantity.values()),
                inventory_rows=len(snaps),movement_rows=len(moves),declared_period=period)
    stable_sqlite(path)
    if digest(path)!=before:raise RuntimeError('Source changed during reconciliation')
    return dict(schema='de-reconciliation-v1',source=dict(path=str(path),sha256=before),
        implementation_sha256=digest(__file__),passed=all(c['passed'] for c in checks),checks=checks,
        quarantine_samples=samples,totals=totals,curated_published=False,source_modified=False,
        limitations=['FIFO assumes integer unit costs and one movement per source event, with restocked returns appended as new lots.',
          'No fixed return window or forced 365-day period. Inventory coverage follows the declared period, not imputed sales days.',
          'Currency, tax, external truth, business policy and CSV/Excel mapping remain unverified.'])


def reconcile_revision(revision,output):
    revision=Path(revision).resolve(strict=True);output=Path(output).resolve()
    if output.exists():raise ValueError('Reconciliation revision exists; preserve previous results')
    raw=verify_raw(revision);raw_hash=digest(revision/'manifest.json')
    stage_hash=digest(revision/'staging/manifest.json')
    stage=json.loads((revision/'staging/manifest.json').read_text(encoding='utf-8'))
    if stage.get('raw_manifest_sha256')!=raw_hash or stage.get('source_id')!=raw['source_id']:
        raise ValueError('Staging does not belong to this raw revision')
    for key,name in [('audit_sha256','audit.json'),('quarantine_sha256','quarantine.json')]:
        if digest(revision/'staging'/name)!=stage[key]:raise ValueError('Staging artifact changed')
    if stage.get('status')!='audit_passed_pending_reconciliation':raise ValueError('Staging audit must pass before reconciliation')
    audit=json.loads((revision/'staging/audit.json').read_text(encoding='utf-8'))
    if audit.get('passed') is not True:raise ValueError('Failed staging audit')
    result=reconcile_database(revision/'raw/ledger.sqlite')
    verify_raw(revision)
    if digest(revision/'manifest.json')!=raw_hash:raise RuntimeError('Raw manifest changed')
    if digest(revision/'staging/manifest.json')!=stage_hash:raise RuntimeError('Staging manifest changed')
    for key,name in [('audit_sha256','audit.json'),('quarantine_sha256','quarantine.json')]:
        if digest(revision/'staging'/name)!=stage[key]:raise RuntimeError('Staging artifact changed during reconciliation')
    output.mkdir(parents=True,exist_ok=False);write_new(output/'reconciliation.json',result)
    write_new(output/'quarantine.json',result['quarantine_samples'])
    manifest=dict(schema='de-reconciliation-manifest-v1',source_id=raw['source_id'],data_kind=raw['data_kind'],
        raw_manifest_sha256=raw_hash,staging_manifest_sha256=stage_hash,
        reconciliation_sha256=digest(output/'reconciliation.json'),
        status='reconciled_pending_curated_design' if result['passed'] else 'quarantined',curated_published=False)
    write_new(output/'manifest.json',manifest)
    return result
