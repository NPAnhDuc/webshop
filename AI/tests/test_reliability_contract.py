import copy
from datetime import date
import json
from pathlib import Path
import pytest
from test_agent_conversation import make_agent,plan
from test_agent_tools import catalog
from shopbot.agent_tools import AgentTools
from shopbot.catalog_planner import search_literals,SearchClarification
from shopbot.turn_trace import TracedAgent

CASES=json.loads((Path(__file__).resolve().parents[1]/'evaluation/regression_contract_20261024_r1/count_cases.json').read_text(encoding='utf-8'))


@pytest.mark.parametrize('case',CASES,ids=[c['id'] for c in CASES])
def test_frozen_literal_count_regressions(case):
    if case.get('clarify'):
        with pytest.raises(SearchClarification):search_literals(case['question'])
    else:
        budget,_,count,_=search_literals(case['question'])
        assert (budget,count)==(case['budget'],case['count'])


def test_wrong_tool_cardinality_never_reaches_answer(make_agent,monkeypatch):
    engine=make_agent(lambda _:plan(limit=1,budget_max_vnd=30_000_000))
    tools=engine.tool_agent.tools;original=tools._execute
    def wrong(role,tool,args):
        output=original(role,tool,args)
        output['data']['products'].append(dict(output['data']['products'][0],id='extra'))
        output['data']['returned_count']=2
        return output
    monkeypatch.setattr(tools,'_execute',wrong)
    result=engine.ask('Cho1máy')
    assert result['basic_action']=='clarify' and not result['rows']


def test_shortage_is_explicit_and_not_padded(make_agent):
    result=make_agent(lambda _:plan(limit=3)).ask('Cho3máydưới20triệu')
    assert result['result_contract']==dict(requested_count=3,returned_count=1,total_matching=1,shortage=True,passed=True)
    assert len(result['rows'])==1 and '1/3' in result['answer']


def test_trace_records_real_arguments_results_and_multi_turn_state(make_agent,tmp_path):
    count=0
    def planner(payload):
        nonlocal count
        count+=1
        if count==1:return plan(limit=2,budget_max_vnd=30_000_000)
        return plan(action='compare',product_refs=[p['ref'] for p in payload['last_selection']],continuation=True)
    engine=make_agent(planner)
    engine.tool_agent=TracedAgent(engine.tool_agent,tmp_path/'trace')
    first=engine.ask('Cho2máy');second=engine.ask('So2máyđó',profile=first['profile'])
    files={json.loads(p.read_text(encoding='utf-8'))['trace_id']:json.loads(p.read_text(encoding='utf-8')) for p in (tmp_path/'trace/customer').glob('*.json')}
    a=files[first['trace_id']];b=files[second['trace_id']]
    assert a['calls'][0]['arguments']['limit']==2 and a['calls'][0]['status']=='success'
    assert b['calls'][0]['tool']=='catalog.compare'
    assert b['state_before']['catalog_context']==a['state_after']['catalog_context']
    assert b['plans']['plan']['action']=='compare' and b['training_allowed'] is False
    assert b['parent_trace_id']==first['trace_id']
    assert 'history' not in b['state_before']


def test_nested_capture_scopes_do_not_mix_calls():
    tools=AgentTools(catalog(),None)
    with tools.capture_calls() as outer:
        with tools.capture_calls() as inner:
            with pytest.raises(PermissionError):tools.execute('customer','admin.finance',{})
        assert not outer
        tools.execute('customer','catalog.search',dict(max_price_exclusive=20_000_000,limit=1))
    assert inner[0]['status']=='denied' and 'output' not in inner[0]
    assert len(outer)==1 and outer[0]['tool']=='catalog.search'


def test_trace_write_failure_does_not_replace_valid_answer(make_agent,tmp_path):
    blocked=tmp_path/'file';blocked.write_text('not a directory')
    engine=make_agent(lambda _:plan());engine.tool_agent=TracedAgent(engine.tool_agent,blocked)
    result=engine.ask('Tìm máy')
    assert result['basic_action']=='answer' and 'trace_id' not in result
    assert any('could not be written' in item for item in result['trace'])


def test_unknown_role_cannot_choose_trace_folder(make_agent,tmp_path):
    traced=TracedAgent(make_agent(lambda _:plan()).tool_agent,tmp_path/'trace')
    with pytest.raises(PermissionError):traced.run('test','../escape',{},date(2026,10,24))
    assert not (tmp_path/'trace').exists()
