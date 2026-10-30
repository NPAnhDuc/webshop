"""Deterministic tool evaluation; no LLM calls and no conversational accuracy claim."""
import json
from pathlib import Path
import sys
from time import perf_counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from shopbot.agent_tools import AgentTools,CatalogTools
from shopbot.curated_reader import CuratedReader
from shopbot.de_snapshot import digest,write_new

out=Path(__file__).parent
revision=ROOT/'data/de_pipeline/retail_sim_v1/curated_20261024_r1'
pin=digest(revision/'manifest.json')  # Deployment must pin this in trusted server configuration.
catalog=CatalogTools(json.loads((ROOT/'data/agent_platform_20261023/catalog_v1/catalog_public.json').read_text(encoding='utf-8')))
tools=AgentTools(catalog,None,curated_reader=CuratedReader(revision,pin))
started=perf_counter();result=tools.execute('admin','admin.data_quality',{});elapsed=perf_counter()-started
assert result['row_counts']==dict(products=67,financial_ledger=1748,operating_expenses=99,inventory_daily=24455)
assert result['data_kind']=='simulation' and result['observed_financial_dates']==dict(first='2025-10-01',last='2026-09-30')
assert result['coverage']['sales']=='unverified; absent days are not zero'
checks=[dict(case='admin_quality_exact_source_counts_dates_coverage',passed=True)]
for role,args,error in [('customer',{},PermissionError),('owner',{},PermissionError),
        ('admin',{'sql':'SELECT * FROM financial_ledger'},ValueError),('admin',{'path':'backend/data'},ValueError)]:
    try: tools.execute(role,'admin.data_quality',args)
    except error: checks.append(dict(case=f'{role}:{list(args)}:blocked',passed=True))
    else: raise AssertionError('Tool accepted forbidden request')
try: AgentTools(catalog,None).execute('admin','admin.data_quality',{})
except ValueError: checks.append(dict(case='unconfigured_source_no_fallback',passed=True))
else: raise AssertionError('Unconfigured reader accepted')
write_new(out/'result.json',result)
write_new(out/'summary.json',dict(kind='deterministic_tool_evaluation',checks=checks,passed=True,
    admin_read_seconds=elapsed,server_pin=pin,model_calls=0,active_source_changed=False,
    conversational_evaluation=False))
snap=out/'code_snapshot';snap.mkdir(exist_ok=False)
for name in ['curated_reader.py','agent_tools.py','de_curated.py','de_snapshot.py']:
    path=ROOT/'shopbot'/name;(snap/name).write_bytes(path.read_bytes())
print(json.dumps(dict(passed=True,cases=len(checks),admin_read_seconds=elapsed)))
