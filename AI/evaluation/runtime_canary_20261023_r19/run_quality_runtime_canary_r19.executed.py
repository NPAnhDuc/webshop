"""Three fresh-runner runtime canaries; never shop QA or training."""
import argparse,copy,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from shopbot.monthly import exclusive,atomic_json
spec=importlib.util.spec_from_file_location('protocol_r17',ROOT/'scripts/run_quality_field_intent_probe_r17.py');protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
BASE=ROOT/'evaluation/quality_loop_20261021'
SOURCE=ROOT/'evaluation/field_intent_20261023_r17_qwen35'
OUT=ROOT/'evaluation/runtime_canary_20261023_r19'
SERVER_LOG=ROOT/'runtime/ollama.err.log'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def code():
    return {str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'app.py',*sorted((ROOT/'shopbot').glob('*.py')),ROOT/'scripts/run_quality_field_intent_probe_r17.py',Path(__file__).resolve()]}

def prepare():
    if OUT.exists():raise SystemExit('Preserve revision')
    identity=read(SOURCE/'model_identity.json')
    assert protocol.blob_stat(identity['blob_path'])==identity['blob_stat'] and protocol.digest(protocol.model_identity(protocol.EVAL_MODEL))==protocol.digest(identity['evaluation'])
    body=dict(model=protocol.EVAL_MODEL,stream=False,think=False,keep_alive='5m',messages=[dict(role='system',content='Follow the user instruction exactly.'),dict(role='user',content='Chỉ trả lời đúng hai ký tự: OK')],options=dict(temperature=0,num_ctx=1024,num_predict=32,num_gpu=99,num_thread=3,top_k=20,top_p=0.8,min_p=0,presence_penalty=0,repeat_penalty=1,seed=42))
    plans=[]
    for id in ['gpu_greedy','gpu_vendor_sampling','cpu_greedy']:
        req=copy.deepcopy(body)
        if id=='gpu_vendor_sampling':req['options'].update(temperature=0.7,presence_penalty=1.5)
        if id=='cpu_greedy':req['options']['num_gpu']=0
        plans.append(dict(id=id,request=req,expected_exact='OK'))
    OUT.mkdir();atomic_json(OUT/'plans.json',plans);(OUT/'model_identity.json').write_bytes((SOURCE/'model_identity.json').read_bytes());(OUT/'run_quality_runtime_canary_r19.executed.py').write_bytes(Path(__file__).read_bytes())
    paths=[SOURCE/'model_identity.json',SOURCE/'metadata.json',ROOT/'evaluation/decoding_compat_20261023_r18/results.json',ROOT/'evaluation/decoding_compat_20261023_r18/summary.json']
    atomic_json(OUT/'metadata.json',dict(plans_sha256=sha(OUT/'plans.json'),identity_sha256=sha(OUT/'model_identity.json'),code=code(),provenance={str(p):sha(p) for p in paths},config={k:os.getenv(k) for k in protocol.KEYS},design='Three fresh evaluation-alias canaries,unstructured simpleOKinstruction,no QA gold.1024ctx/32output/3threads/seed42;GPUgreedy/GPUofficialsamplingprofile/CPUgreedy. Unload onlyshop-qwen before/after each via emptygeneratekeepalive0;verify psabsence/freshPID andactualoffload. No service restart/modelcreation/download/prod.envchange. Sampling profile changes two parameters,not isolatedtemperatureeffect.'))

def verify(meta):
    assert sha(OUT/'plans.json')==meta['plans_sha256'] and sha(OUT/'model_identity.json')==meta['identity_sha256']
    assert code()==meta['code'] and {k:os.getenv(k) for k in protocol.KEYS}==meta['config']
    for p,h in meta['provenance'].items():assert sha(Path(p))==h,p
    identity=read(OUT/'model_identity.json');assert protocol.blob_stat(identity['blob_path'])==identity['blob_stat'] and protocol.digest(protocol.model_identity(protocol.EVAL_MODEL))==protocol.digest(identity['evaluation'])

