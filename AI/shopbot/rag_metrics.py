"""Deterministic admin metric answers for basic_rag: numbers always come from the shop DB.

A 4B selector picking lines from monthly reports cannot aggregate a quarter and confuses
"lãi gộp" with other lines. For an unambiguous admin question asking known metrics for
resolved calendar periods, analyze_business (the same SQL as the agent finance tool) answers
instead. Anything about targets/plans, causes, subgroups, channels, SKUs, or that already
contains an amount stays on the document path.
"""
import re
from datetime import date

from .retrieval import normalize

METRICS=[
 ('gross_profit',r'\b(?:lai gop|loi nhuan gop)\b','Lãi gộp (lợi nhuận gộp)','totals','gross_profit','VND'),
 ('operating_profit',r'\b(?:(?:loi nhuan|lai) hoat dong|loi nhuan truoc lai vay)\b','Lợi nhuận hoạt động trước lãi vay và thuế','financial','operating_profit_before_interest_tax','VND'),
 ('cost',r'\b(?:gia von|tien von)\b','Giá vốn hàng bán','totals','cost','VND'),
 ('revenue',r'\b(?:doanh thu(?: thuan)?|dt (?:thuan|sau tra hang))\b','Doanh thu thuần','totals','revenue','VND'),
 ('orders',r'\b(?:so don|don hang|luong don)\b','Số đơn hàng','financial','orders','đơn'),
 ('expenses',r'\bchi phi (?:van hanh|hoat dong)\b','Chi phí vận hành','financial','operating_expenses','VND'),
 ('refunds',r'\b(?:tien hoan|hoan tien)\b','Tiền hoàn cho khách','financial','refunds','VND'),
 ('return_units',r'\b(?:hang|san pham) (?:bi )?(?:tra ve|hoan tra)\b','Số sản phẩm hoàn trả','financial','return_units','sản phẩm'),
]
EXCLUDE=re.compile(r'\b(?:muc tieu|ke hoach|du kien|du bao|vi sao|tai sao|nguyen nhan|do dau|nhom|nganh hang|kenh|sku|san pham|'
                   r'laptop|linh kien|gaming|chien dich|campaign|so voi muc|dat bao nhieu phan tram|bao cao .* co|view|cot|bang|sql)\b')
ASK=re.compile(r'\?|\b(?:bao nhieu|bn|la gi|the nao|ra sao|cho (?:toi|minh)|tong)\b')


def metric_source(question,previous=None):
    """Source intent is separate from period/metric, and grants no capability.

    Reading an issued report must not silently become a fresh database query.
    Only a compatible follow-up inherits that preference; a new direct request
    or a product question resets it.
    """
    q=normalize(question)
    has_metric=any(re.search(m[1],q) for m in METRICS)
    explicit_report=(re.search(r'\b(?:doc|trich|theo|trong|tu)\b[^.!?;]{0,65}\bbao cao\b',q)
                     or ('bao cao' in q and re.search(r'\b(?:ghi|da neu)\b',q)))
    if explicit_report:return 'document'
    if has_metric and re.search(r'\b(?:database|du lieu goc|so cai|giao dich goc)\b',q):return 'sql'
    followup=re.search(r'^\s*(?:con\b|cung\b)|\b(?:thang do|quy do|ky do|ky vua noi)\b',q)
    period_question=re.search(r'\b(?:thang|quy)\s*(?:\d|truoc|sau|nay)',q)
    if previous=='document' and followup and (has_metric or period_question):
        return 'document'
    return 'sql'


def periods(scope):
    """Calendar bounds [start, end) for months and quarters in scope, in order."""
    out=[]
    for month in scope.get('months',[]):
        y,m=map(int,month.split('-'))
        out.append((month,date(y,m,1),date(y+(m==12),m%12+1,1)))
    for quarter in scope.get('quarters',[]):
        y,q=int(quarter[:4]),int(quarter[-1])
        out.append((quarter,date(y,3*q-2,1),date(y+(q==4),(3*q)%12+1,1)))
    return out


def metric_request(question,role,scope,source_intent=None):
    if role!='admin':return None
    if (source_intent or metric_source(question))=='document':return None
    q=normalize(question)
    # "sản phẩm hoàn trả" is a shop total, unlike "sản phẩm" as a breakdown.
    if EXCLUDE.search(q.replace('san pham hoan tra',' ')) or not ASK.search(q):return None
    # An amount already in the question is a claim to check against documents.
    if re.search(r'\d{5,}|\d+\s*(?:trieu|ty|vnd|dong|%)',q):return None
    asked=[m for m in METRICS if re.search(m[1],q)]
    # "lợi nhuận gộp" also matches "doanh thu"? no; but "lợi nhuận hoạt động" must not count as gross.
    if not asked:return None
    found=periods(scope)
    if not found or len(found)>4:return None
    return asked,found


def answer_metrics(db,asked,found,today):
    from .business_analysis import analyze_business
    lines=[];claims=[];coverage=[]
    for label,start,end in found:
        if start>=today:
            lines.append(f'Kỳ {label} chưa có dữ liệu (sau ngày tham chiếu {today.isoformat()}).');continue
        report=analyze_business(str(db),start.isoformat(),end.isoformat())
        if not report.get('monthly'):
            lines.append(f'Kỳ {label}: database chưa có giao dịch trong kỳ này.');continue
        months=[row['month'] for row in report['monthly']]
        expected=[f'{start.year+(start.month+i-1)//12}-{(start.month+i-1)%12+1:02}' for i in range((end.year-start.year)*12+end.month-start.month)]
        missing=[m for m in expected if m not in months]
        coverage.append(dict(period=label,months=months,missing=missing))
        for key,_,name,section,field,unit in asked:
            value=(report.get(section) or {}).get(field)
            if value is None:lines.append(f'{name} kỳ {label}: chưa có dữ liệu.');continue
            shown=f'{value:,}'.replace(',','.') if isinstance(value,int) else f'{value:,.0f}'.replace(',','.')
            text=f'{name} kỳ {label}: {shown} {unit}.'
            if len(expected)>1 and section=='totals':
                parts='; '.join(f"{row['month']}: {f'{row[field]:,}'.replace(',','.')}" for row in report['monthly'] if field in row)
                if parts:text+=f' Theo tháng — {parts}.'
            if missing:text+=f' Thiếu dữ liệu tháng: {", ".join(missing)}.'
            lines.append(text);claims.append(dict(text=text,evidence=[dict(chunk_id='sql-financial-ledger',quotes=[text],
                source='financial_ledger (SQL)',period=label,metric=key)]))
    lines.append('Tính trực tiếp bằng SQL trên database shop (data/business_sql/scenario_v1/shop.sqlite, dữ liệu mô phỏng); '
                 'doanh thu thuần đã trừ hoàn trả, chưa có thuế và lãi vay.')
    return '\n\n'.join(lines),claims,coverage
