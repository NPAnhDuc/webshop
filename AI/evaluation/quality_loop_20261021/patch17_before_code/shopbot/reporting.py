"""Application reporting skill: reproducible PNGs from an authorized SQL report.

No model-generated coordinates, executable code or invented chart data. Callers
must enforce admin access before passing financial reports to the renderer.
"""
from collections import defaultdict
from datetime import date, timedelta
import hashlib
from io import BytesIO
import json


def report_fingerprint(report):
    return hashlib.sha256(json.dumps(report,ensure_ascii=False,sort_keys=True,allow_nan=False).encode()).hexdigest()


def explain_visual(report, kind='overview'):
    """Observed comparisons only; never infer a cause from a visual correlation."""
    def money(v): return f'{v:,.0f}'.replace(',','.')+' đ'
    points=[];t=report['totals'];f=report.get('financial')
    if kind=='overview' and report['monthly']:
        high=max(report['monthly'],key=lambda r:r['revenue'])
        low=min(report['monthly'],key=lambda r:r['revenue'])
        if len(report['monthly'])>1:
            points.append(f"Tháng {high['month']} có doanh thu cao nhất: {money(high['revenue'])}; tháng {low['month']} thấp nhất: {money(low['revenue'])}.")
        grouped=defaultdict(int)
        for row in report['products']:grouped[row.get('category') or 'Chưa phân nhóm']+=row['revenue']
        category=max(grouped,key=grouped.get)
        if t['revenue']:
            points.append(f"Nhóm {category} đóng góp {grouped[category]/t['revenue']*100:.2f}% doanh thu trong kỳ.")
    if f:
        value=f['operating_profit_before_interest_tax']
        points.append(f"Sau chi phí vận hành, {'lời' if value>=0 else 'lỗ'} hoạt động trước lãi vay và thuế là {money(abs(value))}.")
        if t['gross_profit']>0:
            points.append(f"Chi phí vận hành chiếm {f['operating_expenses']/t['gross_profit']*100:.2f}% lợi nhuận gộp.")
    points.append('Đây là so sánh quan sát từ SQL; cần thêm chứng cứ để kết luận nguyên nhân hoặc quyết định ngân sách.')
    return '\n\n'.join(points)


