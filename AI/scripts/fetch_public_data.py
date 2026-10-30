"""Download an attributed public benchmark; never load it as shop inventory."""
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
URL='https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip'

def main():
    folder=ROOT/'data'/'structured'/'raw'/'uci_online_retail_ii'
    folder.mkdir(parents=True,exist_ok=True)
    archive=folder/'online-retail-ii.zip'
    partial=archive.with_suffix('.part')
    digest=hashlib.sha256()
    size=0
    with requests.get(URL,stream=True,timeout=(15,90)) as response:
        response.raise_for_status()
        with partial.open('wb') as target:
            for chunk in response.iter_content(1024*1024):
                size+=len(chunk)
                if size>150*1024*1024: raise ValueError('Download exceeds limit')
                target.write(chunk)
                digest.update(chunk)
    if not zipfile.is_zipfile(partial): raise ValueError('Invalid ZIP')
    partial.replace(archive)
    with zipfile.ZipFile(archive) as z:
        members=z.namelist()
    manifest={'name':'Online Retail II','url':URL,'page':'https://archive.ics.uci.edu/dataset/502/online+retail+ii',
        'license':'CC BY 4.0','creator':'Daqing Chen','doi':'10.24432/C5CG6D','retrieved_at':datetime.now(timezone.utc).isoformat(),
        'sha256':digest.hexdigest(),'bytes':size,'members':members,
        'usage':'External retail benchmark only; not electronics shop sales, inventory, prices or policies.'}
    (folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))

if __name__=='__main__': main()
