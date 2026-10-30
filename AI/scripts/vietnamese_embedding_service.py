"""Loopback-only Vietnamese embedding worker. No remote model code or API calls."""
from http.server import BaseHTTPRequestHandler,HTTPServer
import json
import os
from pathlib import Path
import threading
import copy

ROOT=Path(__file__).resolve().parents[1]


def bucket(tokenizer,*texts,limit,pair=False):
    """Pad to a few fixed lengths: CPU kernels cache per input shape, and free-length
    batches made the worker grow by hundreds of MB per few dozen requests."""
    probe=tokenizer(*texts,truncation='only_second' if pair else True,max_length=limit)
    longest=max(len(ids) for ids in probe['input_ids'])
    size=next(b for b in (64,128,160,256,512) if b>=min(longest,limit))
    return tokenizer(*texts,truncation='only_second' if pair else True,max_length=size,padding='max_length',return_tensors='pt')


def main():
    os.environ['HF_HUB_OFFLINE']='1'
    # Bound oneDNN's per-shape primitive cache before torch loads.
    os.environ.setdefault('ONEDNN_PRIMITIVE_CACHE_CAPACITY','16')
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer,AutoModel
    from pyvi.ViTokenizer import tokenize
    torch.set_num_threads(3)
    folder=ROOT/'models/vietnamese-embedding'
    metadata=json.loads((folder/'source-manifest.json').read_text(encoding='utf-8'))
    tokenizer=AutoTokenizer.from_pretrained(folder,local_files_only=True,trust_remote_code=False)
    model=AutoModel.from_pretrained(folder,local_files_only=True,trust_remote_code=False).eval()
    limit=min(512,getattr(model.config,'max_position_embeddings',514)-2)
    adapter=ROOT/'training/conversation_v3/colab_artifacts/20261019/outputs'
    classifier=None;adapter_config=None
    # The conversation adapter is only used by the legacy v3 flow; on an 8 GB machine
    # skipping it leaves RAM for the local LLM (VI_UNDERSTANDING_ADAPTER=0).
    if (adapter/'adapter_config.json').exists() and os.getenv('VI_UNDERSTANDING_ADAPTER','1')!='0':
        from safetensors.torch import load_file
        adapter_config=json.loads((adapter/'adapter_config.json').read_text(encoding='utf-8'))
        if adapter_config['revision']!=metadata['revision']: raise ValueError('Understanding adapter base revision mismatch')
        # Share frozen layers; embedding inference must retain its original last four layers.
        adapted=copy.copy(model);adapted._modules=dict(model._modules)
        adapted.encoder=copy.copy(model.encoder);adapted.encoder._modules=dict(model.encoder._modules)
        adapted.encoder.layer=torch.nn.ModuleList(list(model.encoder.layer[:-4])+list(copy.deepcopy(model.encoder.layer[-4:])))
        class Understanding(torch.nn.Module):
            def __init__(self):
                super().__init__();self.encoder=adapted
                self.heads=torch.nn.ModuleDict({k:torch.nn.Linear(model.config.hidden_size,len(v)) for k,v in adapter_config['labels'].items()})
            def forward(self,inputs):
                hidden=self.encoder(**inputs).last_hidden_state;mask=inputs['attention_mask'].unsqueeze(-1)
                pooled=(hidden*mask).sum(1)/mask.sum(1).clamp(min=1)
                return {k:head(pooled) for k,head in self.heads.items()}
        classifier=Understanding().eval()
        state=load_file(str(adapter/'conversation_adapter.safetensors'))
        if set(state)!=set(adapter_config['trainable_names']): raise ValueError('Unexpected adapter weights')
        classifier.load_state_dict(state,strict=False)
        del state
    # Optional evidence reranker: shares the frozen lower layers, owns its trained
    # top layers + head. Loaded only with a matching manifest and weight hash.
    reranker=None;reranker_info=None
    rerank_dir=ROOT/'models/evidence_reranker_20261024'
    if (rerank_dir/'manifest.json').exists() and (rerank_dir/'trained_layers.pt').exists():
        import hashlib
        reranker_info=json.loads((rerank_dir/'manifest.json').read_text(encoding='utf-8'))
        weights=rerank_dir/'trained_layers.pt'
        if hashlib.sha256(weights.read_bytes()).hexdigest()!=reranker_info['weights_sha256']: raise ValueError('Reranker weight hash mismatch')
        if reranker_info['base_revision']!=metadata['revision']: raise ValueError('Reranker base revision mismatch')
        ranked=copy.copy(model);ranked._modules=dict(model._modules)
        ranked.encoder=copy.copy(model.encoder);ranked.encoder._modules=dict(model.encoder._modules)
        ranked.encoder.layer=torch.nn.ModuleList(list(model.encoder.layer[:-4])+list(copy.deepcopy(model.encoder.layer[-4:])))
        class Reranker(torch.nn.Module):
            def __init__(self):
                super().__init__();self.encoder=ranked;self.head=torch.nn.Linear(model.config.hidden_size,1)
            def forward(self,inputs):return self.head(self.encoder(**inputs).last_hidden_state[:,0]).squeeze(-1)
        reranker=Reranker().eval()
        state=torch.load(weights,map_location='cpu',weights_only=True)
        if any(not (k.startswith('head') or any(f'encoder.layer.{n}.' in k for n in range(8,12))) for k in state): raise ValueError('Unexpected reranker weights')
        missing=reranker.load_state_dict(state,strict=False)
        if any(k.startswith('head') or any(f'encoder.layer.{n}.' in k for n in range(8,12)) for k in missing.missing_keys): raise ValueError('Reranker weights incomplete')
        del state
    lock=threading.Lock()
    class Handler(BaseHTTPRequestHandler):
        def respond(self,status,payload):
            body=json.dumps(payload,ensure_ascii=False).encode()
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def do_GET(self):
            if self.path!='/health': return self.respond(404,{'error':'not found'})
            self.respond(200,{'ready':True,'model':metadata['model'],'revision':metadata['revision'],'max_tokens':limit,'device':'cpu','local_only':True,'understanding_adapter':classifier is not None,
                              'evidence_reranker':reranker_info['weights_sha256'][:16] if reranker is not None else None})
        def do_POST(self):
            if self.path not in ('/embed','/understand','/rerank'): return self.respond(404,{'error':'not found'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=256000: raise ValueError('Invalid request size')
                payload=json.loads(self.rfile.read(size))
                if self.path=='/rerank':
                    if reranker is None: return self.respond(503,{'error':'No evidence reranker installed'})
                    query=payload['query'];texts=payload['texts']
                    if not isinstance(query,str) or not 0<len(query)<=2000 or not isinstance(texts,list) or not 1<=len(texts)<=64 or any(not isinstance(t,str) or len(t)>4000 for t in texts):
                        raise ValueError('Invalid rerank request')
                    scores=[]
                    with lock,torch.inference_mode():
                        for i in range(0,len(texts),16):
                            batch=texts[i:i+16]
                            inputs=bucket(tokenizer,[tokenize(query)]*len(batch),[tokenize(t) for t in batch],limit=160,pair=True)
                            scores.extend(reranker(inputs).tolist())
                    return self.respond(200,{'scores':scores,'reranker':reranker_info['weights_sha256'][:16]})
                if self.path=='/understand':
                    if classifier is None: return self.respond(503,{'error':'No understanding adapter installed'})
                    question=payload['question'];memory=payload.get('memory',{});today=payload['today']
                    if not isinstance(question,str) or len(question)>4000 or not isinstance(memory,dict): raise ValueError('Invalid conversation')
                    text=('Câu hiện tại: '+question+'\nNgày hiện tại: '+today+'\nNgữ cảnh đã xác nhận: '+
                          json.dumps({k:v for k,v in memory.items() if k!='history'},ensure_ascii=False)+
                          '\nHội thoại gần nhất: '+json.dumps(memory.get('history',[])[-2:],ensure_ascii=False))
                    with lock,torch.inference_mode():
                        inputs=bucket(tokenizer,[tokenize(text)],limit=limit)
                        outputs=classifier(inputs);predictions={}
                        for key,logits in outputs.items():
                            probs=logits[0].softmax(-1);index=int(probs.argmax())
                            predictions[key]={'label':adapter_config['labels'][key][index],'confidence':round(float(probs[index]),5)}
                    return self.respond(200,{'predictions':predictions,'model':'PhoBERT conversation-v3','scope':'Experimental advisory; confidence not calibrated on real conversations'})
                values=payload['texts']
                if not isinstance(values,list) or not 1<=len(values)<=128 or any(not isinstance(x,str) or len(x)>16000 for x in values): raise ValueError('Invalid batch')
                vectors=[];truncated=[]
                with lock,torch.inference_mode():
                    for i in range(0,len(values),8):
                        sentences=[tokenize(v) for v in values[i:i+8]]
                        lengths=[len(tokenizer(s,add_special_tokens=True)['input_ids']) for s in sentences]
                        inputs=bucket(tokenizer,sentences,limit=limit)
                        hidden=model(**inputs).last_hidden_state;mask=inputs['attention_mask'].unsqueeze(-1)
                        embeddings=F.normalize((hidden*mask).sum(1)/mask.sum(1).clamp(min=1),p=2,dim=1)
                        vectors.extend(embeddings.tolist());truncated.extend(n>limit for n in lengths)
                self.respond(200,{'embeddings':vectors,'truncated':truncated,'model':metadata['model'],'revision':metadata['revision']})
            except (ValueError,KeyError,TypeError) as exc: self.respond(400,{'error':str(exc)})
        def log_message(self,fmt,*args): pass
    print(json.dumps({'ready':True,'model':metadata['model'],'max_tokens':limit,'port':8011}),flush=True)
    # One serving thread: torch/oneDNN keep per-thread buffers, and a new thread per
    # request leaked hundreds of MB per few dozen requests. Inference was already
    # serialised by the lock, so throughput is unchanged.
    # Loopback by default; the Docker image sets VI_EMBEDDING_HOST=0.0.0.0 on its private network.
    HTTPServer((os.getenv('VI_EMBEDDING_HOST','127.0.0.1'),8011),Handler).serve_forever()


if __name__=='__main__': main()
