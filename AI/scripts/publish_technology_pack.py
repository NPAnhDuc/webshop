"""Publish the reviewed pack through existing versioned KnowledgeStore only.

Keeps routing/retrieval/chunking/models unchanged. Existing catalog identifiers are
updated with optimistic concurrency; deleted or manually replaced records are not
resurrected. Raw downloaded HTML/PDF never enters the active knowledge store.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import atomic_json, active_documents
from datetime import date

PACK=ROOT/'data/unstructured/technology_20261020'
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
MARKER='## Bổ sung thông số từ gói công nghệ 20/10/2026'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf8'))


def main():
    validation=read(PACK/'validation.json');store=KnowledgeStore(DB)
    assert sha(DB)==validation['financial_db_sha256'],'Financial DB changed since pack preparation'
    assert all(sha(ROOT/p)==v for p,v in validation['code_sha256'].items()),'Chatbot code changed since preparation'
    receipt_path=PACK/'publication.json'
    receipt=read(receipt_path) if receipt_path.exists() else dict(
        started_at=datetime.now(timezone.utc).isoformat(),database=str(DB),
        manifest=str(store.manifest),before_manifest_sha256=sha(store.manifest),published=[])
    backup=PACK/'before_publication_manifest.json'
    if not backup.exists():backup.write_bytes(store.manifest.read_bytes())
    latest={}
    for document in store.all_records():
        if document['document_id'] not in latest or document['version']>latest[document['document_id']]['version']:
            latest[document['document_id']]=document
    plan=[];skipped=[]
    for note in read(PACK/'knowledge_notes.json'):
        path=PACK/note['file'];assert sha(path)==note['sha256'],path
        plan.append(dict(identifier=note['document_id'],text=path.read_text(encoding='utf8').strip(),
                         title=note['title'],doc_type=note['doc_type'],audience='customer',category=note['category'],
                         authority=note['authority']))
    for fact in read(PACK/'catalog_facts.json'):
        path=PACK/fact['file'];assert sha(path)==fact['sha256'],path
        identifier='catalog-'+fact['sku'];old=latest.get(identifier)
        if not old or old['status']!='approved' or old.get('authority')!='external_catalog_fixture':
            skipped.append(dict(document_id=identifier,reason='missing/deleted/unapproved/or stronger/manual authority'))
            continue
        # One canonical projection per SKU. Concatenating the old snapshot with
        # the extended snapshot repeated RAM/display facts and inflated chunks.
        # The original version remains in the versioned store for audit.
        text=path.read_text(encoding='utf8').strip()
        plan.append(dict(identifier=identifier,text=text,title=old['title'],doc_type='product',
                         audience=old['audience'],category=old['category'],authority=old['authority']))
    changes=[]
    for item in plan:
        old=latest.get(item['identifier'])
        if old and old['status']=='deleted':
            skipped.append(dict(document_id=item['identifier'],reason='deleted; never resurrect automatically'));continue
        if old and old['text'].strip()==item['text'] and old['status']=='approved':continue
        if old and old.get('authority') not in ('external_catalog_fixture','external_technical_reference'):
            skipped.append(dict(document_id=item['identifier'],reason='preserve manually curated authority'));continue
        changes.append((item,old))
    for item,old in changes:
        record=store.save(**item,role='admin',approved=True,effective_from='2026-10-20',
                          expected_version=old['version'] if old else 0)
        receipt['published']=[r for r in receipt['published'] if r['document_id']!=record['document_id']]
        receipt['published'].append(dict(document_id=record['document_id'],version=record['version'],sha256=record['sha256']))
        atomic_json(receipt_path,receipt)
    receipt.update(completed_at=datetime.now(timezone.utc).isoformat(),skipped=skipped,
                   after_manifest_sha256=sha(store.manifest),database_sha256=sha(DB),
                   new_technical_documents=sum(r['document_id'].startswith('tech-') for r in receipt['published']),
                   updated_catalog_documents=sum(r['document_id'].startswith('catalog-') for r in receipt['published']),
                   data_kind=store.kind,
                   active_customer_documents=len(active_documents(store.all_records(),'customer',store.kind,date(2026,10,20))),
                   active_admin_documents=len(active_documents(store.all_records(),'admin',store.kind,date(2026,10,20))),
                   unchanged_chatbot_code=all(sha(ROOT/p)==v for p,v in validation['code_sha256'].items()),
                   unchanged_financial_database=sha(DB)==validation['financial_db_sha256'],
                   import_mode='existing KnowledgeStore; next retrieval reads updated manifest; no model training')
    assert receipt['unchanged_chatbot_code'] and receipt['unchanged_financial_database']
    atomic_json(receipt_path,receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='published'},ensure_ascii=False))


if __name__=='__main__':main()
