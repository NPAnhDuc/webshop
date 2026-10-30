"""Resolve a stale ACBS host and the omitted word in the Kaggle slug."""
import json
from pathlib import Path
from probe_requested_sources import probe
from download_requested_datasets import download, ranged_archive
from download_strategy_sources import fetch, ROOT

if __name__=='__main__':
    ref='muhammadshahrayar/transactional-retail-dataset-of-electronics-store'
    entry=probe(ref)
    (ROOT/'runtime'/'acquisition'/'corrected-kaggle-metadata.json').write_text(json.dumps(entry,ensure_ascii=False,indent=2),encoding='utf-8')
    download(entry)
    path=ROOT/'data'/'unstructured'/'reference'/'retail_strategy'/'manifest.json'
    records=json.loads(path.read_text(encoding='utf-8'))
    replacement=fetch(('frt-acbs-2025','https://acbs.com.vn/Files/Domains/ACBS/WFL-1585/250508065942-1015-1015000001.pdf'))
    replacement['original_requested_url']='https://content.acbs.com.vn/Files/Domains/ACBS/WFL-1585/250508065942-1015-1015000001.pdf'
    records=[replacement if r['id']==replacement['id'] else r for r in records]
    path.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    annual=path.parent/'frt-annual-2025-bsc.pdf'
    try:
        if not annual.exists():
            ranged_archive('https://new.bsc.com.vn/News/NewsAttachedFile/1308340',annual,require_zip=False)
        replacement=fetch(('frt-annual-2025-bsc','https://new.bsc.com.vn/News/NewsAttachedFile/1308340'))
        records=[replacement if r['id']==replacement['id'] else r for r in records]
        path.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    except Exception as e:
        print('Annual report retry:',str(e),flush=True)
