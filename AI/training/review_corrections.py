"""Admit source-backed tutor corrections, never validation/test groups or guesses."""
import argparse
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent

def verify_feedback(feedback,catalog,corpus):
    if feedback.get('approved') is not True or not feedback.get('reviewed_by'):
        raise ValueError('Correction requires an identified reviewer and explicit approval')
    source_id=feedback['source_id']
    product=catalog[source_id]
    doc=corpus[source_id]
    if doc['split']!='train':raise ValueError('Never turn validation/test source groups into training corrections')
    field=feedback['field']
    value=product['attributes'].get(field,product.get(field))
    if value is None:raise ValueError('No source value; do not invent a correction')
    if feedback['expected_answer']!=json.dumps(value,ensure_ascii=False):
        raise ValueError('Expected answer must equal the exact source value')
    quote=feedback.get('evidence_quote','')
    if not quote or quote not in doc['text']:
        raise ValueError('Evidence must be a verbatim quote from the referenced source document')
    if json.dumps(value,ensure_ascii=False) not in quote:
        raise ValueError('Evidence quote does not contain the asserted value')
    if not feedback.get('question','').strip():raise ValueError('Missing question')
    return {'id':'tutor:'+hashlib.sha256(json.dumps(feedback,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
       'question':feedback['question'],'expected_answer':feedback['expected_answer'],'positive_id':source_id,
       'field':field,'group_id':source_id,'split':'train','answerability':'supported',
       'label_origin':'reviewed_source_correction','reviewed_by':feedback['reviewed_by'],
       'evidence_quote':quote,'source_sha256':product['source_sha256']}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('feedback_jsonl')
    args=parser.parse_args()
    load=lambda path:[json.loads(s) for s in Path(path).read_text(encoding='utf-8').splitlines() if s.strip()]
    catalog={r['record_id']:r for r in load(HERE.parent/'data/structured/processed/product_catalog.jsonl')}
    corpus={r['id']:r for r in load(HERE/'data/corpus.jsonl')}
    accepted=[verify_feedback(f,catalog,corpus) for f in load(args.feedback_jsonl)]
    # Write a new artifact atomically; never alter the frozen base questions or test files.
    target=HERE/'data/qa-train-corrections.jsonl'
    staging=target.with_suffix('.jsonl.part')
    staging.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in accepted),encoding='utf-8')
    staging.replace(target)
    print(json.dumps({'accepted':len(accepted),'file':str(target),'test_changed':False}))

if __name__=='__main__':main()
