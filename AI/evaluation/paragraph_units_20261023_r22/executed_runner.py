"""Offline source paragraph audit, without inference or production mutation."""
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shopbot.chunking import chunk_document
from shopbot.monthly import active_documents
from shopbot.rag_answer import evidence_fragments
from shopbot.retrieval import normalize

BASE=ROOT/'evaluation/quality_loop_20261021'
OUT=ROOT/'evaluation/paragraph_units_20261023_r22'
MANIFEST=ROOT/'data/unstructured/managed/ecdd21ab64861674/manifest.json'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def content_blocks(text):
    """Keep exact source spans; no completion of a split sentence or paragraph."""
    return [block.strip() for block in re.split(r'\n\s*\n',text)
            if block.strip() and not block.lstrip().startswith('#')
            and not normalize(block.strip()).startswith(('nguon:','doi chieu:'))]


def write(name,value):
    path=OUT/name
    text=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    if path.exists():assert path.read_text(encoding='utf-8')==text,name
    else:path.write_text(text,encoding='utf-8')


def main():
    OUT.mkdir(exist_ok=True)
    patch9=read(ROOT/'evaluation/quoted_clauses_20261023_r20_v2/metadata.json')['code']
    assert all(sha(ROOT/k)==v for k,v in patch9.items())
    documents=active_documents(read(MANIFEST),'customer','demo',date(2026,10,21))
    documents=[d for d in documents if d.get('authority')=='external_technical_reference']
    rows=read(BASE/'candidate_v9_development/results.json')
    requested={re.search('“([^”]+)”',r['question'])[1] for r in rows if re.search('“([^”]+)”',r['question'])}
    assert len(requested)==28
    records=[]
    for doc in documents:
        chunks=chunk_document(doc,max_words=100)
        original_blocks=content_blocks(doc['text'])
        candidates=[]
        for chunk in chunks:
            body=chunk['text'].split('\n\n',1)[-1]
            for block in content_blocks(body):
                assert block in chunk['text'],(doc['document_id'],block)
                candidates.append(dict(text=block,quotes=[block],source_chunk_id=chunk['chunk_id'],
                                       section=chunk['section'],words=len(block.split()),
                                       entire_original_paragraph=block in original_blocks,
                                       contains_table='|' in block))
        before=evidence_fragments(chunks)
        joined=' '.join(' '.join(c['text'].split()) for c in candidates)
        original=' '.join(' '.join(block.split()) for block in original_blocks)
        # Preservation audit only, not semantic acceptance or a model score.
        assert joined==original,(doc['document_id'],'source content was lost/reordered')
        records.append(dict(document_id=doc['document_id'],title=doc['title'],
                            in_quoted_development=doc['title'] in requested,
                            source_paragraphs=len(original_blocks),chunk_count=len(chunks),
                            sentence_fragment_count=len(before),paragraph_units=candidates,
                            main_content_words=len(original.split()),
                            chunk_splits_original_paragraph=any(not c['entire_original_paragraph'] for c in candidates),
                            exact_source_span=True,content_preserved=True))
    assert requested<={r['title'] for r in records}
    summary=dict(technical_documents=len(records),quoted_development_documents=sum(r['in_quoted_development'] for r in records),
                 chunks=sum(r['chunk_count'] for r in records),
                 source_paragraphs=sum(r['source_paragraphs'] for r in records),
                 candidate_units=sum(len(r['paragraph_units']) for r in records),
                 split_paragraph_documents=[r['document_id'] for r in records if r['chunk_splits_original_paragraph']],
                 max_unit_words=max(c['words'] for r in records for c in r['paragraph_units']),
                 exact_span_and_content_checks=True,model_calls=0,production_changed=False,
                 semantic_gain_measured=False)
    write('metadata.json',dict(manifest_sha256=sha(MANIFEST),baseline_results_sha256=sha(BASE/'candidate_v9_development/results.json'),
                              production_code=patch9,runner_sha256=sha(Path(__file__)),
                              max_words=100,date='2026-10-21',mode='offline source audit only'))
    write('paragraph_units.json',records)
    write('summary.json',summary)
    (OUT/'executed_runner.py').write_bytes(Path(__file__).read_bytes())
    assert all(sha(ROOT/k)==v for k,v in patch9.items())
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':main()
