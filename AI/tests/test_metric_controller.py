import hashlib
import json
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

from shopbot import metric_contract as contract
from shopbot.metric_controller import load_controller,predict_features,refine_metric


def configuration():
    return dict(contract_version=contract.CONTRACT_VERSION,base_model=contract.BASE_MODEL,
        base_revision=contract.BASE_REVISION,labels=contract.LABELS,feature_dim=768,max_tokens=256,
        pooling='masked_mean_l2',segmentation='pyvi',kind='linear',temperature=1,threshold=.95,
        input_contract_sha256=hashlib.sha256(Path(contract.__file__).read_bytes()).hexdigest(),
        weights=[np.zeros((7,768)).tolist(),[20,0,0,0,0,0,0]])


def install(tmp_path,monkeypatch,config=None):
    config=config or configuration();path=tmp_path/'controller.json';path.write_text(json.dumps(config))
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setenv('METRIC_CONTROLLER_PATH',str(path));monkeypatch.setenv('METRIC_CONTROLLER_SHA256',digest)
    monkeypatch.setenv('VI_EMBEDDING_URL','http://127.0.0.1:8011')
    response=Mock();response.json.return_value=dict(revision=contract.BASE_REVISION,truncated=[False],embeddings=[[0]*768])
    post=Mock(return_value=response);monkeypatch.setattr('shopbot.metric_controller.requests.post',post)
    return path,digest,post,response


def test_integrity_contract_and_weight_validation(tmp_path,monkeypatch):
    path,digest,_,_=install(tmp_path,monkeypatch)
    assert load_controller(str(path),digest)[0]['kind']=='linear'
    with pytest.raises(ValueError): load_controller(str(path),'0'*64)
    config=configuration();config['base_revision']='wrong';path,digest,_,_=install(tmp_path,monkeypatch,config)
    load_controller.cache_clear()
    with pytest.raises(ValueError):load_controller(str(path),digest)
    config=configuration();config['weights'][0]=[[0]];path,digest,_,_=install(tmp_path,monkeypatch,config)
    with pytest.raises(ValueError):load_controller(str(path),digest)


def test_scope_does_not_change_intent_period_filter_or_permissions(tmp_path,monkeypatch):
    _,_,post,_=install(tmp_path,monkeypatch)
    plan=dict(intent='top_products',metric='units',changed_slots=[],time_mode='explicit',category='mouse',limit=2)
    corrected=refine_metric('Doanh số','admin',{},plan)
    assert corrected['metric']=='revenue' and corrected['changed_slots']==['metric']
    assert plan['metric']=='units'
    assert corrected['metric_decision']['source']=='Colab metric-v4.1'
    assert {k:v for k,v in corrected.items() if k not in ('metric','changed_slots','metric_decision')}=={k:v for k,v in plan.items() if k not in ('metric','changed_slots')}
    post.reset_mock()
    assert refine_metric('Doanh số','customer',{},plan) is plan
    compare=dict(plan,intent='compare');assert refine_metric('Doanh số','admin',{},compare) is compare
    assert not post.called


@pytest.mark.parametrize('label',[3,4,5,6])
def test_unsupported_or_nonexplicit_predictions_cannot_override(tmp_path,monkeypatch,label):
    config=configuration();config['weights'][1]=[20 if i==label else 0 for i in range(7)]
    install(tmp_path,monkeypatch,config)
    plan=dict(intent='top_products',metric='units',changed_slots=[])
    assert refine_metric('Cùng tiêu chí','admin',{},plan) is plan


def test_uncertainty_truncation_and_worker_failure_preserve_planner(tmp_path,monkeypatch):
    config=configuration();config['weights'][1]=[0]*7
    _,_,post,response=install(tmp_path,monkeypatch,config)
    plan=dict(intent='top_products',metric='units',changed_slots=[])
    assert refine_metric('Có thể là gì','admin',{},plan) is plan
    response.json.return_value['truncated']=[True]
    assert refine_metric('Câu dài','admin',{},plan) is plan
    post.side_effect=ValueError('bad response')
    assert refine_metric('Lỗi worker','admin',{},plan) is plan


def test_exact_gelu_export_math():
    config=dict(kind='mlp',temperature=1,threshold=.8)
    first=np.zeros((128,768),dtype=np.float32);bias=np.zeros(128,dtype=np.float32);bias[0]=1
    last=np.zeros((7,128),dtype=np.float32);last[2,0]=10
    prediction=predict_features(config,[first,bias,last,np.zeros(7)],np.zeros(768))
    assert prediction['label']=='gross_profit' and prediction['accepted']
    with pytest.raises(ValueError):predict_features(config,[],[0])
