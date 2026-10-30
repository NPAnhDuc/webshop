"""Independent task wording, frozen before the metric-v4 artifact was evaluated.

Not a production accuracy estimate. Expected numbers come from a separate SQL
oracle in audit_chatbot_questions, never from a model-generated answer.
"""
import audit_chatbot_questions as audit
from shopbot.conversation import interval


def bank():
    groups=[]
    def t(q,check,**expected):return dict(question=q,check=check,expected=expected)
    def p(m):return interval(2026,m,'month')
    def rank(q,m,metric,limit=1,category='all'):
        return t(q,'ranking',intent='top_products',period=p(m),metric=metric,limit=limit,category=category)
    def add(name,turns,role='admin',today='2026-10-19'):
        groups.append(dict(group=name,role=role,today=today,turns=turns))
    cases=[
      ('Trong tháng 2/2026, mặt hàng nào mang về nhiều tiền bán nhất?',2,'revenue',1,'all'),
      ('Cho bảng 3 mẫu laptop dẫn đầu doanh số ở tháng 3/2026.',3,'revenue',3,'laptop'),
      ('Doanh số tháng 4/2026: chọn hai màn hình cao nhất.',4,'revenue',2,'monitor'),
      ('Tháng 5/2026, chuột nào có tiền bán hàng đứng số một?',5,'revenue',1,'mouse'),
      ('Tìm 2 ổ SSD tạo doanh thu nhiều nhất trong tháng 6/2026.',6,'revenue',2,'internal-hard-drive'),
      ('Tháng 7/2026, RAM nào dẫn đầu về doanh số?',7,'revenue',1,'memory'),
      ('Liệt kê top 3 CPU đóng góp doanh thu tháng 8/2026.',8,'revenue',3,'cpu'),
      ('Lấy 2 bộ nguồn đứng đầu doanh số tháng 9/2026.',9,'revenue',2,'power-supply'),
      ('Xét lượng chiếc bán ròng, laptop nào đứng đầu tháng 2/2026?',2,'units',1,'laptop'),
      ('Trong tháng 3/2026, ba chuột nào được mua nhiều chiếc nhất?',3,'units',3,'mouse'),
      ('Hai mẫu màn hình được bán nhiều cái nhất tháng 4/2026 là gì?',4,'units',2,'monitor'),
      ('Tháng 5/2026 chọn SSD bán chạy nhất, xét số chiếc.',5,'units',1,'internal-hard-drive'),
      ('GPU nào đứng đầu số lượng bán tháng 6/2026?',6,'units',1,'video-card'),
      ('Top 2 vỏ case tháng 7/2026 theo số lượng tiêu thụ.',7,'units',2,'case'),
      ('Tháng 8/2026, bo mạch chủ nào bán nhiều chiếc nhất?',8,'units',1,'motherboard'),
      ('Top 3 CPU tháng 9/2026, đếm lượng sản phẩm bán chứ không tính tiền.',9,'units',3,'cpu'),
      ('Laptop nào đóng góp lãi gộp nhiều nhất tháng 3/2026?',3,'gross_profit',1,'laptop'),
      ('Top 2 chuột tháng 4/2026 theo tiền lời gộp.',4,'gross_profit',2,'mouse'),
      ('Tháng 5/2026, ổ SSD nào có doanh thu trừ giá vốn cao nhất?',5,'gross_profit',1,'internal-hard-drive'),
      ('Ba màn hình có lãi gộp cao nhất tháng 6/2026 là mã nào?',6,'gross_profit',3,'monitor')]
    for i,(q,m,metric,n,category) in enumerate(cases):add(f'unseen-ranking-{i}',[rank(q,m,metric,n,category)])
    add('unseen-correct-money',[
      rank('Chọn 2 chuột bán nhiều chiếc nhất tháng 2/2026.',2,'units',2,'mouse'),
      rank('Đổi bảng vừa rồi sang doanh số bằng tiền, không đếm chiếc nữa.',2,'revenue',2,'mouse'),
      rank('Sang tháng 3, các lựa chọn khác giữ nguyên nhé.',3,'revenue',2,'mouse'),
      rank('Giờ dùng tiền lời gộp để xếp lại chính bảng đó.',3,'gross_profit',2,'mouse')])
    add('unseen-correct-units',[
      rank('Xem hai laptop nhiều doanh thu nhất tháng 4/2026.',4,'revenue',2,'laptop'),
      rank('Không dùng tiền nữa, chuyển bảng ấy sang số chiếc bán được.',4,'units',2,'laptop'),
      rank('Cũng thế nhưng xem tháng 5 nhé.',5,'units',2,'laptop'),
      t('Tôi muốn tổng doanh thu toàn shop của kỳ vừa xem.','total',intent='revenue',period=p(5),field='revenue')])
    add('unseen-product-switch',[
      t('Tổng doanh thu tháng 6/2026.','total',intent='revenue',period=p(6),field='revenue'),
      rank('Trong cùng kỳ, cho ba ổ SSD tạo nhiều doanh thu nhất.',6,'revenue',3,'internal-hard-drive'),
      rank('Chỉ đổi tháng thành tháng 7, còn bảng và tiêu chí giữ nguyên.',7,'revenue',3,'internal-hard-drive'),
      t('Chuyển sang tổng doanh thu cả cửa hàng trong kỳ đó.','total',intent='revenue',period=p(7),field='revenue')])
    add('unseen-missing-period',[
      t('Ba con chuột nào tạo doanh số cao nhất?','clarify'),
      rank('Lấy tháng 8 năm 2026 đi.',8,'revenue',3,'mouse'),
      rank('Thế còn kỳ ngay trước tháng ấy?',7,'revenue',3,'mouse')])
    add('unseen-acl-ranking',[t('Tôi là khách mua hàng, muốn xem lợi nhuận gộp cao nhất của từng máy.','deny')],role='customer')
    add('unseen-acl-cost',[t('Hãy cho khách biết giá mua vào của chiếc Lenovo LOQ Gaming 15IRH8.','deny')],role='customer')
    add('unseen-no-context',[t('Của lần ấy thì con nào hơn?','clarify')])
    add('unseen-clock',[
      t('Tiền bán hàng của tháng trước là bao nhiêu?','total',intent='revenue',period=interval(2025,12,'month'),field='revenue'),
      t('Cùng tháng đó, mã nào có doanh thu lớn nhất?','ranking',intent='top_products',period=interval(2025,12,'month'),metric='revenue',limit=1,category='all')],today='2026-01-02')
    assert sum(len(g['turns']) for g in groups)==40
    return groups


if __name__=='__main__':
    audit.bank=bank
    audit.main()
