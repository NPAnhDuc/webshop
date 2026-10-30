"""Train Vietnamese conversation understanding on Colab; never memorize shop money."""
import copy
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
from torch.utils.data import DataLoader
from transformers import AutoTokenizer,AutoModel
from huggingface_hub import HfApi
from pyvi.ViTokenizer import tokenize
from safetensors.torch import save_file

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs';OUT.mkdir(exist_ok=True)
random.seed(61019);np.random.seed(61019);torch.manual_seed(61019)
assert torch.cuda.is_available(),'This training run requires a Colab GPU; select T4 first.'
torch.set_num_threads(2)
DEVICE='cuda'
MODEL='dangvantuan/vietnamese-embedding'
REVISION=HfApi().model_info(MODEL).sha
labels=json.loads((ROOT/'data/labels.json').read_text())
tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False)
encoder=AutoModel.from_pretrained(MODEL,revision=REVISION,trust_remote_code=False)
max_length=min(256,encoder.config.max_position_embeddings-2)

class Understanding(nn.Module):
    def __init__(self):
        super().__init__();self.encoder=encoder
        self.heads=nn.ModuleDict({key:nn.Linear(encoder.config.hidden_size,len(values)) for key,values in labels.items()})
    def forward(self,inputs):
        hidden=self.encoder(**inputs).last_hidden_state;mask=inputs['attention_mask'].unsqueeze(-1)
        pooled=(hidden*mask).sum(1)/mask.sum(1).clamp(min=1)
        return {key:head(pooled) for key,head in self.heads.items()}

net=Understanding().to(DEVICE)
for parameter in net.encoder.parameters(): parameter.requires_grad=False
# Adapt four top transformer layers; keep the pretrained lexical layers fixed.
for layer in net.encoder.encoder.layer[-4:]:
    for parameter in layer.parameters(): parameter.requires_grad=True
trainable_names={name for name,p in net.named_parameters() if p.requires_grad}
optimizer=torch.optim.AdamW([
    {'params':[p for name,p in net.named_parameters() if p.requires_grad and name.startswith('encoder.')],'lr':2e-5},
    {'params':list(net.heads.parameters()),'lr':8e-4}],weight_decay=.01)
datasets={s:[json.loads(line) for line in (ROOT/f'data/{s}.jsonl').read_text().splitlines()] for s in ('train','validation','test')}
groups={s:{r['group_id'] for r in rows} for s,rows in datasets.items()}
assert not(groups['train']&groups['validation'] or groups['train']&groups['test'] or groups['validation']&groups['test'])

def collate(rows):
    inputs=tokenizer([tokenize(r['text']) for r in rows],padding=True,truncation=True,max_length=max_length,return_tensors='pt')
    targets={key:torch.tensor([values.index(r['labels'][key]) for r in rows]) for key,values in labels.items()}
    return {k:v.to(DEVICE) for k,v in inputs.items()},{k:v.to(DEVICE) for k,v in targets.items()},rows

loaders={s:DataLoader(rows,batch_size=16,shuffle=s=='train',collate_fn=collate,num_workers=0) for s,rows in datasets.items()}

@torch.inference_mode()
def evaluate(split):
    net.eval();correct={key:0 for key in labels};joint=0;failures=[];total=0
    for inputs,targets,rows in loaders[split]:
        outputs=net(inputs);predicted={key:value.argmax(1) for key,value in outputs.items()}
        matches=torch.stack([predicted[key]==targets[key] for key in labels]).all(0)
        joint+=matches.sum().item();total+=len(rows)
        for key in labels: correct[key]+=(predicted[key]==targets[key]).sum().item()
        for i,row in enumerate(rows):
            if not matches[i].item(): failures.append({'id':row['id'],'question':row['question'],'memory':row['memory'],'expected':row['labels'],
                'predicted':{key:labels[key][predicted[key][i].item()] for key in labels}})
    return {'samples':total,'joint_accuracy':joint/total,'head_accuracy':{key:n/total for key,n in correct.items()}},failures

started=time.monotonic();validation=[];best=-1;best_epoch=None;steps=0
print('SHOPBOT V3 — Vietnamese contextual understanding',flush=True)
print(json.dumps({'gpu':torch.cuda.get_device_name(),'model':MODEL,'revision':REVISION,'samples':{s:len(v) for s,v in datasets.items()},
    'trainable_parameters':sum(p.numel() for p in net.parameters() if p.requires_grad),'max_tokens':max_length}),flush=True)
for epoch in range(1,5):
    net.train();loss_sum=0
    for inputs,targets,rows in loaders['train']:
        optimizer.zero_grad(set_to_none=True)
        outputs=net(inputs)
        loss=sum(nn.functional.cross_entropy(outputs[key],targets[key]) for key in labels)/len(labels)
        loss.backward();torch.nn.utils.clip_grad_norm_([p for p in net.parameters() if p.requires_grad],1.)
        optimizer.step();steps+=1;loss_sum+=loss.item()
    metrics,_=evaluate('validation');metrics.update(epoch=epoch,train_loss=loss_sum/len(loaders['train']))
    validation.append(metrics);print('VALIDATION',json.dumps(metrics),flush=True)
    if metrics['joint_accuracy']>best:
        best=metrics['joint_accuracy'];best_epoch=epoch
        save_file({name:value.detach().cpu().half().contiguous() for name,value in net.state_dict().items() if name in trainable_names},str(OUT/'conversation_adapter.safetensors'))

from safetensors.torch import load_file
net.load_state_dict(load_file(str(OUT/'conversation_adapter.safetensors')),strict=False)
test,failures=evaluate('test')
report={'task':'Vietnamese conversational intent/time/metric/unit classification','base_model':MODEL,'base_revision':REVISION,
    'gpu':torch.cuda.get_device_name(),'epochs':4,'selected_epoch':best_epoch,'optimizer_steps':steps,
    'elapsed_seconds':time.monotonic()-started,'peak_cuda_bytes':torch.cuda.max_memory_allocated(),
    'validation':validation,'test':test,'deployment_approved':False,
    'limitations':['Synthetic template families; requires independent human conversation evaluation.',
        'This adapter does not answer financial questions; validated SQL tools compute numbers.',
        'No automatic deployment; live multi-turn comparison against Qwen planner still required.']}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
(OUT/'tutor-failures.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in failures))
(OUT/'adapter_config.json').write_text(json.dumps({'base_model':MODEL,'revision':REVISION,'max_tokens':max_length,'labels':labels,
    'trainable_names':sorted(trainable_names),'pooling':'masked_mean','segmentation':'pyvi'},ensure_ascii=False,indent=2))
print('FROZEN TEST',json.dumps(test),flush=True)
print('Tutor review queue:',len(failures),'cases; no automatic self-labeling.',flush=True)
print('SECONDS',round(report['elapsed_seconds'],2),'STEPS',steps,flush=True)
