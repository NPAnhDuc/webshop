"""Calendar and dialogue-period constraints, independent of LLM-generated queries.

This module resolves dates only. It never chooses financial values or business actions.
"""
import re
from datetime import date
from .retrieval import normalize


def resolve_scope(question,today,previous=None):
    q=normalize(question);previous=previous or {}
    # A full date is a reference clock, not an implicit requested reporting month.
    full_dates=list(re.finditer(r'\b(\d{1,2})/(\d{1,2})/(20\d{2})\b',q))
    reference=today
    for match in full_dates:
        prefix=q[max(0,match.start()-45):match.start()]
        if not (re.search(r'hom nay|tinh (?:tu |o )?(?:ngay )?|tham chieu',prefix) or match.start()<7):continue
        try:reference=date(int(match[3]),int(match[2]),int(match[1]))
        except ValueError:continue
    for match in reversed(full_dates):q=q[:match.start()]+' '+q[match.end():]
    q=re.split(r'\b(?:khong dung|khong lay)\s+(?:bao cao\s+)?thang',q)[0]
    years=re.findall(r'\b20\d{2}\b',q)
    year=int(years[-1]) if years else reference.year
    if 'nam ngoai' in q:year=reference.year-1
    month_pairs=[]
    for match in re.finditer(r'(?<![\d/])(\d{1,2})\s*/\s*(20\d{2})\b',q):
        if 1<=int(match[1])<=12:month_pairs.append((int(match[2]),int(match[1])))
    for match in re.finditer(r'\bthang\s+(\d{1,2})(?:\s*(?:/|nam)\s*(20\d{2}))?',q):
        if 1<=int(match[1])<=12:month_pairs.append((int(match[2] or year),int(match[1])))
    quarters=[]
    for match in re.finditer(r'\b(?:quy\s*|q\s*)(iv|iii|ii|i|[1-4])\b(?:\s*(?:/|nam)\s*(20\d{2}))?',q):
        n={'i':1,'ii':2,'iii':3,'iv':4}.get(match[1],int(match[1]) if match[1].isdigit() else 0)
        quarters.append(f'{int(match[2] or year)}-Q{n}')
    previous_months=previous.get('months',[])
    if re.search(r'\bthang\s+(?:ngay\s+)?sau\s+thang\s+(?:vua|truoc)',q) and previous_months:
        y,m=map(int,previous_months[-1].split('-'));month_pairs=[(y+(m==12),m%12+1)]
    elif 'thang truoc' in q:
        month_pairs=[(reference.year-(reference.month==1),(reference.month-2)%12+1)]
    elif re.search(r'\bthang (?:nay|hien tai)\b',q):month_pairs=[(reference.year,reference.month)]
    elif not month_pairs and re.search(r'\b(?:hai thang do|cung thang do|thang do|ky do|ky vua noi)\b',q):
        month_pairs=[tuple(map(int,x.split('-'))) for x in previous_months]
    if 'quy truoc' in q:
        current=(reference.month-1)//3+1
        quarters=[f'{reference.year-(current==1)}-Q{(current-2)%4+1}']
    elif re.search(r'\bquy (?:nay|hien tai)\b',q):quarters=[f'{reference.year}-Q{(reference.month-1)//3+1}']
    months=sorted(set(f'{y:04}-{m:02}' for y,m in month_pairs))
    quarters=list(dict.fromkeys(quarters))
    return dict(months=months,quarters=quarters,reference_date=reference.isoformat())


def filter_periods(documents,scope):
    months=set(scope.get('months',[]));quarters=set(scope.get('quarters',[]))
    implied={f'{m[:4]}-Q{(int(m[-2:])-1)//3+1}' for m in months}
    result=[]
    for doc in documents:
        identifier=doc.get('document_id','');kind=doc.get('doc_type')
        if kind=='monthly_report' and (months or quarters):
            period=doc.get('period') or identifier.removeprefix('monthly-report-')
            if months and period not in months:continue
            if not months and quarters and (not re.fullmatch(r'20\d{2}-\d{2}',period) or f'{period[:4]}-Q{(int(period[-2:])-1)//3+1}' not in quarters):continue
        if kind=='sales_plan' and (quarters or implied):
            period=identifier.removeprefix('sales-plan-')
            if period not in (quarters or implied):continue
        result.append(doc)
    return result
