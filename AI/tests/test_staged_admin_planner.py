import pytest
import shopbot.admin_conversation as module


@pytest.mark.parametrize('operation',['data_quality','unsupported','clarify'])
def test_non_financial_actions_never_request_metric_or_date_slots(monkeypatch,operation):
    calls=[]
    def chat(system,payload,schema,max_tokens):
        calls.append(schema);return dict(operation=operation)
    monkeypatch.setattr(module,'chat',chat)
    assert module.StagedAdminPlanner()({'question':'fixture'})==dict(operation=operation,metric='overview',time_mode='missing',period_unit='none')
    assert len(calls)==1 and set(calls[0]['properties'])=={'operation'}


@pytest.mark.parametrize('operation',['finance','chart','compare'])
def test_slot_stage_cannot_replace_classified_action(monkeypatch,operation):
    calls=[]
    def chat(system,payload,schema,max_tokens):
        calls.append(schema)
        if len(calls)==1:return dict(operation=operation)
        assert schema['properties']['operation']['enum']==[operation]
        assert payload['operation']==operation
        return dict(operation=operation,metric='cost',time_mode='explicit',period_unit='month')
    monkeypatch.setattr(module,'chat',chat)
    assert module.StagedAdminPlanner()({'question':'fixture'})['operation']==operation
    assert module.SCHEMA['properties']['operation']['enum']==['finance','chart','compare','data_quality','unsupported','clarify']


def test_model_cannot_change_action_between_stages(monkeypatch):
    replies=iter([dict(operation='chart'),dict(operation='finance')])
    monkeypatch.setattr(module,'chat',lambda *args,**kwargs:next(replies))
    with pytest.raises(ValueError,match='changed operation'):module.StagedAdminPlanner()({})


def test_invalid_action_or_extra_authority_slot_fails_closed(monkeypatch):
    monkeypatch.setattr(module,'chat',lambda *args,**kwargs:dict(operation='data_quality',role='admin'))
    with pytest.raises(ValueError,match='Invalid operation'):module.StagedAdminPlanner()({})
