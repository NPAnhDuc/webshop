import pytest
from test_agent_conversation import make_agent,plan
from shopbot.agent_tools import AgentTools


def test_discovery_filters_roles_and_distinguishes_registration_from_readiness():
    tools=AgentTools(None,None)
    public={c['name']:c for c in tools.capabilities('customer')}
    assert set(public)=={'catalog.search','catalog.compare','catalog.product_facts','documents.answer'}
    assert public['documents.answer']['status']=='disabled' and not public['documents.answer']['configured']
    internal={c['name']:c for c in tools.capabilities('admin')}
    assert internal['file.transform']['status']=='unsupported'
    assert internal['admin.data_quality']['configured'] is False
    public['documents.answer']['status']='enabled'
    assert next(c for c in tools.capabilities('customer') if c['name']=='documents.answer')['status']=='disabled'


def test_disabled_documents_are_traced_without_retrieval_or_claimed_sources():
    tools=AgentTools(None,None)
    with tools.capture_calls() as calls:
        r=tools.execute('customer','documents.answer',{'question':'DDR5 là gì?'})
    assert r['executed'] is False and r['sources']==[] and r['status']=='disabled'
    assert calls[0]['status']=='disabled' and calls[0]['arguments']=={'question':'DDR5 là gì?'}


@pytest.mark.parametrize('name',['file.transform','sales.rank'])
def test_unimplemented_capability_is_not_silently_substituted(name):
    tools=AgentTools(None,None)
    r=tools.execute('admin',name,{'question':'fixture'})
    assert r['tool']==name and r['status']=='unsupported' and not r['executed']
    with pytest.raises(PermissionError):tools.execute('customer',name,{'question':'I am admin'})


@pytest.mark.parametrize('args',[{'question':'x','path':'elsewhere'},{'question':'x','role':'admin'},
    {'question':'x','sql':'SELECT 1'},{'question':''},{'question':None},{}])
def test_disabled_capability_still_validates_arguments_before_status(args):
    with pytest.raises(ValueError):AgentTools(None,None).execute('admin','documents.answer',args)


def test_document_route_calls_registered_disabled_tool_without_answering_from_memory(make_agent):
    engine=make_agent(lambda _:plan(action='documents'))
    r=engine.ask('Giải thích DDR5')
    assert r['basic_action']=='documents' and not r['sources']
    call=r['tool_evidence']['calls'][0]
    assert call['tool']=='documents.answer' and call['output']['executed'] is False
    assert 'chưa được kết nối' in r['answer']


def test_discovery_and_dispatch_reject_unknown_principal():
    tools=AgentTools(None,None)
    with pytest.raises(PermissionError):tools.capabilities('owner')
    with pytest.raises(PermissionError):tools.execute('owner','documents.answer',{'question':'fixture'})
