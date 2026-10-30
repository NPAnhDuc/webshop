"""Frozen live evaluation of a Colab head; never deploys it automatically."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--controller',required=True);parser.add_argument('--sha256',required=True)
    parser.add_argument('--output',required=True);args=parser.parse_args()
    controller=Path(args.controller).resolve();raw=controller.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=args.sha256:raise ValueError('Candidate SHA256 mismatch')
    output=Path(args.output).resolve();output.mkdir(parents=True,exist_ok=False)
    config=json.loads(raw);report_path=controller.with_name('report.json')
    training=json.loads(report_path.read_text(encoding='utf8'))
    env=dict(os.environ,METRIC_CONTROLLER_PATH=str(controller),METRIC_CONTROLLER_SHA256=args.sha256,PYTHONIOENCODING='utf-8')
    jobs=[
      ('core106','audit_chatbot_questions.py',ROOT/'training/conversation_v3/audit_improved_20261019_verified_v2'),
      ('followup12','audit_chatbot_followups.py',ROOT/'training/conversation_v3/audit_new_wording_20261019_v2'),
      ('wording40','audit_chatbot_metric_holdout.py',ROOT/'training/metric_v4/audit_unseen_20261019_baseline/reviewed')]
    results={};all_regressions=[];all_repairs=[]
    for label,script,baseline in jobs:
        target=output/label
        print('START',label,flush=True)
        subprocess.run([sys.executable,str(ROOT/'scripts'/script),'--output',str(target)],env=env,check=True,cwd=ROOT,timeout=1800)
        before=[json.loads(v) for v in (baseline/'results.jsonl').read_text(encoding='utf8').splitlines()]
        after=[json.loads(v) for v in (target/'results.jsonl').read_text(encoding='utf8').splitlines()]
        if [(r['id'],r['question']) for r in before]!=[(r['id'],r['question']) for r in after]:
            raise ValueError('Question bank changed: '+label)
        regressions=[a['id'] for b,a in zip(before,after) if b['status']=='PASS' and a['status']=='FAIL']
        repairs=[a['id'] for b,a in zip(before,after) if b['status']=='FAIL' and a['status']=='PASS']
        summary=json.loads((target/'summary.json').read_text(encoding='utf8'))
        results[label]=dict(baseline_passed=sum(r['status']=='PASS' for r in before),
                            passed=summary['passed'],failed=summary['failed'],regressions=regressions,repairs=repairs,
                            execution_errors=sum(any(f['code']=='execution_error' for f in r['failures']) for r in after))
        all_regressions.extend(label+':'+v for v in regressions);all_repairs.extend(label+':'+v for v in repairs)
        print('RESULT',label,json.dumps(results[label]),flush=True)
    precision=training['test'].get('accepted_precision')
    approved=not all_regressions and bool(all_repairs) and precision is not None and precision>=.995
    approved=approved and all(not v['execution_errors'] for v in results.values()) and config['threshold']<=1
    final=dict(controller_sha256=args.sha256,training_report_sha256=hashlib.sha256(report_path.read_bytes()).hexdigest(),
               encoder_revision=config['base_revision'],training_device=training['device'],
               synthetic_test_accepted_precision=precision,synthetic_test_coverage=training['test']['coverage'],
               live=results,regressions=all_regressions,repairs=all_repairs,deployment_recommended=approved,
               decision_scope='Admin top-products metric only; original Vietnamese encoder, intent, dates, permissions and SQL remain unchanged.',
               limitations=['158 live questions are development regressions, not a production accuracy estimate.',
                            'Known unsupported/data-missing tasks remain FAIL; no fabricated policy, tax or future sales.'])
    (output/'selection.json').write_text(json.dumps(final,ensure_ascii=False,indent=2),encoding='utf8')
    print('SELECTION',json.dumps(final,ensure_ascii=True),flush=True)


if __name__=='__main__':main()
