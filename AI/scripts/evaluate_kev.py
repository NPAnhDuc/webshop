"""Measure a small local Kev smoke set, not a held-out accuracy benchmark."""
import json,time
from pathlib import Path
import requests
root=Path(__file__).resolve().parents[1]
rows=[json.loads(v) for v in (root/'data/structured/training/routing-seeds/seeds.jsonl').read_text(encoding='utf-8').splitlines()]
report=[]
for i in [0,6,12,16]:
    row=rows[i]
    start=time.monotonic()
    r=requests.post('http://127.0.0.1:8009/v1/systemone',json={'model':'kev-latest','state':row['state'],'questions':row['questions']},timeout=90)
    r.raise_for_status()
    a=r.json()['answers']['intent']
    report.append({'question':row['state'],'expected':row['labels']['intent'],'choice':a['choice'],'probabilities':a['probabilities'],'seconds':round(time.monotonic()-start,2)})
output={'scope':'4 hand-authored seed smoke checks; not independent eval or calibration','results':report,'correct':sum(v['expected']==v['choice'] for v in report)}
(root/'runtime/kev-smoke.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(output,ensure_ascii=True,indent=2))
