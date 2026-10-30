"""Frozen three-request local decoding compatibility diagnostic; no QA gold."""
import argparse,hashlib,importlib.util,json,os,sys,time,copy
from pathlib import Path
import requests
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
from shopbot.monthly import exclusive,atomic_json
spec=importlib.util.spec_from_file_location('r17_protocol',ROOT/'scripts/run_quality_field_intent_probe_r17.py');protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
BASE=ROOT/'evaluation/quality_loop_20261021'
SOURCE=ROOT/'evaluation/field_intent_20261023_r17_qwen35'
BASELINE=ROOT/'evaluation/field_intent_20261023_r16'
OUT=ROOT/'evaluation/decoding_compat_20261023_r18'
SERVER_LOG=ROOT/'runtime/ollama.err.log'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def code():
    return {str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'app.py',*sorted((ROOT/'shopbot').glob('*.py')),ROOT/'scripts/run_quality_field_intent_probe_r17.py',Path(__file__).resolve()]}

def prepare():
    if OUT.exists():raise SystemExit('Preserve existing revision')
    case=read(SOURCE/'bank.json')[0];baseline=read(BASELINE/'results.json')[0];assert case['id']==baseline['id']
    body=copy.deepcopy(baseline['request']);body['model']=protocol.EVAL_MODEL
    assert json.loads(body['messages'][1]['content'])==case['payload'] and body['format']==protocol.schema_for(case['payload'])
    plans=[]
    for mode in ['full_schema','json_object','unconstrained']:
        request=copy.deepcopy(body)
        if mode=='json_object':request['format']='json'
        if mode=='unconstrained':request.pop('format')
        plans.append(dict(id=mode,source_case=case['id'],request=request))
    identity=read(SOURCE/'model_identity.json')
    assert protocol.blob_stat(identity['blob_path'])==identity['blob_stat']
    assert protocol.digest(protocol.model_identity(protocol.EVAL_MODEL))==protocol.digest(identity['evaluation'])
    OUT.mkdir();atomic_json(OUT/'plans.json',plans);(OUT/'model_identity.json').write_bytes((SOURCE/'model_identity.json').read_bytes())
    (OUT/'run_quality_decoding_compat_r18.executed.py').write_bytes(Path(__file__).read_bytes())
    paths=[SOURCE/'bank.json',SOURCE/'gold.json',SOURCE/'metadata.json',SOURCE/'results.json',SOURCE/'model_identity.json',BASELINE/'results.json']
    atomic_json(OUT/'metadata.json',dict(plans_sha256=sha(OUT/'plans.json'),identity_sha256=sha(OUT/'model_identity.json'),code=code(),provenance={str(p):sha(p) for p in paths},config={k:os.getenv(k) for k in protocol.KEYS},design='Three preregistered decoding modes for exact first failedr17input:fullschema,jsonobject,unconstrained. Same messages/options/alias; only format differs. No QA semanticgold sent/scored. Read-onlymodelidentity/blobstat pinned from verifiedr17weights; no modelcreation/service/configchange. Preserve HTTPstatus/errorbody/fullsuccessresponse and filterednewruntimeerrors pervariant.'))

def verify(meta):
    assert sha(OUT/'plans.json')==meta['plans_sha256'] and sha(OUT/'model_identity.json')==meta['identity_sha256']
    assert code()==meta['code'] and {k:os.getenv(k) for k in protocol.KEYS}==meta['config']
    for p,h in meta['provenance'].items():assert sha(Path(p))==h,p
    identity=read(OUT/'model_identity.json');assert protocol.blob_stat(identity['blob_path'])==identity['blob_stat']
    assert protocol.digest(protocol.model_identity(protocol.EVAL_MODEL))==protocol.digest(identity['evaluation'])

def log_errors(offset):
    size=SERVER_LOG.stat().st_size
    with SERVER_LOG.open('rb') as f:
        f.seek(max(offset if size>=offset else 0,size-100000));chunk=f.read(100000).decode('utf8',errors='replace')
    return [line for line in chunk.splitlines() if any(k in line.lower() for k in ['got exception','send_error','out of memory','cuda error','failed to load','grammar stack'])]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    with exclusive(BASE/'runner.lock'):
        if args.prepare_only:prepare();verify(read(OUT/'metadata.json'));print('3 decoding modes frozen; no inference.');return
        meta=read(OUT/'metadata.json');verify(meta);plans=read(OUT/'plans.json');rows=read(OUT/'results.json') if (OUT/'results.json').exists() else []
        assert [r['id'] for r in rows]==[p['id'] for p in plans[:len(rows)]]
        infra=0
        for p in plans[len(rows):]:
            verify(meta);start=time.monotonic();offset=SERVER_LOG.stat().st_size;row=dict(id=p['id'],request=p['request'],runtime_log_offset_before=offset)
            try:
                response=requests.post(os.environ['OLLAMA_BASE_URL'].rstrip('/')+'/api/chat',json=p['request'],timeout=(5,120));row['http_status']=response.status_code
                if response.ok:
                    raw=response.json();row['response']=raw;row['transport_ok']=True;infra=0
                    try:
                        selected=json.loads(raw['message']['content']);payload=json.loads(p['request']['messages'][1]['content'])
                        row['selection']=selected;row['derived_plan']=protocol.derive_plan(selected,payload);row['contract_valid']=True
                    except (ValueError,KeyError,TypeError,AssertionError) as exc:row['contract_valid']=False;row['parse_error']=type(exc).__name__+': '+str(exc)[:300]
                else:
                    row.update(transport_ok=False,error_body=response.text[:4096]);infra+=1
                    if any(term in response.text.lower() for term in ['out of memory','unsupported architecture','cuda error','failed to load']):infra=3
            except requests.RequestException as exc:row.update(transport_ok=False,request_error=type(exc).__name__+': '+str(exc)[:400]);infra+=1
            row['seconds']=round(time.monotonic()-start,3);row['runtime_errors']=log_errors(offset)
            try:row['runtime_ps']=requests.get(os.environ['OLLAMA_BASE_URL'].rstrip('/')+'/api/ps',timeout=(5,15)).json()
            except requests.RequestException as exc:row['runtime_ps_error']=type(exc).__name__
            rows.append(row);atomic_json(OUT/'results.json',rows);print(p['id'],row.get('http_status',row.get('request_error')),row.get('contract_valid'),flush=True)
            if infra>=3:break
        verify(meta);atomic_json(OUT/'integrity.json',dict(unchanged=True,planned=len(plans),attempted=len(rows),complete=len(rows)==len(plans),qa_semantics_scored=False))
if __name__=='__main__':main()
