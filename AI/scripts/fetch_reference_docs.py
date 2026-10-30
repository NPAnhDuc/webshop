"""Fetch a small allowlist of public business guides with robots and provenance."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from shopbot.layout import UNSTRUCTURED

SOURCES = {
    'business-plan': 'https://legacy.sba.gov/business-guide/plan-your-business/write-your-business-plan',
    'marketing-sales': 'https://legacy.sba.gov/business-guide/manage-your-business/marketing-sales',
    'market-research': 'https://legacy.sba.gov/business-guide/plan-your-business/market-research-competitive-analysis',
}
AGENT = 'ShopBotResearch/1.0'


class MainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = False
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == 'main': self.in_main = True
        if self.in_main and tag in ('script', 'style'): self.hidden += 1
        if self.in_main and tag in ('p', 'h1', 'h2', 'h3', 'li', 'br'): self.parts.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style') and self.hidden: self.hidden -= 1
        if tag == 'main': self.in_main = False

    def handle_data(self, data):
        if self.in_main and not self.hidden: self.parts.append(data)


def main():
    folder = UNSTRUCTURED / 'reference' / 'sba'
    folder.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers['User-Agent'] = AGENT
    robots = session.get('https://legacy.sba.gov/robots.txt', timeout=30)
    robots.raise_for_status()
    parser = RobotFileParser()
    parser.parse(robots.text.splitlines())
    records = []
    for name, url in SOURCES.items():
        if not parser.can_fetch(AGENT, url): raise ValueError('Disallowed by robots: ' + name)
        response = session.get(url, timeout=45)
        response.raise_for_status()
        if urlsplit(response.url).hostname != 'legacy.sba.gov': raise ValueError('Unexpected redirect')
        extractor = MainText()
        extractor.feed(response.text)
        body = '\n\n'.join(line.strip() for line in ''.join(extractor.parts).splitlines() if line.strip())
        if len(body) < 500: raise ValueError('Unexpected/empty article: ' + name)
        raw = folder / (name + '.html')
        raw.write_bytes(response.content)
        text = ('# EXTERNAL REFERENCE — NOT SHOP POLICY\n\n'
                'Nguồn tham khảo phương pháp kinh doanh của U.S. Small Business Administration. '
                'Không phải kế hoạch, ngân sách hoặc chính sách được shop phê duyệt.\n\n'
                f'Nguồn: {url}\n\n' + body)
        (folder / (name + '.md')).write_text(text, encoding='utf-8')
        history = folder/'history'/datetime.now(ZoneInfo('Asia/Bangkok')).strftime('%Y-%m')
        history.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(response.content).hexdigest()
        (history/(name+'-'+digest[:16]+'.md')).write_text(text, encoding='utf-8')
        records.append({'name': name, 'url': url, 'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'sha256': hashlib.sha256(response.content).hexdigest(), 'bytes': len(response.content),
                        'authority': 'external_reference_only', 'audience': 'admin',
                        'rights_note': 'Public SBA guide; retain attribution; third-party material may have separate rights.'})
    (folder / 'manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'downloaded_documents': len(records), 'folder': str(folder)}))
    return records


if __name__ == '__main__': main()
