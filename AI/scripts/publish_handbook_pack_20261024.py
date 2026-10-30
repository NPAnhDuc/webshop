"""Publish the verified handbook pack (admin-only) through the versioned KnowledgeStore.

Refuses to publish if the DB changed since verification. New documents only; never
overwrites or resurrects. Writes publication.json with manifest hashes before/after.
"""
import hashlib
import json
import sys
from datetime import date,datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import atomic_json,active_documents

PACK=ROOT/'data/unstructured/handbook_20261024'
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
EFFECTIVE='2026-10-24'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf8'))


def main():
    verification=read(PACK/'verification.json')
    assert sha(DB)==verification['database_sha256'],'Database changed since SQL verification; rebuild the pack'
    store=KnowledgeStore(DB);existing={d['document_id'] for d in store.all_records()}
    receipt=dict(started_at=datetime.now(timezone.utc).isoformat(),database=str(DB),manifest=str(store.manifest),
                 before_manifest_sha256=sha(store.manifest),published=[],skipped=[])
    (PACK/'before_publication_manifest.json').write_bytes(store.manifest.read_bytes())
    for note in read(PACK/'knowledge_notes.json'):
        path=PACK/note['file'];assert sha(path)==note['sha256'],path
        assert note['audience']=='admin',note['document_id']
        text=path.read_text(encoding='utf8').strip();expected=0
        if note['document_id'] in existing:
            old=max((d for d in store.all_records() if d['document_id']==note['document_id']),key=lambda d:d['version'])
            # Only a newer build of our own handbook document may replace it.
            if old.get('authority')!='internal_methodology' or old['status']=='deleted':
                receipt['skipped'].append(dict(document_id=note['document_id'],reason='not ours or deleted; never overwrite'));continue
            if old['text'].strip()==text:continue
            expected=old['version']
        record=store.save(note['document_id'],text,role='admin',title=note['title'],
                          doc_type=note['doc_type'],audience='admin',approved=True,effective_from=EFFECTIVE,
                          category=note['category'],expected_version=expected,authority=note['authority'])
        receipt['published'].append(dict(document_id=record['document_id'],version=record['version'],sha256=record['sha256']))
    receipt.update(completed_at=datetime.now(timezone.utc).isoformat(),after_manifest_sha256=sha(store.manifest),
                   unchanged_database=sha(DB)==verification['database_sha256'],effective_from=EFFECTIVE,
                   active_admin_documents=len(active_documents(store.all_records(),'admin',store.kind,date.fromisoformat(EFFECTIVE))),
                   active_customer_documents=len(active_documents(store.all_records(),'customer',store.kind,date.fromisoformat(EFFECTIVE))))
    assert receipt['unchanged_database']
    atomic_json(PACK/'publication.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='published'},ensure_ascii=False),len(receipt['published']))


if __name__=='__main__':main()
