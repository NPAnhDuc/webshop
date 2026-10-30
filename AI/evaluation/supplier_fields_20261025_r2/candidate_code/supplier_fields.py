"""Source-field bindings for concrete supplier lookups, not answer generation.

Reject a related but different field (e.g. lead time for MOQ). No numbers,
suppliers, benchmark IDs or shop terms are encoded here.
"""
import re
from .retrieval import normalize

FIELDS={
 'supplier_moq':r'\bmoq\b|\bso luong dat(?: hang)? toi thieu\b',
 'supplier_lead_time':r'\blead\s*time\b|\bthoi gian giao hang\b|\bthoi gian giao cua nha cung cap\b',
}
CONCEPT=re.compile(r'\b(?:la gi|nghia la|giai thich|khai niem|cach tinh|tinh the nao|huong dan)\b')


def fields(text):
 return {name for name,pattern in FIELDS.items() if re.search(pattern,normalize(text))}


def evidence_fields(fragment):
 text=normalize(fragment['text']);found=fields(text)
 if 'supplier_lead_time' in found and not re.search(r'\blead\s*time\b|\bnha (?:cung cap|phan phoi)\b',text):
  # Generic delivery-to-customer time is not supplier lead time. An explicit
  # procurement source title can supply the domain, but the query cannot.
  title=normalize(fragment['source'].get('title',''))
  if not re.search(r'\b(?:nhap hang|thu mua|nha cung cap|nha phan phoi)\b',title):found.remove('supplier_lead_time')
 return found


def requested_field(part,question):
 if CONCEPT.search(normalize(question)):return None
 local=fields(part)
 if len(local)==1:return next(iter(local))
 all_fields=fields(question)
 # A lone supplier name in a comparison inherits the only requested attribute;
 # when two distinct attributes are requested, leave each part independent.
 if not local and len(all_fields)==1:return next(iter(all_fields))
 return None


def bind_supplier_evidence(question,parts,answers,fragments):
 """Return filtered advisory selections and a trace; never fill a missing fact."""
 result={key:list(value) for key,value in answers.items()};bindings=[]
 for key,part in parts.items():
  wanted=requested_field(part,question)
  if wanted is None:continue
  kept=[];rejected=[]
  for identifier in result[key]:
   fragment=fragments[identifier];source=fragment['source']
   if (source.get('authority') in ('shop_policy','synthetic_shop_document')
       and wanted in evidence_fields(fragment)):kept.append(identifier)
   else:rejected.append(identifier)
  result[key]=kept
  bindings.append(dict(part_id=key,requested_field=wanted,kept_ids=kept,rejected_ids=rejected))
 return result,bindings
