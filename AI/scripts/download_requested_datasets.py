"""Versioned, attributed acquisition of the user's Kaggle dataset list."""
import concurrent.futures
import csv
import hashlib
import json
import shutil
import time
import zipfile
import base64
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT=Path(__file__).resolve().parents[1]

def ranged_archive(url, archive, require_zip=True):
    """Bounded range transfer; verify the publisher's MD5 when supplied."""
    with requests.get(url,headers={'Range':'bytes=0-0'},stream=True,timeout=(20,45)) as probe:
        probe.raise_for_status()
        if probe.status_code!=206: raise ValueError('Server does not support partial download')
        total=int(probe.headers['Content-Range'].split('/')[-1])
        if total>25*1024**3: raise ValueError('Archive exceeds 25GiB cap')
        resolved=probe.url
        etag=probe.headers.get('ETag','')
        hashes=probe.headers.get('x-goog-hash','')
    chunks=archive.parent/'download-chunks'
    chunks.mkdir(exist_ok=True)
    marker=chunks/'source.json'
    identity={'etag':etag,'bytes':total}
    if marker.exists() and json.loads(marker.read_text())!=identity:
        raise ValueError('Source changed; existing chunk directory needs a new version')
    marker.write_text(json.dumps(identity))
    block=4*1024*1024
    count=(total+block-1)//block
    def transfer(index):
        start=index*block
        end=min(start+block,total)-1
        target=chunks/f'{index:06d}.chunk'
        if target.exists() and target.stat().st_size==end-start+1: return target
        for attempt in range(4):
            try:
                with requests.get(resolved,headers={'Range':f'bytes={start}-{end}'},timeout=(20,60)) as r:
                    r.raise_for_status()
                    if r.status_code!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{total}':
                        raise ValueError('Range mismatch')
                    if len(r.content)!=end-start+1: raise ValueError('Truncated chunk')
                    target.write_bytes(r.content)
                return target
            except (requests.RequestException,ValueError):
                if attempt==3: raise
        return target
    print(json.dumps({'archive':archive.parent.name,'transfer_bytes':total,'chunks':count}),flush=True)
    done=0
    checkpoint=time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        for future in concurrent.futures.as_completed([pool.submit(transfer,i) for i in range(count)]):
            future.result()
            done+=1
            if time.monotonic()-checkpoint>20 or done==count:
                print(json.dumps({'archive':archive.parent.name,'chunks_done':done,'chunks_total':count}),flush=True)
                checkpoint=time.monotonic()
    partial=archive.with_suffix('.zip.part')
    digest=hashlib.md5()
    with partial.open('wb') as out:
        for i in range(count):
            body=(chunks/f'{i:06d}.chunk').read_bytes()
            out.write(body)
            digest.update(body)
    expected=next((v[4:] for v in hashes.split(', ') if v.startswith('md5=')),None)
    if expected and base64.b64encode(digest.digest()).decode()!=expected: raise ValueError('Publisher MD5 mismatch')
    if require_zip and not zipfile.is_zipfile(partial): raise ValueError('Invalid ZIP')
    partial.replace(archive)
    # Only remove the exact chunk files written above, after archive verification.
    for i in range(count): (chunks/f'{i:06d}.chunk').unlink()
    marker.unlink()
    chunks.rmdir()

def download(entry):
    ref=entry['dataset']
    folder=ROOT/'data'/'structured'/'raw'/ref.replace('/','__')
    folder.mkdir(parents=True,exist_ok=True)
    meta=entry.get('metadata',{})
    record={'dataset':ref,'source_url':'https://www.kaggle.com/datasets/'+ref,
            'retrieved_at':datetime.now(timezone.utc).isoformat(),
            'version':meta.get('currentVersionNumber'),'license':meta.get('licenseName','unverified'),
            'source_bytes':meta.get('totalBytes'),'usage':'external_research_only',
            'redistribution':'excluded_pending_rights_review',
            'not_shop_sales_or_inventory':True}
    (folder/'source-metadata.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding='utf-8')
    archive=folder/'dataset.zip'
    partial=folder/'dataset.zip.part'
    try:
        if entry.get('status')!=200:
            raise ValueError('Source access denied/unavailable: '+str(entry.get('status')))
        if not archive.exists():
            url='https://www.kaggle.com/api/v1/datasets/download/'+ref
            if record['version']: url+='?datasetVersionNumber='+str(record['version'])
            if meta.get('totalBytes',0)>10_000_000:
                ranged_archive(url,archive)
            for attempt in range(0 if archive.exists() else 3):
                try:
                    with requests.get(url,stream=True,timeout=(30,120)) as r:
                        r.raise_for_status()
                        if 'text/html' in r.headers.get('Content-Type',''):
                            raise ValueError('HTML login/challenge instead of archive')
                        count=0
                        checkpoint=time.monotonic()
                        with partial.open('wb') as target:
                            for chunk in r.iter_content(4*1024*1024):
                                count+=len(chunk)
                                if count>25*1024**3: raise ValueError('Archive exceeds 25GiB cap')
                                target.write(chunk)
                                if time.monotonic()-checkpoint>30:
                                    print(json.dumps({'dataset':ref,'downloaded_MB':round(count/1e6)}),flush=True)
                                    checkpoint=time.monotonic()
                    if not zipfile.is_zipfile(partial): raise ValueError('Not a valid ZIP archive')
                    partial.replace(archive)
                    break
                except requests.RequestException:
                    if attempt==2: raise
        digest=hashlib.sha256()
        with archive.open('rb') as source:
            for chunk in iter(lambda:source.read(4*1024*1024),b''): digest.update(chunk)
        record.update(bytes=archive.stat().st_size,sha256=digest.hexdigest())
        files=[]
        extracted=folder/'original'
        extracted.mkdir(exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            if sum(i.file_size for i in z.infolist())>40*1024**3:
                raise ValueError('Expanded archive exceeds 40GiB cap')
            for info in z.infolist():
                path=(extracted/info.filename).resolve()
                if not path.is_relative_to(extracted.resolve()): raise ValueError('Unsafe ZIP path')
                if info.is_dir(): continue
                if path.suffix.lower() not in ('.csv','.json','.jsonl','.txt','.md','.xlsx','.xls'):
                    continue
                path.parent.mkdir(parents=True,exist_ok=True)
                if not path.exists() or path.stat().st_size!=info.file_size:
                    with z.open(info) as src,path.open('wb') as dst: shutil.copyfileobj(src,dst,4*1024*1024)
                file={'file':str(path.relative_to(folder)),'bytes':path.stat().st_size}
                if path.suffix.lower()=='.csv':
                    # csv.reader counts quoted multiline fields correctly without loading into RAM.
                    with path.open(encoding='utf-8-sig',errors='replace',newline='') as stream:
                        reader=csv.reader(stream)
                        file['columns']=next(reader,[])
                        file['rows']=sum(1 for _ in reader)
                files.append(file)
        record.update(status='downloaded',files=files)
    except Exception as e:
        record.update(status='unavailable',error=str(e))
    (folder/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False),flush=True)
    return record

if __name__=='__main__':
    entries=json.loads((ROOT/'runtime'/'acquisition'/'kaggle-metadata.json').read_text(encoding='utf-8'))
    with concurrent.futures.ThreadPoolExecutor(3) as pool:
        records=list(pool.map(download,entries))
    (ROOT/'runtime'/'acquisition'/'datasets-summary.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
