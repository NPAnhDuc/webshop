"""Conservative coverage check for campaign product eligibility in tables.

A campaign-name cell is not an eligibility field. Keep the cited table as
context, but do not report complete coverage when that schema lacks scope.
"""
import re
from .retrieval import normalize


def asks_product_scope(text):
 text=normalize(text)
 return bool(re.search(r'\b(?:ap dung (?:cho|voi|tren)|dieu kien|pham vi|doi tuong)\b',text)
             and re.search(r'\b(?:san pham|nhom|gaming|laptop|sku|dong may|tat ca|toan bo)\b',text))


def table_scope_coverage(parts,answers,fragments):
 missing=[];trace=[]
 for key,part in parts.items():
  if not asks_product_scope(part):continue
  selected=[fragments[i] for i in answers[key]]
  if not selected:continue
  tables=[]
  for fragment in selected:
   lines=[line.strip() for line in fragment['text'].splitlines() if line.strip()]
   if fragment['source'].get('doc_type')!='marketing' or len(lines)<3 or not all(line.startswith('|') for line in lines):break
   headers=[normalize(cell.strip()) for cell in lines[0].strip('|').split('|')]
   scope_columns=[i for i,h in enumerate(headers) if re.search(r'\b(?:nhom hang|san pham ap dung|doi tuong|pham vi|dieu kien|sku ap dung)\b',h)]
   has_scope=any(i<len(cells) and cells[i].strip() not in ('','-','—')
                 for line in lines[2:]
                 for cells in [[cell.strip() for cell in line.strip('|').split('|')]]
                 for i in scope_columns)
   tables.append(has_scope)
  else:
   if tables and not any(tables):
    missing.append(key)
    trace.append(dict(part_id=key,reason='campaign_table_has_no_product_eligibility_field',evidence_ids=list(answers[key])))
 return missing,trace
