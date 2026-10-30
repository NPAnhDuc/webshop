"""Bind table rows to identifiers the user typed verbatim (C-BTS, SKU-123).

The 4B selector can pick a neighbouring row of the same table (C-TET for a
C-BTS question). A typed code is an exact key: rows naming another code are
dropped, the row naming the asked code is kept. A validity question ("còn hạn
không") is then a date comparison against the row's own end date, never a guess.
"""
import re
from datetime import date

from .retrieval import normalize

CODE=re.compile(r'(?<![\w-])[A-Z][A-Z0-9]{0,5}-[A-Z0-9]{2,}(?![\w-])')
VALIDITY=re.compile(r'\b(?:con han|het han|con hieu luc|het hieu luc|con ap dung|da ket thuc|con chay)\b')


def _table(text):
    rows=[[c.strip() for c in line.strip().strip('|').split('|')] for line in text.splitlines()
          if line.strip().startswith('|') and not re.fullmatch(r'\|[\s|:-]+\|?',line.strip())]
    return rows[0] if len(rows)>1 else None,rows[1:] if len(rows)>1 else []


def row_code(text):
    """Code of a single-row table fragment, else None."""
    _,rows=_table(text)
    if len(rows)!=1 or not rows[0]:return None
    return rows[0][0] if CODE.fullmatch(rows[0][0]) else None


def bind_identifier_rows(question,part_ids,answers,fragments):
    codes=set(CODE.findall(question))
    if not codes:return answers,[],[]
    keyed=[k for k,f in fragments.items() if row_code(f['text']) in codes]
    if not keyed:return answers,[],[]
    bound={};bindings=[]
    for key,selected in answers.items():
        kept=[i for i in selected if not (row_code(fragments[i]['text']) and row_code(fragments[i]['text']) not in codes)]
        dropped=[i for i in selected if i not in kept]
        names=CODE.findall(part_ids[key])
        if dropped or names:
            add=[i for i in keyed if i not in kept and (not names or row_code(fragments[i]['text']) in names)]
            kept=(kept+add)[:3]
        if kept!=selected:bindings.append(dict(part=key,dropped=dropped,added=[i for i in kept if i not in selected]))
        bound[key]=kept
    if not any(i in keyed for v in bound.values() for i in v):
        first=next(iter(bound));bound[first]=(bound[first]+keyed)[:3]
        bindings.append(dict(part=first,dropped=[],added=keyed[:3]))
    return bound,bindings,keyed


def validity_check(question,part_ids,keyed,fragments,reference_date):
    """Compare each asked row's start/end column with the reference date."""
    if not keyed or not VALIDITY.search(normalize(question)):return None,set()
    reference=date.fromisoformat(reference_date)
    results=[]
    for identifier in keyed:
        header,rows=_table(fragments[identifier]['text'])
        if not header:continue
        labels=[normalize(h) for h in header];row=rows[0]
        def column(word):
            index=next((i for i,l in enumerate(labels) if word in l),None)
            if index is None or index>=len(row):return None
            try:return date.fromisoformat(row[index])
            except ValueError:return None
        end=column('ket thuc');begin=column('bat dau')
        if end is None:continue
        state='chưa bắt đầu' if begin and reference<begin else 'đã hết hạn' if reference>end else 'còn hiệu lực'
        results.append(dict(operation='compare_dates',evidence_id=identifier,code=row[0],start=begin.isoformat() if begin else None,
                            end=end.isoformat(),reference_date=reference.isoformat(),state=state,
                            source=fragments[identifier]['source'],quote=fragments[identifier]['text']))
    if not results:return None,set()
    covered={k for k,p in part_ids.items() if VALIDITY.search(normalize(p))}
    return results,covered


def render_validity(result):
    verdict={'đã hết hạn':'Không còn hạn','còn hiệu lực':'Còn hạn','chưa bắt đầu':'Chưa bắt đầu'}[result['state']]
    period=f"từ {result['start']} đến {result['end']}" if result['start'] else f"kết thúc {result['end']}"
    return f"{verdict}: {result['code']} áp dụng {period} theo nguồn; so với ngày tham chiếu {result['reference_date']} là {result['state']}."
