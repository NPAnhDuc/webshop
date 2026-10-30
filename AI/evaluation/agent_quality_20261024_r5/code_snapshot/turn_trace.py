"""Server-owned per-turn JSON traces, separate from knowledge and training data."""
import copy
from datetime import datetime,timezone
import json
import re
from pathlib import Path
from time import perf_counter
from uuid import uuid4


def state(profile,role):
    profile=profile or {}
    if profile.get('owner_role',role)!=role:return {}
    keys=['owner_role','catalog_context']+(['admin_context'] if role=='admin' else [])
    return {key:copy.deepcopy(profile[key]) for key in keys if key in profile}


class TracedAgent:
    def __init__(self,agent,directory):
        self.agent=agent;self.tools=agent.tools
        self.directory=Path(directory).resolve()

    def run(self,question,role,memory,today):
        if role not in ('customer','admin'):raise PermissionError('Unknown server role for turn trace')
        identifier=uuid4().hex;started=perf_counter()
        before=state(memory,role);result=None;error=None
        parent=(memory or {}).get('trace_parent_id')
        if not isinstance(parent,str) or not re.fullmatch('[0-9a-f]{32}',parent):parent=None
        with self.tools.capture_calls() as calls:
            try:
                result=self.agent.run(question,role,memory,today)
                return result
            except Exception as exc:
                error=type(exc).__name__;raise
            finally:
                record=dict(schema='agent-turn-trace-v1',trace_id=identifier,
                    parent_trace_id=parent,
                    recorded_at=datetime.now(timezone.utc).isoformat(),server_date=today.isoformat(),
                    principal_role=role,question=question,training_allowed=False,
                    state_before=before,state_after=state(result.get('profile'),role) if result else {},
                    plans={key:copy.deepcopy(result[key]) for key in ['plan','admin_plan'] if result and key in result},
                    calls=copy.deepcopy(calls),
                    result={key:copy.deepcopy(result[key]) for key in ['intent','basic_action','answer','sources','result_contract'] if result and key in result},
                    error_type=error,seconds=perf_counter()-started)
                try:
                    # Role folders are diagnostics separation, not an HTTP auth layer.
                    folder=self.directory/role;folder.mkdir(parents=True,exist_ok=True)
                    with (folder/(identifier+'.json')).open('x',encoding='utf-8') as stream:
                        json.dump(record,stream,ensure_ascii=False,indent=2)
                    if result is not None:
                        result['trace_id']=identifier
                        result.setdefault('profile',{})['trace_parent_id']=identifier
                except OSError:
                    if result is not None:result.setdefault('trace',[]).append('audit: structured turn trace could not be written')
