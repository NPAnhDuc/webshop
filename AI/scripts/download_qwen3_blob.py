"""Verified public Ollama blob, with resumable HTTPS range parts for slow networks."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
from pathlib import Path
import requests
import time

ROOT=Path(__file__).resolve().parents[1]
DIGEST='85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9'
TOTAL=2497280480
FOLDER=ROOT/'models/ollama/blobs'
final=FOLDER/('sha256-'+DIGEST)
if final.exists():
    with final.open('rb') as stream:
        if final.stat().st_size!=TOTAL or hashlib.file_digest(stream,'sha256').hexdigest()!=DIGEST: raise ValueError('Existing Qwen3 blob checksum mismatch')
    print('QWEN3 ALREADY VERIFIED',DIGEST,flush=True)
    raise SystemExit(0)
URL='https://registry.ollama.ai/v2/library/qwen3/blobs/sha256:'+DIGEST
prefix=FOLDER/('sha256-'+DIGEST+'.download-single')
start=prefix.stat().st_size if prefix.exists() else 0
PARTS=ROOT/'runtime/qwen3-download';PARTS.mkdir(exist_ok=True)

def fetch(bounds):
    a,b=bounds;path=PARTS/f'{a}-{b}.part'
    if path.exists() and path.stat().st_size==b-a+1: return path
    for attempt in range(3):
        try:
            with requests.get(URL,headers={'Range':f'bytes={a}-{b}'},stream=True,timeout=(20,90)) as response:
                response.raise_for_status()
                if response.status_code!=206 or response.headers.get('content-range')!=f'bytes {a}-{b}/{TOTAL}': raise ValueError('Unexpected range response')
                with path.open('wb') as stream:
                    for chunk in response.iter_content(256*1024): stream.write(chunk)
            if path.stat().st_size!=b-a+1: raise ValueError('Incomplete range')
            print(f'Qwen3 verified range size {b-a+1}; end {b+1}/{TOTAL}',flush=True)
            return path
        except requests.RequestException:
            if attempt==2: raise
            time.sleep(2)

ranges=[(a,min(TOTAL-1,a+64*1024*1024-1)) for a in range(start,TOTAL,64*1024*1024)]
with ThreadPoolExecutor(max_workers=8) as pool: paths=list(pool.map(fetch,ranges))
output=PARTS/'merged.gguf';digest=hashlib.sha256()
with output.open('wb') as stream:
    for path in ([prefix] if start else [])+paths:
        with path.open('rb') as source:
            for chunk in iter(lambda:source.read(1024*1024),b''): stream.write(chunk);digest.update(chunk)
assert output.stat().st_size==TOTAL and digest.hexdigest()==DIGEST,'Blob SHA256 mismatch'
output.replace(FOLDER/('sha256-'+DIGEST))
print('QWEN3 SHA256 VERIFIED',DIGEST,flush=True)
