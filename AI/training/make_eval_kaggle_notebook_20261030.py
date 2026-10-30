"""Write training/eval_kaggle_20261030.ipynb: the frozen quality runner on Kaggle T4 x2.

GPU 0 runs the current production setup (base qwen3 + v1 selector), GPU 1 runs v5 + v1 selector.
Each T4 holds both of its models at once, so there is no model swapping (the 6 GB local GPU
swapped on every product question). Both runs share one CPU embedding worker, the same code,
data and Ollama build, so base vs v5 is a like-for-like comparison. Bank files, gold and code
are unchanged; only absolute Windows paths in the bank metadata are rewritten.
"""
import json
from pathlib import Path

CELLS=[
('markdown','''# ShopBot — đánh giá mốc vs v5 trên Kaggle (T4 x2)

1. **Settings → Accelerator: GPU T4 x2**, **Internet: On**.
2. **Add Input**:
   - dataset `shopbot-eval-bundle` (private; file `shopbot-eval-bundle.zip` từ `AI/training/kaggle_upload`),
   - dataset `shopbot-qwen-v1-gguf` (thư mục `model_v1`, file GGUF v1),
   - output của notebook `notebook2599ec05b1` (GGUF v5, phiên bản 7).
3. **Save Version → Save & Run All**.

GPU 0: mốc (qwen3 gốc + selector v1). GPU 1: v5 + selector v1. Kết quả: `/kaggle/working/results/*.zip` và `summary.json`.
Bộ held-out 300 và phần validation của bộ 539 bị khoá: chỉ dùng để quyết định promote, không đọc từng câu để sửa code.'''),
('code','''%%capture
!pip install -q python-dotenv pyvi langgraph==1.2.15 langchain-core==1.6.11'''),
('code','''import glob, hashlib, json, os, shutil, subprocess, time
from pathlib import Path
START=time.time()
# The bundle may arrive extracted or as the zip itself.
apps=glob.glob('/kaggle/input/**/AI/app.py',recursive=True)
if not apps:
    z=glob.glob('/kaggle/input/**/shopbot-eval-bundle.zip',recursive=True)[0]
    shutil.unpack_archive(z,'/tmp/bundle'); apps=glob.glob('/tmp/bundle/**/AI/app.py',recursive=True)
SRC=Path(apps[0]).parent
manifest=json.loads((SRC/'BUNDLE_MANIFEST.json').read_text(encoding='utf8'))['files']
bad=[f for f,h in manifest.items() if hashlib.sha256((SRC/f).read_bytes()).hexdigest()!=h]
assert not bad, bad[:5]
print(SRC, len(manifest), 'files verified')

RUNS={'base':dict(gpu='0',port=11434,model='qwen3:4b-instruct-2507-q4_K_M'),
      'v5':dict(gpu='1',port=11435,model='shopbot-qwen-sft-20261029-v5')}
SELECTOR='shopbot-qwen-sft-20261026'
for name,run in RUNS.items():
    ai=Path(f'/kaggle/working/{name}/AI'); run['ai']=ai
    if ai.exists(): shutil.rmtree(ai)
    # Large read-only folders are linked, everything the runner writes is a private copy.
    shutil.copytree(SRC,ai,ignore=shutil.ignore_patterns('models','training'))
    os.symlink(SRC/'models',ai/'models'); os.symlink(SRC/'training',ai/'training')
    env=(ai/'.env').read_text(encoding='utf8').replace('http://127.0.0.1:11434',f'http://127.0.0.1:{run["port"]}')
    (ai/'.env').write_text(env,encoding='utf8')
    # The managed knowledge folder is named after a hash of the database path (shopbot.knowledge.namespace),
    # so it has to follow the database to its new path or the bot silently loses those documents.
    db=(ai/'data/business_sql/scenario_v1/shop.sqlite').resolve()
    ns=hashlib.sha256(str(db).encode()).hexdigest()[:16]
    os.rename(ai/'data/unstructured/managed/ecdd21ab64861674',ai/'data/unstructured/managed'/ns)
    docs=json.loads((ai/'data/unstructured/managed'/ns/'manifest.json').read_text(encoding='utf8'))
    assert len(docs)==254, len(docs)
    for meta in ai.glob('evaluation/*/metadata.json'):
        m=json.loads(meta.read_text(encoding='utf8'))
        m['database']=str(db)
        m['knowledge_manifest']=str(ai/'data/unstructured/managed'/ns/'manifest.json')
        meta.write_text(json.dumps(m,ensure_ascii=False,indent=1),encoding='utf8')
print({k:str(v['ai']) for k,v in RUNS.items()})'''),
('code','''# Same Ollama build as the shop machine (0.40.5); CUDA here instead of Vulkan, for both runs alike.
!apt-get -qq update > /dev/null && apt-get -qq install -y zstd > /dev/null; curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.40.5 sh > /kaggle/working/ollama_install.log 2>&1; ollama --version
os.makedirs('/tmp/ollama',exist_ok=True)
for name,run in RUNS.items():
    env=dict(os.environ,CUDA_VISIBLE_DEVICES=run['gpu'],OLLAMA_HOST=f'127.0.0.1:{run["port"]}',OLLAMA_MODELS='/tmp/ollama',
             OLLAMA_MAX_LOADED_MODELS='2',OLLAMA_KEEP_ALIVE='-1',OLLAMA_NUM_PARALLEL='1')
    run['serve']=subprocess.Popen(['ollama','serve'],env=env,stdout=open(f'/kaggle/working/ollama_{name}.log','w'),stderr=subprocess.STDOUT)
time.sleep(8)
ol=lambda *a:subprocess.run(['ollama',*a],env=dict(os.environ,OLLAMA_HOST='127.0.0.1:11434',OLLAMA_MODELS='/tmp/ollama'),capture_output=True,text=True)
print(ol('pull','qwen3:4b-instruct-2507-q4_K_M').returncode)
# GGUFs are told apart by hash, not by file name (both are Qwen3-4B-Instruct-2507.Q4_K_M.gguf).
WANT={'a9309a4775b0060e81d5796dd6ab32db03c7509107f67c4d105ccdd700d50d6d':SELECTOR,
      '0dcc6414012d2240c8709952385a49136cd17e14780bd2cd99fe57d444bfe6f5':'shopbot-qwen-sft-20261029-v5'}
# A notebook tagged as a utility script is mounted under /kaggle/usr rather than /kaggle/input.
ggufs=glob.glob('/kaggle/input/**/*.gguf',recursive=True)+glob.glob('/kaggle/usr/**/*.gguf',recursive=True)
found={}
for g in ggufs:
    h=hashlib.sha256(open(g,'rb').read()).hexdigest()
    if h in WANT: found[WANT[h]]=g
assert len(found)==2, (found, ggufs)
# Reuse the base model's template and stop tokens, as scripts/import_qwen_sft_ollama.ps1 does.
template=[l for l in ol('show','--modelfile','qwen3:4b-instruct-2507-q4_K_M').stdout.splitlines() if not l.startswith(('FROM ','#'))]
for name,gguf in found.items():
    Path(f'/tmp/{name}.Modelfile').write_text('\\n'.join([f'FROM {gguf}',*template]),encoding='utf8')
    print(name, ol('create',name,'-f',f'/tmp/{name}.Modelfile').returncode)
print(ol('list').stdout)'''),
('code','''# One CPU embedding worker shared by both runs (as on the shop machine).
emb=subprocess.Popen(['python','scripts/vietnamese_embedding_service.py'],cwd=RUNS['base']['ai'],
    env=dict(os.environ,HF_HUB_DISABLE_TELEMETRY='1',TOKENIZERS_PARALLELISM='false',CUDA_VISIBLE_DEVICES=''),
    stdout=open('/kaggle/working/embedding.log','w'),stderr=subprocess.STDOUT)
import requests
for _ in range(120):
    try: print(requests.get('http://127.0.0.1:8011/health',timeout=3).json()); break
    except Exception: time.sleep(5)
# Load each run's two models once; they stay resident (OLLAMA_KEEP_ALIVE=-1).
for name,run in RUNS.items():
    for m in (run['model'],SELECTOR):
        r=requests.post(f'http://127.0.0.1:{run["port"]}/api/generate',json=dict(model=m,prompt='Chào',stream=False,
            options=dict(num_predict=3,num_ctx=6144,num_gpu=99)),timeout=900).json()
        print(name,m,round(r.get('load_duration',0)/1e9,1),'s load')'''),
('code','''WORKER=r\'\'\'
import json,os,subprocess,sys,time
from pathlib import Path
ai=Path(sys.argv[1]);tag=sys.argv[2];deadline=float(sys.argv[3])
ROUNDS=[('run_quality_loop_kb3_20261024.py','quality_loop_20261024_kb3','validation'),
        ('run_heldout_20261028.py','heldout_20261028','all'),
        ('run_quality_loop_kb3_20261024.py','quality_loop_20261024_kb3','development'),
        ('run_expansion_20261029.py','expansion_20261029','all')]
def drop_infra(path):
    # Rows that failed only because a service was down are asked again on the next try.
    p=path/'results.json'
    if p.exists():
        r=json.loads(p.read_text(encoding='utf8'))
        bad=[i for i,x in enumerate(r) if any(c['cause']=='INFRASTRUCTURE' for c in x['checks']['issues'])]
        if bad:p.write_text(json.dumps(r[:bad[0]],ensure_ascii=False,indent=1),encoding='utf8')
for script,bank,split in ROUNDS:
    name=f'kaggle_{tag}_{split}' if bank!='expansion_20261029' else f'kaggle_{tag}_all'
    if bank=='heldout_20261028':name=f'kaggle_{tag}_heldout'
    for attempt in range(6):
        if time.time()>deadline:print('deadline, skip',name,flush=True);break
        drop_infra(ai/'evaluation'/bank/name)
        print('==',name,'try',attempt,time.strftime('%H:%M:%S'),flush=True)
        if subprocess.run([sys.executable,'scripts/'+script,'--round',name,'--split',split],cwd=ai).returncode==0:break
        time.sleep(20)
print('== worker done',flush=True)
\'\'\'
Path('/kaggle/working/worker.py').write_text(WORKER,encoding='utf8')
# Stop starting new attempts after ~11 h so the notebook can still save its outputs.
deadline=START+11*3600
for name,run in RUNS.items():
    env=dict(os.environ,PYTHONIOENCODING='utf8',OLLAMA_BASE_URL=f'http://127.0.0.1:{run["port"]}',
             OLLAMA_MODEL=run['model'],OLLAMA_SELECTOR_MODEL=SELECTOR)
    run['worker']=subprocess.Popen(['python','/kaggle/working/worker.py',str(run['ai']),name,str(deadline)],cwd=run['ai'],env=env,
        stdout=open(f'/kaggle/working/worker_{name}.log','w'),stderr=subprocess.STDOUT)
def done(ai,bank,name):
    p=ai/'evaluation'/bank/name/'results.json'
    return len(json.loads(p.read_text(encoding='utf8'))) if p.exists() else 0
while any(r['worker'].poll() is None for r in RUNS.values()):
    time.sleep(600)
    print(time.strftime('%H:%M'),{n:{p.parent.name:done(r['ai'],p.parent.parent.name,p.parent.name) for p in r['ai'].glob('evaluation/*/kaggle_*/results.json')} for n,r in RUNS.items()},flush=True)
print({n:r['worker'].returncode for n,r in RUNS.items()})'''),
('code','''# Totals per round and PASS -> not PASS from base to v5. Locked rounds (held-out, expansion validation) show counts only.
from collections import Counter
out=Path('/kaggle/working/results'); out.mkdir(exist_ok=True)
summary={}
banks={'quality_loop_20261024_kb3':['validation','development'],'heldout_20261028':['heldout'],'expansion_20261029':['all']}
for bank,splits in banks.items():
    for split in splits:
        rows={}
        for name,run in RUNS.items():
            p=run['ai']/'evaluation'/bank/f'kaggle_{name}_{split}'/'results.json'
            rows[name]={r['id']:r for r in json.loads(p.read_text(encoding='utf8'))} if p.exists() else {}
        both=sorted(set(rows['base'])&set(rows['v5']))
        ok=lambda n,i:rows[n][i]['checks']['status']=='PASS_CHECKS'
        lost=[i for i in both if ok('base',i) and not ok('v5',i)]; won=[i for i in both if ok('v5',i) and not ok('base',i)]
        locked=bank=='heldout_20261028' or bank=='expansion_20261029'
        if bank=='expansion_20261029':
            lost_dev=[i for i in lost if rows['v5'][i]['split']=='development']
            entry_ids=dict(pass_to_fail_development=lost_dev,pass_to_fail_validation=len(lost)-len(lost_dev))
        else:entry_ids=dict(pass_to_fail=len(lost) if locked else lost)
        summary[f'{bank}/{split}']=dict(cases=len(both),
            base=dict(Counter(rows['base'][i]['checks']['status'] for i in both)),v5=dict(Counter(rows['v5'][i]['checks']['status'] for i in both)),
            fail_to_pass=len(won),pass_to_fail_count=len(lost),**entry_ids)
print(json.dumps(summary,ensure_ascii=False,indent=1))
(Path('/kaggle/working')/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding='utf8')
# Full rounds go back to the shop machine for the existing scorers (score_heldout / score_expansion).
for name,run in RUNS.items():
    for d in run['ai'].glob('evaluation/*/kaggle_*'):
        shutil.make_archive(str(out/f'{d.parent.name}__{d.name}'),'zip',d)
print(sorted(p.name for p in out.iterdir()), round((time.time()-START)/3600,2),'h')'''),
]

