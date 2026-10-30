"""Post-run comparison only; not a model prompt, retraining or validation."""
import json
import re
from pathlib import Path
OUT=Path(__file__).parent;OLD=OUT.parent/'agent_quality_20261024_r7'
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
def write(name,value):
 with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
norm=lambda s:re.sub(r'agent_quality_20261024_r[0-9]+','REV',s)
old={r['id']:r for r in read(OLD/'results.json')};rows=read(OUT/'results.json')
traces={p.stem:read(p) for p in (OUT/'traces').rglob('*.json')};parents={};cases={}
prior=read(OLD/'human_review.json')['cases']
for row in rows:
 r=row['result'];p=old[row['id']]['result'];t=traces[r['trace_id']]
 assert norm(r['answer'])==norm(p['answer']),row['id']
 call_args=lambda x:[(c['tool'],c['arguments']) for c in x.get('tool_evidence',{}).get('calls',[])]
 assert call_args(r)==call_args(p),row['id']
 parent=parents.get(row['conversation'])
 assert t['parent_trace_id']==(parent['id'] if parent and parent['role']==row['role'] else None)
 assert t['principal_role']==row['role'] and t['question']==row['question']
 assert not t['training_allowed'] and t['error_type'] is None
 parents[row['conversation']]=dict(id=r['trace_id'],role=row['role'])
 cases[row['id']]=dict(semantic_pass=prior[row['id']]['semantic_pass'],
  same_answer_and_tool_args_as_r7=True,reason='Carry forward r7 semantic review after identical normalized answer and tool/args verification. New20 lexical scope probes are not included in this end-to-end score.')
assert len(rows)==106 and len(traces)==106
write('human_review.json',dict(protocol='Separate comparison with r7, no new semantic gains in106. Development already exposed.',cases=cases))
write('semantic_summary.json',dict(passed=sum(x['semantic_pass'] for x in cases.values()),total=106,previous_passed=103,
 unchanged_answer_count=106,remaining_failures=[k for k,v in cases.items() if not v['semantic_pass']],
 complete_contract_sessions_passed=4,complete_contract_sessions_total=6,accepted_for_application=False,
 new_scope_probe_before=9,new_scope_probe_after=20,new_scope_probe_total=20,new_scope_probes_model_evaluated=False))
write('trace_verification.json',dict(turns=106,trace_records=106,role_question_parent_links_passed=True,same_tool_args_as_r7=True))
write('test_verification.json',dict(targeted_passed=131,targeted_seconds=13.36,log='AI/runtime/tests-capability-scope-r2b.log',
 full_suite_rerun=False,earlier_r7_full_suite_passed=409,
 initial_collection_attempt='No tests ran: mistakenly named nonexistent test_turn_trace.py; corrected selection and reran successfully.'))
print(json.dumps(read(OUT/'semantic_summary.json')))
