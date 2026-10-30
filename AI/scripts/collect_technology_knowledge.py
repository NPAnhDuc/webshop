"""Download a fixed, official-source research pack. Never modifies chatbot/index/DB.

No authentication bypass, browser impersonation or generated product specifications.
Raw archives are research-only; curated summaries are created separately after review.
"""
import argparse
import concurrent.futures
import hashlib
import io
import json
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'data/unstructured/technology_20261020'
UA = 'TechStoreKnowledgeResearch/1.0'
MAX_BYTES = 15 * 1024 * 1024
SOURCES = [
 ('intel-gaming-laptop','guide','https://www.intel.com/content/www/us/en/gaming/resources/how-to-pick-the-best-gaming-laptop.html'),
 ('intel-ram','guide','https://www.intel.com/content/www/us/en/gaming/resources/how-much-ram-gaming.html'),
 ('intel-cpu','guide','https://www.intel.com/content/www/us/en/gaming/resources/gaming-cpu.html'),
 ('intel-pc-components','guide','https://www.intel.com/content/www/us/en/gaming/resources/how-to-build-a-gaming-pc.html'),
 ('intel-bottleneck','guide','https://www.intel.com/content/www/us/en/gaming/resources/what-is-bottlenecking-my-pc.html'),
 ('intel-cpu-gpu','technology','https://www.intel.com/content/www/us/en/products/docs/processors/cpu-vs-gpu.html'),
 ('intel-thunderbolt','technology','https://www.intel.com/content/www/us/en/architecture-and-technology/thunderbolt/thunderbolt-4-vs-usb-c.html'),
 ('intel-wifi-bands','technology','https://www.intel.com/content/www/us/en/support/articles/000099711/wireless.html'),
 ('intel-wifi6','technology','https://www.intel.com/content/www/us/en/gaming/resources/wifi-6.html'),
 ('kingston-ddr4-ddr5','technology','https://www.kingston.com/en/blog/pc-performance/ddr-memory-generation-differences'),
 ('kingston-m2','technology','https://www.kingston.com/en/blog/pc-performance/two-types-m2-vs-ssd'),
 ('kingston-ssd-form','technology','https://www.kingston.com/en/blog/pc-performance/ssd-form-factors'),
 ('kingston-nvme-sata','technology','https://www.kingston.com/unitedkingdom/en/blog/pc-performance/nvme-vs-sata'),
 ('kingston-ssd-faq','technology','https://www.kingston.com/en/ssd/ssd-faq'),
 ('kingston-ddr5-pdf','technology','https://media.kingston.com/kingston/articles/MKF_954-DDR5-Collateral_us.pdf'),
 ('kingston-flash-vn','technology','https://media.kingston.com/pdfs/MKF_283.2_Flash_Memory_Guide_VN.pdf'),
 ('usb-power-delivery','technology','https://www.usb.org/usb-charger-pd'),
 ('dell-battery','technology','https://www.dell.com/support/kbdoc/en-us/000175212/dell-laptop-battery-frequently-asked-questions?lang=en'),
 ('samsung-refresh','technology','https://insights.samsung.com/2026/06/17/finding-the-right-refresh-rate-know-the-best-hz-for-your-needs/'),
 ('samsung-oled','technology','https://www.samsung.com/us/tvs/tv-buying-guide/why-oled-tvs-are-worth-it/'),
 ('benq-panels','technology','https://www.benq.com/en-us/knowledge-center/knowledge/how-to-choose-between-tn-va-and-ips-panels-for-the-games-you-play/.html'),
 ('benq-input-response','technology','https://www.benq.com/en-us/knowledge-center/knowledge/gaming-monitor-input-lag-versus-response-time-whats-the-difference-and-why-should-i-care.html'),
 ('benq-photo','guide','https://www.benq.com/en-us/knowledge-center/knowledge/choosing-the-right-monitor-photo-editing.html'),
 ('adobe-photoshop','software','https://helpx.adobe.com/photoshop/desktop/get-started/technical-requirements-installation/adobe-photoshop-on-desktop-technical-requirements.html'),
 ('lenovo-loq15irh8','device_family','https://psref.lenovo.com/syspool/Sys/PDF/LOQ/LOQ_15IRH8/LOQ_15IRH8_Spec.pdf'),
 ('lenovo-loq-datasheet','device_family','https://psref.lenovo.com/syspool/Sys/PDF/datasheet/Lenovo_LOQ_15IRH8_Datasheet_EN.pdf'),
 ('msi-modern15-408au','different_regional_variant','https://storage-asset.msi.com/specSheet/au/bnp/Modern%2015%20B12M-408AU.pdf'),
 ('msi-modern15-081sg','different_regional_variant','https://storage-asset.msi.com/specSheet/sg/bnp/Modern%2015%20B12M-081SG.pdf'),
 ('msi-modern15-ca','different_regional_variant','https://ca.msi.com/Business-Productivity/Modern-15-B12X/Specification'),
]
_locks = {}
_robots = {}
_guard = threading.Lock()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fetch_one(source):
    identifier, scope, url = source
    record = dict(id=identifier, url=url, scope=scope,
                  fetched_at=datetime.now(timezone.utc).isoformat(),
                  rights='copyright retained by publisher; research archive only; redistribution not cleared',
                  review_status='unreviewed', indexed=False)
    host = urlparse(url).netloc
    with _guard:
        lock = _locks.setdefault(host, threading.Lock())
    try:
        with lock:
            if host not in _robots:
                robots_url = f'https://{host}/robots.txt'
                try:
                    response = requests.get(robots_url, headers={'User-Agent':UA}, timeout=15)
                    parser = RobotFileParser()
                    if response.status_code == 200:
                        parser.parse(response.text.splitlines())
                        _robots[host] = (parser, 'read_200')
                        (PACK/'robots'/f'{host}.txt').write_text(response.text, encoding='utf8')
                    else:
                        _robots[host] = (None, f'unavailable_http_{response.status_code}')
                except requests.RequestException:
                    _robots[host] = (None, 'unavailable_network')
            parser, robot_status = _robots[host]
            record['robots_status'] = robot_status
            if parser and not parser.can_fetch(UA, url):
                record['status'] = 'robots_disallowed'
                return record
            time.sleep(0.5)
            with requests.get(url, headers={'User-Agent':UA}, timeout=(12,45), stream=True) as response:
                record.update(http_status=response.status_code, final_url=response.url,
                              content_type=response.headers.get('Content-Type',''))
                response.raise_for_status()
                chunks=[];size=0
                for chunk in response.iter_content(65536):
                    size+=len(chunk)
                    if size>MAX_BYTES:raise ValueError('download exceeds 15 MB limit')
                    chunks.append(chunk)
                payload=b''.join(chunks)
        is_pdf=payload.startswith(b'%PDF-')
        if is_pdf:
            reader=PdfReader(io.BytesIO(payload))
            text='\n\n'.join(f'[Page {i+1}]\n'+(p.extract_text() or '') for i,p in enumerate(reader.pages))
            title=identifier;record['pages']=len(reader.pages)
        else:
            if 'html' not in record['content_type'].lower():raise ValueError('unexpected MIME type')
            soup=BeautifulSoup(payload,'html.parser',from_encoding='utf-8')
            title=soup.title.get_text(' ',strip=True) if soup.title else identifier
            for tag in soup(['script','style','nav','footer','header','noscript','iframe','form']):tag.decompose()
            body=soup.find('main') or soup.find('article') or soup.body or soup
            text='\n'.join(line.strip() for line in body.get_text('\n').splitlines() if line.strip())
            if re.search(r'^\s*(access denied|just a moment|verify you are human)',title,re.I):
                raise ValueError('blocked/challenge page, not a source document')
        if len(text)<500:raise ValueError('insufficient extracted text; manual review required')
        ext='pdf' if is_pdf else 'html'
        raw=PACK/'raw'/f'{identifier}.{ext}';extracted=PACK/'extracted'/f'{identifier}.txt'
        raw.write_bytes(payload);extracted.write_bytes(text.encode('utf8'))
        record.update(status='downloaded',title=title,bytes=len(payload),sha256=digest(payload),
                      text_sha256=digest(extracted.read_bytes()),characters=len(text),
                      raw=str(raw.relative_to(PACK)),extracted=str(extracted.relative_to(PACK)))
    except Exception as exc:
        record.update(status='failed',error=f'{type(exc).__name__}: {exc}'[:400])
    return record


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--extra',type=Path,help='Append new [id,scope,url] entries without retrying blocked sources')
    options=args.parse_args()
    for folder in ['raw','extracted','curated','device_facts','robots']:(PACK/folder).mkdir(parents=True,exist_ok=True)
    previous=json.loads((PACK/'manifest.json').read_text(encoding='utf8')) if options.extra and (PACK/'manifest.json').exists() else []
    sources=json.loads(options.extra.read_text(encoding='utf8')) if options.extra else SOURCES
    existing={r['id'] for r in previous}
    sources=[s for s in sources if s[0] not in existing]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results=previous+list(pool.map(fetch_one,sources))
    (PACK/'manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'folder':str(PACK),'sources':len(results),'downloaded':sum(r['status']=='downloaded' for r in results),
                      'bytes':sum(r.get('bytes',0) for r in results),
                      'unavailable':[{'id':r['id'],'status':r['status'],'http':r.get('http_status')} for r in results if r['status']!='downloaded']},ensure_ascii=False))


if __name__=='__main__':main()
