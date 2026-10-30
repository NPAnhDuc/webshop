import random
import re
import json
from contextlib import contextmanager
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data' / 'structured' / 'shop.db'


@contextmanager
def connect(path=DB, readonly=False):
    con = sqlite3.connect(f'file:{Path(path).as_posix()}?mode=ro', uri=True) if readonly else sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    try:
        with con:
            yield con
    finally:
        con.close()


def initialize(path=DB):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with connect(path) as con:
        con.executescript('''
        CREATE TABLE IF NOT EXISTS products (
          sku TEXT PRIMARY KEY, name TEXT, price INTEGER, stock INTEGER,
          panel TEXT, ram INTEGER, battery INTEGER, weight REAL, category TEXT);
        CREATE TABLE IF NOT EXISTS sales (
          day TEXT, sku TEXT, quantity INTEGER, revenue INTEGER, cost INTEGER);
        ''')
        if con.execute('SELECT COUNT(*) FROM products').fetchone()[0]:
            return
        products = [
            ('DEMO-A','Laptop mẫu A OLED 14',18900000,12,'OLED',16,70,1.3,'laptop'),
            ('DEMO-B','Laptop mẫu B OLED 15',19900000,7,'OLED',16,65,1.5,'laptop'),
            ('DEMO-C','Laptop mẫu C IPS 14',14900000,18,'IPS',16,80,1.2,'laptop'),
            ('DEMO-D','Laptop mẫu D Gaming',21900000,8,'IPS 144Hz',32,60,2.2,'laptop'),
            ('DEMO-E','Laptop mẫu E OLED nhẹ',20900000,5,'OLED',16,75,1.1,'laptop'),
            ('DEMO-F','Laptop mẫu F phổ thông',11900000,0,'IPS',8,45,1.6,'laptop'),
            ('DEMO-SSD','SSD mẫu 1TB',1590000,30,'',0,0,0,'ssd'),
        ]
        con.executemany('INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?)', products)
        rng = random.Random(42)
        rows = []
        start, end = date(2025,1,1), date(2026,10,15)
        for offset in range((end-start).days+1):
            day = start + timedelta(days=offset)
            for p in products:
                qty = rng.randint(0,3)
                if day.month == 8 and p[0] in ('DEMO-A','DEMO-C'):
                    qty += 2  # deterministic back-to-school event
                rows.append((day.isoformat(),p[0],qty,qty*p[2],qty*int(p[2]*0.85)))
        con.executemany('INSERT INTO sales VALUES (?,?,?,?,?)', rows)


class CustomerTools:
    """Public projection only; never exposes sales or cost."""
    def __init__(self, path=DB):
        self.path = path

    def mentioned_skus(self,text):
        with connect(self.path,readonly=True) as con:
            codes=[(r['sku'],r['name']) for r in con.execute('SELECT sku,name FROM products')]
        return [sku for sku,name in codes if any(value and re.search(r'(?<!\w)'+re.escape(value)+r'(?!\w)',text,re.I) for value in (sku,name))]

    def products(self, low=0, high=10**12, skus=(), display=False, battery=False, category='laptop'):
        with connect(self.path, readonly=True) as con:
            projection='sku,name,price,stock,panel,ram,battery,weight,category'
            if skus:
                rows = con.execute('SELECT '+projection+' FROM products WHERE sku IN (' + ','.join('?' for _ in skus) + ')', tuple(skus))
            else:
                rows = con.execute('SELECT '+projection+' FROM products WHERE price BETWEEN ? AND ? AND stock>0 AND category=?', (low,high,category))
            result = [dict(r) for r in rows]
            if con.execute("SELECT 1 FROM sqlite_master WHERE name='product_facts'").fetchone():
                for product in result:
                    fact=con.execute('SELECT record_json FROM product_facts WHERE sku=?',(product['sku'],)).fetchone()
                    if fact:
                        record=json.loads(fact[0])
                        for key in ('cpu','gpu','brand','part_number'):
                            if record.get(key): product[key]=record[key]
                        product['spec_source']=record.get('source_dataset','product_facts')
        return sorted(result, key=lambda p: (int(display and 'OLED' in (p['panel'] or '')), (p['battery'] or 0) if battery else 0, -p['price']), reverse=True)


