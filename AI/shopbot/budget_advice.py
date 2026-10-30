"""Budget product suggestions read straight from the shop database.

"Gợi ý máy khoảng 20 triệu màn hình đẹp" is a catalog filter, not a document question:
without this path the router answered it with the nearest article (refresh rate).
Prices, stock and specs come from `products` / `product_facts`; nothing is generated.
Ranking only uses fields the records hold, and the reply says which criterion it used.
"""
import json
import re
import sqlite3
from .retrieval import normalize

# Customer wording that asks the shop to pick products for them.
ASKS_FOR_PICK = re.compile(r'\b(?:goi y|tu van|nen mua|nen chon|nen lay|chon giup|chon dum|tim giup|tim dum|tim (?:may|con|mau|laptop)'
                           r'|kiem (?:may|con|giup)|recommend|co (?:may|con|mau|loai) nao|(?:may|con|mau|laptop) nao|mua (?:may|con|laptop|man hinh))\b')
MONEY = re.compile(r'(?P<bound>khoang|tam|tam khoang|quanh|duoi|nho hon|toi da|khong qua|khong vuot qua|tren|tu|hon)?\s*'
                   r'(?P<number>\d+(?:[.,]\d+)?)\s*(?P<unit>trieu|tr|cu)(?![a-z])')
# Category nouns, most specific first; "máy"/"con máy" alone means a laptop in this catalog.
CATEGORIES = [
    ('video-card', r'\b(?:card (?:man hinh|do hoa)|vga|gpu rtx|rtx)\b', 'card đồ hoạ'),
    ('monitor', r'\b(?:man hinh (?:roi|choi game|gaming|may tinh))\b|^(?!.*\b(?:may|laptop)\b).*\bman hinh\b', 'màn hình'),
    ('memory', r'\b(?:ram|bo nho)\b(?! \d+ ?gb (?:cho|de))', 'RAM'),
    ('internal-hard-drive', r'\b(?:ssd|o cung)\b', 'SSD'),
    ('cpu', r'\b(?:cpu|chip|vi xu ly)\b', 'CPU'),
    ('motherboard', r'\b(?:mainboard|bo mach chu|main)\b', 'mainboard'),
    ('power-supply', r'\b(?:nguon|psu)\b', 'nguồn'),
    ('mouse', r'\b(?:chuot)\b', 'chuột'),
    ('case', r'\b(?:case|vo may)\b', 'vỏ case'),
    ('laptop', r'\b(?:laptop|may tinh xach tay|notebook|may)\b', 'laptop'),
]
SCREEN = re.compile(r'\b(?:man hinh|man|hien thi)\b.{0,12}\b(?:dep|net|sac net|chat luong|xin|tot|dinh)\b|\b(?:do hoa|chinh anh|thiet ke|xem phim)\b')
GAMING = re.compile(r'\b(?:choi game|gaming|game)\b')
LIGHT = re.compile(r'\b(?:nhe|mong nhe|di chuyen|mang di)\b')


def vnd(amount):
    return f'{amount:,}'.replace(',', '.') + 'đ'


def money(match):
    value = float(match['number'].replace(',', '.'))
    return int(round(value * 1_000_000))


def request(question):
    """(category, label, low, high, budget) for a pick-with-budget request, else None."""
    q = normalize(question)
    found = list(MONEY.finditer(q))
    if len(found) != 1 or not ASKS_FOR_PICK.search(q):
        return None
    m = found[0]
    budget = money(m)
    if not 1_000_000 <= budget <= 200_000_000:
        return None
    bound = m['bound'] or ''
    if bound in ('duoi', 'nho hon'):
        low, high = 0, budget - 1
    elif bound in ('toi da', 'khong qua', 'khong vuot qua'):
        low, high = 0, budget
    elif bound in ('tren', 'tu', 'hon'):
        low, high = budget, budget * 2
    else:  # "khoảng/tầm 20 triệu" or a bare amount: a band around it
        low, high = int(budget * 0.85), int(budget * 1.1)
    rest = q[:m.start()] + ' ' + q[m.end():]
    for category, pattern, label in CATEGORIES:
        if re.search(pattern, rest):
            return category, label, low, high, budget, bound
    return None


def _specs(record):
    a = record.get('attributes') or {}
    def first(*keys):
        for k in keys:
            if a.get(k) not in (None, ''):
                return a[k]
    resolution = first('Display Resolution', 'resolution')
    if isinstance(resolution, list) and len(resolution) == 2:
        resolution = f'{resolution[0]}x{resolution[1]}'
    pixels = 0
    if isinstance(resolution, str) and re.fullmatch(r'\d+x\d+', resolution):
        w, h = map(int, resolution.split('x'))
        pixels = w * h
    weight = first('Weight (Kg)')
    weight = float(re.search(r'\d+(?:\.\d+)?', weight)[0]) if isinstance(weight, str) and re.search(r'\d', weight) else None
    dedicated = (first('Graphics Memory Accessibility') == 'Dedicated')
    display = first('Display Type', 'panel_type')
    if isinstance(display, str):
        display = re.sub(r'\s*Display$', '', display).replace('FHD LED', 'Full HD').replace('WQXGA', '').strip()
        display = re.sub(r'^FHD\b', 'Full HD', display)
    return dict(display=display, resolution=resolution, pixels=pixels,
                refresh=first('refresh_rate'), size=first('Display Size (Inch)', 'screen_size'),
                cpu=record.get('cpu') or first('Processor Model'), gpu=record.get('gpu'), dedicated=dedicated,
                ram=first('RAM'), weight=weight)


