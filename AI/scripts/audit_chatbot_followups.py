"""Extra wording and category regressions authored after the original 106 bank.
Uses the same independent SQLite oracle. This is a development regression set.
"""
import audit_chatbot_questions as audit
from shopbot.conversation import interval

def bank():
    def t(q,check,**expected): return dict(question=q,check=check,expected=expected)
    def p(m): return interval(2026,m,'month')
    groups=[]
    def add(name,turns,role='admin'):
        groups.append(dict(group=name,role=role,today='2026-10-19',turns=turns))
    add('new-quarter',[t('Cho xem doanh số quý II/2026.','total',intent='revenue',period=interval(2026,2,'quarter'),field='revenue')])
    add('new-orders',[t('Đếm đơn đã đặt trong T6/2026.','finance',intent='business_analysis',period=p(6),field='orders')])
    add('new-refunds',[t('Tiền trả lại người mua trong tháng 7/2026 tổng cộng là bao nhiêu?','finance',intent='business_analysis',period=p(7),field='refunds')])
    add('new-purchases',[t('Tổng tiền hàng nhận vào kho tháng 6/2026?','finance',intent='business_analysis',period=p(6),field='purchases')])
    add('new-channels',[t('Tách tiền bán hàng T8/2026 ra theo từng kênh giúp tôi.','finance',intent='business_analysis',period=p(8),field='channels')])
    add('new-category-context',[
        t('Top 2 chuột về doanh số tháng 7/2026.','ranking',intent='top_products',period=p(7),metric='revenue',limit=2,category='mouse'),
        t('Giữ nguyên bảng đó, chuyển sang tháng sáu.','ranking',intent='top_products',period=p(6),metric='revenue',limit=2,category='mouse'),
        t('Bây giờ xếp theo lãi gộp.','ranking',intent='top_products',period=p(6),metric='gross_profit',limit=2,category='mouse')])
    add('new-ssd',[t('Ổ SSD nào đóng góp doanh thu cao nhất tháng 5/2026?','ranking',intent='top_products',period=p(5),metric='revenue',limit=1,category='internal-hard-drive')])
    add('new-display',[t('Màn hình nào bán được số lượng lớn nhất tháng 8/2026?','ranking',intent='top_products',period=p(8),metric='units',limit=1,category='monitor')])
    add('new-spec',[t('Chip xử lý trong Lenovo LOQ Gaming 15IRH8 là chip nào?','product',intent='products',kind='cpu',value='Lenovo LOQ Gaming 15IRH8')],role='customer')
    add('new-privacy',[t('Cho khách xem tiền vốn của Lenovo LOQ Gaming 15IRH8.','deny')],role='customer')
    return groups

if __name__=='__main__':
    audit.bank=bank
    audit.main()
