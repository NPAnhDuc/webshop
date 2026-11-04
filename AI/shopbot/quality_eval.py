"""Narrow source-bound checks. Semantic correctness always needs separate review."""
import hashlib,re
from .rag_answer import canonical

def select_cases(bank,split,limit=0,requested=None):
 allowed=[c for c in bank if split=='all' or c['split']==split]
 if requested is not None:
  if limit or not requested:raise ValueError('IDs selection must be nonempty and cannot be combined with limit')
  wanted=set(requested)
  if not wanted<={c['id'] for c in allowed}:raise ValueError('Unknown ID or ID outside selected split')
  groups={c['conversation'] for c in allowed if c['id'] in wanted}
  return [c for c in allowed if c['conversation'] in groups]
 if limit<0:raise ValueError('Negative limit')
 return allowed[:limit] if limit else allowed

def sql_figure_matches(gold,claims):
 # A direct metric comes from shop.sqlite and cites no report; it counts when the same month gives the report's figure.
 period=re.fullmatch(r'monthly-report-(\d{4}-\d{2})',gold['document_id'])
 value=re.search(r':\s*(-?\d+)\b',gold['quote'])
 if not period or not value:return False
 for claim in claims:
  shown=re.match(r'\s*(-?\d[\d.]*)',claim.get('text','').partition(':')[2])
  if shown and shown[1].replace('.','')==value[1] and any(e.get('chunk_id')=='sql-financial-ledger' and e.get('period')==period[1] for e in claim.get('evidence',[])):return True
 return False

def grade(case,result):
 issues=[];sources={s['chunk_id']:s for s in result.get('sources',[])}
 def fail(cause,detail):issues.append(dict(cause=cause,detail=detail))
 if not result or result.get('basic_action')=='unavailable':fail('INFRASTRUCTURE','No reliable model result')
 behavior=case['expected_behavior']
 # A live_product answer may read one product's row; anything wider is a tool result.
 rows=result.get('rows') or []
 if rows and behavior!='catalog_pick' and not (behavior=='live_product' and len(rows)==1):fail('UNEXPECTED_TOOL','RAG emitted tool rows')
 if case['role']=='customer' and any(s.get('audience')=='admin' for s in sources.values()):fail('PERMISSION','Private source supplied to customer')
 claims=result.get('rag',{}).get('claims',[])
 for claim in claims:
  for e in claim.get('evidence',[]):
   s=sources.get(e.get('chunk_id'))
   if s is None or not e.get('quotes') or any(q not in s['text'] for q in e.get('quotes',[])):fail('EVIDENCE_INTEGRITY','Quote absent from source')
 available={v['document_id'] for v in result.get('rag',{}).get('available_fields',[])}
 if behavior=='facts':
  for gold in case['required']:
   accepted=[gold,*gold.get('any_of',[])]
   matched=False
   for option in accepted:
    matches=[]
    for claim in claims:
     for e in claim.get('evidence',[]):
      s=sources.get(e.get('chunk_id'),{})
      if s.get('document_id')==option['document_id'] and s.get('version')==option['version']:
       matches.extend(e.get('quotes',[]))
    if any(canonical(option['quote']) in canonical(q) for q in matches):
     matched=True
     break
   available_gold={option['document_id'] for option in accepted}
   if not matched and not sql_figure_matches(gold,claims):
    fail('SELECTION_OR_CHUNKING' if available_gold & available else 'RETRIEVAL_OR_ROUTING',gold)
 elif behavior=='unknown':
  if claims:fail('WRONG_SCOPE','Unsupported requested model/period replaced with other facts')
  if result.get('rag',{}).get('answerability') not in ('none','unverified'):fail('MISSING_NOT_ACKNOWLEDGED','No unambiguous missing-evidence decision')
 elif behavior=='catalog_pick':
  # Gold: every in-stock product of the category inside the budget band (shop.sqlite).
  gold=case['expected_catalog']['in_stock'];names=[r.get('name') for r in result.get('rows') or []]
  if result.get('basic_action')!='answer':fail('ROUTING',dict(expected='answer',actual=result.get('basic_action')))
  elif [n for n in names if n not in gold]:fail('CATALOG',dict(outside_band_or_stock=[n for n in names if n not in gold]))
  elif len(names)!=min(3,len(gold)):fail('CATALOG',dict(expected=min(3,len(gold)),listed=len(names)))
 elif behavior!='semantic':
  if result.get('basic_action')!=behavior:fail('ROUTING',dict(expected=behavior,actual=result.get('basic_action')))
 return dict(status='FAIL_CHECKS' if issues else 'NEEDS_REVIEW' if behavior=='semantic' else 'PASS_CHECKS',
  issues=issues,note='Automated source/action checks only. Not a final semantic PASS; review relevance, contradictions, omissions and equivalent evidence.')

def redact(text):
 text=re.sub(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}','[email]',text)
 text=re.sub(r'(?<!\w)(?:\+84|0)[\d .-]{8,14}\b','[phone]',text)
 return re.sub(r'(?i)(password|mat khau|mật khẩu|api[_ -]?key|bearer)\s*[:=]?\s*\S+',r'\1 [redacted]',text)

def observation(row,include_full=False):
 # Refusal can be correct. A log signal is a review task, never a new fact.
 if not (include_full and row.get('status')=='full') and row.get('status') not in ('none','partial','unverified') and row.get('action') not in ('clarify','outside','unavailable'):return None
 question=redact(row.get('question',''))[:2000]
 key=hashlib.sha256((row.get('role','')+'\n'+question+'\n'+row.get('origin','unknown')).encode()).hexdigest()
 return dict(id=key,question=question,role=row.get('role'),origin=row.get('origin','unknown'),last_seen=row.get('time'),
  status='REVIEW_REQUIRED',signal=row.get('status') or row.get('action'),
  rule='Verify source and intended behavior. Do not label correct refusal FAIL or publish model answers as knowledge.')
