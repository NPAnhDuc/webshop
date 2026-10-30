"""Correct overbroad numeric gold spans in a NEW revision, never rewrite r2."""
import hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.quality_eval import grade

OLD=ROOT/'evaluation/context_revision_20261021_r2'
OUT=ROOT/'evaluation/context_revision_20261021_r3'


def main():
    if OUT.exists():raise SystemExit('Revision exists; do not overwrite')
    read=lambda p:json.loads(p.read_text(encoding='utf8'))
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    bank=read(OLD/'bank.json');gold=read(OLD/'gold_sources.json')
    owners={(d['document_id'],d['version']):d for d in gold}
    changes=[]
    for case in bank:
        for required in case['required']:
            doc=owners[required['document_id'],required['version']]
            label=required['quote'].split(':',1)[0]
            # These fixtures request numeric financial fields. Bound at the
            # actual value/unit, preserving the exact approved-source spelling.
            match=re.search(re.escape(label)+r':\s*[-+]?\d+(?:[.,]\d+)*\s*(?:VND)?\.',doc['text'])
            assert match,(required['document_id'],label)
            corrected=match[0]
            if corrected!=required['quote']:
                changes.append(dict(id=case['id'],before=required['quote'],after=corrected))
                required['quote']=corrected
    assert len(changes)==8
    OUT.mkdir()
    (OUT/'bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'gold_sources.json').write_bytes((OLD/'gold_sources.json').read_bytes())
    meta=read(OLD/'metadata.json')
    meta.update(bank_sha256=sha(OUT/'bank.json'),gold_sha256=sha(OUT/'gold_sources.json'),
                note='Fixture-only revision3 of revision2: same48questions/splits/source. All8numeric required spans bounded directly from approved source, independently of bot output. Old artifacts preserved. No quality improvement is claimed from rescoring.24reserved remain unqueried.')
    (OUT/'metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'FIXTURE_CORRECTIONS.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    # Inference never receives gold. Replay the SAME recorded24development
    # outputs under corrected spans; label provenance and old timings honestly.
    original=OLD/'context_r2_baseline';rows=read(original/'results.json')
    cases={c['id']:c for c in bank if c['split']=='development'}
    for row in rows:row['checks']=grade(cases[row['id']],row['result'])
    replay=OUT/'baseline_regraded';replay.mkdir()
    (replay/'results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (replay/'human_review.json').write_bytes((original/'human_review.json').read_bytes())
    (replay/'provenance.json').write_text(json.dumps(dict(method='Regrade existing inference, NO new model calls',
        original_results=str(original/'results.json'),original_results_sha256=sha(original/'results.json'),
        original_metadata=read(original/'metadata.json'),corrected_bank_sha256=meta['bank_sha256'],
        semantic_review_unchanged=True,all_timings_from_original_run=True,reserved_opened=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (OUT/'README.md').write_text('''# Context revision3 — fixture correction only

Same48 questions/splits and source as r2. Initial numeric extractor captured the rest of a paragraph, flagging four correct development answers. This revision bounds ALL8 numeric gold fields from the approved source, without using model answers to write gold. R2 bank/results stay immutable. No chatbot improvement is claimed from changed automatic counts.

baseline_regraded reuses original24development outputs and original timings, with provenance; no fresh inference. Semantic review remains12PASS/12FAIL.24reserved confirmation cases remain unqueried; related intent/shared source and Codex authorship mean this is not independent human testing. Keep reserved sealed during development repairs.
''',encoding='utf8')
    print('New fixture revision3 saved; old r2 unchanged, no model called.')


if __name__=='__main__':main()
