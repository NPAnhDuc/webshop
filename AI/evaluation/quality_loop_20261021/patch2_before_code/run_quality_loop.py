"""Frozen, resumable QA batches with no in-run repair or knowledge mutation."""
import argparse,hashlib,json,os,sys,time
from collections import Counter
from datetime import date,datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT/'.env')
os.environ['CHATBOT_MODE']='basic_rag';os.environ['RAG_PIPELINE']='grounded'
from shopbot.engine import Engine
from shopbot.knowledge import KnowledgeStore,namespace
from shopbot.monthly import atomic_json,exclusive
from shopbot.quality_eval import grade,observation
BASE=ROOT/'evaluation/quality_loop_20261021'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def code():return {str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'app.py',Path(__file__).resolve(),*sorted((ROOT/'shopbot').glob('*.py'))]}
def mine():
 tasks={}
 for path in sorted((ROOT/'runtime/rag-basic'/namespace(Path(read(BASE/'metadata.json')['database']))).glob('turns*.jsonl')):
  with path.open(encoding='utf8') as f:
   for line in f:
    try:
     record=json.loads(line)
     item=observation(record,include_full=record.get('origin')=='interactive')
    except (ValueError,TypeError,KeyError):continue
    if item:
     old=tasks.get(item['id']);item['occurrences']=(old or {}).get('occurrences',0)+1;tasks[item['id']]=item
 atomic_json(BASE/'log_review_queue.json',list(tasks.values()))
 for category in ['interactive','evaluation','unattributed']:
  items=[v for v in tasks.values() if ('interactive' if v['origin']=='interactive' else 'unattributed' if v['origin']=='unknown' else 'evaluation')==category]
  atomic_json(BASE/(category+'_review_queue.json'),items)
 return len(tasks)
def summary(out,bank,rows):
 counts=Counter(r['checks']['status'] for r in rows);issues=Counter(x['cause'] for r in rows for x in r['checks']['issues'])
 info=dict(total=len(bank),completed=len(rows),checks=dict(counts),issue_signals=dict(issues),
  pending_semantic_review=sum(r['checks']['status']=='NEEDS_REVIEW' for r in rows),
  warning='PASS_CHECKS is NOT semantic acceptance. Failing checks also need review for equivalent valid evidence. No wrong answer is inserted into knowledge.')
 atomic_json(out/'progress.json',info)
 lines=['# Vòng kiểm thử RAG',f"Đã hỏi {len(rows)}/{len(bank)} lượt. Kết quả kiểm tra tự động: {dict(counts)}.",
 'Đây chưa phải điểm đúng/nghiệm thu. Cần kiểm tra nghĩa, thông tin thừa, tự mâu thuẫn và nguồn tương đương. Rubric/gold không được đưa vào bot.',
 '| ID | Vai trò | Kiểm tra | Câu hỏi | Lỗi |','|---|---|---|---|---|']
 for row in rows:
  lines.append('| '+ ' | '.join([row['id'],row['role'],row['checks']['status'],row['question'].replace('|','/'),','.join(dict.fromkeys(x['cause'] for x in row['checks']['issues']))])+' |')
 (out/'CHECKS.md').write_text('\n\n'.join(lines[:3])+'\n\n'+'\n'.join(lines[3:])+'\n',encoding='utf8')
 atomic_json(out/'failure_queue.json',[dict(id=r['id'],role=r['role'],question=r['question'],checks=r['checks']) for r in rows if r['checks']['status']!='PASS_CHECKS'])
 return info

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--round',required=True);parser.add_argument('--split',choices=['development','validation','all'],default='development');parser.add_argument('--limit',type=int,default=0)
 args=parser.parse_args()
 if not __import__('re').fullmatch(r'[a-zA-Z0-9_-]+',args.round):raise SystemExit('Invalid round name')
 source=read(BASE/'metadata.json');db=Path(source['database']);manifest=Path(source['knowledge_manifest'])
 def data_ok():
  for path,key in [(db,'database_sha256'),(manifest,'knowledge_sha256'),(BASE/'bank.json','bank_sha256'),(BASE/'gold_sources.json','gold_sha256')]:
   assert sha(path)==source[key],f'Frozen input changed: {path.name}; create a new bank revision rather than silently rewriting gold'
 data_ok();bank=[c for c in read(BASE/'bank.json') if args.split=='all' or c['split']==args.split]
 if args.limit:
  assert args.limit>0;bank=bank[:args.limit]
 out=BASE/args.round;out.mkdir(exist_ok=True)
 config={k:os.getenv(k) for k in ['CHATBOT_MODE','RAG_PIPELINE','OLLAMA_MODEL','OLLAMA_BASE_URL','OLLAMA_NUM_GPU','VI_EMBEDDING_URL','RAG_RERANK']}
 config['split']=args.split;config['limit']=args.limit
 frozen=dict(code=code(),config=config,ids=[c['id'] for c in bank],source=source,created=datetime.now(timezone.utc).isoformat())
 if (out/'metadata.json').exists():
  prior=read(out/'metadata.json');assert all(prior[k]==frozen[k] for k in ['code','config','ids','source']),'Round code/config changed; use a new round name';frozen=prior
 else:atomic_json(out/'metadata.json',frozen)
 os.environ['RAG_LOG_ORIGIN']='quality_loop:'+args.round
 rows=read(out/'results.json') if (out/'results.json').exists() else []
 assert [r['id'] for r in rows]==[c['id'] for c in bank[:len(rows)]]
 memories={r['conversation']:r['result'].get('profile') for r in rows}
 engine=Engine(db,today=date.fromisoformat(source['today']));infrastructure=0
 for c in bank[len(rows):]:
  assert code()==frozen['code'],'Code changed during round; stop and start new revision'
  data_ok();start=time.monotonic()
  try:result=engine.ask(c['question'],c['role'],memories.get(c['conversation']))
  except Exception as exc:result=dict(answer='',error=type(exc).__name__+': '+str(exc)[:250])
  memories[c['conversation']]=result.get('profile');checks=grade(c,result)
  row=dict(id=c['id'],role=c['role'],question=c['question'],conversation=c['conversation'],split=c['split'],topic=c['topic'],seconds=round(time.monotonic()-start,3),checks=checks,result=result)
  rows.append(row);atomic_json(out/'results.json',rows);summary(out,bank,rows)
  print(c['id'],checks['status'],row['seconds'],flush=True)
  infrastructure=infrastructure+1 if any(i['cause']=='INFRASTRUCTURE' for i in checks['issues']) else 0
  if infrastructure>=3:raise RuntimeError('Three infrastructure failures: stop rather than label unavailable model as knowledge failure')
 data_ok();assert code()==frozen['code'];atomic_json(out/'integrity.json',dict(unchanged=True,cases=len(rows),bank_sha256=source['bank_sha256'],code=frozen['code']))
 info=summary(out,bank,rows);info['log_tasks']=mine();print(json.dumps(info,ensure_ascii=False),flush=True)
if __name__=='__main__':
 try:
  with exclusive(BASE/'runner.lock'):main()
 except OSError as exc:
  if getattr(exc,'winerror',None) in (33,36) or exc.errno in (11,13):raise SystemExit('Another quality runner owns the lock; do not run a second model batch')
  raise
