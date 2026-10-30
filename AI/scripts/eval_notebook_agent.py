"""Score the notebook agent on evaluation/notebook_agent_20261030/bank.json with the real model."""
import argparse
import json
import statistics
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot import notebook_agent as agent
from shopbot import notebook_eval as evaluation


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round',required=True)
    parser.add_argument('--split',default='dev',choices=['dev','test','all'])
    parser.add_argument('--model')
    args=parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    output=evaluation.BANK_PATH.parent/args.round;output.mkdir(parents=True,exist_ok=True)
    rows=[]
    with (output/'runs.jsonl').open('w',encoding='utf-8') as log:
        for item in evaluation.load_bank(args.split):
            expected=evaluation.expected_value(item)
            result=agent.run_agent(item['question'],model=args.model)
            correct=result.status=='answered' and evaluation.grade(item,result.answer,expected)
            row=dict(id=item['id'],split=item['split'],correct=correct,output_correct=evaluation.output_has_expected(item,result.evidence,expected),
                expected=expected,**result.summary())
            rows.append(row);log.write(json.dumps(row,ensure_ascii=False)+'\n');log.flush()
            print(f"{item['id']} {'OK ' if correct else 'BAD'} {result.status} cells={len(result.cells)} {result.seconds}s | {expected} | {result.answer or result.rejected_answer}",flush=True)
    summary=dict(round=args.round,split=args.split,model=rows[0]['model'],questions=len(rows),correct=sum(row['correct'] for row in rows),
        output_correct=sum(row['output_correct'] for row in rows),answered=sum(row['status']=='answered' for row in rows),
        wrong_answered=[row['id'] for row in rows if row['status']=='answered' and not row['correct']],
        mean_cells=round(statistics.mean(row['cell_count'] for row in rows),2),mean_seconds=round(statistics.mean(row['seconds'] for row in rows),1),
        max_seconds=max(row['seconds'] for row in rows))
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':raise SystemExit(main())
