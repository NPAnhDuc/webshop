"""Summarize saved manual judgments; never infer semantic status from checks."""
import hashlib,json,statistics
from collections import Counter
from pathlib import Path

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def save(name,value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

rows=read(OUT/'results.json');before=read(BASE/'candidate_v5_development/results.json')
old={r['id']:r for r in before};reviews=read(OUT/'human_review.json')
source=read(BASE/'metadata.json');gold=read(BASE/'gold_sources.json')
for name,key in [('bank.json','bank_sha256'),('gold_sources.json','gold_sha256')]:
    assert hashlib.sha256((BASE/name).read_bytes()).hexdigest()==source[key]
assert len(rows)==479 and read(OUT/'integrity.json')['unchanged']
assert [r['id'] for r in rows]==[r['id'] for r in before]
assert set(reviews)<=set(old)
assert all(v['status'] in ['PASS','FAIL'] for v in reviews.values())
changed=[r['id'] for r in rows if any(r['result'].get(k)!=old[r['id']]['result'].get(k) for k in ['answer','sources','basic_action'])]
prior_review=read(BASE/'candidate_v5_development/human_review.json')
prior_unchanged=all(i not in changed for i in prior_review)
assert len(prior_review)==112 and prior_unchanged
owners={(g['document_id'],g['version']):g for g in gold}
quotes=0;issues=[];private=[]
for row in rows:
    result=row['result'];sources=result.get('sources',[])
    for s in sources:
        if row['role']=='customer' and s.get('audience')=='admin':private.append(row['id'])
    for claim in result.get('rag',{}).get('claims',[]):
        for evidence in claim.get('evidence',[]):
            for quote in evidence.get('quotes',[]):
                quotes+=1;matching=[s for s in sources if s.get('source')==evidence.get('source')]
                if not any(quote in owners.get((s.get('document_id'),s.get('version')),{}).get('text','') for s in matching):issues.append(dict(id=row['id'],quote=quote))
coverage=dict(total=479,reviewed=len(reviews),unreviewed=len(rows)-len(reviews),
    reviewed_subset=dict(Counter(v['status'] for v in reviews.values())),
    inherited=sum('inherited_from' in v for v in reviews.values()),
    fresh=sum('inherited_from' not in v for v in reviews.values()),
    pending_ids=[r['id'] for r in rows if r['id'] not in reviews],
    roles={role:dict(total=sum(r['role']==role for r in rows),reviewed=sum(r['role']==role and r['id'] in reviews for r in rows),statuses=dict(Counter(reviews[r['id']]['status'] for r in rows if r['role']==role and r['id'] in reviews))) for role in ['customer','admin']},
    warning=('All479development judgments recorded; Codex-authored, repeated numeric probes, not independent or overall600/real-useraccuracy.' if len(reviews)==479 else 'Partial nonrepresentative semantic coverage, not overall479or600accuracy.')+' Statuses come only from saved Codex review; source/check agreement is not semantic PASS.')
save('review_coverage.json',coverage)
comparison=dict(cases=479,before_round='candidate_v5_development',after_round=OUT.name,
    before_checks=dict(Counter(r['checks']['status'] for r in before)),after_checks=dict(Counter(r['checks']['status'] for r in rows)),
    changed_check_ids=[r['id'] for r in rows if r['checks']['status']!=old[r['id']]['checks']['status']],
    changed_answer_action_source_ids=changed,changed_cases_reviewed=all(i in reviews for i in changed),
    prior112review_cases_unchanged=prior_unchanged,semantic_coverage=coverage,
    quote_checks=quotes,quote_issues=issues,private_source_leaks=private,
    timings=dict(before_total_seconds=round(sum(r['seconds'] for r in before),3),after_total_seconds=round(sum(r['seconds'] for r in rows),3),before_median_seconds=statistics.median(r['seconds'] for r in before),after_median_seconds=statistics.median(r['seconds'] for r in rows)),
    reserved_opened=False,production_accepted=False,
    warning='No semantic gain claimed from unchanged checks or newly reviewed coverage. Warmup/cache uncontrolled; no speed attribution.')
save('comparison.json',comparison)
save('decision.json',dict(state='full479_semantic_review_complete' if len(reviews)==479 else 'full479_completed_semantic_review_in_progress',candidate_retained=True,production_accepted=False,reserved_opened=False,reason='Checksunchangedfrompatch5,all15changedcasesreadcorrect,112priorreviewsexactoutputs. '+('All367previously-unreviewed cases now read;29failuresremain, prioritize source-preamble phantom part documented inCOHORT_02_FINDINGS before openingreserved.' if len(reviews)==479 else 'Readremainingcoveragebeforeanotherrepairoropeningreserved.')))
print(json.dumps({k:v for k,v in comparison.items() if k!='semantic_coverage'},ensure_ascii=False,indent=2))
print('Coverage:',coverage['reviewed'],coverage['reviewed_subset'],'pending',coverage['unreviewed'])