class AdminTools:
    def __init__(self, path=DB):
        self.path = path

    def revenue(self, start, end):
        with connect(self.path, readonly=True) as con:
            rows = con.execute('''SELECT substr(day,1,7) AS month, SUM(revenue) AS revenue,
              SUM(revenue-cost) AS profit, SUM(quantity) AS units FROM sales
              WHERE day>=? AND day<? GROUP BY month ORDER BY month''', (start,end))
            return [dict(r) for r in rows]

    def inventory(self,as_of=None):
        with connect(self.path, readonly=True) as con:
            daily=con.execute("SELECT 1 FROM sqlite_master WHERE name='inventory_daily' AND type='table'").fetchone()
            if daily:
                target=as_of or con.execute('SELECT MAX(day) FROM inventory_daily').fetchone()[0]
                return [dict(r) for r in con.execute('SELECT p.sku,p.name,i.quantity stock,i.day as_of FROM inventory_daily i JOIN products p ON p.sku=i.sku WHERE i.day=? ORDER BY i.quantity,p.sku',(target,))]
            if as_of: raise ValueError('Bộ dữ liệu này chưa có ảnh chụp tồn kho theo ngày; không thể dùng tồn hiện tại thay cho tồn lịch sử.')
            return [dict(r) for r in con.execute('SELECT sku,name,stock FROM products ORDER BY stock')]

    def top_products(self,start,end,metric='units',limit=5,category='all'):
        columns={'units':'units','revenue':'revenue','gross_profit':'gross_profit'}
        if metric not in columns: raise ValueError('Chưa có cách phân bổ chi phí vận hành để xếp lợi nhuận hoạt động theo SKU.')
        if not isinstance(limit,int) or not 1<=limit<=10: raise ValueError('Giới hạn kết quả phải từ 1 đến 10.')
        from .conversation import CATEGORIES
        if category not in CATEGORIES: raise ValueError('Nhóm sản phẩm không hợp lệ.')
        scope=" AND sku IN (SELECT sku FROM products WHERE category=?)" if category!='all' else ''
        params=(start,end,category) if category!='all' else (start,end)
        with connect(self.path,readonly=True) as con:
            if limit==1:
                return [dict(r) for r in con.execute(f'''WITH totals AS (
                    SELECT sku,SUM(quantity) units,SUM(revenue) revenue,SUM(revenue-cost) gross_profit
                    FROM sales WHERE day>=? AND day<? {scope} GROUP BY sku)
                    SELECT t.*,p.name,p.category,COUNT(*) OVER() AS tied_count
                    FROM totals t JOIN products p ON p.sku=t.sku
                    WHERE t.{columns[metric]}=(SELECT MAX({columns[metric]}) FROM totals)
                    ORDER BY t.sku LIMIT 10''',params)]
            rows=con.execute(f'''WITH totals AS (
                SELECT sku,SUM(quantity) units,SUM(revenue) revenue,SUM(revenue-cost) gross_profit
                FROM sales WHERE day>=? AND day<? {scope} GROUP BY sku)
                SELECT t.*,p.name,p.category FROM totals t JOIN products p ON p.sku=t.sku
                ORDER BY {columns[metric]} DESC,t.sku LIMIT ?''',params+(limit,))
            return [dict(r) for r in rows]



def dataset_source(path=DB):
    with connect(path,readonly=True) as con:
        if not con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='metadata'").fetchone():
            return 'demo'
        row=con.execute("SELECT value FROM metadata WHERE key='source'").fetchone()
        return row[0] if row else 'demo'
