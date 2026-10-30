"""Colab CPU/GPU: freeze Vietnamese encoder, learn and calibrate metric heads."""
import hashlib
import json
import os
from pathlib import Path
import random
import time

os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
import numpy as np
import torch
from torch import nn
from transformers import AutoTokenizer,AutoModel
from pyvi.ViTokenizer import tokenize
from scipy.optimize import minimize_scalar
from scipy.special import softmax
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,f1_score,classification_report,log_loss

ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
manifest=json.loads((ROOT/'data/manifest.json').read_text())
LABELS=manifest['labels'];seed=202610194
random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
torch.set_num_threads(2)
device='cuda' if torch.cuda.is_available() else 'cpu'
started=time.monotonic()
tokenizer=AutoTokenizer.from_pretrained(manifest['base_model'],revision=manifest['base_revision'],trust_remote_code=False)
encoder=AutoModel.from_pretrained(manifest['base_model'],revision=manifest['base_revision'],trust_remote_code=False).eval().to(device)
for parameter in encoder.parameters():parameter.requires_grad=False
limit=min(256,encoder.config.max_position_embeddings-2)
datasets={s:[json.loads(line) for line in (ROOT/f'data/{s}.jsonl').read_text().splitlines()] for s in ('train','validation','test')}
all_texts=[r['text'] for rows in datasets.values() for r in rows]
assert len(all_texts)==len(set(all_texts)),'Normalized-text leakage between splits'

@torch.inference_mode()
def encode(split):
    rows=datasets[split]
    texts=[tokenize(r['text']) for r in rows]
    key=hashlib.sha256((manifest['base_revision']+json.dumps(texts,ensure_ascii=False)).encode()).hexdigest()
    cache=OUT/f'features-{split}-{key[:12]}.npz'
    if cache.exists():
        saved=np.load(cache,allow_pickle=False);return saved['features'],saved['truncated']
    vectors=[];truncated=[];batch_size=32 if device=='cuda' else 8
    for start in range(0,len(texts),batch_size):
        batch=texts[start:start+batch_size]
        lengths=tokenizer(batch,truncation=False)['input_ids']
        truncated.extend(len(v)>limit for v in lengths)
        inputs=tokenizer(batch,padding=True,truncation=True,max_length=limit,return_tensors='pt').to(device)
        hidden=encoder(**inputs).last_hidden_state
        mask=inputs['attention_mask'].unsqueeze(-1)
        pooled=(hidden*mask).sum(1)/mask.sum(1).clamp(min=1)
        vectors.append(nn.functional.normalize(pooled,p=2,dim=1).cpu().numpy())
        if start%256==0 or start+batch_size>=len(texts):
            print('EMBEDDING',split,min(start+batch_size,len(texts)),'/',len(texts),flush=True)
    features=np.concatenate(vectors).astype('float32');truncated=np.array(truncated,dtype=bool)
    np.savez_compressed(cache,features=features,truncated=truncated)
    return features,truncated

print('METRIC V4 — FROZEN VIETNAMESE ENCODER + SUPERVISED HEAD',flush=True)
print(json.dumps(dict(device=device,base=manifest['base_model'],revision=manifest['base_revision'],
    samples={k:len(v) for k,v in datasets.items()},encoder_trainable_parameters=0,max_tokens=limit)),flush=True)
X={};truncation={};Y={s:np.array([LABELS.index(r['label']) for r in rows]) for s,rows in datasets.items()}
for split in datasets:
    X[split],truncated=encode(split);truncation[split]=dict(count=int(truncated.sum()),samples=len(truncated))
del encoder
if device=='cuda':torch.cuda.empty_cache()

def stats(logits,split):
    predicted=logits.argmax(1)
    return dict(samples=len(predicted),accuracy=float(accuracy_score(Y[split],predicted)),
                macro_f1=float(f1_score(Y[split],predicted,labels=list(range(len(LABELS))),average='macro',zero_division=0)))

candidates=[];best=None
for regularization in (.3,1.,3.,10.,30.):
    model=LogisticRegression(C=regularization,class_weight='balanced',max_iter=2500,random_state=seed)
    model.fit(X['train'],Y['train'])
    assert list(model.classes_)==list(range(len(LABELS)))
    logits=model.decision_function(X['validation']);metrics=stats(logits,'validation')
    metrics.update(kind='linear',C=regularization,log_loss=float(log_loss(Y['validation'],softmax(logits,axis=1),labels=list(range(len(LABELS))))))
    candidates.append(metrics);print('VALIDATION',json.dumps(metrics),flush=True)
    key=(metrics['macro_f1'],-metrics['log_loss'])
    if best is None or key>best['key']:
        best=dict(key=key,kind='linear',weights=[model.coef_.astype('float32'),model.intercept_.astype('float32')],metrics=metrics)

# A small nonlinear head can distinguish contrastive/negated metric phrases.
class MetricHead(nn.Module):
    def __init__(self):
        super().__init__();self.first=nn.Linear(768,128);self.last=nn.Linear(128,len(LABELS));self.drop=nn.Dropout(.15)
    def forward(self,features):return self.last(self.drop(nn.functional.gelu(self.first(features))))

