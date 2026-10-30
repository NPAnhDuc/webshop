"""Monthly data/knowledge refresh. Updates facts and retrieval, never model weights."""
import calendar
from contextlib import contextmanager, closing
from datetime import date, datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
from zoneinfo import ZoneInfo
from .layout import ROOT
from .store import connect, dataset_source
from .validation import validate, sales_hash


def local_today():
    return datetime.now(ZoneInfo('Asia/Bangkok')).date()


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False, suffix='.tmp') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        temporary = Path(stream.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def atomic_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent, delete=False, suffix='.tmp') as stream:
        stream.write(text)
        temporary = Path(stream.name)
    try: os.replace(temporary, path)
    finally: temporary.unlink(missing_ok=True)


def read_json(path, default=None):
    path = Path(path)
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default


def month_bounds(month):
    if not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])', month): raise ValueError('Use month YYYY-MM')
    year, number = map(int, month.split('-'))
    return date(year, number, 1), date(year, number, calendar.monthrange(year, number)[1])


@contextmanager
def exclusive(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as lock:
        if path.stat().st_size == 0:
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == 'nt': msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else: fcntl.flock(lock, fcntl.LOCK_UN)


def active_documents(documents, role, data_kind, as_of):
    grouped = {}
    for doc in documents:
        if doc['data_kind'] != data_kind or doc['status'] not in ('approved','deleted'): continue
        if doc['effective_from'] > as_of.isoformat(): continue
        grouped.setdefault(doc['document_id'], []).append(doc)
    active = []
    for versions in grouped.values():
        # Pick the latest version first; an expired version must not revive an older one.
        doc = max(versions, key=lambda d: (d['version'], d['effective_from']))
        if doc['status']=='deleted':continue
        if doc.get('effective_to') and doc['effective_to'] < as_of.isoformat(): continue
        if doc['audience'] == 'customer' or role == 'admin': active.append(doc)
    return active


class MonthlyUpdater:
    def __init__(self, db_path=None, root=ROOT, today=None):
        self.root = Path(root).resolve()
        self.structured = self.root / 'data' / 'structured'
        self.unstructured = self.root / 'data' / 'unstructured'
        self.runtime = self.root / 'runtime' / 'monthly'
        self.db = Path(db_path or self.structured / 'shop.db').resolve()
        if not self.db.is_relative_to((self.root / 'data').resolve()): raise ValueError('Database outside data directory')
        self.today = today or local_today()
        self.kind = 'demo' if dataset_source(self.db) == 'demo' else 'shop'
        self.namespace = hashlib.sha256(str(self.db).encode()).hexdigest()[:16]
        self.runtime.mkdir(parents=True, exist_ok=True)

    @property
    def index_path(self):
        return self.runtime / (self.namespace + '-knowledge.json')

    def _ledger(self):
        with connect(self.db) as con:
            con.execute('CREATE TABLE IF NOT EXISTS sales_ingestion (id TEXT PRIMARY KEY,payload_hash TEXT NOT NULL)')
            con.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT)')
            bootstrapped = con.execute("SELECT value FROM metadata WHERE key='ledger_bootstrapped'").fetchone()
            if bootstrapped: return
            rows = con.execute('SELECT day,sku,quantity,revenue,cost FROM sales').fetchall()
            count = con.execute('SELECT COUNT(*) FROM sales_ingestion').fetchone()[0]
            if self.kind == 'shop' and rows and not count:
                raise ValueError('Legacy shop database lacks sale IDs; re-import the original JSON before monthly updates')
            if self.kind == 'demo' and not count:
                for row in rows:
                    record = dict(row, id=f"demo:{row['day']}:{row['sku']}")
                    con.execute('INSERT INTO sales_ingestion VALUES (?,?)', (record['id'], sales_hash(record)))
                con.execute("INSERT OR IGNORE INTO metadata VALUES ('catalog_as_of','2026-10-15')")
            con.execute("INSERT OR REPLACE INTO metadata VALUES ('ledger_bootstrapped','true')")

    def _documents(self, month=None):
        from .retrieval import extract
        target_month = month
        published = read_json(self.index_path, {'documents':[]})['documents']
        documents = [d for d in published if d.get('doc_type')!='monthly_report' and d['period']!=month] if month else []
        versions = read_json(self.runtime / 'document-versions.json', {})
        updated = dict(versions)
        for manifest in sorted((self.unstructured / 'monthly').glob('????-??/manifest*.json')):
            period = manifest.parent.name
            if target_month is not None and period != target_month: continue
            month = period
            month_bounds(period)
            if period > self.today.strftime('%Y-%m'): continue
            payload = read_json(manifest)
            if not isinstance(payload,dict): raise ValueError('Document manifest must be an object')
            if payload.get('ready') is not True: continue
            kind = payload.get('data_kind')
            if kind not in ('demo', 'shop'): raise ValueError('Document manifest needs data_kind demo/shop')
            for item in payload.get('documents', []):
                if not isinstance(item,dict): raise ValueError('Document entry must be an object')
                if item.get('status') != 'approved': continue
                identifier = item['document_id']
                if not re.fullmatch(r'[\w-]{1,100}', identifier): raise ValueError('Invalid document_id')
                version = item['version']
                if type(version) is not int or version < 1: raise ValueError('Version must be a positive integer')
                if item['audience'] not in ('customer', 'admin'): raise ValueError('Invalid audience')
                effective = date.fromisoformat(item['effective_from'])
                until = item.get('effective_to')
                if until and date.fromisoformat(until) < effective: raise ValueError('Invalid validity interval')
                if until: until = date.fromisoformat(until).isoformat()
                path = (manifest.parent / item['file']).resolve()
                if path.parent != manifest.parent.resolve(): raise ValueError('Document path must stay in its month folder')
                if path.suffix.lower() not in ('.md', '.txt', '.pdf', '.docx') or path.stat().st_size > 10*1024*1024:
                    raise ValueError('Unsupported or oversized document')
                body = extract(path).strip()
                if not body: raise ValueError('Empty document or scanned PDF needs OCR')
                doc = dict(document_id=identifier, version=version, audience=item['audience'],
                           status='approved', data_kind=kind, effective_from=effective.isoformat(),
                           effective_to=until, source=f'{month}/{path.name}', text=body,
                           period=month, doc_type='shop_document')
                fingerprint = hashlib.sha256(json.dumps({k:v for k,v in doc.items() if k not in ('source','period')},sort_keys=True).encode()).hexdigest()
                key = f'{kind}:{identifier}:{version}'
                if key in updated and updated[key] != fingerprint: raise ValueError('Document changed without a version bump: ' + identifier)
                updated[key] = fingerprint
                documents.append(doc)
        return documents, updated

    def _batch(self, month, allow_current):
        path = self.structured / 'monthly' / month / 'shop.json'
        if not path.exists(): return None, False
        payload = read_json(path)
        if not isinstance(payload,dict): raise ValueError('Batch must be an object')
        if payload.get('ready') is not True: return None, False
        if month == self.today.strftime('%Y-%m') and not allow_current:
            state = read_json(self.runtime/(self.namespace+'-state.json'), {})
            accepted = state.get(month, {}).get('accepted_batch_hash')
            if accepted != hashlib.sha256(path.read_bytes()).hexdigest(): return None, True
        if payload.get('month') != month or payload.get('data_kind') != self.kind:
            raise ValueError('Batch month/data_kind does not match; never mix shop data with demo data')
        if 'complete' in payload and type(payload['complete']) is not bool: raise ValueError('complete must be boolean')
        products, sales = validate(payload)
        for row in sales:
            if row['day'][:7] != month or date.fromisoformat(row['day']) > self.today:
                raise ValueError('Sale outside batch month or in the future')
        observed = date.fromisoformat(payload['inventory_as_of'])
        if observed.isoformat() != payload['inventory_as_of']: raise ValueError('Use ISO inventory_as_of')
        if observed.strftime('%Y-%m') != month or observed > self.today: raise ValueError('Invalid inventory_as_of')
        return payload, False

    def _apply(self, payload):
        if payload is None: return {'inserted':0, 'duplicates':0, 'catalog_updated':False}
        inserted = duplicates = 0
        with connect(self.db) as con:
            con.execute('BEGIN IMMEDIATE')
            for row in payload['sales']:
                previous = con.execute('SELECT payload_hash FROM sales_ingestion WHERE id=?', (row['id'],)).fetchone()
                if previous and previous[0] != sales_hash(row): raise ValueError('Conflicting sale ID: ' + row['id'])
            previous = con.execute("SELECT value FROM metadata WHERE key='catalog_as_of'").fetchone()
            catalog_as_of = previous[0] if previous else 'unknown'
            update_catalog = catalog_as_of != 'unknown' and payload['inventory_as_of'] >= catalog_as_of
            keys = ['sku','name','price','stock','panel','ram','battery','weight','category']
            for product in payload['products']:
                exists = con.execute('SELECT 1 FROM products WHERE sku=?', (product['sku'],)).fetchone()
                if update_catalog:
                    con.execute('INSERT OR REPLACE INTO products VALUES (?,?,?,?,?,?,?,?,?)', tuple(product[k] for k in keys))
                elif not exists:
                    historical = dict(product, stock=0)
                    con.execute('INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?)', tuple(historical[k] for k in keys))
            if update_catalog:
                con.execute("INSERT OR REPLACE INTO metadata VALUES ('catalog_as_of',?)", (payload['inventory_as_of'],))
            for row in payload['sales']:
                cursor = con.execute('INSERT OR IGNORE INTO sales_ingestion VALUES (?,?)', (row['id'], sales_hash(row)))
                if cursor.rowcount:
                    con.execute('INSERT INTO sales VALUES (?,?,?,?,?)', tuple(row[k] for k in ('day','sku','quantity','revenue','cost')))
                    inserted += 1
                else: duplicates += 1
        return dict(inserted=inserted, duplicates=duplicates, catalog_updated=update_catalog)

    def _rows(self, month):
        with connect(self.db, readonly=True) as con:
            return [dict(r) for r in con.execute('SELECT day,sku,quantity,revenue,cost FROM sales WHERE substr(day,1,7)=? ORDER BY day,sku,revenue,cost,quantity', (month,))]

    def _fingerprint(self, month, documents, deferred):
        path = self.structured / 'monthly' / month / 'shop.json'
        value = {'batch':hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None,
                 'documents':documents, 'rows':self._rows(month), 'sales_deferred':deferred,
                 'calendar_closed':month < self.today.strftime('%Y-%m')}
        return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()

    def process(self, month, allow_current=False):
        month_bounds(month)
        if month > self.today.strftime('%Y-%m'): raise ValueError('Future month')
        with exclusive(self.runtime / 'updater.lock'):
            self._ledger()
            documents, versions = self._documents(month)
            payload, deferred = self._batch(month, allow_current)
            fingerprint = self._fingerprint(month, documents, deferred)
            state_path = self.runtime / (self.namespace + '-state.json')
            state = read_json(state_path, {})
            if state.get(month, {}).get('fingerprint') == fingerprint: return {'month':month, 'status':'unchanged'}
            result = self._apply(payload)
            rows = self._rows(month)
            complete = bool(payload and payload.get('complete') is True and month < self.today.strftime('%Y-%m'))
            revenue, cost, units = (sum(r[k] for r in rows) for k in ('revenue','cost','quantity'))
            run_version = state.get(month, {}).get('version', 0) + 1
            report = {'document_id':'monthly-report-'+month, 'version':run_version, 'audience':'admin',
                      'data_kind':self.kind, 'status':'approved', 'effective_from':self.today.isoformat(),
                      'effective_to':None, 'period':month, 'doc_type':'monthly_report',
                      'source':'SQL monthly report '+month,
                      'text':f'# Báo cáo tháng {month}\n\nNguồn: SQLite sales; loại dữ liệu: {self.kind}.\n\n'+
                             (f'Doanh thu: {revenue} VND. Lợi nhuận gộp: {revenue-cost} VND. Số lượng: {units}. Số dòng: {len(rows)}.' if rows else 'Chưa có số liệu bán hàng cho tháng này; không suy ra doanh thu bằng không.')+
                             ('\n\nTháng đang diễn ra: dữ liệu chưa đầy đủ.' if month == self.today.strftime('%Y-%m') else '')+
                             ('\n\nChưa xác nhận dữ liệu đủ cho cả tháng.' if not complete and month < self.today.strftime('%Y-%m') else '')+
                             ('\n\nLô bán hàng tháng hiện tại đang chờ chốt, chưa được nạp.' if deferred else '')}
            old = read_json(self.index_path, {'documents':[]})
            reports = [d for d in old['documents'] if d.get('doc_type') == 'monthly_report' and d['period'] != month]
            snapshot = self.structured / 'snapshots' / month / (fingerprint[:16]+'.db')
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            if not snapshot.exists():
                with connect(self.db, readonly=True) as source, closing(sqlite3.connect(snapshot)) as target:
                    source.backup(target)
            result.update(month=month, status='updated', version=run_version, data_kind=self.kind,
                          sales_deferred=deferred, document_count=len(documents), revenue=revenue,
                          complete=complete,
                          profit=revenue-cost, units=units, snapshot=str(snapshot.relative_to(self.root)))
            report_path = self.unstructured/'generated'/month/f'{self.namespace}-v{run_version}.md'
            report['source'] = str(report_path.relative_to(self.unstructured))
            report['authority'] = 'derived_from_sql'
            atomic_text(report_path, report['text'])
            atomic_json(self.index_path, {'documents':documents+reports+[report], 'updated_at':datetime.now(ZoneInfo('Asia/Bangkok')).isoformat()})
            atomic_json(self.runtime / 'document-versions.json', versions)
            atomic_json(self.runtime / 'reports' / f'{self.namespace}-{month}.json', result)
            data_path = self.structured/'monthly'/month/'shop.json'
            accepted = hashlib.sha256(data_path.read_bytes()).hexdigest() if payload is not None else state.get(month,{}).get('accepted_batch_hash')
            state[month] = dict(fingerprint=self._fingerprint(month, documents, deferred), version=run_version, accepted_batch_hash=accepted)
            atomic_json(state_path, state)
            return result

    def run_pending(self):
        months = set()
        for folder in (self.structured/'monthly', self.unstructured/'monthly'):
            if folder.exists(): months.update(p.name for p in folder.iterdir() if p.is_dir() and re.fullmatch(r'\d{4}-\d{2}',p.name))
        results = []
        for month in sorted(months):
            if month > self.today.strftime('%Y-%m'): continue
            try: results.append(self.process(month))
            except (ValueError, OSError, KeyError, TypeError, sqlite3.Error) as exc:
                error = {'month':month, 'status':'rejected', 'error':str(exc)}
                atomic_json(self.runtime/'errors'/f'{self.namespace}-{month}.json', error)
                results.append(error)
        return results
