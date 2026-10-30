"""Build a separate admin analytics projection; never change the active bot source."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from .de_contract import assess_curated_contract
from .de_snapshot import digest, stable_sqlite, verify_raw, write_new


# Explicit projection excludes customer identifiers, addresses and arbitrary tables.
TABLES = {
    'products': {'sku': 'TEXT', 'stock': 'INTEGER'},
    'financial_ledger': {'id': 'TEXT', 'day': 'TEXT', 'sku': 'TEXT',
        'quantity': 'INTEGER', 'revenue': 'INTEGER', 'cost': 'INTEGER', 'kind': 'TEXT'},
    'operating_expenses': {'id': 'TEXT', 'day': 'TEXT', 'amount': 'INTEGER'},
    'inventory_daily': {'day': 'TEXT', 'sku': 'TEXT', 'quantity': 'INTEGER', 'value': 'INTEGER'},
}
KEYS = {'products': ['sku'], 'financial_ledger': ['id'],
        'operating_expenses': ['id'], 'inventory_daily': ['day', 'sku']}


def _read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def _projection(db, table):
    fields = ','.join('"'+field+'"' for field in TABLES[table])
    return sorted(db.execute(f'SELECT {fields} FROM "{table}"').fetchall())


def _totals(db):
    revenue, cost = db.execute('SELECT COALESCE(SUM(revenue),0),COALESCE(SUM(cost),0) FROM financial_ledger').fetchone()
    expenses = db.execute('SELECT COALESCE(SUM(amount),0) FROM operating_expenses').fetchone()[0]
    # No calendar fill: absent transaction dates/months remain absent.
    monthly = db.execute('SELECT substr(day,1,7),SUM(revenue),SUM(cost) FROM financial_ledger GROUP BY 1 ORDER BY 1').fetchall()
    monthly_expenses = db.execute('SELECT substr(day,1,7),SUM(amount) FROM operating_expenses GROUP BY 1 ORDER BY 1').fetchall()
    return dict(net_revenue=revenue, net_cogs=cost, gross_profit=revenue-cost,
        operating_expenses=expenses, operating_profit_before_interest_tax=revenue-cost-expenses,
        monthly_finance=monthly, monthly_expenses=monthly_expenses)


def build_curated(revision, reconciliation, eligibility, output):
    revision = Path(revision).resolve(strict=True)
    reconciliation = Path(reconciliation).resolve(strict=True)
    eligibility = Path(eligibility).resolve(strict=True)
    output = Path(output).resolve()
    if output.exists():
        raise ValueError('Curated revision exists; never overwrite it')
    raw = verify_raw(revision)
    upstream = [revision/'manifest.json', revision/'staging/manifest.json',
        revision/'staging/audit.json', revision/'staging/quarantine.json',
        reconciliation/'manifest.json', reconciliation/'reconciliation.json', reconciliation/'quarantine.json',
        eligibility/'manifest.json', eligibility/'contract.json', eligibility/'assumptions.json']
    hashes = {p: digest(p) for p in upstream}
    gate = _read(eligibility/'manifest.json')
    contract = _read(eligibility/'contract.json')
    if (gate.get('schema') != 'de-curated-eligibility-v1'
            or gate.get('status') != 'eligible_for_simulation_curated_build'
            or gate.get('data_kind') != 'simulation' or gate.get('source_id') != raw['source_id']
            or gate.get('contract_sha256') != hashes[eligibility/'contract.json']
            or gate.get('assumptions_sha256') != hashes[eligibility/'assumptions.json']):
        raise ValueError('Invalid eligibility contract')
    output.mkdir(parents=True, exist_ok=False)
    try:
        # Revalidate every upstream gate rather than trusting an eligibility flag.
        assess_curated_contract(revision, reconciliation, eligibility/'assumptions.json', output/'revalidated_gate')
        if _read(output/'revalidated_gate/contract.json') != contract:
            raise ValueError('Contract differs from supported source semantics/grains/metrics')
        source = revision/'raw/ledger.sqlite'
        target = output/'curated.sqlite'
        with closing(sqlite3.connect(source.as_uri()+'?mode=ro', uri=True)) as src, closing(sqlite3.connect(target)) as dst:
            src.execute('PRAGMA query_only=ON'); src.execute('BEGIN')
            dst.execute('PRAGMA foreign_keys=ON')
            checks = []; counts = {}
            for table, fields in TABLES.items():
                ddl = ','.join('"'+key+'" '+kind+' NOT NULL' for key,kind in fields.items())
                ddl += ',PRIMARY KEY ('+','.join('"'+key+'"' for key in KEYS[table])+')'
                if 'sku' in fields and table != 'products':
                    ddl += ',FOREIGN KEY (sku) REFERENCES products(sku)'
                dst.execute(f'CREATE TABLE "{table}" ({ddl})')
                rows = _projection(src, table)
                marks = ','.join('?' for _ in fields)
                dst.executemany(f'INSERT INTO "{table}" VALUES ({marks})', rows)
                actual = _projection(dst, table)
                counts[table] = len(actual)
                checks.append(dict(check='exact_projection:'+table, passed=actual==rows))
            expected = _totals(src); observed = _totals(dst)
            checks.append(dict(check='finance_and_monthly_totals', passed=observed==expected))
            checks.append(dict(check='integrity', passed=dst.execute('PRAGMA integrity_check').fetchone()[0]=='ok'))
            checks.append(dict(check='foreign_keys', passed=not dst.execute('PRAGMA foreign_key_check').fetchall()))
            if not all(check['passed'] for check in checks):
                raise ValueError('Curated parity checks failed')
            dst.execute('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL)')
            dst.executemany('INSERT INTO metadata VALUES (?,?)', [
                ('source','demo'), ('scenario_id',raw['source_id']), ('data_kind','simulation'),
                ('currency','VND'), ('visibility','admin_only'),
                ('period_start',contract['period']['start_inclusive']),
                ('period_end',contract['period']['end_inclusive']),
                ('sales_completeness','unverified'), ('contract_sha256',hashes[eligibility/'contract.json'])])
            dst.commit()
        stable_sqlite(target)
        # Verify persisted rows after closing and reopening, not only in-memory inserts.
        with closing(sqlite3.connect(target.as_uri()+'?mode=ro', uri=True)) as db:
            checks.append(dict(check='persisted_finance_totals', passed=_totals(db)==expected))
        verify_raw(revision)
        if any(digest(path)!=value for path,value in hashes.items()):
            raise RuntimeError('Upstream changed during materialization')
        if not all(check['passed'] for check in checks):
            raise ValueError('Persisted curated parity failed')
        report = dict(schema='de-curated-parity-v1', passed=True, checks=checks,
            row_counts=counts, totals=observed, data_kind='simulation',
            active_source_changed=False, source_modified=False)
        write_new(output/'parity.json', report)
        manifest = dict(schema='de-curated-build-v1', status='built_verified_not_activated',
            source_id=raw['source_id'], data_kind='simulation', visibility='admin_only',
            database_path='curated.sqlite', database_sha256=digest(target),
            database_bytes=target.stat().st_size, parity_sha256=digest(output/'parity.json'),
            contract_sha256=hashes[eligibility/'contract.json'],
            eligibility_manifest_sha256=hashes[eligibility/'manifest.json'],
            raw_manifest_sha256=hashes[revision/'manifest.json'],
            reconciliation_manifest_sha256=hashes[reconciliation/'manifest.json'],
            implementation_sha256=digest(__file__), curated_published=False, active_source_changed=False,
            limitations=['Internal simulated analytics projection; not activated or a drop-in app database.',
                'No orders/customer PII, purchase or movement tables; order counts and FIFO replay require raw lineage.',
                'No CSV/Excel mapping, forecast or completeness certification. Absent sales dates remain unknown.'])
        # Last artifact is the completion marker. Failed partial outputs are retained.
        write_new(output/'manifest.json', manifest)
        return manifest
    except Exception as exc:
        write_new(output/'build.failed.json', dict(status='incomplete', error_type=type(exc).__name__, active_source_changed=False))
        raise