head=MetricHead()
features=torch.from_numpy(X['train']);targets=torch.from_numpy(Y['train'])
counts=np.bincount(Y['train'],minlength=len(LABELS));class_weights=torch.tensor(len(targets)/(len(LABELS)*counts),dtype=torch.float32)
optimizer=torch.optim.AdamW(head.parameters(),lr=.002,weight_decay=.01)
generator=torch.Generator().manual_seed(seed)
loader=torch.utils.data.DataLoader(torch.utils.data.TensorDataset(features,targets),batch_size=64,shuffle=True,generator=generator)
for epoch in range(1,41):
    head.train();total_loss=0.
    for batch,labels in loader:
        optimizer.zero_grad(set_to_none=True)
        loss=nn.functional.cross_entropy(head(batch),labels,weight=class_weights)
        loss.backward();optimizer.step();total_loss+=float(loss.detach())
    head.eval()
    with torch.inference_mode():logits=head(torch.from_numpy(X['validation'])).numpy()
    metrics=stats(logits,'validation')
    metrics.update(kind='mlp',epoch=epoch,train_loss=total_loss/len(loader),
                   log_loss=float(log_loss(Y['validation'],softmax(logits,axis=1),labels=list(range(len(LABELS))))))
    candidates.append(metrics)
    if epoch%5==0:print('VALIDATION',json.dumps(metrics),flush=True)
    key=(metrics['macro_f1'],-metrics['log_loss'])
    if key>best['key']:
        best=dict(key=key,kind='mlp',weights=[v.detach().numpy().copy() for v in (head.first.weight,head.first.bias,head.last.weight,head.last.bias)],metrics=metrics)

def logits_of(split):
    x=torch.from_numpy(X[split]);weights=[torch.from_numpy(v) for v in best['weights']]
    if best['kind']=='linear':return (x@weights[0].T+weights[1]).numpy()
    return (nn.functional.gelu(x@weights[0].T+weights[1])@weights[2].T+weights[3]).numpy()

validation_logits=logits_of('validation')
def nll(temp):return log_loss(Y['validation'],softmax(validation_logits/temp,axis=1),labels=list(range(len(LABELS))))
temperature=float(minimize_scalar(nll,bounds=(.15,5.),method='bounded').x)
probabilities=softmax(validation_logits/temperature,axis=1)
prediction=probabilities.argmax(1);confidence=probabilities.max(1)
# Tune acceptance only on validation, never on frozen test results.
threshold=1.000001;acceptance=None
for threshold_candidate in np.linspace(.70,.999,300):
    accept=(confidence>=threshold_candidate)&np.isin(prediction,[0,1,2,3,4,6])
    if accept.sum()>=30 and float((prediction[accept]==Y['validation'][accept]).mean())>=.995:
        threshold=float(threshold_candidate);acceptance=dict(samples=int(accept.sum()),precision=float((prediction[accept]==Y['validation'][accept]).mean()));break

test_logits=logits_of('test');test_prob=softmax(test_logits/temperature,axis=1)
test_pred=test_prob.argmax(1);test_conf=test_prob.max(1)
test_accept=(test_conf>=threshold)&np.isin(test_pred,[0,1,2,3,4,6])
test_metrics=stats(test_logits,'test')
test_metrics.update(accepted=int(test_accept.sum()),accepted_precision=float((test_pred[test_accept]==Y['test'][test_accept]).mean()) if test_accept.any() else None,
                    coverage=float(test_accept.mean()),classification_report=classification_report(Y['test'],test_pred,target_names=LABELS,zero_division=0,output_dict=True))
config=dict(contract_version=manifest['version'],base_model=manifest['base_model'],base_revision=manifest['base_revision'],
            input_contract_sha256=manifest['input_contract_sha256'],labels=LABELS,kind=best['kind'],
            max_tokens=limit,feature_dim=768,pooling='masked_mean_l2',segmentation='pyvi',
            temperature=temperature,threshold=threshold,weights=[v.tolist() for v in best['weights']])
(OUT/'metric_controller.json').write_text(json.dumps(config,separators=(',',':')),encoding='utf8')
failures=[]
for row,label,confidence in zip(datasets['test'],test_pred,test_conf):
    if LABELS[label]!=row['label']:failures.append(dict(id=row['id'],question=row['question'],memory=row['memory'],expected=row['label'],predicted=LABELS[label],confidence=float(confidence)))
(OUT/'tutor-failures.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in failures),encoding='utf8')
report=dict(training='Frozen Vietnamese encoder; supervised linear/MLP head trained on Colab CPU or GPU',device=device,
            selected=best['metrics'],temperature=temperature,validation_acceptance=acceptance,threshold=threshold,
            test=test_metrics,truncation=truncation,elapsed_seconds=time.monotonic()-started,
            trainable_parameters=sum(v.size for v in best['weights']),encoder_trainable_parameters=0,
            source_revision=manifest['base_revision'],deployment_approved=False,
            limitations=['Synthetic phrasing-family test is not production accuracy.','Live 106+12 regressions and new independent questions must pass before activation.',
                        'No financial number is learned. No intent, role or SQL is selected by this head.'])
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print('FROZEN TEST',json.dumps(test_metrics),flush=True)
print('SELECTED',best['kind'],'THRESHOLD',threshold,'SECONDS',round(report['elapsed_seconds'],1),flush=True)
print('CONTROLLER SHA256',hashlib.sha256((OUT/'metric_controller.json').read_bytes()).hexdigest(),flush=True)