def _line(i, p):
    s = p['specs'];parts = []
    if s['display'] or s['resolution']:
        screen = ' '.join(str(x) for x in [s['display'], f"({s['resolution']})" if s['resolution'] else None] if x)
        if s['refresh']:
            screen += f", {s['refresh']} Hz"
        parts.append('màn hình ' + screen)
    if s['cpu']:
        parts.append(str(s['cpu']))
    if s['gpu']:
        parts.append(str(s['gpu']))
    if s['ram']:
        parts.append('RAM ' + str(s['ram']))
    if s['weight']:
        parts.append(f"{s['weight']:g} kg".replace('.', ','))
    return f"{i}. {p['name']} – {vnd(p['price'])}" + (f": {'; '.join(parts)}" if parts else '')


def advise(question, db_path):
    """A reply dict (answer, rows) for a budget pick request, or None when the question is not one."""
    parsed = request(question)
    if not parsed:
        return None
    category, label, low, high, budget, bound = parsed
    q = normalize(question)
    with sqlite3.connect(f'file:{db_path}?mode=ro', uri=True) as con:
        rows = con.execute('SELECT p.name, p.price, p.stock, f.record_json FROM products p '
                           'LEFT JOIN product_facts f USING(sku) WHERE p.category=?', (category,)).fetchall()
    items = [dict(name=n, price=int(price), stock=int(stock or 0), specs=_specs(json.loads(rec) if rec else {}))
             for n, price, stock, rec in rows if price]
    in_band = [p for p in items if low <= p['price'] <= high]
    if SCREEN.search(q) and category in ('laptop', 'monitor'):
        criterion = 'độ phân giải màn hình cao nhất trước'
        key = lambda p: (-p['specs']['pixels'], -(p['specs']['refresh'] or 0), -p['price'])
    elif GAMING.search(q) and category == 'laptop':
        criterion = 'ưu tiên máy có card đồ hoạ rời'
        key = lambda p: (not p['specs']['dedicated'], -p['price'])
    elif LIGHT.search(q) and category == 'laptop':
        criterion = 'nhẹ nhất trước'
        key = lambda p: (p['specs']['weight'] or 99, p['price'])
    else:
        criterion = 'giá gần ngân sách nhất trước'
        key = lambda p: (abs(p['price'] - budget), p['price'])
    band = (f'dưới {vnd(budget)}' if bound in ('duoi', 'nho hon') else
            f'từ {vnd(budget)}' if bound in ('tren', 'tu', 'hon') else
            f'đến {vnd(high)}' if not low else f'{vnd(low)} – {vnd(high)}')
    available = sorted([p for p in in_band if p['stock'] > 0], key=key)
    sold_out = sorted([p for p in in_band if p['stock'] <= 0], key=key)
    if available:
        head = f"Trong tầm {band}, shop có {len(available)} mẫu {label} còn hàng. Xếp theo {criterion}:"
        picks = [_line(i + 1, p) for i, p in enumerate(available[:3])]
        if sold_out and key(sold_out[0]) < key(available[0]):
            picks.append(f"{sold_out[0]['name']} ({vnd(sold_out[0]['price'])}) hợp tiêu chí hơn nhưng đang hết hàng.")
        if criterion.startswith('độ phân giải'):
            best = available[0]['specs']['pixels']
            if best and all(p['specs']['pixels'] == best for p in available[:3]):
                picks.append(f"Các mẫu còn hàng trong tầm này có cùng độ phân giải {available[0]['specs']['resolution']}.")
            sharper = sorted([p for p in items if p['stock'] > 0 and p['specs']['pixels'] > best and p not in in_band],
                             key=lambda p: abs(p['price'] - budget))
            if sharper:
                picks.append(f"Màn hình nét hơn gần ngân sách nhất: {_line(0, sharper[0])[3:]}")
    else:
        head = f"Hiện shop không có {label} nào còn hàng trong tầm {band}."
        nearest = sorted([p for p in items if p['stock'] > 0], key=lambda p: abs(p['price'] - budget))[:2]
        picks = (['Gần ngân sách nhất:'] + [_line(i + 1, p) for i, p in enumerate(nearest)]) if nearest else []
    note = 'Giá theo danh mục của shop; giá và tồn kho chính xác tại thời điểm mua xem trên trang sản phẩm.'
    return dict(answer='\n\n'.join(x for x in [head, '\n'.join(picks), note] if x),
                rows=[dict(name=p['name'], price=p['price'], stock=p['stock']) for p in available[:3]],
                criterion=criterion, band=(low, high), category=category)
