"""Fixed SQL + document review, with no causal or missing-target invention."""
from collections import defaultdict
from .store import connect


def money(value):return f'{value:,.0f}'.replace(',','.')+' đ'


def review_business(path,report,documents):
    financial=report.get('financial') or {};totals=report['totals']
    categories=defaultdict(lambda:dict(revenue=0,gross_profit=0,units=0))
    for row in report['products']:
        category=categories[row['category'] or 'unknown']
        for key in category:category[key]+=row[key]
    grouped=[dict(category=k,**v) for k,v in categories.items()]
    grouped.sort(key=lambda r:(-r['revenue'],r['category']))
    period=report['period'];start=period['start_inclusive'];end=period['end_exclusive']
    target=financial.get('target_revenue')
    plan_sources=[d for d in documents if d.get('doc_type')=='sales_plan' and
                  target and str(target) in d['text']]
    # SQL targets are labelled as SQL targets unless an actual retrieved plan
    # supports this value. Never claim a policy document contains SQL facts.
    citations=[dict(source=f'SQL financial_ledger + monthly_targets; {start} ≤ ngày < {end}',kind='sql')]
    lines=[f'**Đối chiếu thực hiện và kế hoạch: {start} ≤ ngày < {end}**']
    variance=None
    if target:
        variance=totals['revenue']-target
        lines.append(f"Thực hiện **{money(totals['revenue'])}**, mục tiêu **{money(target)}**; "+
                     ('vượt' if variance>=0 else 'thiếu')+f" **{money(abs(variance))}**; đạt **{totals['revenue']/target*100:.2f}%**. Mục tiêu lấy từ bảng monthly_targets.")
        for d in plan_sources[:1]:
            lines.append(f"[Nguồn: {d['source']}, đoạn {d['section']}] ")
            citations.append(d)
    else:lines.append('Chưa có mục tiêu được ghi nhận cho kỳ này; không coi mục tiêu thiếu là bằng không.')
    if grouped:
        lines.append('Doanh thu và lãi gộp thực hiện theo nhóm:\n\n| Nhóm | Doanh thu | Lãi gộp | Số lượng ròng |\n|---|---:|---:|---:|\n'+'\n'.join(
            f"| {r['category']} | {money(r['revenue'])} | {money(r['gross_profit'])} | {r['units']} |" for r in grouped))
        lines.append('Chưa có mục tiêu riêng từng nhóm trong dữ liệu này, nên chưa thể quy phần hụt kế hoạch cho nhóm nào. Đóng góp doanh thu thực hiện không phải bằng chứng nguyên nhân.')
    priorities=sorted((r for r in report['products'] if r['gross_profit']>0),key=lambda r:(-r['gross_profit'],r['sku']))[:3]
    snapshot=financial.get('inventory_as_of');stocks={}
    if snapshot:
        with connect(path,readonly=True) as con:
            stocks={r['sku']:r['quantity'] for r in con.execute('SELECT sku,quantity FROM inventory_daily WHERE day=?',(snapshot,))}
    if priorities:
        lines.append('**Danh sách ưu tiên kiểm tra trước khi đề xuất chiến dịch/nhập hàng:**\n\n'+'\n'.join(
            f"- {r['name']}: đóng góp lãi gộp **{money(r['gross_profit'])}**; "+
            (f"tồn cuối ngày {snapshot}: **{stocks[r['sku']]}**." if r['sku'] in stocks else 'chưa có ảnh chụp tồn phù hợp.') for r in priorities))
        lines.append('Đây là ưu tiên rà soát dựa trên lãi gộp quan sát được, chưa phải dự báo. Cần kiểm tra khả năng cung ứng, giá vốn và biên sau giảm trước khi quyết định; chưa tự thay giá, tăng ngân sách hoặc đặt hàng.')
    constraints=[d for d in documents if d.get('doc_type') in ('policy','marketing','strategy')]
    return dict(answer='\n\n'.join(lines),categories=grouped,target=target,variance=variance,
                priorities=priorities,inventory_as_of=snapshot,sources=citations,
                constraints=constraints,limitations=['No category targets: cannot attribute the plan gap to categories.',
                    'Observed gross profit is not a causal effect or forecast.'])
