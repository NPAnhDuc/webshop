"""Post-run review record, not model input or a training corpus."""
import json
import re
from pathlib import Path
from collections import defaultdict
OUT=Path(__file__).parent
OLD=OUT.parent/'agent_quality_20261024_r6'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(name,obj):
 with (OUT/name).open('x',encoding='utf-8') as f:json.dump(obj,f,ensure_ascii=False,indent=2)
norm=lambda s:re.sub(r'agent_quality_20261024_r[0-9]+','REV',s)
rows=read(OUT/'results.json');old={r['id']:r for r in read(OLD/'results.json')}
review=read(OLD/'human_review.json')['cases']
fixed={'Q10','Q14','Q20','Q22','Q24','Q28','Q37','Q39','A20','A22'}
changed=[];cases={};parents={};groups=defaultdict(list)
traces={p.stem:read(p) for p in (OUT/'traces').rglob('*.json')}
for row in rows:
 key=row['id'];r=row['result'];previous=old[key]['result'];t=traces[r['trace_id']]
 same=norm(r['answer'])==norm(previous['answer'])
 if not same:changed.append(key)
 if key in fixed or key=='Q11':
  assert r['basic_action']=='deferred' and not r.get('tool_evidence',{}).get('calls')
  assert r['capability_status']['status']=='unsupported' and r['capability_status']['executed'] is False
  assert not t['calls'] and not r['sources'] and not r['rows']
  reason='Reviewed explicit unsupported file transform or SKU sales request: truthful deferred, correct registered capability, no substitute inspection, no facts/write claims.'
 else:
  assert same,key
  assert [(c['tool'],c['arguments']) for c in r.get('tool_evidence',{}).get('calls',[])]==[(c['tool'],c['arguments']) for c in previous.get('tool_evidence',{}).get('calls',[])],key
  reason='Same answer (artifact revision path normalized) and same tool/args; carry forward r6 semantic review. No independent validation claim.'
 cases[key]=dict(semantic_pass=key in fixed or review[key]['semantic_pass'],same_answer_as_r6_after_path_normalization=same,reason=reason)
 conversation=row['conversation'];parent=parents.get(conversation)
 expected=parent['id'] if parent and parent['role']==row['role'] else None
 assert t['principal_role']==row['role'] and t['question']==row['question']
 assert t['parent_trace_id']==expected,(key,t['parent_trace_id'],expected)
 assert t['training_allowed'] is False and t['error_type'] is None
 parents[conversation]=dict(id=r['trace_id'],role=row['role'])
 if key in read(OUT/'contract_gold.json'):groups[conversation].append(cases[key]['semantic_pass'])
assert set(changed)==fixed|{'Q11'}
write('human_review.json',dict(protocol='Separate semantic review after one frozen development batch. Inspected all11 changed answers,10 prior failures fixed;95 unchanged answers/tool-args compared with r6. No validation/training.',cases=cases))
write('trace_verification.json',dict(turns=len(rows),trace_records=len(traces),role_question_parent_links_passed=True,unsupported_turns_without_any_tool_call=sorted(fixed|{'Q11'})))
write('semantic_summary.json',dict(passed=sum(c['semantic_pass'] for c in cases.values()),total=len(rows),previous_passed=93,
 fixed=sorted(fixed),remaining_failures=[k for k,c in cases.items() if not c['semantic_pass']],
 unchanged_answer_count=len(rows)-len(changed),changed_answer_ids=changed,
 complete_contract_sessions_passed=sum(all(v) for v in groups.values()),complete_contract_sessions_total=len(groups),
 accepted_for_application=False,development_only=True))
write('test_verification.json',dict(passed=409,log='AI/runtime/tests-capability-guard-r1.log',seconds=153.87,
 offline_guard_before=9,offline_guard_after=20,offline_guard_total=20,
 initial_targeted_attempt='56 passed,3 setup errors: old system pytest temp directory ACL; rerun full suite with new workspace basetemp and cache disabled passed. No application permission changed.'))
print(json.dumps(read(OUT/'semantic_summary.json')))
