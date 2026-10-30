from .monthly import local_today
from .retrieval import normalize
import re

def compare_periods(question,tools):
    q=normalize(question)
    y=re.search(r'\b(20\d{2})\b',q)
    year=int(y[1]) if y else local_today().year
    if len(set(re.findall(r'\b20\d{2}\b',q)))>1: return None
    quarters=re.findall(r'quy\s*([1-4])\b',q)
    months=re.findall(r'thang\s*(\d{1,2})\b',q)
    def interval(n,quarter=False):
        m=(n-1)*3+1 if quarter else n
        if not 1<=m<=12: raise ValueError('Tháng không hợp lệ')
        end=m+(3 if quarter else 1)
        return f'{year}-{m:02d}-01',f'{year+1}-01-01' if end>12 else f'{year}-{end:02d}-01'
    if len(quarters)==2:
        first,second=[interval(int(n),True) for n in quarters]
        labels=[f'{year}-Q{n}' for n in quarters]
    elif len(months)==2 and all(1<=int(n)<=12 for n in months):
        first,second=[interval(int(n)) for n in months]
        labels=[f'{year}-{int(n):02d}' for n in months]
    else: return None
    a,b=tools.revenue(*first),tools.revenue(*second)
    if not a or not b: return None
    totals=[sum(v['revenue'] for v in rows) for rows in (a,b)]
    diff=totals[0]-totals[1]
    percent=round(diff/totals[1]*100,2) if totals[1] else None
    rows=[{'month':label,'revenue':total,'profit':sum(v['profit'] for v in values)} for label,total,values in zip(labels,totals,(a,b))]
    return {'rows':rows,'difference':diff,'percent':percent,'labels':labels,'sources':[{'source':f'SQLite sales — mô phỏng; {first} so với {second}'}]}
