import sqlite3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / 'AI' / 'data' / 'business_sql' / 'scenario_v1'
SHOP_DB = SCENARIO_DIR / 'shop.sqlite'
DOCS_MANIFEST = SCENARIO_DIR / 'documents' / 'manifest.json'
PRODUCT_SQL_DB = ROOT / 'AI' / 'data' / 'product_sql' / 'products.sqlite'
BACKEND_DATA_JSON = ROOT / 'backend' / 'data' / 'store_state.json'
SEED_DATA_TS = ROOT / 'backend' / 'src' / 'db' / 'seedData.ts'

print(f"Syncing from Scenario V1: {SHOP_DB}...")
con_shop = sqlite3.connect(SHOP_DB)
con_shop.row_factory = sqlite3.Row

con_prod = sqlite3.connect(PRODUCT_SQL_DB)
con_prod.row_factory = sqlite3.Row

# Build image lookup map from products.sqlite
img_map = {}
category_img_fallbacks = {}
for r in con_prod.execute("SELECT i.product_id, i.local_path, p.category_id FROM product_images i JOIN products p ON p.product_id = i.product_id WHERE i.local_path IS NOT NULL"):
    p_id = r['product_id']
    cat = r['category_id']
    loc = r['local_path']
    # loc looks like ../product_images/images/laptop/xxx.jpg
    if loc.startswith('../product_images/images/'):
        clean_path = '/images/' + loc.replace('../product_images/images/', '')
        img_map[p_id] = clean_path
        if cat not in category_img_fallbacks:
            category_img_fallbacks[cat] = clean_path

print(f"Loaded {len(img_map)} exact image paths, and category fallbacks.")

# Category definitions
CAT_MAP = {
    'case': {'id': 'cat-case', 'slug': 'case', 'name': 'Vỏ Case'},
    'cpu': {'id': 'cat-cpu', 'slug': 'cpu', 'name': 'CPU - Vi xử lý'},
    'internal-hard-drive': {'id': 'cat-ssd', 'slug': 'ssd', 'name': 'Ổ cứng SSD'},
    'laptop': {'id': 'cat-laptop', 'slug': 'laptop', 'name': 'Laptop'},
    'memory': {'id': 'cat-ram', 'slug': 'ram', 'name': 'RAM - Bộ nhớ trong'},
    'monitor': {'id': 'cat-monitor', 'slug': 'monitor', 'name': 'Màn hình'},
    'motherboard': {'id': 'cat-mainboard', 'slug': 'mainboard', 'name': 'Mainboard - Bo mạch chủ'},
    'mouse': {'id': 'cat-accessories', 'slug': 'accessories', 'name': 'Chuột & Phụ kiện'},
    'power-supply': {'id': 'cat-psu', 'slug': 'psu', 'name': 'Nguồn máy tính PSU'},
    'video-card': {'id': 'cat-vga', 'slug': 'vga', 'name': 'Card đồ họa VGA'},
}

