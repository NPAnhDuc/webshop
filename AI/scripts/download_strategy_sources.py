"""Download the user's explicit research sources; never publish as shop policy."""
import concurrent.futures
import hashlib
import json
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import requests
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
 ('frt-annual-2025-bsc', 'https://new.bsc.com.vn/News/NewsAttachedFile/1308340'),
 ('frt-acbs-2025', 'https://content.acbs.com.vn/Files/Domains/ACBS/WFL-1585/250508065942-1015-1015000001.pdf'),
 ('frt-bsc', 'https://new.bsc.com.vn/Report/ReportFile/12763326'),
 ('mwg-tcbs-2026-06', 'https://www.tcbs.com.vn/wp-content/uploads/2026/06/MWG_Bao_cao_phan_tich_chi_tiet_VI-1.pdf'),
 ('dmx-fpts-2026', 'https://file.fpts.com.vn/FileStore2/File/2026/07/20/DMXPrelistingValuationReportJun26_d70e56fd.pdf'),
 ('phs-4331', 'https://phs.vn/research-file/4331'),
 ('phs-4469', 'https://www.phs.vn/research-file/4469'),
 ('mwg-dsc-q1-2025', 'https://extgw.dsc.com.vn/eback/uploads/Format_MWG_BC_Q1_2025_be0eb6e481.pdf'),
 ('bestbuy-fy2026-10k', 'https://www.sec.gov/Archives/edgar/data/764478/000076447826000009/bby-20260131.htm'),
 ('bestbuy-fy2026-q4-transcript', 'https://www.roic.ai/quote/BBY:US/transcripts/2026-year/4-quarter'),
 ('bestbuy-fy2026-q3-transcript', 'https://www.roic.ai/quote/BBY:US/transcripts/2026-year/3-quarter'),
 ('upmetrics-electronics-plan', 'https://templates.upmetrics.co/wp-content/uploads/2023/11/electronics-shop-business-plan.pdf'),
 ('sharpsheets-electronics-plan', 'https://sharpsheets.io/blog/electronics-store-business-plan-pdf-example/'),
 ('profitableventure-electronics-plan', 'https://www.profitableventure.com/electronics-store-business-plan/'),
 ('visme-computer-marketing', 'https://www.visme.co/templates/marketing-playbooks/computer-store-marketing-playbook-templates-1425289648/'),
]

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        if tag in ('script','style','noscript','svg'): self.hidden += 1
        if tag in ('p','div','h1','h2','h3','li','tr','br'): self.parts.append('\n')
    def handle_endtag(self, tag):
        if tag in ('script','style','noscript','svg') and self.hidden: self.hidden -= 1
    def handle_data(self, data):
        if not self.hidden: self.parts.append(data)

def fetch(source):
    name, url = source
    folder = ROOT/'data'/'unstructured'/'reference'/'retail_strategy'
    folder.mkdir(parents=True,exist_ok=True)
    record = dict(id=name,url=url,retrieved_at=datetime.now(timezone.utc).isoformat(),
                  authority='external_reference_only',audience='admin',
                  redistribution='excluded_from_customer_deliverables',
                  rights_note='Copyright retained by issuer. Local research only; no redistribution permission inferred.',
                  identity_review='pending_manual_review')
    try:
        cached = next(iter(folder.glob(name+'.pdf')),None)
        if cached:
            content=cached.read_bytes()
            record['final_url']=url
        else:
            with requests.get(url,stream=True,timeout=(20,90),headers={'User-Agent':'ShopBotResearch/1.0'}) as r:
                record.update(http_status=r.status_code,final_url=r.url)
                r.raise_for_status()
                chunks=[]
                size=0
                for chunk in r.iter_content(1024*1024):
                    size+=len(chunk)
                    if size>100*1024*1024: raise ValueError('Source exceeds 100MB research limit')
                    chunks.append(chunk)
                content=b''.join(chunks)
        is_pdf = content.lstrip().startswith(b'%PDF-')
        suffix='.pdf' if is_pdf else '.html'
        raw=folder/(name+suffix)
        raw.write_bytes(content)
        if is_pdf:
            reader=PdfReader(raw)
            sections=[]
            for i,page in enumerate(reader.pages,1):
                sections.append(f'## Trang {i}\n\n'+(page.extract_text() or ''))
            body='\n\n'.join(sections)
            record['pages']=len(reader.pages)
        else:
            extractor=VisibleText()
            extractor.feed(content.decode('utf-8',errors='replace'))
            body='\n\n'.join(line.strip() for line in ''.join(extractor.parts).splitlines() if line.strip())
            if any(s in body[:2000].lower() for s in ('just a moment','access denied','enable javascript and cookies')):
                raise ValueError('Challenge/error page, not source content')
        if len(body)<500: raise ValueError('Insufficient extracted text; needs OCR or manual download')
        # Quarantine until title/issuer have been checked. These files are not indexed automatically.
        text=f'# EXTERNAL REFERENCE — {name}\n\nNguồn: {url}\n\nChỉ dùng thử nghiệm nội bộ; không phải mục tiêu, ngân sách hoặc chính sách của shop. Danh tính tài liệu cần duyệt trước khi lập chỉ mục.\n\n'+body
        extracted=folder/(name+'.txt')
        extracted.write_text(text,encoding='utf-8')
        record.update(status='downloaded_pending_review',file=raw.name,text_file=extracted.name,
                      bytes=len(content),sha256=hashlib.sha256(content).hexdigest(),text_chars=len(body),
                      preview=body[:700])
    except Exception as e:
        record.update(status='unavailable',error=str(e))
    print(json.dumps({k:v for k,v in record.items() if k not in ('preview','rights_note')},ensure_ascii=False),flush=True)
    return record

if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(4) as pool:
        records=list(pool.map(fetch,SOURCES))
    folder=ROOT/'data'/'unstructured'/'reference'/'retail_strategy'
    (folder/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'downloaded':sum(r['status']=='downloaded_pending_review' for r in records),'total':len(records)}),flush=True)
