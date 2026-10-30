"""Contrastive E5 retriever pilot with source-group separation and frozen test."""
import argparse
import json
import random
from collections import defaultdict
from pathlib import Path

def read(path):return [json.loads(x) for x in Path(path).read_text(encoding='utf-8').splitlines() if x.strip()]
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')

def main():
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel,AutoTokenizer
    from huggingface_hub import model_info
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',default='.')
    parser.add_argument('--epochs',type=int,default=3)
    args=parser.parse_args()
    root=Path(args.root)
    out=root/'outputs/retriever'
    out.mkdir(parents=True,exist_ok=True)
    torch.manual_seed(42)
    rng=random.Random(42)
    device='cuda' if torch.cuda.is_available() else 'cpu'
    if device!='cuda':raise RuntimeError('Select GPU runtime in Colab; this script will not silently train on CPU')
    model_id='intfloat/multilingual-e5-small'
    revision=model_info(model_id).sha
    tokenizer=AutoTokenizer.from_pretrained(model_id,revision=revision)
    model=AutoModel.from_pretrained(model_id,revision=revision).to(device)
    docs=read(root/'data/corpus.jsonl')
    qa=read(root/'data/qa.jsonl')
    # Only source-supported examples train retrieval. Missing-answer cases are checked separately.
    train=[r for r in qa if r['split']=='train' and r['answerability']=='supported']
    groups=defaultdict(list)
    for q in train:groups[q['positive_id']].append(q)
    documents={d['id']:d for d in docs}
    def encode(texts,grad=False):
        inputs=tokenizer(texts,padding=True,truncation=True,max_length=384,return_tensors='pt').to(device)
        with torch.set_grad_enabled(grad):
            hidden=model(**inputs).last_hidden_state
            mask=inputs['attention_mask'].unsqueeze(-1)
            return F.normalize((hidden*mask).sum(1)/mask.sum(1).clamp(min=1),p=2,dim=1)
    @torch.no_grad()
    def evaluate(split,name):
        model.eval()
        vectors=torch.cat([encode(['passage: '+d['text'] for d in docs[i:i+8]]) for i in range(0,len(docs),8)])
        questions=[q for q in qa if q['split']==split and q['answerability']=='supported']
        results=[]
        for start in range(0,len(questions),8):
            batch=questions[start:start+8]
            scores=encode(['query: '+q['question'] for q in batch])@vectors.T
            top=scores.topk(min(3,len(docs)),dim=1).indices.tolist()
            for q,indices in zip(batch,top):
                found=[docs[i]['id'] for i in indices]
                results.append({'id':q['id'],'question':q['question'],'positive_id':q['positive_id'],'retrieved_ids':found,'recall_at_1':found[0]==q['positive_id'],'recall_at_3':q['positive_id'] in found})
        report={'split':split,'samples':len(results),'recall_at_1':sum(r['recall_at_1'] for r in results)/max(1,len(results)),
                'recall_at_3':sum(r['recall_at_3'] for r in results)/max(1,len(results)),
                'metric_scope':'Retrieval only; not generative answer quality, policy safety or production accuracy','results':results}
        write(out/(name+'.json'),report)
        print(name,{k:v for k,v in report.items() if k!='results'},flush=True)
        return report
    baseline=evaluate('validation','baseline-validation')
    best=baseline['recall_at_1']
    best_epoch=0
    candidate=out/'candidate'
    model.save_pretrained(candidate)
    tokenizer.save_pretrained(candidate)
    optimizer=torch.optim.AdamW(model.parameters(),lr=1e-5)
    ids=list(groups)
    history=[]
    for epoch in range(args.epochs):
        rng.shuffle(ids)
        model.train()
        losses=[]
        for start in range(0,len(ids),8):
            batch_ids=ids[start:start+8]
            if len(batch_ids)<2:continue
            batch=[rng.choice(groups[i]) for i in batch_ids]
            optimizer.zero_grad()
            queries=encode(['query: '+q['question'] for q in batch],True)
            passages=encode(['passage: '+documents[i]['text'] for i in batch_ids],True)
            loss=F.cross_entropy((queries@passages.T)/0.05,torch.arange(len(batch),device=device))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0)
            optimizer.step()
            losses.append(loss.item())
        report=evaluate('validation',f'epoch-{epoch+1}-validation')
        history.append({'epoch':epoch+1,'loss':sum(losses)/max(1,len(losses)),'recall_at_1':report['recall_at_1']})
        # Strict improvement required. Ties preserve the baseline.
        if report['recall_at_1']>best:
            best=report['recall_at_1'];best_epoch=epoch+1
            model.save_pretrained(candidate)
            tokenizer.save_pretrained(candidate)
    model.save_pretrained(out/'last-trained')
    tokenizer.save_pretrained(out/'last-trained')
    del model
    torch.cuda.empty_cache()
    model=AutoModel.from_pretrained(candidate).to(device)
    test=evaluate('test','frozen-candidate-test')
    failures=[{'question':r['question'],'failure':'positive_source_not_top1','source_id':r['positive_id'],
               'evidence':documents[r['positive_id']]['text'],'action':'Review query wording, chunking or hard negatives. Do not invent a new fact.',
               'status':'needs_teacher_review','split':'validation'}
              for r in baseline['results'] if not r['recall_at_1']]
    write(out/'tutor-review-queue.json',failures)
    write(out/'training-summary.json',{'encoder':model_id,'revision':revision,'device':device,'epochs':history,
         'selected_epoch':best_epoch,'validation_improved':best_epoch>0,'trained_weights_selected':best_epoch>0,
         'deployment_approved':False,'test_recall_at_1':test['recall_at_1'],'training_examples':len(train),
         'training_source_groups':len(groups),'weights_training_performed':True,
         'limitation':'Small templated pilot. Failure queue is proposals, not automatic knowledge approval.'})
    print('Saved candidate, frozen test results, and tutor review queue to',out,flush=True)

if __name__=='__main__':main()
