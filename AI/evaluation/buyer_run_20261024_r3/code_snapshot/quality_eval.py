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

def grade(case,result):
 issues=[];sources={s['chunk_id']:s for s in result.get('sources',[])}
 def fail(cause,detail):issues.append(dict(cause=cause,detail=detail))
 if not result or result.get('basic_action')=='unavailable':fail('INFRASTRUCTURE','No reliable model result')
 if result.get('rows'):fail('UNEXPECTED_TOOL','RAG emitted tool rows')
 if case['role']=='customer' and any(s.get('audience')=='admin' for s in sources.values()):fail('PERMISSION','Private source supplied to customer')
 claims=result.get('rag',{}).get('claims',[])
 for claim in claims:
  for e in claim.get('evidence',[]):
   s=sources.get(e.get('chunk_id'))
   if s is None or not e.get('quotes') or any(q not in s['text'] for q in e.get('quotes',[])):fail('EVIDENCE_INTEGRITY','Quote absent from source')
 behavior=case['expected_behavior']
 available={v['document_id'] for v in result.get('rag',{}).get('available_fields',[])}
 if behavior=='facts':
  for gold in case['required']:
   matches=[]
   for claim in claims:
    for e in claim.get('evidence',[]):
     s=sources.get(e.get('chunk_id'),{})
     if s.get('document_id')==gold['document_id'] and s.get('version')==gold['version']:
      matches.extend(e.get('quotes',[]))
   if not any(canonical(gold['quote']) in canonical(q) for q in matches):
    fail('SELECTION_OR_CHUNKING' if gold['document_id'] in available else 'RETRIEVAL_OR_ROUTING',gold)
 elif behavior=='unknown':
  if claims:fail('WRONG_SCOPE','Unsupported requested model/period replaced with other facts')
  if result.get('rag',{}).get('answerability') not in ('none','unverified'):fail('MISSING_NOT_ACKNOWLEDGED','No unambiguous missing-evidence decision')
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
