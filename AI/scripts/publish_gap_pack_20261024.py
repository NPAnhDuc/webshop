"""Stage and publish the 24/10 gap pack through the versioned KnowledgeStore only.

--stage writes knowledge_notes.json (sha256 per curated file, source capture, evidence
anchors). --publish adds new tech-* documents (never overwrites, never resurrects) and
writes publication.json with manifest hashes before/after. Raw HTML/PDF never enters
the store. Retrieval/chunking/model code is untouched.
"""
import argparse
import hashlib
import json
import sys
from datetime import date,datetime,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import atomic_json,active_documents

PACK=ROOT/'data/unstructured/technology_20261024_gaps'
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
EFFECTIVE='2026-10-24'
NOTES=[
 dict(document_id='tech-gpu-integrated-discrete',file='curated/gpu-integrated-discrete.md',
      title='GPU tích hợp và GPU rời khác nhau thế nào? GPU tích hợp có luôn yếu hơn không?',
      sources=[dict(id='intel-integrated-discrete',capture='web_reviewed',reviewed_on_page='09/04/2024',
                    anchor='Discrete graphics has its own dedicated memory that is not shared with the CPU.')]),
 dict(document_id='tech-vram-system-ram',file='curated/vram-system-ram.md',title='VRAM khác RAM máy tính ở đâu?',
      sources=[dict(id='nvidia-vram-explained',capture='local',
                    anchor='VRAM is high speed memory located on your graphics card.'),
               dict(id='intel-shared-video-memory',capture='web_reviewed',reviewed_on_page='05/23/2025',
                    anchor='The Graphics Processing Unit (GPU) does not have a dedicated memory')]),
 dict(document_id='tech-cpu-name-generation',file='curated/cpu-name-generation.md',
      title='Hai CPU cùng tên i5 có giống nhau không? Đọc thế hệ CPU Intel Core thế nào?',
      sources=[dict(id='intel-core-generation',capture='web_reviewed',reviewed_on_page='01/08/2025',
                    anchor='the generation of the processor is the number (or the two numbers) after the i9, i7, i5, or i3'),
               dict(id='intel-core-names-numbers',capture='web_reviewed',reviewed_on_page='04/17/2026',
                    anchor='have a SKU number that begins with 1, 2, etc. representing the generation')]),
 dict(document_id='tech-psu-80plus',file='curated/psu-80plus.md',
      title='Nguồn 80 PLUS là gì? Chứng nhận 80 PLUS có chứng minh đủ công suất cho bộ PC không?',
      sources=[dict(id='clearesult-80plus-program',capture='local',
                    anchor='80% energy efficient or greater at 10%, 20%, 50% and 100% of rated load with a true power factor of 0.9 or higher'),
               dict(id='clearesult-80plus-faq',capture='local',anchor='80 PLUS is a performance specification and certification program for internal power supply units')]),
 dict(document_id='tech-ssd-free-space',file='curated/ssd-free-space.md',
      title='Ổ SSD gần đầy có làm chậm máy không? Vì sao SSD cần chừa dung lượng trống?',
      sources=[dict(id='samsung-op-whitepaper',capture='local',
                    anchor='free space in the SSD is required to allow the firmware (FW) feature to run smoothly'),
               dict(id='samsung-op-845dc',capture='local',anchor='Over-provisioning')]),
]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf8'))


def stage():
    manifest={r['id']:r for r in read(PACK/'manifest.json')}
    notes=[]
    for note in NOTES:
        path=PACK/note['file'];text=path.read_text(encoding='utf8')
        for source in note['sources']:
            record=manifest[source['id']]
            assert record['url'] in text,f"{note['document_id']}: source URL missing from body"
            if source['capture']=='local':
                assert record['status']=='downloaded',source['id']
                extracted=(PACK/record['extracted']).read_text(encoding='utf8')
                assert source['anchor'] in extracted,f"anchor not in local source: {source['id']}"
            else:
                assert record['status']=='failed' and record.get('http_status')==403,source['id']
            source.update(url=record['url'],fetched_at=record['fetched_at'],http_status=record.get('http_status'),
                          raw_sha256=record.get('sha256'))
        notes.append(dict(document_id=note['document_id'],title=note['title'],doc_type='glossary',audience='customer',
                          category='all',authority='external_technical_reference',status='staged_reviewed_summary',
                          reviewed_on='2026-10-24',sources=note['sources'],
                          rights='short paraphrase; source rights retained; raw source redistribution not cleared',
                          file=note['file'],sha256=sha(path),words=len(text.split())))
    atomic_json(PACK/'knowledge_notes.json',notes)
    print(json.dumps([dict(id=n['document_id'],words=n['words'],captures=[s['capture'] for s in n['sources']]) for n in notes],ensure_ascii=False))


def publish():
    store=KnowledgeStore(DB);before=sha(store.manifest);db_before=sha(DB)
    existing={d['document_id'] for d in store.all_records()}
    receipt=dict(started_at=datetime.now(timezone.utc).isoformat(),database=str(DB),manifest=str(store.manifest),
                 before_manifest_sha256=before,published=[],skipped=[])
    (PACK/'before_publication_manifest.json').write_bytes(store.manifest.read_bytes())
    for note in read(PACK/'knowledge_notes.json'):
        path=PACK/note['file'];assert sha(path)==note['sha256'],path
        if note['document_id'] in existing:
            receipt['skipped'].append(dict(document_id=note['document_id'],reason='exists; never overwrite in gap pack'));continue
        record=store.save(note['document_id'],path.read_text(encoding='utf8').strip(),role='admin',title=note['title'],
                          doc_type=note['doc_type'],audience=note['audience'],approved=True,effective_from=EFFECTIVE,
                          category=note['category'],expected_version=0,authority=note['authority'])
        receipt['published'].append(dict(document_id=record['document_id'],version=record['version'],sha256=record['sha256']))
    receipt.update(completed_at=datetime.now(timezone.utc).isoformat(),after_manifest_sha256=sha(store.manifest),
                   unchanged_financial_database=sha(DB)==db_before,effective_from=EFFECTIVE,
                   active_customer_documents=len(active_documents(store.all_records(),'customer',store.kind,date.fromisoformat(EFFECTIVE))),
                   import_mode='existing KnowledgeStore; new documents only; no model training')
    assert receipt['unchanged_financial_database']
    atomic_json(PACK/'publication.json',receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k!='published'},ensure_ascii=False),len(receipt['published']))


if __name__=='__main__':
    parser=argparse.ArgumentParser();group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--stage',action='store_true');group.add_argument('--publish',action='store_true')
    stage() if parser.parse_args().stage else publish()