def to_slug(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text

def extract_brand(name, category):
    name_upper = name.upper()
    for b in ['ASUS', 'LENOVO', 'DELL', 'APPLE', 'ACER', 'MSI', 'HP', 'INTEL', 'AMD', 'CORSAIR', 'KINGSTON', 'SAMSUNG', 'WESTERN DIGITAL', 'CRUCIAL', 'G.SKILL', 'TEAMGROUP', 'AOC', 'LOGITECH', 'RAZER', 'NZXT', 'DEEPCOOL', 'MONTECH', 'GIGABYTE', 'THERMALRIGHT', 'LIAN LI']:
        if b in name_upper:
            if b == 'WESTERN DIGITAL': return 'Western Digital'
            if b == 'G.SKILL': return 'G.Skill'
            if b == 'TEAMGROUP': return 'TEAMGROUP'
            return b.title() if b not in ['ASUS', 'MSI', 'HP', 'AMD', 'AOC', 'NZXT'] else b
    return 'Chính hãng'

# 1. READ PRODUCTS & PRODUCT_FACTS
prod_rows = con_shop.execute("""
    SELECT p.*, f.record_json, f.standard_cost, f.segment
    FROM products p
    LEFT JOIN product_facts f ON f.sku = p.sku
""").fetchall()

products = []
brands_dict = {}
inventory = {}

for r in prod_rows:
    sku = r['sku']
    cat_raw = r['category']
    cat_info = CAT_MAP.get(cat_raw, {'id': f'cat-{cat_raw}', 'slug': cat_raw, 'name': cat_raw})
    name = r['name']
    brand_name = extract_brand(name, cat_raw)
    brand_slug = to_slug(brand_name)
    brand_id = f'b-{brand_slug}'
    brands_dict[brand_slug] = {'id': brand_id, 'name': brand_name, 'slug': brand_slug}

    # Image determination
    if sku in img_map:
        image_url = img_map[sku]
    else:
        # Fallback to category image
        image_url = category_img_fallbacks.get(cat_raw, '/images/laptop/apple-macbook-air-late-2020-15bf0f5ed3d4.jpg')

    price = int(r['price'])
    cost_price = int(r['standard_cost']) if r['standard_cost'] else int(price * 0.8)
    original_price = int(round(price * 1.12 / 10000.0) * 10000)
    discount_percent = int(round((1 - price / original_price) * 100)) if original_price > price else 0
    stock_qty = int(r['stock']) if r['stock'] is not None else 10

    # Parse facts/attributes
    attrs = {}
    record_json_raw = r['record_json']
    if record_json_raw:
        try:
            facts = json.loads(record_json_raw)
            attrs = facts.get('attributes', {})
        except Exception:
            pass

    specs = {}
    highlights = []

    if cat_raw == 'laptop':
        specs['cpu_model'] = attrs.get('Processor Model', 'Intel Core / AMD Ryzen')
        specs['cpu_brand'] = 'Apple' if 'Apple' in str(specs['cpu_model']) or 'MacBook' in name else ('Intel' if 'Intel' in str(specs['cpu_model']) or 'Core' in str(specs['cpu_model']) or 'i5' in str(specs['cpu_model']) or 'i7' in str(specs['cpu_model']) or '13' in str(specs['cpu_model']) or '12' in str(specs['cpu_model']) else 'AMD')
        specs['ram_gb'] = int(r['ram']) if r['ram'] else (16 if '16GB' in name or 'Legion' in name or 'LOQ' in name else 8)
        specs['ram_type'] = 'DDR5' if ('DDR5' in str(attrs.get('RAM Type', '')) or 'Legion' in name or 'LOQ' in name) else 'DDR4'
        specs['screen_inch'] = float(attrs.get('Display Size (Inch)', 15.6)) if attrs.get('Display Size (Inch)') else 15.6
        specs['gpu_model'] = attrs.get('Graphics Chipset', 'Đồ họa chuyên dụng' if 'Gaming' in name or 'Nitro' in name or 'TUF' in name or 'Victus' in name or 'Legion' in name or 'LOQ' in name else 'Đồ họa tích hợp')
        specs['gpu_type'] = 'discrete' if ('RTX' in str(specs['gpu_model']) or 'Gaming' in name or 'Nitro' in name or 'TUF' in name or 'Victus' in name or 'Legion' in name or 'LOQ' in name) else 'integrated'
        specs['resolution'] = attrs.get('Display Resolution', '1920x1080 (FHD)')
        specs['panel'] = 'IPS'
        if 'OLED' in name or 'Retina' in str(attrs.get('Display Type', '')):
            specs['panel'] = 'OLED' if 'OLED' in name else 'IPS'
        specs['storage_gb'] = 512
        specs['storage_type'] = 'NVMe'
        specs['warranty_months'] = 24
        specs['demand'] = ['gaming', 'design_graphics'] if specs['gpu_type'] == 'discrete' else ['study_office', 'thin_light']

        highlights = [
            f"Màn hình {specs['screen_inch']} inch {specs['resolution']} sắc nét",
            f"Bộ vi xử lý {specs['cpu_model']} mạnh mẽ",
            f"Đồ họa {specs['gpu_model']}",
            f"RAM {specs['ram_gb']}GB {specs['ram_type']} & SSD 512GB NVMe tốc độ cao"
        ]

    elif cat_raw == 'cpu':
        specs['socket'] = 'AM5' if 'Ryzen' in name and ('9' in name or '7' in name or '5 7' in name or '5 9' in name) else 'LGA1700'
        specs['cores'] = attrs.get('core_count', 8 if 'Ryzen 7' in name or 'i7' in name else (14 if '14600' in name else 6))
        specs['tdp_w'] = attrs.get('tdp', 105 if 'X' in name or 'K' in name else 65)
        specs['has_igpu'] = 'F' not in name
        highlights = [
            f"Socket {specs['socket']}, công suất TDP {specs['tdp_w']}W",
            f"Số nhân xử lý: {specs['cores']} nhân đa nhiệm vượt trội",
            "Tương thích hoàn hảo tản nhiệt và bo mạch chủ đời mới"
        ]

    elif cat_raw == 'motherboard':
        specs['socket'] = 'AM5' if ('B650' in name or 'B850' in name or 'X670' in name) else ('LGA1700' if ('B760' in name or 'Z790' in name) else 'AM4')
        specs['form_factor'] = 'mATX' if ('M' in name and 'B550M' in name) else 'ATX'
        specs['ram_type'] = 'DDR5' if ('B650' in name or 'B850' in name or 'B760' in name or 'Z790' in name) else 'DDR4'
        specs['ram_slots'] = 4
        specs['supported_form_factors'] = [specs['form_factor']]
        highlights = [
            f"Hỗ trợ CPU Socket {specs['socket']} chuẩn {specs['form_factor']}",
            f"Hỗ trợ RAM {specs['ram_type']} tốc độ cao với 4 khe cắm",
            "Tích hợp WiFi tốc độ cao và cổng xuất hình cao cấp"
        ]

    elif cat_raw == 'memory':
        specs['ram_type'] = 'DDR4' if ('DDR4' in name or 'Ripjaws' in name) else 'DDR5'
        specs['ram_gb'] = 32
        specs['ram_speed_mhz'] = 3200 if specs['ram_type'] == 'DDR4' else 6000
        highlights = [
            f"Dung lượng 32GB chuẩn {specs['ram_type']} Bus {specs['ram_speed_mhz']}MHz",
            "Độ trễ tối ưu, tản nhiệt nhôm cao cấp",
            "Hỗ trợ Intel XMP 3.0 và AMD EXPO ép xung ổn định"
        ]

    elif cat_raw == 'video-card':
        specs['vram_gb'] = 16 if '16G' in name else 8
        specs['length_mm'] = 204 if 'INSPIRE' in name else 307
        specs['tgp_w'] = 160 if '4060' in name else 220
        highlights = [
            f"VRAM {specs['vram_gb']}GB GDDR6 hiệu năng đỉnh cao",
            f"Chiều dài VGA {specs['length_mm']}mm phù hợp đa số case",
            "Hỗ trợ Ray Tracing thế hệ mới và DLSS 3.5 siêu mượt"
        ]

    elif cat_raw == 'internal-hard-drive':
        specs['storage_gb'] = 2000 if ('2TB' in name or '990' in name or 'SN850' in name) else 1000
        specs['storage_type'] = 'NVMe'
        specs['interface'] = 'NVMe M.2'
        highlights = [
            f"Dung lượng {specs['storage_gb']}GB chuẩn NVMe M.2 PCIe Gen 4x4",
            "Tốc độ đọc ghi cực nhanh",
            "Bảo hành chính hãng 5 năm an tâm dữ liệu"
        ]

    elif cat_raw == 'power-supply':
        specs['psu_watt'] = 750 if '750' in name else 650
        specs['modular'] = 'full' if 'RM' in name else 'non'
        specs['certification'] = '80 Plus Gold' if 'RM' in name else '80 Plus Bronze'
        highlights = [
            f"Công suất thực {specs['psu_watt']}W đạt chuẩn {specs['certification']}",
            f"Thiết kế {specs['modular']} modular dây cáp gọn gàng",
            "Linh kiện tụ điện Nhật Bản bền bỉ, an toàn điện áp"
        ]

    elif cat_raw == 'case':
        specs['supported_form_factors'] = ['ATX', 'mATX', 'ITX']
        specs['max_gpu_length_mm'] = 360
        specs['max_cooler_height_mm'] = 170
        highlights = [
            "Hỗ trợ bo mạch chủ ATX, Micro-ATX, Mini-ITX",
            "Mặt kính cường lực cao cấp, tối ưu luồng gió Airflow",
            "Không gian rộng rãi lắp card đồ họa dài tới 360mm"
        ]

    elif cat_raw == 'monitor':
        specs['screen_inch'] = 27 if '27' in name else 24
        specs['panel'] = 'IPS'
        specs['refresh_hz'] = 180 if '180' in name or '24G4' in name else 165
        specs['resolution'] = '2560 x 1440 (2K)' if specs['screen_inch'] == 27 else '1920 x 1080 (FHD)'
        highlights = [
            f"Kích thước {specs['screen_inch']} inch độ phân giải {specs['resolution']}",
            f"Tần số quét cao {specs['refresh_hz']}Hz chuyên game mượt mà",
            f"Tấm nền {specs['panel']} góc nhìn rộng 178 độ chuẩn màu"
        ]

    elif cat_raw == 'mouse':
        highlights = [
            "Cảm biến quang học chính xác cao",
            "Kết nối độ trễ siêu thấp",
            "Thiết kế công thái học nhẹ nhàng"
        ]

    slug = to_slug(name)
    variant_id = f"var-{sku[:8]}-1"
    variants = [
        {
            'id': variant_id,
            'productId': sku,
            'sku': f"SKU-{sku[:8].upper()}",
            'name': 'Bản tiêu chuẩn chính hãng',
            'price': price,
            'originalPrice': original_price,
            'costPrice': cost_price,
            'status': 'active'
        }
    ]

    product_item = {
        'id': sku,
        'categoryId': cat_info['id'],
        'categorySlug': cat_info['slug'],
        'brandId': brand_id,
        'brandName': brand_name,
        'name': name,
        'slug': slug,
        'description': f"{name} chính hãng phân phối tại Việt Nam, bảo hành đầy đủ, hỗ trợ trả góp 0%, tư vấn thông số kỹ thuật chuẩn.",
        'highlights': highlights,
        'imageUrl': image_url,
        'images': [image_url],
        'price': price,
        'originalPrice': original_price,
        'discountPercent': discount_percent,
        'isHot': (cat_raw == 'laptop' and ('Legion' in name or 'LOQ' in name or 'Air' in name or 'TUF' in name)) or ('9800X3D' in name or '990 Pro' in name),
        'isNew': '2024' in name or '2025' in name or '9800X3D' in name or '9600X' in name or '5060' in name,
        'hasInstallment0': True,
        'status': 'active',
        'createdAt': '2026-10-19T08:00:00Z',
        'variants': variants,
        'specs': specs,
        'stockStatus': {
            'status': 'in_stock' if stock_qty > 3 else ('low_stock' if stock_qty > 0 else 'out_of_stock'),
            'availableQty': stock_qty
        }
    }
    products.append(product_item)

    inventory[variant_id] = {
        'variantId': variant_id,
        'productId': sku,
        'sku': f"SKU-{sku[:8].upper()}",
        'quantity': stock_qty,
        'reserved': 0,
        'costPrice': cost_price,
        'updatedAt': '2026-10-19T11:15:00Z'
    }

# Sort products
products.sort(key=lambda p: (0 if p['categorySlug'] == 'laptop' else 1, p['categorySlug'], p['name']))
print(f"Processed {len(products)} products and inventory records.")

categories = list(CAT_MAP.values())
brands = list(brands_dict.values())
brands.sort(key=lambda b: b['name'])

# 2. READ STRATEGIC DOCUMENTS
print(f"Reading documents from {DOCS_MANIFEST}...")
with open(DOCS_MANIFEST, 'r', encoding='utf-8') as f:
    docs_raw = json.load(f)

documents = []
for d in docs_raw:
    doc_id = d['document_id']
    title = d['title']
    content = d['text']
    doc_type = d.get('doc_type', 'strategy')
    if doc_type == 'strategy':
        mapped_type = 'sales_plan'
    elif doc_type == 'sales_plan':
        mapped_type = 'sales_plan'
    elif doc_type == 'policy':
        mapped_type = 'policy'
    elif doc_type == 'marketing':
        mapped_type = 'marketing'
    elif doc_type == 'procurement':
        mapped_type = 'management_report'
    else:
        mapped_type = 'management_report'

    # Extract period from doc_id or title
    period = '2026'
    m = re.search(r'(202[56](?:-Q[1-4]|-0[1-9]|-1[0-2]))', doc_id)
    if m:
        period = m.group(1)

    # Chunk content by markdown headers ##
    chunks = []
    sections = re.split(r'\n(?=## )', content)
    for idx, sec in enumerate(sections):
        lines = sec.strip().split('\n')
        h_line = lines[0].strip('# ').strip()
        body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else h_line
        keywords = re.findall(r'\b[a-zA-Z0-9_]{3,}\b', sec.lower())
        chunks.append({
            'id': f"chunk-{doc_id}-{idx+1}",
            'headingPath': f"{title} > {h_line}",
            'text': body[:400] if len(body) > 400 else body,
            'keywords': list(set(keywords))[:8]
        })

    documents.append({
        'id': doc_id,
        'docType': mapped_type,
        'title': title,
        'period': period,
        'effectiveFrom': d.get('effective_from') or '2025-10-01',
        'effectiveTo': d.get('effective_to') or '2026-12-31',
        'version': f"1.{d.get('version', 0)}",
        'status': 'indexed',
        'content': content,
        'chunks': chunks
    })

print(f"Processed {len(documents)} strategic RAG documents.")

# 3. READ ORDERS & ORDER ITEMS
print("Reading orders from shop.sqlite...")
prod_dict = {p['id']: p for p in products}
order_rows = con_shop.execute("SELECT * FROM orders ORDER BY day ASC").fetchall()
item_rows = con_shop.execute("SELECT * FROM order_items").fetchall()

order_items_map = {}
for item in item_rows:
    oid = item['order_id']
    if oid not in order_items_map:
        order_items_map[oid] = []
    p_info = prod_dict.get(item['sku'], {})
    p_name = p_info.get('name', 'Sản phẩm công nghệ')
    order_items_map[oid].append({
        'variantId': f"var-{item['sku'][:8]}-1",
        'productId': item['sku'],
        'productName': p_name,
        'sku': f"SKU-{item['sku'][:8].upper()}",
        'price': int(item['list_price']),
        'costPrice': int(item['cost']),
        'qty': int(item['quantity']),
        'specsSummary': p_name
    })

orders = []
CUST_NAMES = ['Anh Tuấn', 'Chị Mai', 'Anh Hoàng', 'Chị Linh', 'Anh Dũng', 'Chị Hương', 'Anh Khoa', 'Chị Ngọc', 'Anh Nam', 'Chị Hà']
CITIES = ['Hà Nội', 'TP. Hồ Chí Minh', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ', 'Bình Dương']

for idx, ord_r in enumerate(order_rows):
    oid = ord_r['id']
    items = order_items_map.get(oid, [])
    subtotal = sum(i['price'] * i['qty'] for i in items)
    cust_idx = idx % len(CUST_NAMES)
    city_idx = idx % len(CITIES)

    orders.append({
        'id': oid,
        'orderCode': oid,
        'customerName': CUST_NAMES[cust_idx],
        'customerPhone': f"098{idx % 10000:04d}{idx % 1000:03d}",
        'customerAddress': f"{12 + (idx % 80)} Phố Huế, Quận Hai Bà Trưng",
        'customerCity': CITIES[city_idx],
        'notes': 'Giao trong giờ hành chính',
        'items': items,
        'subtotal': subtotal,
        'discount': 0,
        'total': subtotal,
        'channel': ord_r['channel'] or 'web',
        'status': 'completed' if ord_r['day'] < '2026-09-01' else 'shipping',
        'paymentMethod': 'cod' if idx % 2 == 0 else 'banking',
        'paymentStatus': 'paid' if ord_r['day'] < '2026-09-01' else 'pending',
        'createdAt': f"{ord_r['day']}T09:30:00Z",
        'statusTimeline': [
            {'status': 'new', 'timestamp': f"{ord_r['day']}T09:30:00Z", 'note': 'Khách đặt đơn'},
            {'status': 'completed', 'timestamp': f"{ord_r['day']}T14:00:00Z", 'note': 'Giao hàng thành công'}
        ]
    })

print(f"Processed {len(orders)} orders with order items.")

# 4. READ RECEIPTS
receipt_rows = con_shop.execute("SELECT * FROM receipts ORDER BY day ASC").fetchall()
movements = []
for r in receipt_rows:
    sku = r['sku']
    movements.append({
        'id': r['id'],
        'variantId': f"var-{sku[:8]}-1",
        'productId': sku,
        'type': 'in',
        'qty': int(r['quantity']),
        'refType': 'purchase_order',
        'refId': r['line_id'],
        'note': f"Nhập kho lô hàng {r['line_id']} giá vốn {r['unit_cost']:,}₫",
        'createdAt': f"{r['day']}T10:00:00Z"
    })
print(f"Processed {len(movements)} warehouse receipts.")

# 5. COPY MONTHLY SUMMARY TO BACKEND DATA
monthly_summary_src = SCENARIO_DIR / 'monthly_summary.json'
monthly_summary_dst = ROOT / 'backend' / 'data' / 'monthly_summary.json'
with open(monthly_summary_src, 'r', encoding='utf-8') as f:
    monthly_data = json.load(f)
with open(monthly_summary_dst, 'w', encoding='utf-8') as f:
    json.dump(monthly_data, f, ensure_ascii=False, indent=2)
print("Copied monthly_summary.json to backend/data.")

# 6. UPDATE store_state.json
state = {}
if BACKEND_DATA_JSON.exists():
    try:
        with open(BACKEND_DATA_JSON, 'r', encoding='utf-8') as f:
            state = json.load(f)
    except Exception:
        pass

state['categories'] = categories
state['brands'] = brands
state['products'] = products
state['inventory'] = inventory
state['documents'] = documents
state['orders'] = orders
state['movements'] = movements
if 'promotions' not in state or not state['promotions']:
    state['promotions'] = []

with open(BACKEND_DATA_JSON, 'w', encoding='utf-8') as f:
    json.dump(state, f, ensure_ascii=False, indent=2)
print(f"Successfully updated {BACKEND_DATA_JSON}!")

# 7. UPDATE seedData.ts
with open(SEED_DATA_TS, 'r', encoding='utf-8') as f:
    content = f.read()

categories_ts = 'export const INITIAL_CATEGORIES: Category[] = ' + json.dumps(categories, ensure_ascii=False, indent=2) + ';\n'
brands_ts = 'export const INITIAL_BRANDS: Brand[] = ' + json.dumps(brands, ensure_ascii=False, indent=2) + ';\n'
products_ts = 'export const INITIAL_PRODUCTS: Product[] = ' + json.dumps(products, ensure_ascii=False, indent=2) + ';\n'
docs_ts = 'export const INITIAL_STRATEGIC_DOCUMENTS: StrategicDocument[] = ' + json.dumps(documents, ensure_ascii=False, indent=2) + ';\n'

promo_idx = content.find('export const INITIAL_PROMOTIONS')
doc_idx = content.find('export const INITIAL_STRATEGIC_DOCUMENTS')
if promo_idx != -1 and doc_idx != -1:
    promo_part = content[promo_idx:doc_idx]
else:
    promo_part = ''

new_seed = """import { Category, Brand, Product, StrategicDocument, Promotion } from '../types/index.js';\n\n""" + categories_ts + "\n" + brands_ts + "\n" + products_ts + "\n" + promo_part + "\n" + docs_ts

with open(SEED_DATA_TS, 'w', encoding='utf-8') as f:
    f.write(new_seed)

print(f"Successfully updated {SEED_DATA_TS}!")
print("ALL DONE SYNCING SCENARIO V1!")
