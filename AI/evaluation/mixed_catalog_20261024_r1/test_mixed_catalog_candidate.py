import pytest
from test_agent_conversation import make_agent,plan
from test_catalog_planner import payload
from shopbot.catalog_planner import StagedCatalogPlanner,validate_mixed_questions

Q='Tìm 3 laptop dưới 30 triệu và giải thích OLED là gì'
PARTS=dict(catalog_question='Tìm 3 laptop dưới 30 triệu',knowledge_question='giải thích OLED là gì')


def test_mixed_search_keeps_exact_catalog_evidence_and_honest_disabled_knowledge(make_agent):
    engine=make_agent(lambda _:plan(action='search_documents',budget_max_vnd=30_000_000,limit=3,**PARTS))
    r=engine.ask(Q)
    assert r['basic_action']=='answer' and r['partial'] and len(r['rows'])==3
    assert [c['tool'] for c in r['tool_evidence']['calls']]==['catalog.search','documents.answer']
    assert r['tool_evidence']['calls'][1]['arguments']==dict(question=PARTS['knowledge_question'])
    assert r['components']['catalog']['status']=='completed'
    assert r['components']['documents']['status']=='disabled' and r['components']['documents']['executed'] is False
    assert len(r['sources'])==1 and 'chưa được kết nối' in r['answer']
    assert r['profile']['catalog_context']['filters']['limit']==3


def test_mixed_comparison_binds_prior_actual_selection_without_claiming_knowledge(make_agent):
    def planner(p):
        if not p['last_selection']:return plan(budget_max_vnd=30_000_000,limit=3)
        return plan(action='compare_documents',product_refs=[p['last_selection'][0]['ref'],p['last_selection'][1]['ref']],
            catalog_question='So máy thứ1 với thứ2',knowledge_question='giải thích RAM là gì')
    engine=make_agent(planner);first=engine.ask('Tìm 3 laptop dưới 30 triệu')
    r=engine.ask('So máy thứ1 với thứ2 và giải thích RAM là gì',profile=first['profile'])
    assert [c['tool'] for c in r['tool_evidence']['calls']]==['catalog.compare','documents.answer']
    assert r['partial'] and '| RAM (GB) |' in r['answer']
    assert len(r['profile']['history'])==2


@pytest.mark.parametrize('parts',[
 dict(catalog_question='Tìm laptop',knowledge_question=PARTS['knowledge_question']),
 dict(catalog_question=Q,knowledge_question=PARTS['knowledge_question']),
 dict(catalog_question='Tìm 3 laptop',knowledge_question=PARTS['knowledge_question']),
 dict(catalog_question=PARTS['catalog_question'],knowledge_question='Giải thích OLED'),
 dict(catalog_question='',knowledge_question=PARTS['knowledge_question']),
])
def test_unquoted_overlapping_or_dropped_constraints_fail_closed(parts,make_agent):
    with pytest.raises(ValueError):validate_mixed_questions(Q,parts)
    r=make_agent(lambda _:plan(action='search_documents',**parts)).ask(Q)
    assert r['basic_action']=='unavailable' and not r['rows'] and 'tool_evidence' not in r


def test_mixed_planner_extracts_source_spans_before_catalog_operands():
    seen=[]
    def caller(system,data,schema,**kwargs):
        seen.append(data)
        if 'action' in schema['properties']:return dict(action='search_documents')
        if 'catalog_question' in schema['properties']:return PARTS
        return dict(category='laptop',brand='',continuation=False,clear_brand=False,extra_requirements=[])
    p=payload();p['question']=Q
    r=StagedCatalogPlanner(caller)(p)
    assert r['action']=='search_documents' and r['budget_max_vnd']==30_000_000 and r['limit']==3
    assert r['knowledge_question']==PARTS['knowledge_question']
    assert seen[2]['request']==PARTS['catalog_question'] and not r['unsupported_filters']
    assert len(seen)==3 and all('catalog' not in c for c in seen)


def test_missing_catalog_budget_still_reports_knowledge_branch_status(make_agent):
    parts=dict(catalog_question='Tìm laptop',knowledge_question='giải thích OLED')
    r=make_agent(lambda _:plan(action='search_documents',budget_max_vnd=0,**parts)).ask('Tìm laptop và giải thích OLED')
    assert r['basic_action']=='clarify' and r['partial'] and not r['rows']
    assert [c['tool'] for c in r['tool_evidence']['calls']]==['documents.answer']
    assert r['components']['catalog']['status']=='clarify'
