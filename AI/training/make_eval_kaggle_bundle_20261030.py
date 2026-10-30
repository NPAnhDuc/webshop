"""Pack what the frozen quality runner needs into training/kaggle_upload/shopbot-eval-bundle.zip.

Contents: bot code, the runner/scorers, the three evaluation banks (kb3 121/479, held-out 300,
expansion 539), the shop database and knowledge files the bot reads, the Vietnamese embedding
worker with its model, reranker and adapter, and a .env holding only model settings.
Secrets in AI/.env (ADMIN_PASSWORD, AI_INTERNAL_KEY) are never copied.
Upload the zip as a PRIVATE Kaggle dataset: the held-out bank is evaluation-only.
"""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'training/kaggle_upload/shopbot-eval-bundle.zip'
FILES=['app.py','scripts/run_quality_loop.py','scripts/run_quality_loop_kb3_20261024.py','scripts/run_heldout_20261028.py',
 'scripts/run_expansion_20261029.py','scripts/score_heldout_20261028.py','scripts/score_expansion_20261029.py',
 'scripts/vietnamese_embedding_service.py']
BANKS=['evaluation/quality_loop_20261024_kb3','evaluation/heldout_20261028','evaluation/expansion_20261029']
DIRS=['shopbot','data/business_sql','data/unstructured','data/knowledge_imports','data/product_sql','runtime/monthly',
 'runtime/embedding-cache','models/vietnamese-embedding','models/evidence_reranker_20261024',
 'training/conversation_v3/colab_artifacts/20261019/outputs']
# Same values as AI/.env minus secrets; the notebook overrides the Ollama URL and models per run.
ENV='''LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen3:4b-instruct-2507-q4_K_M
OLLAMA_NUM_GPU=99
SHOP_DATABASE=data/business_sql/scenario_v1/shop.sqlite
PLANNER_MODEL=qwen3:4b-instruct-2507-q4_K_M
PLANNER_NUM_GPU=99
CONVERSATION_MODE=semantic
VI_EMBEDDING_URL=http://127.0.0.1:8011
VI_UNDERSTANDING_URL=http://127.0.0.1:8011
RAG_SYNTHESIS='1'
RAG_ANSWER_MODE='extractive'
RAG_RERANK='0'
CHATBOT_MODE='basic_rag'
RAG_EVIDENCE_RERANK='1'
OLLAMA_SELECTOR_MODEL='shopbot-qwen-sft-20261026'
'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    paths=[ROOT/f for f in FILES]
    for bank in BANKS:paths+=[ROOT/bank/n for n in ('bank.json','gold_sources.json','metadata.json')]
    for d in DIRS:paths+=[p for p in sorted((ROOT/d).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith(('.lock','.tmp'))]
    env=dict(l.split('=',1) for l in (ROOT/'.env').read_text(encoding='utf8').splitlines() if '=' in l and not l.startswith('#'))
    for k,v in (l.split('=',1) for l in ENV.splitlines()):
        assert k=='OLLAMA_BASE_URL' or env.get(k)==v,(k,env.get(k),v)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    manifest={}
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in paths:
            rel=p.relative_to(ROOT).as_posix();z.write(p,'AI/'+rel);manifest[rel]=sha(p)
        z.writestr('AI/.env',ENV)
        z.writestr('AI/BUNDLE_MANIFEST.json',json.dumps(dict(created='2026-10-30',files=manifest),ensure_ascii=False,indent=1))
    size=OUT.stat().st_size
    print(OUT,len(manifest),'files',round(size/2**20,1),'MB')

if __name__=='__main__':main()