def render_report_png(report, kind='overview'):
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.ticker import FuncFormatter
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    if kind not in ('overview','financial_flow'):
        raise ValueError('Loại báo cáo chưa hỗ trợ')
    if not report['quality']['source_rows']:
        raise ValueError('Không có dữ liệu; không tạo biểu đồ bằng các số 0 giả định.')
    t=report['totals'];f=report.get('financial')
    start=report['period']['start_inclusive']
    end=(date.fromisoformat(report['period']['end_exclusive'])-timedelta(days=1)).isoformat()
    label='MÔ PHỎNG' if report['data_source']=='demo' else 'DỮ LIỆU ĐÃ NHẬP'
    blue='#2563eb';green='#059669';red='#dc2626';muted='#475569'
    def money(v): return f'{v:,.0f}'.replace(',','.')+' đ'
    def style(ax):
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.16)
        ax.set_axisbelow(True)
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:,.0f}'))
    if kind=='overview':
        fig=Figure(figsize=(14,9),dpi=150,facecolor='white');FigureCanvasAgg(fig)
        axes=fig.subplots(2,2)
        months=report['monthly'];x=list(range(len(months)))
        a=axes[0,0]
        a.plot(x,[r['revenue']/1e6 for r in months],marker='o',color=blue,label='Doanh thu')
        a.plot(x,[r['gross_profit']/1e6 for r in months],marker='o',color=green,label='Lợi nhuận gộp')
        a.set_xticks(x,[r['month'] for r in months],rotation=35,ha='right')
        a.set_title('Diễn biến theo tháng');a.set_ylabel('Triệu VND');a.legend(frameon=False);style(a)
        grouped=defaultdict(int)
        for r in report['products']: grouped[r.get('category') or 'Chưa phân nhóm']+=r['revenue']
        groups=sorted(grouped.items(),key=lambda r:r[1])
        a=axes[0,1]
        a.barh([r[0] for r in groups],[r[1]/1e6 for r in groups],color=blue)
        a.set_title('Doanh thu theo nhóm hàng');a.set_xlabel('Triệu VND')
        a.spines[['top','right']].set_visible(False)
        a=axes[1,0]
        values=[t['revenue'],t['cost'],t['gross_profit']]
        labels=['Doanh thu','Giá vốn','LN gộp'];colors=[blue,'#f59e0b',green]
        if f:
            values += [f['operating_expenses'],f['operating_profit_before_interest_tax']]
            labels += ['Chi phí\nvận hành','LN hoạt động\ntrước lãi/thuế']
            colors += ['#a855f7',green if values[-1]>=0 else red]
        bars=a.bar(range(len(values)),[v/1e6 for v in values],color=colors)
        a.set_xticks(range(len(values)),labels);a.set_title('Cấu phần kết quả kinh doanh');a.set_ylabel('Triệu VND');style(a)
        a.bar_label(bars,labels=[f'{v/1e6:,.1f}' for v in values],padding=3,fontsize=8)
        a=axes[1,1]
        channels=f.get('channels',[]) if f else []
        if channels:
            bars=a.bar([r['channel'] for r in channels],[r['net_revenue']/1e6 for r in channels],color=[blue,green,'#f59e0b'][:len(channels)])
            a.bar_label(bars,labels=[f"{r['net_revenue']/1e6:,.1f}" for r in channels],padding=3)
            a.set_title('Doanh thu sau hoàn trả theo kênh');a.set_ylabel('Triệu VND');style(a)
        else:
            a.axis('off');a.text(.05,.75,'Chưa có dữ liệu kênh bán hàng.\nKhông tự phân bổ tỷ trọng.',color=muted,fontsize=13)
        fig.suptitle(f'BÁO CÁO KINH DOANH · {label}\n{start} đến {end}',fontsize=17,fontweight='bold',y=.98)
        fig.tight_layout(rect=(.02,.10,.99,.92),h_pad=2.7,w_pad=2.4)
    else:
        fig=Figure(figsize=(16,5),dpi=150,facecolor='white');FigureCanvasAgg(fig)
        a=fig.subplots();a.set_xlim(0,16);a.set_ylim(0,5);a.axis('off')
        nodes=[('Doanh thu thuần' if f else 'Doanh thu',t['revenue'],blue),
               ('Trừ giá vốn',t['cost'],'#d97706'),('Lợi nhuận gộp',t['gross_profit'],green)]
        if f: nodes += [('Trừ chi phí\nvận hành',f['operating_expenses'],'#9333ea'),
                        ('LN hoạt động\ntrước lãi và thuế',f['operating_profit_before_interest_tax'],green if f['operating_profit_before_interest_tax']>=0 else red)]
        width=2.65;gap=(15.4-len(nodes)*width)/max(1,len(nodes)-1)
        for i,(title,value,color) in enumerate(nodes):
            left=.3+i*(width+gap)
            a.add_patch(FancyBboxPatch((left,2),width,1.6,boxstyle='round,pad=0.03',facecolor='#f8fafc',edgecolor=color,linewidth=2))
            a.text(left+width/2,3.05,title,ha='center',va='center',fontsize=12,color=muted)
            a.text(left+width/2,2.43,money(value),ha='center',va='center',fontsize=12,fontweight='bold',color=color)
            if i<len(nodes)-1:
                a.add_patch(FancyArrowPatch((left+width+.04,2.8),(left+width+gap-.05,2.8),arrowstyle='-|>',mutation_scale=16,color=muted))
        a.text(8,4.5,f'SƠ ĐỒ LỜI/LỖ · {label}',ha='center',fontsize=19,fontweight='bold')
        a.text(8,4.05,f'{start} đến {end}',ha='center',fontsize=12,color=muted)
        a.text(8,1.35,'Doanh thu − giá vốn = lợi nhuận gộp; lợi nhuận gộp − chi phí vận hành = lợi nhuận hoạt động.' if f else
               'Chưa có chi phí vận hành: chỉ xác định được lợi nhuận gộp.',ha='center',fontsize=11,color=muted)
        a.text(8,.87,'Chưa tính lãi vay và thuế thu nhập. Tiền nhập kho không được trừ lần nữa vào lợi nhuận.',ha='center',fontsize=10,color=muted)
        fig.subplots_adjust(left=.01,right=.99,top=.99,bottom=.13)
    fingerprint=report_fingerprint(report)
    fig.text(.02,.045,f"Nguồn: SQL · {report['quality']['source_rows']} dòng · báo cáo {fingerprint[:12]}",fontsize=9,color=muted)
    fig.text(.02,.017,'Giữ nguyên phạm vi và đơn vị khi phân tích. Biến động không tự chứng minh nguyên nhân hoặc hiệu quả marketing.',fontsize=9,color=muted)
    output=BytesIO()
    fig.savefig(output,format='png',dpi=150,metadata={'ReportSHA256':fingerprint,'DataSource':report['data_source'],'ChartKind':kind})
    fig.clear()
    return output.getvalue()