def ps():
    response=requests.get(os.environ['OLLAMA_BASE_URL'].rstrip('/')+'/api/ps',timeout=(5,10));response.raise_for_status();return response.json()

def unload():
    response=requests.post(os.environ['OLLAMA_BASE_URL'].rstrip('/')+'/api/generate',json=dict(model=protocol.EVAL_MODEL,stream=False,keep_alive=0),timeout=(5,30));response.raise_for_status();raw=response.json()
    assert not raw.get('response') and raw.get('eval_count',0)==0,'Unload unexpectedly generated tokens'
    snapshots=[]
    for _ in range(20):
        state=ps();snapshots.append(state)
        if not any(x.get('name')==protocol.EVAL_MODEL for x in state.get('models',[])):return dict(response=raw,absent=True,last_ps=state)
        time.sleep(0.25)
    raise RuntimeError('Evaluation alias still loaded after unload')

def runtime_processes():
    cmd="Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'llama-server.exe' -and $_.CommandLine -like '*chatbotshop*runtime*ollama*' } | Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"
    run=subprocess.run(['powershell','-NoProfile','-Command',cmd],capture_output=True,text=True,timeout=15)
    return dict(returncode=run.returncode,stdout=run.stdout.strip(),stderr=run.stderr[:500])

def errors_since(offset):
    size=SERVER_LOG.stat().st_size
    with SERVER_LOG.open('rb') as f:
        f.seek(max(offset if size>=offset else 0,size-100000));text=f.read(100000).decode('utf8',errors='replace')
    return [line for line in text.splitlines() if any(term in line.lower() for term in ['got exception','send_error','out of memory','cuda error','failed to load','grammar stack'])]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    with exclusive(BASE/'runner.lock'):
        if args.prepare_only:prepare();verify(read(OUT/'metadata.json'));print('3 fresh-runner canaries frozen,no inference.');return
        meta=read(OUT/'metadata.json');verify(meta);plans=read(OUT/'plans.json');rows=read(OUT/'results.json') if (OUT/'results.json').exists() else [];assert [r['id'] for r in rows]==[p['id'] for p in plans[:len(rows)]]
        infra=0
        for p in plans[len(rows):]:
            verify(meta);row=dict(id=p['id'],request=p['request']);start=time.monotonic();offset=SERVER_LOG.stat().st_size;stop=False
            try:
                row['unload_before']=unload();row['processes_before']=runtime_processes()
                response=requests.post(os.environ['OLLAMA_BASE_URL'].rstrip('/')+'/api/chat',json=p['request'],timeout=(5,120));row['http_status']=response.status_code
                if response.ok:
                    raw=response.json();row['response']=raw;content=raw.get('message',{}).get('content','');row['canary_exact']=content=='OK';row['canary_trimmed']=content.strip()=='OK';infra=0
                else:
                    row['error_body']=response.text[:4096];infra+=1
                    if any(t in response.text.lower() for t in ['out of memory','unsupported architecture','cuda error','failed to load']):stop=True
                row['runtime_ps']=ps();row['runtime_processes']=runtime_processes()
            except (requests.RequestException,AssertionError,RuntimeError,subprocess.TimeoutExpired) as exc:
                row['control_error']=type(exc).__name__+': '+str(exc)[:400];infra+=1;stop=True
            finally:
                row['runtime_errors']=errors_since(offset)
                try:row['unload_after']=unload()
                except Exception as exc:row['cleanup_error']=type(exc).__name__+': '+str(exc)[:400];stop=True
            row['seconds']=round(time.monotonic()-start,3);rows.append(row);atomic_json(OUT/'results.json',rows);print(p['id'],row.get('http_status'),row.get('canary_exact'),row.get('control_error'),flush=True)
            if stop or infra>=3:break
        verify(meta);atomic_json(OUT/'integrity.json',dict(unchanged=True,planned=3,attempted=len(rows),complete=len(rows)==3,qa_semantics_scored=False))
if __name__=='__main__':main()
