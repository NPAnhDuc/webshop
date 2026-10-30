import concurrent.futures
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
DATASETS = [
 'mkechinov/ecommerce-events-history-in-electronics-store',
 'mkechinov/ecommerce-purchase-history-from-electronics-store',
 'mkechinov/ecommerce-behavior-data-from-multi-category-store',
 'muhammadshahrayar/transactional-retail-of-electronics-store',
 'abdelrahmanemad594/laptop-prices',
 'juanmerinobermejo/laptops-price-dataset',
 'msjahid/ryans-laptop-inventory-and-specifications',
 'elvinrustam/ebay-laptops-and-netbooks-sales',
 'olistbr/brazilian-ecommerce',
]

def probe(name):
    result = {'dataset': name}
    try:
        r = requests.get('https://www.kaggle.com/api/v1/datasets/view/'+name, timeout=60)
        result['status'] = r.status_code
        if r.ok:
            result['metadata'] = r.json()
        else:
            result['error'] = r.text[:200]
    except Exception as e:
        result['error'] = str(e)
    print(json.dumps({k:v for k,v in result.items() if k!='metadata'}), flush=True)
    return result

if __name__ == '__main__':
    folder = ROOT/'runtime'/'acquisition'
    folder.mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        results = list(pool.map(probe, DATASETS))
    (folder/'kaggle-metadata.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    for r in results:
        m=r.get('metadata',{})
        print(json.dumps({'dataset':r['dataset'], 'bytes':m.get('totalBytes'), 'licenses':m.get('licenses'), 'files':m.get('resources',m.get('files')), 'keys':list(m)},ensure_ascii=False),flush=True)
