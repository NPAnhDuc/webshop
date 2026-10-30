"""Before/after confirmed-state contract under a deliberately incorrect advisory plan."""
from datetime import date
import json
from pathlib import Path
import sqlite3
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from shopbot.admin_conversation import AdminConversation
from shopbot.agent_tools import AgentTools
from shopbot.de_snapshot import digest,write_new
out=Path(__file__).parent;db=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
bank=json.loads((out/'bank.json').read_text(encoding='utf-8'));checks=[]
for c in bank:
    agent=AdminConversation(AgentTools(None,db),lambda _:dict(operation='clarify',metric='overview',time_mode='missing',period_unit='none'))
    result=agent.run(c['question'],'admin',c['memory'],date(2026,10,23))
    calls=result.get('tool_evidence',{}).get('calls',[])
    with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True) as con:
        costs=[con.execute('SELECT SUM(cost) FROM financial_ledger WHERE day>=? AND day<?',(p['start'],p['end'])).fetchone()[0] for p in c['expected_periods']]
    actual=result.get('metric_rows',[])
    numeric=(bool(actual) and (actual[0].get('baseline')==costs[0] and actual[0].get('current')==costs[1] if len(costs)==2 else actual[0].get('value')==costs[0]))
    passed=(result['basic_action']=='answer' and [c['arguments'] for c in calls]==c['expected_periods']
        and result.get('admin_plan',{}).get('operation')==c['expected_operation'] and numeric)
    checks.append(dict(id=c['id'],passed=passed,action=result['basic_action'],cost_oracle=costs,actual_calls=calls))
write_new(out/(sys.argv[1]+'.json'),dict(bank_sha256=digest(out/'bank.json'),checks=checks,passed=sum(c['passed'] for c in checks),total=3,oracle='independent raw SQL; no bot calculation function used for expected values'))
print(json.dumps(dict(passed=sum(c['passed'] for c in checks),total=3)))