def main():
    nb=dict(nbformat=4,nbformat_minor=4,metadata=dict(kernelspec=dict(name='python3',display_name='Python 3',language='python'),
        language_info=dict(name='python')),cells=[])
    for kind,src in CELLS:
        cell=dict(cell_type=kind,metadata={},source=src)
        if kind=='code':cell.update(outputs=[],execution_count=None)
        nb['cells'].append(cell)
    out=Path(__file__).resolve().parent/'eval_kaggle_20261030.ipynb'
    out.write_text(json.dumps(nb,ensure_ascii=False,indent=1),encoding='utf8')
    print(out)
    # Same cells as one plain script, for pasting into a single Kaggle cell (the browser pane cannot upload files).
    parts=['import subprocess']
    for kind,src in CELLS:
        if kind=='markdown':parts.append('\n'.join('# '+l for l in src.splitlines()));continue
        lines=[]
        for l in src.splitlines():
            if l.startswith('%%'):continue
            lines.append(f'subprocess.run(r"""{l[1:]}""",shell=True,check=True)' if l.startswith('!') else l)
        parts.append('\n'.join(lines))
    script=out.with_suffix('.py')
    script.write_text('\n\n'.join(parts)+'\n',encoding='utf8')
    print(script)

if __name__=='__main__':main()
