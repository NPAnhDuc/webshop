"""Deterministic before/after capability contracts; no model or source I/O."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shopbot.agent_tools import CatalogTools,AgentTools
from shopbot.de_snapshot import digest,write_new
out=Path(__file__).parent;cases=json.loads((out/'cases.json').read_text(encoding='utf-8'))
catalog=CatalogTools(dict(schema='agent-catalog-v1',products=[],data_kind='simulation',captured_at='2026-10-24',source={'path':'fixture'}))
tools=AgentTools(catalog,None);results=[]
for case in cases:
    try:
        result=tools.execute(case['role'],case['tool'],case['arguments'])
        actual=result.get('status','executed')
    except (ValueError,PermissionError,TypeError) as exc:actual=type(exc).__name__
    results.append(dict(id=case['id'],actual=actual,passed=actual==case['expected']))
write_new(out/(sys.argv[1]+'.json'),dict(cases_sha256=digest(out/'cases.json'),results=results,
    passed=sum(r['passed'] for r in results),total=len(results)))
print(json.dumps(results))
