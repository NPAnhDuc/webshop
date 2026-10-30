"""Download official sources for the 24/10 knowledge gaps found by the buyer bank.

Reuses fetch_one from collect_technology_knowledge (robots.txt check, no auth bypass,
challenge-page rejection, 15 MB limit, sha256). Never touches the chatbot/index/DB.
Gaps: integrated vs discrete GPU, VRAM vs RAM, CPU naming/generation, 80 PLUS, full SSD.
The shop-internal question (which warranty document wins) has no external source.
"""
import concurrent.futures
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('collector',ROOT/'scripts/collect_technology_knowledge.py')
collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
PACK=ROOT/'data/unstructured/technology_20261024_gaps'
SOURCES=[
 ('intel-integrated-discrete','technology','https://www.intel.com/content/www/us/en/support/articles/000057824/graphics.html'),
 ('intel-shared-video-memory','technology','https://www.intel.com/content/www/us/en/support/articles/000041253/graphics.html'),
 ('nvidia-vram-explained','technology','https://www.nvidia.com/en-in/geforce/news/rtx-40-series-vram-video-memory-explained/'),
 ('intel-core-generation','technology','https://www.intel.com/content/www/us/en/support/articles/000032203/processors/intel-core-processors.html'),
 ('intel-core-names-numbers','technology','https://www.intel.com/content/www/us/en/support/articles/000100149/processors/intel-core-processors.html'),
 ('clearesult-80plus-program','technology','https://www.clearesult.com/80plus/program-details'),
 ('clearesult-80plus-faq','technology','https://www.clearesult.com/insights/answering-your-80-PLUS-questions'),
 ('kingston-overprovisioning','technology','https://www.kingston.com/en/blog/pc-performance/overprovisioning'),
 ('kingston-full-ssd','technology','https://www.kingston.com/en/blog/pc-performance/full-ssd-solutions'),
 # Kingston returns 403 to scripts and the web tool; Samsung's papers cover the same mechanism.
 ('samsung-op-whitepaper','technology','https://download.semiconductor.samsung.com/resources/white-paper/S190311-SAMSUNG-Memory-Over-Provisioning-White-paper.pdf'),
 ('samsung-op-845dc','technology','https://download.semiconductor.samsung.com/resources/others/Samsung_SSD_845DC_04_Over-provisioning.pdf'),
]


def main():
    collector.PACK=PACK
    for folder in ['raw','extracted','curated','robots']:(PACK/folder).mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(collector.fetch_one,SOURCES))
    (PACK/'manifest.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps([{k:r.get(k) for k in ('id','status','http_status','bytes','characters','error')} for r in results],ensure_ascii=False,indent=1))


if __name__=='__main__':main()
