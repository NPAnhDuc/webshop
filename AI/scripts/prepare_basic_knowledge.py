"""Publish reproducible catalog SPEC snapshots and short sourced glossary notes.

No prices, stocks, costs, suppliers, real shop policies or assumed storefront URLs.
"""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.store import connect
from shopbot.knowledge import KnowledgeStore
from shopbot.monthly import atomic_text

GLOSSARY={
 'oled':('OLED là gì?', 'OLED dùng các điểm ảnh tự phát sáng, không cần đèn nền truyền thống. Nói đơn giản, từng điểm ảnh có thể tự bật hoặc tắt để tạo hình ảnh.',
    'https://www.samsung.com/us/tvs/tv-buying-guide/why-oled-tvs-are-worth-it/'),
 'refresh-rate':('Tần số quét là gì?', 'Tần số quét cho biết màn hình làm mới hình ảnh bao nhiêu lần trong một giây, đo bằng Hz. Ví dụ 144 Hz là 144 lần làm mới mỗi giây. Máy còn cần CPU và GPU tạo đủ khung hình để tận dụng màn hình tần số quét cao.',
    'https://insights.samsung.com/2026/06/17/finding-the-right-refresh-rate-know-the-best-hz-for-your-needs/'),
 'nvme':('NVMe là gì?', 'NVMe là giao thức giao tiếp dành cho lưu trữ không mất dữ liệu, thường được dùng với SSD qua PCIe. Nói đơn giản, đó là cách máy tính trao đổi lệnh với ổ lưu trữ; tên NVMe không phải dung lượng ổ.',
    'https://nvmexpress.org/'),
 'ddr5':('DDR5 là gì?', 'DDR5 là một thế hệ bộ nhớ RAM, kế tiếp DDR4. Máy dùng RAM DDR4 không mặc nhiên lắp được RAM DDR5; cần kiểm tra hệ thống có hỗ trợ DDR5 trước khi mua.',
    'https://stage.crucial.com/articles/about-memory/everything-about-ddr5-ram'),
}


def publish(store,identifier,text,**metadata):
    prior=[d for d in store.records() if d['document_id']==identifier]
    latest=max(prior,key=lambda d:d['version']) if prior else None
    if latest and latest['status']=='approved' and latest['text']==text.strip():
        if not (store.folder/latest['source']).exists():atomic_text(store.folder/latest['source'],latest['text'])
        return False
    store.save(identifier,text,role='admin',approved=True,effective_from='2026-10-20',
        expected_version=latest['version'] if latest else 0,**metadata)
    return True


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--db',default=str(ROOT/'data/business_sql/scenario_v1/shop.sqlite'))
    args=parser.parse_args();store=KnowledgeStore(args.db);count=0
    with connect(args.db,readonly=True) as con:
        for product in con.execute('SELECT sku,name,category,panel,ram,battery,weight FROM products ORDER BY sku'):
            fact=con.execute('SELECT record_json FROM product_facts WHERE sku=?',(product['sku'],)).fetchone()
            if not fact:continue
            record=json.loads(fact[0]);attrs=record.get('attributes') or {};name=product['name']
            paragraphs=[f'# {name}',
                'Bản thông số tham khảo từ danh mục thử nghiệm; chưa xác minh SKU đang kinh doanh tại Việt Nam. Không phải báo giá hoặc cam kết tồn kho.',
                f"Mã danh mục: {product['sku']}. Nguồn bộ dữ liệu: {record.get('source_dataset','chưa rõ')}. Mã linh kiện: {record.get('part_number') or 'chưa có'}. Thiếu trường nào thì chưa xác nhận trường đó."]
            values=[('CPU',record.get('cpu')),('GPU',record.get('gpu')),('RAM',str(product['ram'])+' GB' if product['ram'] else None),
                ('màn hình',product['panel']),('kích thước màn hình',str(record['screen_inches'])+' inch' if record.get('screen_inches') else None),
                ('dung lượng pin',str(product['battery'])+' Wh' if product['battery'] else None),('cân nặng',str(product['weight'])+' kg' if product['weight'] else None)]
            for label,value in values:
                if value:paragraphs.append(f'{name}: {label} {value}.')
            for key,label in [('RAM Type','loại RAM'),('Installed SSD Type','chuẩn SSD'),('Display Resolution','độ phân giải'),
                ('HDMI Port','cổng HDMI'),('LAN','cổng mạng LAN'),('Operating System','hệ điều hành')]:
                if attrs.get(key):paragraphs.append(f'{name}: {label} {attrs[key]} (theo nguồn danh mục bên ngoài).')
            if attrs.get('Warranty'):
                paragraphs.append(f"{name}: thông tin bảo hành của nguồn bán lẻ bên ngoài là {attrs['Warranty']}; đây không phải chính sách bảo hành đã cam kết của shop Việt Nam.")
            count+=publish(store,'catalog-'+product['sku'],'\n\n'.join(paragraphs),title=name,doc_type='product',
                audience='customer',category=product['category'],authority='external_catalog_fixture')
    for identifier,(title,body,url) in GLOSSARY.items():
        text=f'# {title}\n\n{body}\n\nNguồn kỹ thuật: {url}\n\nBản diễn giải kỹ thuật tham khảo, không phải chính sách hoặc bài hướng dẫn đã duyệt riêng của shop.'
        count+=publish(store,'glossary-'+identifier,text,title=title,doc_type='glossary',audience='customer',authority='technical_reference')
    print(json.dumps(dict(published=count,total_versions=len(store.records()),manifest=str(store.manifest),prices_indexed=False,stocks_indexed=False)))


if __name__=='__main__':main()
