"""Read-only ledger staging audit. Never clean, merge or publish source records."""
from datetime import date,datetime,timezone
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

FIELDS={
    'products':{'sku':'text'},
    'orders':{'id':'text','day':'date'},
    'order_items':{'id':'text','order_id':'text','sku':'text','quantity':'int','list_price':'int','discount':'int','revenue':'int','cost':'int'},
    'returns':{'id':'text','item_id':'text','day':'date','sku':'text','quantity':'int','refund':'int','cost_reversal':'int','restock':'int'},
    'financial_ledger':{'id':'text','day':'date','sku':'text','quantity':'int','revenue':'int','cost':'int','kind':'text'},
    'operating_expenses':{'id':'text','day':'date','amount':'int'},
}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def audit_database(path,catalog_path=None,sample_limit=25):
    path=Path(path).resolve(strict=True)
    if type(sample_limit) is not int or not 0<=sample_limit<=100:raise ValueError('Sample limit must be 0..100')
    if Path(str(path)+'-wal').exists() and Path(str(path)+'-wal').stat().st_size:
        raise ValueError('Export a stable SQLite snapshot before auditing an active WAL database')
    before=sha(path);checks=[];quarantine=[];profiles={}
    catalog_source=None
    if catalog_path is not None:
        catalog_path=Path(catalog_path).resolve(strict=True)
        blob=catalog_path.read_bytes();snapshot=json.loads(blob)
        if snapshot.get('schema')!='agent-catalog-v1':raise ValueError('Expected public catalog schema agent-catalog-v1')
        catalog_source=dict(path=str(catalog_path),sha256=hashlib.sha256(blob).hexdigest())
    def record(name,count,samples=()):
        checks.append(dict(check=name,passed=count==0,violations=count))
        for item in samples:
            if len(quarantine)<sample_limit:quarantine.append(dict(check=name,**item))
    with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)) as con:
        con.row_factory=sqlite3.Row
        con.execute('PRAGMA query_only=ON');con.execute('BEGIN')
        integrity=con.execute('PRAGMA integrity_check').fetchall()
        record('sqlite_integrity',0 if len(integrity)==1 and integrity[0][0]=='ok' else len(integrity))
        fk=con.execute('PRAGMA foreign_key_check').fetchall()
        record('foreign_keys',len(fk),[dict(table=r[0],rowid=r[1]) for r in fk])
        tables={r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        schema_ok=True
        for table,fields in FIELDS.items():
            columns={r['name'] for r in con.execute(f'PRAGMA table_info("{table}")')}
            missing=set(fields)-columns
            record('schema:'+table,len(missing),[dict(table=table,column=c) for c in sorted(missing)])
            schema_ok &= not missing
        if schema_ok:
            for table,fields in FIELDS.items():
                rows=con.execute('SELECT '+','.join('"'+k+'"' for k in fields)+f' FROM "{table}"').fetchall()
                invalid=[];dates=[];seen=set();duplicates=[]
                for row in rows:
                    identifier=row['sku'] if table=='products' else row['id']
                    if identifier in seen:duplicates.append(dict(table=table,id=identifier))
                    seen.add(identifier)
                    for key,kind in fields.items():
                        v=row[key];valid=(type(v) is int) if kind=='int' else isinstance(v,str) and bool(v.strip())
                        if kind=='date' and valid:
                            try:valid=date.fromisoformat(v).isoformat()==v
                            except ValueError:valid=False
                            if valid:dates.append(v)
                        if not valid:invalid.append(dict(table=table,id=identifier,column=key))
                record('typed_values:'+table,len(invalid),invalid)
                record('unique_identity:'+table,len(duplicates),duplicates)
                profiles[table]=dict(rows=len(rows),first_observed_day=min(dates) if dates else None,
                                     last_observed_day=max(dates) if dates else None)
            def sql_check(name,query):
                rows=con.execute(query).fetchall()
                record(name,len(rows),[dict(r) for r in rows[:sample_limit]])
            for table in ['order_items','returns','financial_ledger']:
                sql_check('known_sku:'+table,f'''SELECT x.id,'{table}' AS source_table FROM {table} x
                    LEFT JOIN products p ON p.sku=x.sku WHERE p.sku IS NULL''')
            sql_check('line_arithmetic','''SELECT id FROM order_items WHERE quantity<=0 OR list_price<0 OR discount<0
                OR revenue<0 OR cost<0 OR revenue<>quantity*list_price-discount''')
            sql_check('ledger_signs','''SELECT id FROM financial_ledger WHERE NOT (
                (kind='sale' AND quantity>0 AND revenue>=0 AND cost>=0) OR
                (kind='return' AND quantity<0 AND revenue<=0 AND cost<=0))''')
            sql_check('nonnegative_expenses','SELECT id FROM operating_expenses WHERE amount<0')
            sql_check('sale_matches_source','''SELECT i.id FROM order_items i LEFT JOIN orders o ON o.id=i.order_id
                LEFT JOIN financial_ledger l ON l.id=i.id WHERE o.id IS NULL OR l.id IS NULL OR l.kind<>'sale'
                OR l.sku<>i.sku OR l.day<>o.day OR l.quantity<>i.quantity OR l.revenue<>i.revenue OR l.cost<>i.cost''')
            sql_check('return_matches_source','''SELECT r.id FROM returns r LEFT JOIN order_items i ON i.id=r.item_id
                LEFT JOIN orders o ON o.id=i.order_id LEFT JOIN financial_ledger l ON l.id=r.id
                WHERE i.id IS NULL OR l.id IS NULL OR r.sku<>i.sku OR r.quantity<=0 OR r.quantity>i.quantity
                OR r.refund<0 OR r.refund>i.revenue OR r.cost_reversal<0 OR r.cost_reversal>i.cost
                OR r.restock NOT IN (0,1) OR (r.restock=0 AND r.cost_reversal<>0) OR r.day<o.day
                OR l.kind<>'return' OR l.sku<>r.sku OR l.day<>r.day OR l.quantity<>-r.quantity
                OR l.revenue<>-r.refund OR l.cost<>-r.cost_reversal''')
            sql_check('return_totals_within_sale','''SELECT i.id FROM order_items i JOIN returns r ON r.item_id=i.id
                GROUP BY i.id,i.quantity,i.revenue,i.cost HAVING SUM(r.quantity)>i.quantity
                OR SUM(r.refund)>i.revenue OR SUM(r.cost_reversal)>i.cost''')
            sql_check('no_unexplained_ledger_rows','''SELECT l.id FROM financial_ledger l
                LEFT JOIN order_items i ON l.kind='sale' AND i.id=l.id
                LEFT JOIN returns r ON l.kind='return' AND r.id=l.id WHERE i.id IS NULL AND r.id IS NULL''')
            if catalog_path is not None:
                ids=[p['id'] for p in snapshot['products']];actual={r[0] for r in con.execute('SELECT sku FROM products')}
                record('catalog_unique_ids',len(ids)-len(set(ids)))
                mismatch=actual.symmetric_difference(ids)
                record('exact_catalog_sku_identity',len(mismatch),[dict(sku=k) for k in sorted(mismatch)])
            if 'metadata' in tables:
                metadata=dict(con.execute("SELECT key,value FROM metadata WHERE key IN ('source','scenario_id')"))
            else:metadata={}
            totals=dict(con.execute('''SELECT COUNT(*) rows,SUM(quantity) net_units,SUM(revenue) net_revenue,
                SUM(cost) net_cogs,SUM(revenue-cost) gross_profit FROM financial_ledger''').fetchone()) if all(
                    c['passed'] for c in checks if c['check'].startswith('typed_values:')) else None
        else:metadata={};totals={}
    if before!=sha(path):raise RuntimeError('Source changed during audit; report not valid')
    if Path(str(path)+'-wal').exists() and Path(str(path)+'-wal').stat().st_size:
        raise RuntimeError('WAL appeared during audit; export a stable snapshot and audit a new revision')
    if catalog_source and sha(catalog_path)!=catalog_source['sha256']:raise RuntimeError('Catalog changed during audit')
    source=dict(path=str(path),sha256=before,metadata=metadata,
                data_kind='simulation' if metadata.get('source')=='demo' else 'unverified_import')
    if catalog_source:source['catalog']=catalog_source
    return dict(schema='de-ledger-audit-v1',implementation_sha256=sha(Path(__file__)),
        audited_at=datetime.now(timezone.utc).isoformat(),source=source,
        passed=all(c['passed'] for c in checks),checks=checks,profiles=profiles,observed_totals=totals,
        quarantine_samples=quarantine,quarantine_sample_limit=sample_limit,
        source_modified=False,curated_published=False,
        limitations=['Staging audit only; not a full ingestion or accounting certification.',
          'Does not replay FIFO, reconcile receipts/inventory or verify tax, currency and business policy.',
          'Observed date span and row counts do not establish complete coverage; absent dates are not filled with zero.',
          'Rows are never deleted, deduplicated, imputed or merged automatically.'])
