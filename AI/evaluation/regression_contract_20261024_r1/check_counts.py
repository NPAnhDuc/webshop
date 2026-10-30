"""Fixed literal oracle, run before/after; never overwrite a result file."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shopbot.catalog_planner import search_literals,SearchClarification
from shopbot.de_snapshot import digest,write_new
out=Path(__file__).parent;cases=json.loads((out/'count_cases.json').read_text(encoding='utf-8'))
results=[]
for c in cases:
    try:
        budget,inclusive,count,_=search_literals(c['question'])
        actual=dict(budget=budget,count=count)
        passed=not c.get('clarify') and budget==c['budget'] and count==c['count']
    except SearchClarification:
        actual=dict(clarify=True);passed=c.get('clarify') is True
    results.append(dict(id=c['id'],passed=passed,actual=actual))
result=dict(cases_sha256=digest(out/'count_cases.json'),implementation_sha256=digest(ROOT/'shopbot/catalog_planner.py'),
    passed=sum(r['passed'] for r in results),total=len(results),results=results)
write_new(out/(sys.argv[1]+'.json'),result)
print(json.dumps(result,ensure_ascii=False))
