"""Write training/qwen_sft_kaggle_20261029_v5.ipynb (v1 notebook: lr 1e-4, catalog-heavy data; v2: doc/admin balanced; v3: two-month reports; v4: three-month returns routes; v5: router families two-metric, no-diacritic, clarify, deferred, private) (QLoRA on Kaggle T4, export GGUF).

The prompt text is assembled by hand in exactly the form Ollama renders for
qwen3:4b-instruct-2507 at inference (system, user, then "<|im_start|>assistant\\n"
with no think block), so the fine-tune sees the same tokens the shop server sends.
"""
import json
from pathlib import Path

CELLS=[
('markdown','''# ShopBot — QLoRA Qwen3-4B-Instruct-2507 (router + chọn bằng chứng)

1. **Settings → Accelerator: GPU T4 x2** (dùng 1 GPU), **Internet: On**.
2. **Add Input** → dataset `shopbot-qwen-sft-v5` (thư mục `data/finetune_qwen_20261029_v5`: `train.jsonl`, `dev.jsonl`, `DATA_CARD.json`).
3. **Run All** (hoặc Save Version → Save & Run All để chạy khi tắt trình duyệt).

Kết quả trong `/kaggle/working`: `metrics.json`, `lora_adapter/`, `gguf/*.gguf` (q4_k_m). Tải file `.gguf` về máy rồi chạy `scripts/import_qwen_sft_ollama.ps1`.

Nhãn được dựng từ database/tài liệu shop, không lấy câu trả lời của bot; dev tách theo sản phẩm/tài liệu. Điểm ở đây chỉ là khớp JSON trên dev; đánh giá thật là bộ 479/121, held-out 300 và expansion chạy lại trên máy; v5 dùng làm OLLAMA_MODEL, giữ selector v1.'''),
('code','''%%capture
!pip install -q unsloth'''),
('code','''import glob, json, os, random, time, torch
SEED=20261026; random.seed(SEED)
MAX_LEN=4096
# If older datasets are still attached, take the v5 copy.
paths=sorted(glob.glob('/kaggle/input/**/train.jsonl',recursive=True),key=lambda p:'v5' not in p)
root=os.path.dirname(paths[0])
train=[json.loads(l) for l in open(f'{root}/train.jsonl',encoding='utf-8')]
dev=[json.loads(l) for l in open(f'{root}/dev.jsonl',encoding='utf-8')]
card=json.load(open(f'{root}/DATA_CARD.json',encoding='utf-8'))
# v5 router families are ~13% of the rows: show them twice so they are not drowned out.
train+=[e for e in train if e['origin'].startswith('v5_')]
print(root, len(train), len(dev), card['sha256'])
print(torch.cuda.get_device_name(0), round(torch.cuda.get_device_properties(0).total_memory/2**30,1),'GB')'''),
('code','''from unsloth import FastLanguageModel
model,tokenizer=FastLanguageModel.from_pretrained('unsloth/Qwen3-4B-Instruct-2507',max_seq_length=MAX_LEN,load_in_4bit=True,dtype=None)
# LoRA B starts at zero, so the 'base' evaluation below is the untouched model.
model=FastLanguageModel.get_peft_model(model,r=16,lora_alpha=32,lora_dropout=0,bias='none',
    target_modules=['q_proj','k_proj','v_proj','o_proj','gate_proj','up_proj','down_proj'],
    use_gradient_checkpointing='unsloth',random_state=SEED)

def prompt(messages):
    # Same text Ollama renders for qwen3:4b-instruct-2507 (no <think> block).
    system,user=messages[0]['content'],messages[1]['content']
    return f'<|im_start|>system\\n{system}<|im_end|>\\n<|im_start|>user\\n{user}<|im_end|>\\n<|im_start|>assistant\\n'

def encode(example):
    head=tokenizer(prompt(example['messages']),add_special_tokens=False)['input_ids']
    tail=tokenizer(example['messages'][2]['content']+'<|im_end|>\\n',add_special_tokens=False)['input_ids']
    ids=head+tail
    # Loss on the assistant JSON only.
    return dict(input_ids=ids,attention_mask=[1]*len(ids),labels=[-100]*len(head)+tail)

enc_train=[encode(e) for e in train]; enc_dev=[encode(e) for e in dev]
too_long=sum(len(e['input_ids'])>MAX_LEN for e in enc_train)
enc_train=[e for e in enc_train if len(e['input_ids'])<=MAX_LEN]
print('train',len(enc_train),'dropped >MAX_LEN',too_long,'max tokens',max(len(e['input_ids']) for e in enc_train))'''),
('code','''def decision(d):
    # Unconstrained generation (no Ollama schema here) can return any JSON
    # shape; anything not matching the schema simply counts as wrong.
    if not isinstance(d,dict) or not isinstance(d.get('answers'),dict) or not isinstance(d.get('missing'),list):return None
    if not all(isinstance(v,list) for v in d['answers'].values()):return None
    try:return ({str(k):sorted(map(str,v)) for k,v in d['answers'].items()},sorted(map(str,d['missing'])))
    except TypeError:return None

def evaluate(rows,limit=None,tag=''):
    """Greedy JSON generation; exact match of the decision fields."""
    FastLanguageModel.for_inference(model)
    rows=rows[:limit] if limit else rows
    stats=dict(n=0,parsed=0,router_action=0,router_n=0,selector_exact=0,selector_missing=0,selector_n=0)
    start=time.time()
    for e in rows:
        ids=tokenizer(prompt(e['messages']),return_tensors='pt',add_special_tokens=False).to('cuda')
        with torch.no_grad():
            out=model.generate(**ids,max_new_tokens=220,do_sample=False,pad_token_id=tokenizer.eos_token_id)
        text=tokenizer.decode(out[0][ids['input_ids'].shape[1]:],skip_special_tokens=True).strip()
        gold=json.loads(e['messages'][2]['content']); stats['n']+=1
        try:pred=json.loads(text); stats['parsed']+=1
        except Exception:pred={}
        if not isinstance(pred,dict):pred={}
        # Per-group gate: catalog lookups must not hide a drop on documents/admin.
        group=f"{e['task']}/{'route' if e['origin']=='route_spec' else 'v5' if e['origin'].startswith('v5_') else 'multi_period' if e['origin']=='multi_period' else 'document' if e['origin'] in ('doc_question','section_heading','generated_from_fragment') else 'catalog'}/{e['role']}"
        g=stats.setdefault('groups',{}).setdefault(group,[0,0]); g[1]+=1
        if e['task']=='router':
            stats['router_n']+=1
            ok=pred.get('action')==gold['action'] and bool(pred.get('private_request'))==gold['private_request']
            stats['router_action']+=ok
        else:
            stats['selector_n']+=1
            got=decision(pred)
            ok=got==decision(gold)
            stats['selector_exact']+=ok
            stats['selector_missing']+=got is not None and got[1]==sorted(gold['missing'])
        g[0]+=ok
    stats['seconds']=round(time.time()-start)
    print(tag,stats); return stats

random.Random(SEED).shuffle(dev)
EVAL_N=160
metrics=dict(data=card['sha256'],base=evaluate(dev,EVAL_N,'base'))'''),
('code','''FastLanguageModel.for_training(model)
from datasets import Dataset
from transformers import Trainer,TrainingArguments,DataCollatorForSeq2Seq
args=TrainingArguments(output_dir='/kaggle/working/run',per_device_train_batch_size=1,gradient_accumulation_steps=8,
    num_train_epochs=2,learning_rate=5e-5,lr_scheduler_type='cosine',warmup_steps=20,weight_decay=0.0,
    fp16=not torch.cuda.is_bf16_supported(),bf16=torch.cuda.is_bf16_supported(),logging_steps=10,
    eval_strategy='steps',eval_steps=100,per_device_eval_batch_size=1,save_strategy='no',report_to='none',seed=SEED,optim='adamw_8bit')
trainer=Trainer(model=model,args=args,train_dataset=Dataset.from_list(enc_train),eval_dataset=Dataset.from_list(enc_dev[:80]),
    data_collator=DataCollatorForSeq2Seq(tokenizer,padding=True,label_pad_token_id=-100))
result=trainer.train(); print(result)
metrics['train']=dict(loss=result.training_loss,seconds=round(result.metrics['train_runtime']),log=trainer.state.log_history)'''),
('code','''metrics['tuned']=evaluate(dev,EVAL_N,'tuned')
metrics['tuned_full_dev']=evaluate(dev,None,'tuned full dev')
json.dump(metrics,open('/kaggle/working/metrics.json','w'),indent=1)
model.save_pretrained('/kaggle/working/lora_adapter'); tokenizer.save_pretrained('/kaggle/working/lora_adapter')'''),
('code','''# GGUF q4_k_m for Ollama (same quantization as the current local model).
model.save_pretrained_gguf('/kaggle/working/gguf',tokenizer,quantization_method='q4_k_m')
for path in glob.glob('/kaggle/working/gguf*/**/*.gguf',recursive=True)+glob.glob('/kaggle/working/*.gguf'):
    print(path, round(os.path.getsize(path)/2**30,2),'GB')'''),
]


def main():
    nb=dict(nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(name='python3',display_name='Python 3',language='python'),
            language_info=dict(name='python')),cells=[])
    for kind,source in CELLS:
        cell=dict(cell_type=kind,metadata={},source=source.splitlines(keepends=True))
        if kind=='code':cell.update(outputs=[],execution_count=None)
        nb['cells'].append(cell)
    out=Path(__file__).with_name('qwen_sft_kaggle_20261029_v5.ipynb')
    out.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf8');print(out)


if __name__=='__main__':main()
