"""Train a Vietnamese cross-encoder that ranks evidence fragments for a question (CPU).

Base: the local dangvantuan/vietnamese-embedding (PhoBERT) at the pinned revision; the lower
8 layers are frozen, the top 4 layers + a scalar head are trained with a listwise loss over
(positive + hard negatives). Dev accuracy/MRR is compared with the current bi-encoder cosine
and BM25 on the same candidates; the model is only saved as a candidate, never auto-enabled.
Run with .venv-kev (torch, transformers, pyvi).
"""
import argparse
import hashlib
import json
import math
import random
import sys
import time
from pathlib import Path

import torch
import torch.nn.functional as F
from pyvi.ViTokenizer import tokenize
from transformers import AutoModel,AutoTokenizer

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'models/vietnamese-embedding'
DATA=ROOT/'data/finetune_20261024'
OUT=ROOT/'models/evidence_reranker_20261024'


def load(split):
    rows=[]
    for name in ('train.jsonl' if split=='train' else 'dev.jsonl','generated.jsonl'):
        path=DATA/name
        if not path.exists():continue
        for line in path.read_text(encoding='utf8').splitlines():
            r=json.loads(line)
            if r['split']==split and r['negatives']:rows.append(r)
    return rows


class CrossEncoder(torch.nn.Module):
    def __init__(self,base):
        super().__init__();self.encoder=AutoModel.from_pretrained(base,local_files_only=True)
        self.head=torch.nn.Linear(self.encoder.config.hidden_size,1)
        for p in self.encoder.parameters():p.requires_grad=False
        for layer in self.encoder.encoder.layer[-4:]:
            for p in layer.parameters():p.requires_grad=True

    def forward(self,inputs):
        return self.head(self.encoder(**inputs).last_hidden_state[:,0]).squeeze(-1)


def encode(tok,query,texts,limit):
    q=tokenize(query)
    return tok([q]*len(texts),[tokenize(t) for t in texts],truncation='only_second',max_length=limit,padding=True,return_tensors='pt')


def baselines(rows):
    """Bi-encoder cosine and BM25 on the same candidate lists (no training)."""
    tok=AutoTokenizer.from_pretrained(BASE,local_files_only=True);enc=AutoModel.from_pretrained(BASE,local_files_only=True).eval()
    def bm25(query,docs,k1=1.5,b=0.75):
        terms=[d for d in docs];avg=sum(map(len,terms))/len(terms);n=len(terms)
        df={w:sum(w in d for d in terms) for w in set(query)}
        return [sum(math.log(1+(n-df[w]+.5)/(df[w]+.5))*d.count(w)*(k1+1)/(d.count(w)+k1*(1-b+b*len(d)/avg)) for w in query) for d in terms]
    def embed(texts):
        x=tok([tokenize(t) for t in texts],truncation=True,max_length=256,padding=True,return_tensors='pt')
        with torch.inference_mode():h=enc(**x).last_hidden_state
        m=x['attention_mask'].unsqueeze(-1);return F.normalize((h*m).sum(1)/m.sum(1),dim=-1)
    acc={'cosine':0,'bm25':0}
    for r in rows:
        cands=[r['positive']]+r['negatives'];v=embed([r['query']]+cands)
        acc['cosine']+=int((v[1:]@v[0]).argmax().item()==0)
        bm=bm25(tokenize(r['query']).lower().split(),[tokenize(c).lower().split() for c in cands])
        acc['bm25']+=int(max(range(len(cands)),key=lambda i:bm[i])==0)
    return {k:round(v/len(rows),4) for k,v in acc.items()}


def evaluate(model,tok,rows,limit):
    model.eval();top1=0;mrr=0.
    with torch.inference_mode():
        for r in rows:
            scores=model(encode(tok,r['query'],[r['positive']]+r['negatives'],limit))
            rank=int((scores>scores[0]).sum().item())+1;top1+=rank==1;mrr+=1/rank
    model.train();return dict(top1=round(top1/len(rows),4),mrr=round(mrr/len(rows),4))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--epochs',type=int,default=2);parser.add_argument('--limit',type=int,default=160)
    parser.add_argument('--lr',type=float,default=3e-5);parser.add_argument('--seed',type=int,default=20261024)
    args=parser.parse_args();torch.manual_seed(args.seed);random.seed(args.seed);torch.set_num_threads(4)
    train,dev=load('train'),load('dev')
    print('train',len(train),'dev',len(dev),flush=True)
    base_scores=baselines(dev);print('baselines on dev',base_scores,flush=True)
    tok=AutoTokenizer.from_pretrained(BASE,local_files_only=True);model=CrossEncoder(BASE)
    params=[p for p in model.parameters() if p.requires_grad]
    opt=torch.optim.AdamW(params,lr=args.lr,weight_decay=0.01)
    steps=args.epochs*len(train);sched=torch.optim.lr_scheduler.LambdaLR(opt,lambda s:min(1,(s+1)/50)*max(0.,1-s/steps))
    history=[dict(epoch=0,**evaluate(model,tok,dev,args.limit))];print(history[-1],flush=True)
    start=time.time()
    for epoch in range(1,args.epochs+1):
        random.shuffle(train);total=0.
        for i,r in enumerate(train):
            scores=model(encode(tok,r['query'],[r['positive']]+r['negatives'][:8],args.limit))
            loss=F.cross_entropy(scores.unsqueeze(0),torch.zeros(1,dtype=torch.long))
            loss.backward();torch.nn.utils.clip_grad_norm_(params,1.0);opt.step();sched.step();opt.zero_grad();total+=loss.item()
            if (i+1)%100==0:print(f'epoch {epoch} step {i+1}/{len(train)} loss {total/(i+1):.4f} {time.time()-start:.0f}s',flush=True)
        history.append(dict(epoch=epoch,loss=round(total/len(train),4),**evaluate(model,tok,dev,args.limit)));print(history[-1],flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    state={k:v for k,v in model.state_dict().items() if k.startswith('head') or any(f'encoder.layer.{n}.' in k for n in range(8,12))}
    torch.save(state,OUT/'trained_layers.pt')
    manifest=dict(base=str(BASE.relative_to(ROOT)),base_revision=json.loads((BASE/'source-manifest.json').read_text(encoding='utf8'))['revision'],
                  trained='encoder layers 8-11 + linear head on [CLS]; layers 0-7 frozen and shared with base',
                  data_card=json.loads((DATA/'DATA_CARD.json').read_text(encoding='utf8')),train=len(train),dev=len(dev),
                  args=vars(args),history=history,dev_baselines=base_scores,
                  weights_sha256=hashlib.sha256((OUT/'trained_layers.pt').read_bytes()).hexdigest(),
                  status='candidate; not enabled in the chatbot until end-to-end banks pass')
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(history=history,baselines=base_scores),ensure_ascii=False))


if __name__=='__main__':main()
