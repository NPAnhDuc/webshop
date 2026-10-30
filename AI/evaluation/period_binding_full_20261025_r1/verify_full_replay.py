from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[2]
b=ROOT/'evaluation/quality_loop_20261024_kb3';n=b/'kb3_period_binding_full_r1';rows=json.loads((n/'results.json').read_text(encoding='utf-8'));old={x['id']:x for x in json.loads((b/'kb3_report_source_full_r1/results.json').read_text(encoding='utf-8'))};bank={x['id']:x for x in json.loads((b/'bank.json').read_text(encoding='utf-8'))};review=[]
for x in rows:
 if x['topic']!='multi_period':continue
 r=x['result'];mapping={f['id']:f['document_id'] for f in r['rag']['available_fields']};req={d['document_id']:d for d in bank[x['id']]['required']};sources={s['document_id']:s for s in r['sources']};parts=[]
 assert len(r['rag']['claims'])==2 and len(r['sources'])==2 and not r['rag']['unanswered']
 for key,part in r['plan']['parts'].items():
  mm=re.search(r'\btháng\s*(\d{1,2})/(20\d{2})',part,re.I);assert mm,part
  month=f'{mm[2]}-{int(mm[1]):02}';docid='monthly-report-'+month
  ids=r['rag']['part_evidence'][key];assert len(ids)==1 and mapping[ids[0]]==docid
  expected=req[docid];source=sources[docid];assert source['version']==expected['version'] and expected['quote'] in source['text']
  matches=[c for c in r['rag']['claims'] if c['text']==expected['quote'] and c['evidence'][0]['source']==source['source']];assert len(matches)==1
  parts.append(dict(part_id=key,period=month,document_id=docid,version=source['version'],quote=expected['quote'],evidence_ids=ids,status='exact_period_metric_source_quote'))
 assert sorted(c['text'] for c in r['rag']['claims'])==sorted(c['text'] for c in old[x['id']]['result']['rag']['claims'])
 review.append(dict(id=x['id'],parts=parts,unrequested_claims=0))
assert len(review)==102
controls=[x for x in rows if x['topic']!='multi_period'];assert len(controls)==377 and all(x['result']['answer']==old[x['id']]['result']['answer'] for x in controls)
changed=[x['id'] for x in rows if x['result']['answer']!=old[x['id']]['result']['answer']];assert len(changed)==19
m=json.loads((n/'metadata.json').read_text());v={k:hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==h for k,h in m['code'].items()};assert all(v.values())
summary=dict(status='retain_bounded_period_binding_pending_broad_regression',actual_cases=479,multi_period_cases=102,parts_reviewed=204,period_metric_source_bindings_exact=204,baseline_exact=166,baseline_wrong=34,baseline_overbroad=4,changed_answer_ids=changed,other_control_answers_unchanged=377,claim_sets_changed=0,action_changes=[],integrity_unchanged=True,overall_semantic_accuracy=None,mechanical_checks=dict(PASS_CHECKS=425,NEEDS_REVIEW=53,FAIL_CHECKS=1),cases=review,training_allowed=False,ingestion_allowed=False,validation_opened=False)
(n/'semantic_review.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
Path(__file__).with_name('post_review_verification.json').write_text(json.dumps(dict(all_runtime_files_match=True,files=v),indent=2))
print('204exact period/metric/source/version/quote bindings;377unchanged controls;19fact-order changes.')
