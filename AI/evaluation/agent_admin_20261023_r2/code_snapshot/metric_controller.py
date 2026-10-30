"""Optional Colab-trained metric head; cannot choose tools, periods or permissions.

The original Vietnamese embedding service remains unchanged. Only reviewed,
versioned JSON weights are accepted; no pickle or executable model is loaded.
"""
from functools import lru_cache
import hashlib
import json
import math
import os
from pathlib import Path
from urllib.parse import urlparse

import numpy as np
import requests

from . import metric_contract as contract


@lru_cache(maxsize=4)
def load_controller(path, expected_sha256):
    raw=Path(path).read_bytes()
    if len(raw)>8_000_000 or hashlib.sha256(raw).hexdigest()!=expected_sha256:
        raise ValueError('Metric controller integrity mismatch')
    config=json.loads(raw)
    expected=dict(contract_version=contract.CONTRACT_VERSION,base_model=contract.BASE_MODEL,
                  base_revision=contract.BASE_REVISION,labels=contract.LABELS,feature_dim=768,
                  max_tokens=256,pooling='masked_mean_l2',segmentation='pyvi',
                  input_contract_sha256=hashlib.sha256(Path(contract.__file__).read_bytes()).hexdigest())
    if any(config.get(k)!=v for k,v in expected.items()):
        raise ValueError('Metric controller input/encoder contract mismatch')
    kind=config.get('kind')
    shapes={'linear':[(7,768),(7,)],'mlp':[(128,768),(128,),(7,128),(7,)]}
    if kind not in shapes: raise ValueError('Unsupported metric head')
    weights=[np.asarray(v,dtype=np.float32) for v in config.get('weights',[])]
    if [w.shape for w in weights]!=shapes[kind] or any(not np.isfinite(w).all() for w in weights):
        raise ValueError('Invalid metric head weights')
    if not .01<float(config['temperature'])<20 or not 0<float(config['threshold'])<=1.00001:
        raise ValueError('Invalid metric calibration')
    return config,weights


def predict_features(config,weights,features):
    x=np.asarray(features,dtype=np.float32)
    if x.shape!=(768,) or not np.isfinite(x).all(): raise ValueError('Invalid metric features')
    logits=x@weights[0].T+weights[1]
    if config['kind']=='mlp':
        # Exact GELU used by torch training (not the tanh approximation).
        hidden=.5*logits*(1+np.asarray([math.erf(float(v)/math.sqrt(2)) for v in logits]))
        logits=hidden@weights[2].T+weights[3]
    logits=logits/float(config['temperature']);probs=np.exp(logits-logits.max());probs/=probs.sum()
    index=int(probs.argmax());confidence=float(probs[index]);label=contract.LABELS[index]
    return dict(label=label,confidence=confidence,accepted=confidence>=float(config['threshold']))


def refine_metric(question,role,memory,plan):
    """Fail open to the existing planner; scope is admin product ranking only."""
    path=os.getenv('METRIC_CONTROLLER_PATH','');sha=os.getenv('METRIC_CONTROLLER_SHA256','')
    if not path or not sha or role!='admin' or plan.get('intent')!='top_products': return plan
    url=os.getenv('VI_EMBEDDING_URL','').rstrip('/')
    if urlparse(url).hostname not in ('127.0.0.1','localhost','::1'): return plan
    try:
        config,weights=load_controller(path,sha)
        text=contract.metric_text(question,memory,'top_products')
        response=requests.post(url+'/embed',json={'texts':[text]},timeout=(2,15))
        response.raise_for_status();payload=response.json()
        if payload.get('revision')!=contract.BASE_REVISION or payload.get('truncated')!=[False]: return plan
        prediction=predict_features(config,weights,payload['embeddings'][0])
        # Inherit/uncertain/clarify predictions remain with the conversational
        # planner. They are not allowed to replace a tool or a pending request.
        if not prediction['accepted'] or prediction['label'] not in ('revenue','units','gross_profit'): return plan
        revised=dict(plan);revised['metric']=prediction['label']
        revised['changed_slots']=list(dict.fromkeys([*plan.get('changed_slots',[]),'metric']))
        revised['metric_decision']={'source':'Colab metric-v4.1','label':prediction['label'],
                                    'confidence':round(prediction['confidence'],6),'sha256':sha}
        return revised
    except (OSError,ValueError,KeyError,TypeError,IndexError,requests.RequestException):
        return plan
