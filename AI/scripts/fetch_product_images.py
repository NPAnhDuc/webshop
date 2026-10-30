"""Download reviewed product image candidates with provenance; reject non-images."""
import concurrent.futures
import hashlib
import html
import io
import json
import re
import warnings
import argparse
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'data'/'product_images'
CATALOG=ROOT/'data'/'structured'/'processed'/'product_catalog.jsonl'

def fetch(item):
    index,product,selection=item
    record={k:product[k] for k in ('record_id','model','category')}
    record.update(search_index=index,match_scope=selection['match_scope'],
                  exact_sku_verified=False,match_notes=selection['notes'],
                  commercial_reuse_approved=False,rights_status='copyright_of_original_owner_permission_not_verified',
                  retrieved_at=datetime.now(timezone.utc).isoformat(),status='missing')
    failures=[]
    for candidate in selection['candidates']:
        try:
            url=html.unescape(candidate['image'])
            with requests.get(url,stream=True,timeout=(10,35),headers={'User-Agent':'ShopBotProductResearch/1.0'}) as response:
                response.raise_for_status()
                parts=[]
                count=0
                for part in response.iter_content(65536):
                    count+=len(part)
                    if count>15*1024*1024:raise ValueError('Image exceeds 15MB limit')
                    parts.append(part)
                body=b''.join(parts)
            with warnings.catch_warnings():
                warnings.simplefilter('error',Image.DecompressionBombWarning)
                with Image.open(io.BytesIO(body)) as im:
                    im.verify()
                with Image.open(io.BytesIO(body)) as im:
                    width,height=im.size
                    fmt=im.format
            if min(width,height)<180: raise ValueError('Image too small')
            suffix={'JPEG':'.jpg','PNG':'.png','WEBP':'.webp','GIF':'.gif'}.get(fmt)
            if not suffix:raise ValueError('Unsupported raster format '+str(fmt))
            slug=re.sub(r'[^a-z0-9]+','-',product['model'].lower()).strip('-')[:90]
            path=FOLDER/'images'/product['category']/(slug+'-'+product['record_id'][:12]+suffix)
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(body)
            record.update(status='downloaded_pending_visual_review',local_path=path.relative_to(FOLDER).as_posix(),
                          source_page=candidate['page'],source_title=candidate['title'],image_url=url,
                          width=width,height=height,bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
            break
        except Exception as e:
            failures.append({'source_page':candidate['page'],'error':str(e)})
    if failures:record['failed_attempts']=failures
    if record['status']=='missing':record['reason']='No verified matching candidate' if not selection['candidates'] else 'All selected image sources unavailable'
    print(json.dumps({'index':index,'model':product['model'],'status':record['status']}),flush=True)
    # Per-product records survive interruptions.
    folder=FOLDER/'records'
    folder.mkdir(exist_ok=True)
    (folder/(product['record_id']+'.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    return record

def preview(records):
    thumbs=FOLDER/'preview'
    thumbs.mkdir(exist_ok=True)
    for page,start in enumerate(range(0,len(records),20),1):
        sheet=Image.new('RGB',(1200,5*210),'#eeeeee')
        draw=ImageDraw.Draw(sheet)
        for offset,r in enumerate(records[start:start+20]):
            x=(offset%4)*300
            y=(offset//4)*210
            if r.get('local_path'):
                with Image.open(FOLDER/r['local_path']) as im:
                    tile=ImageOps.contain(im.convert('RGB'),(280,165))
                    sheet.paste(tile,(x+(300-tile.width)//2,y))
            draw.text((x+8,y+168),f"{r['search_index']:02d} {r['model'][:40]}",fill='black')
            draw.text((x+8,y+187),r['status'][:42],fill='black')
        sheet.save(thumbs/f'contact-sheet-{page}.jpg')
    cards=[]
    for r in records:
        picture=(f'<img loading="lazy" src="{html.escape(r["local_path"])}">' if r.get('local_path') else '<p>Chưa có ảnh đúng model</p>')
        source=(f'<a href="{html.escape(r["source_page"])}">Nguồn ảnh</a>' if r.get('source_page') else '')
        cards.append(f'<article>{picture}<h3>{html.escape(r["model"])}</h3><p>{html.escape(r["match_notes"])}</p>{source}</article>')
    body='<!doctype html><meta charset="utf-8"><title>Ảnh danh mục sản phẩm</title><style>body{font-family:Arial;margin:24px;background:#f4f5f7}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}article{background:white;padding:16px;border-radius:12px}img{width:100%;height:200px;object-fit:contain}p{color:#555;font-size:13px}</style><h1>Ảnh sản phẩm tham khảo</h1><p>Đối chiếu model ngoại hình. Chưa xác minh SKU/cấu hình đầy đủ hoặc quyền sử dụng thương mại.</p><main>'+''.join(cards)+'</main>'
    (FOLDER/'gallery.html').write_text(body,encoding='utf-8')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--only',type=int,nargs='*')
    args=parser.parse_args()
    products=[json.loads(line) for line in CATALOG.read_text(encoding='utf-8').splitlines()]
    selections=json.loads((FOLDER/'selected_sources.json').read_text(encoding='utf-8'))
    if len(products)!=len(selections):raise ValueError('Catalog changed; review candidate mapping again')
    if any(p['record_id']!=s.get('product_id') for p,s in zip(products,selections)):
        raise ValueError('Product IDs changed; review image mapping again')
    tasks=[(i,p,s) for i,(p,s) in enumerate(zip(products,selections)) if args.only is None or i in args.only]
    with concurrent.futures.ThreadPoolExecutor(6) as pool:
        new_records=list(pool.map(fetch,tasks))
    previous=json.loads((FOLDER/'manifest.json').read_text(encoding='utf-8')) if (FOLDER/'manifest.json').exists() else []
    indexed={r['record_id']:r for r in previous}
    indexed.update({r['record_id']:r for r in new_records})
    records=[indexed[p['record_id']] for p in products]
    (FOLDER/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    preview(records)
    print(json.dumps({'downloaded':sum('local_path' in r for r in records),'total':len(records)}),flush=True)

if __name__=='__main__':main()
