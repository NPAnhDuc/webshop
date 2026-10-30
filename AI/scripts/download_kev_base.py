"""Download a pinned public model shard using bounded parallel HTTP ranges."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib,json,os,time
import requests
root=Path(__file__).resolve().parents[1]
repo=root/'models/huggingface/hub/models--Qwen--Qwen3.5-0.8B-Base'
snapshots=list((repo/'snapshots').iterdir())
assert len(snapshots)==1
snapshot=snapshots[0]
name='model.safetensors-00001-of-00001.safetensors'
meta=requests.get(f'https://huggingface.co/api/models/Qwen/Qwen3.5-0.8B-Base/revision/{snapshot.name}?blobs=true',timeout=30)
meta.raise_for_status()
info=next(v for v in meta.json()['siblings'] if v['rfilename']==name)
size=info['size'];expected=info['lfs']['sha256']
url=f'https://huggingface.co/Qwen/Qwen3.5-0.8B-Base/resolve/{snapshot.name}/{name}'
existing=snapshot/name
if existing.exists() and existing.stat().st_size==size:
    digest=hashlib.sha256()
    with existing.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):digest.update(block)
    if digest.hexdigest()==expected:
        print('Existing model verified; no download needed',flush=True)
        raise SystemExit(0)
folder=root/'models/downloads/kev-base';folder.mkdir(parents=True,exist_ok=True)
step=4*1024*1024

def get_part(i):
    start=i*step;end=min(size,start+step)-1
    target=folder/f'{i:04d}.part'
    if target.exists() and target.stat().st_size==end-start+1:return target
    for retry in range(4):
        try:
            r=requests.get(url,headers={'Range':f'bytes={start}-{end}'},timeout=(20,120))
            r.raise_for_status()
            if r.status_code!=206 or len(r.content)!=end-start+1:raise ValueError('Invalid range response')
            target.write_bytes(r.content)
            return target
        except Exception:
            if retry==3:raise
            time.sleep(2)

count=(size+step-1)//step
started=time.time();done=0
with ThreadPoolExecutor(max_workers=32) as pool:
    for future in as_completed([pool.submit(get_part,i) for i in range(count)]):
        done+=future.result().stat().st_size
        if done//(64*1024*1024)!=(done-step)//(64*1024*1024):
            print(f'{done}/{size} bytes; {time.time()-started:.0f}s',flush=True)
staging=snapshot/(name+'.verified-part')
digest=hashlib.sha256()
with staging.open('wb') as out:
    for i in range(count):
        data=(folder/f'{i:04d}.part').read_bytes();digest.update(data);out.write(data)
if digest.hexdigest()!=expected:raise ValueError('SHA256 mismatch')
staging.replace(snapshot/name)
manifest={'repo':'Qwen/Qwen3.5-0.8B-Base','revision':snapshot.name,'file':name,'sha256':digest.hexdigest(),'bytes':size}
(folder/'manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(manifest),flush=True)

