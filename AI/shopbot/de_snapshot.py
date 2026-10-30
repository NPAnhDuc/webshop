"""Versioned raw capture and staging audit; never merge or publish curated data."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
from contextlib import closing
from .de_audit import audit_database


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def write_new(path,value):
    with Path(path).open('x',encoding='utf-8') as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)


def stable_sqlite(path):
    for suffix in ('-wal','-journal'):
        extra=Path(str(path)+suffix)
        if extra.exists() and extra.stat().st_size:
            raise ValueError('Export a stable SQLite source; active WAL/journal is not captured')


def capture_raw(database,catalog,output,source_id):
    database=Path(database).resolve(strict=True);catalog=Path(catalog).resolve(strict=True)
    output=Path(output).resolve()
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,79}',source_id):raise ValueError('Invalid source_id')
    if database==catalog or not database.is_file() or not catalog.is_file():raise ValueError('Choose two distinct source files')
    if output.exists():raise ValueError('Revision already exists; never overwrite a captured revision')
    stable_sqlite(database)
    # Hash before copying. The final manifest is the completion marker; partial
    # directories are retained on failure for inspection, never silently reused.
    originals={database:digest(database),catalog:digest(catalog)}
    output.mkdir(parents=True,exist_ok=False)
    write_new(output/'capture.started.json',dict(source_id=source_id,started_at=datetime.now(timezone.utc).isoformat()))
    try:
        raw=output/'raw';raw.mkdir()
        artifacts={}
        for origin,name in [(database,'ledger.sqlite'),(catalog,'catalog_public.json')]:
            target=raw/name
            with origin.open('rb') as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
            stable_sqlite(database)
            if digest(target)!=originals[origin] or digest(origin)!=originals[origin]:
                raise RuntimeError('Source changed during capture; incomplete revision must not be used')
            artifacts[name]=dict(path='raw/'+name,sha256=originals[origin],bytes=target.stat().st_size,origin=str(origin))
        stable_sqlite(database)
        if any(digest(p)!=h for p,h in originals.items()):raise RuntimeError('Source changed during capture')
        metadata={}
        try:
            with closing(sqlite3.connect((raw/'ledger.sqlite').as_uri()+'?mode=ro',uri=True)) as con:
                metadata=dict(con.execute("SELECT key,value FROM metadata WHERE key IN ('source','scenario_id')"))
        except sqlite3.Error:
            pass  # Raw capture retains invalid input; the staging audit must reject it.
        manifest=dict(schema='de-raw-capture-v1',status='captured',source_id=source_id,
            captured_at=datetime.now(timezone.utc).isoformat(),artifacts=artifacts,
            source_metadata=metadata,data_kind='simulation' if metadata.get('source')=='demo' else 'unverified_import',
            implementation_sha256=digest(__file__),curated_published=False,
            provenance='Explicit local source files; no folders, evaluation gold or other trade sources merged.',
            rights='No new usage rights inferred from archiving a local source.')
        write_new(output/'manifest.json',manifest)
        return manifest
    except Exception as exc:
        write_new(output/'capture.failed.json',dict(error_type=type(exc).__name__,status='incomplete',curated_published=False))
        raise


def verify_raw(output):
    output=Path(output).resolve(strict=True)
    manifest=json.loads((output/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema')!='de-raw-capture-v1' or manifest.get('status')!='captured':raise ValueError('Incomplete or unknown raw revision')
    artifacts=manifest.get('artifacts',{})
    if set(artifacts)!={'ledger.sqlite','catalog_public.json'}:raise ValueError('Unexpected raw artifacts')
    for name,item in artifacts.items():
        if item.get('path')!='raw/'+name:raise ValueError('Unexpected artifact path')
        path=(output/item['path']).resolve(strict=True)
        if not path.is_relative_to(output):raise ValueError('Artifact escaped raw revision')
        if path.stat().st_size!=item['bytes'] or digest(path)!=item['sha256']:raise ValueError('Raw artifact hash/size mismatch')
    stable_sqlite(output/'raw/ledger.sqlite')
    if (output/'capture.failed.json').exists():raise ValueError('Failed capture must not be used')
    return manifest


def stage_audit(output):
    output=Path(output).resolve(strict=True)
    manifest=verify_raw(output)
    staging=output/'staging'
    if staging.exists():raise ValueError('Staging already exists; preserve prior results')
    manifest_hash=digest(output/'manifest.json')
    report=audit_database(output/'raw/ledger.sqlite',output/'raw/catalog_public.json')
    verify_raw(output)
    if digest(output/'manifest.json')!=manifest_hash:raise RuntimeError('Raw manifest changed during staging')
    staging.mkdir(exist_ok=False)
    write_new(staging/'audit.json',report)
    write_new(staging/'quarantine.json',report['quarantine_samples'])
    result=dict(schema='de-staging-audit-v1',source_id=manifest['source_id'],
        status='audit_passed_pending_reconciliation' if report['passed'] else 'quarantined',
        raw_manifest_sha256=manifest_hash,audit_sha256=digest(staging/'audit.json'),
        quarantine_sha256=digest(staging/'quarantine.json'),implementation_sha256=digest(__file__),
        data_kind=report['source']['data_kind'],curated_published=False,
        limitation='No CSV/Excel mapping, FIFO/receipts/inventory reconciliation or curated publication yet.')
    write_new(staging/'manifest.json',result)
    return result
