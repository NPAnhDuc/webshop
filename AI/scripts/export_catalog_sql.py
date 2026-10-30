"""Export the small curated catalog to a standalone SQLite SQL package."""
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'data'/'structured'/'processed'/'product_catalog.jsonl'
OUTPUT=ROOT/'data'/'product_sql'

SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE sources (
  source_id TEXT PRIMARY KEY,
  source_url TEXT NOT NULL,
  license_note TEXT NOT NULL,
  usage_scope TEXT NOT NULL DEFAULT 'external_research_only'
);
CREATE TABLE categories (
  category_id TEXT PRIMARY KEY,
  name_vi TEXT NOT NULL
);
CREATE TABLE products (
  product_id TEXT PRIMARY KEY,
  category_id TEXT NOT NULL REFERENCES categories(category_id),
  source_id TEXT NOT NULL REFERENCES sources(source_id),
  name TEXT NOT NULL,
  brand TEXT,
  part_number TEXT,
  cpu TEXT,
  ram_gb REAL CHECK (ram_gb IS NULL OR ram_gb >= 0),
  gpu TEXT,
  screen_inches REAL CHECK (screen_inches IS NULL OR screen_inches > 0),
  socket TEXT,
  form_factor TEXT,
  source_price REAL CHECK (source_price IS NULL OR source_price >= 0),
  source_currency TEXT,
  shop_price_vnd INTEGER CHECK (shop_price_vnd IS NULL OR shop_price_vnd >= 0),
  cost_price_vnd INTEGER CHECK (cost_price_vnd IS NULL OR cost_price_vnd >= 0),
  stock_quantity INTEGER CHECK (stock_quantity IS NULL OR stock_quantity >= 0),
  supplier TEXT,
  bestseller_verified INTEGER NOT NULL DEFAULT 0 CHECK (bestseller_verified IN (0,1)),
  approved_for_shop_sales INTEGER NOT NULL DEFAULT 0 CHECK (approved_for_shop_sales IN (0,1)),
  source_file TEXT NOT NULL,
  source_row INTEGER NOT NULL CHECK (source_row > 0),
  source_sha256 TEXT NOT NULL CHECK (length(source_sha256) = 64),
  selection_term TEXT NOT NULL,
  attributes_json TEXT NOT NULL CHECK (json_valid(attributes_json))
);
CREATE INDEX products_category_idx ON products(category_id);
CREATE INDEX products_name_idx ON products(name);
CREATE VIEW laptop_catalog AS SELECT * FROM products WHERE category_id='laptop';
CREATE VIEW pc_parts_catalog AS SELECT * FROM products WHERE category_id<>'laptop';
CREATE TABLE product_images (
  product_id TEXT PRIMARY KEY REFERENCES products(product_id),
  local_path TEXT,
  source_page TEXT,
  image_url TEXT,
  source_title TEXT,
  image_sha256 TEXT,
  width INTEGER,
  height INTEGER,
  status TEXT NOT NULL,
  match_scope TEXT NOT NULL,
  match_notes TEXT NOT NULL,
  exact_sku_verified INTEGER NOT NULL DEFAULT 0 CHECK(exact_sku_verified IN (0,1)),
  commercial_reuse_approved INTEGER NOT NULL DEFAULT 0 CHECK(commercial_reuse_approved IN (0,1))
);
CREATE VIEW product_catalog_with_images AS
  SELECT p.*, i.local_path AS image_path, i.status AS image_status,
    i.match_scope AS image_match_scope, i.exact_sku_verified AS image_exact_sku_verified
  FROM products p LEFT JOIN product_images i ON i.product_id=p.product_id;
"""
NAMES={'laptop':'Laptop','cpu':'CPU','motherboard':'Bo mạch chủ','memory':'RAM',
 'internal-hard-drive':'Ổ lưu trữ','video-card':'Card đồ họa','power-supply':'Nguồn máy tính',
 'case':'Vỏ máy tính','monitor':'Màn hình','mouse':'Chuột'}

def export():
    rows=[json.loads(line) for line in INPUT.read_text(encoding='utf-8').splitlines() if line.strip()]
    if not 1<=len(rows)<=100: raise ValueError('Expected a compact catalog of at most 100 products')
    OUTPUT.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(':memory:')
    db.executescript(SCHEMA)
    for source in sorted({r['source_dataset'] for r in rows}):
        url=('https://github.com/'+source if source=='docyx/pc-part-dataset' else 'https://www.kaggle.com/datasets/'+source)
        license_note=('Repository MIT; underlying PCPartPicker data terms need separate review.' if source=='docyx/pc-part-dataset' else 'Apache 2.0 according to Kaggle metadata; preserve attribution and review underlying source rights.')
        db.execute('INSERT INTO sources VALUES(?,?,?,?)',(source,url,license_note,'external_research_only'))
    for category in sorted({r['category'] for r in rows}):
        db.execute('INSERT INTO categories VALUES(?,?)',(category,NAMES.get(category,category)))
    for r in rows:
        if not r['model']:raise ValueError('Product without a source name')
        values=(r['record_id'],r['category'],r['source_dataset'],r['model'],r['brand'],r['part_number'],
                r['cpu'],r['ram_gb'],r['gpu'],r['screen_inches'],r['socket'],r['form_factor'],
                r['price_original'],r['currency'],r['shop_price_vnd'],r['cost_price'],r['stock'],r['supplier'],
                int(r['bestseller_verified']),int(r['approved_for_shop_sales']),r['source_file'],r['source_row'],
                r['source_sha256'],r['selection_term'],json.dumps(r['attributes'],ensure_ascii=False,allow_nan=False))
        db.execute('INSERT INTO products VALUES('+','.join('?' for _ in values)+')',values)
    image_manifest=ROOT/'data'/'product_images'/'manifest.json'
    images=json.loads(image_manifest.read_text(encoding='utf-8')) if image_manifest.exists() else []
    ids={r['record_id'] for r in rows}
    for image in images:
        if image['record_id'] not in ids:continue
        local='../product_images/'+image['local_path'] if image.get('local_path') else None
        if local:
            image_file=(OUTPUT/local).resolve()
            if not image_file.is_relative_to((ROOT/'data'/'product_images').resolve()):
                raise ValueError('Image path outside product image folder')
            if hashlib.sha256(image_file.read_bytes()).hexdigest()!=image['sha256']:
                raise ValueError('Image checksum mismatch: '+image['model'])
        values=(image['record_id'],local,image.get('source_page'),image.get('image_url'),image.get('source_title'),
                image.get('sha256'),image.get('width'),image.get('height'),image['status'],
                image['match_scope'],image['match_notes'],int(image['exact_sku_verified']),int(image['commercial_reuse_approved']))
        db.execute('INSERT INTO product_images VALUES('+','.join('?' for _ in values)+')',values)
    db.commit()
    sql='-- SQLite 3 SQL. UTF-8. Curated external catalog; not live shop inventory.\n'
    sql+='-- Source prices preserve their original currency. Unknown shop values remain NULL.\n'
    # iterdump orders tables alphabetically; enable FK enforcement after all parent rows exist.
    sql+='PRAGMA foreign_keys=OFF;\n'+'\n'.join(db.iterdump())+'\nPRAGMA foreign_keys=ON;\n'
    (OUTPUT/'products.sqlite.sql').write_text(sql,encoding='utf-8')
    # Execute the actual exported SQL in a fresh database and verify its contents.
    staged=OUTPUT/'products.building.sqlite'
    if staged.exists():staged.unlink()
    target=sqlite3.connect(staged)
    target.executescript(sql)
    assert target.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert target.execute('PRAGMA foreign_key_check').fetchall()==[]
    assert target.execute('SELECT count(*) FROM products').fetchone()[0]==len(rows)
    assert target.execute('SELECT count(*) FROM product_images').fetchone()[0]==len([i for i in images if i['record_id'] in ids])
    for r in rows:
        stored=target.execute('SELECT attributes_json,source_sha256,source_row FROM products WHERE product_id=?',(r['record_id'],)).fetchone()
        assert json.loads(stored[0])==r['attributes']
        assert stored[1:]==(r['source_sha256'],r['source_row'])
    assert target.execute('SELECT count(*) FROM products WHERE shop_price_vnd IS NOT NULL OR cost_price_vnd IS NOT NULL OR stock_quantity IS NOT NULL OR bestseller_verified<>0 OR approved_for_shop_sales<>0').fetchone()[0]==0
    target.close()
    staged.replace(OUTPUT/'products.sqlite')
    counts=dict(Counter(r['category'] for r in rows))
    manifest={'dialect':'SQLite 3','products':len(rows),'categories':counts,
              'source_jsonl_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),
              'sql_sha256':hashlib.sha256((OUTPUT/'products.sqlite.sql').read_bytes()).hexdigest(),
              'verification':'SQL executed in fresh database; integrity, foreign keys, all original attributes and NULL shop values verified.',
              'currency_note':'PC part source prices USD; laptop prices absent. No conversion to VND.',
              'sales_rank_note':'Representative selection, not verified bestseller ranking.'}
    manifest['images_downloaded']=db.execute('SELECT count(*) FROM product_images WHERE local_path IS NOT NULL').fetchone()[0]
    (OUTPUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    readme=f'''# Danh mục sản phẩm SQL đã chọn

{len(rows)} mẫu: {sum(r['category']=='laptop' for r in rows)} laptop và {sum(r['category']!='laptop' for r in rows)} linh kiện/phụ kiện. Không nạp toàn bộ repo 66.778 sản phẩm.

- `products.sqlite.sql`: schema và dữ liệu INSERT, định dạng SQLite 3, UTF-8.
- `products.sqlite`: database đã import sẵn từ chính file SQL và kiểm tra toàn vẹn.
- `manifest.json`: số lượng theo nhóm, checksum và kết quả kiểm tra.

Các bảng: `sources`, `categories`, `products`. Hai view: `laptop_catalog`, `pc_parts_catalog`.
`attributes_json` giữ toàn bộ thuộc tính gốc. Các cột thông dụng như RAM, CPU, GPU, màn hình, socket có sẵn để lọc; thuộc tính không có trong nguồn để NULL.

## Cách dùng

Mở `products.sqlite` bằng DB Browser for SQLite hoặc DBeaver. Hoặc import `products.sqlite.sql` vào database SQLite mới, trống.

```sql
SELECT name, cpu, ram_gb, gpu, screen_inches FROM laptop_catalog;
SELECT name, socket, form_factor FROM pc_parts_catalog WHERE category_id='motherboard';
SELECT category_id, COUNT(*) FROM products GROUP BY category_id;
SELECT name, image_path, image_status, image_match_scope FROM product_catalog_with_images;
```

## Phạm vi dữ liệu

Đây là danh mục tham khảo đã chọn theo dòng sản phẩm; chưa xác nhận xếp hạng bán chạy hay SKU đang bán tại Việt Nam. Giá gốc của linh kiện được giữ bằng USD; không dùng làm giá bán của shop. Dữ liệu laptop Ryan's không có giá bán.

Giá shop bằng VND, giá vốn, tồn kho và nhà cung cấp để NULL. Bảo hành trong `attributes_json` là thông tin của nguồn Ryan's, không phải chính sách của shop. Chưa ghép mã sản phẩm với giao dịch REES46 vì không có bảng đối chiếu đã xác minh.

Giữ nguồn và điều kiện sử dụng trong bảng `sources`; giấy phép repo không thay thế điều khoản của nguồn dữ liệu bên dưới. Gói này dùng thử nội bộ, chưa phải danh mục được duyệt để bán hàng.

Ảnh lưu riêng trong `../product_images/`. Bảng `product_images` liên kết bằng `product_id`, giữ URL trang nguồn, URL ảnh gốc, SHA-256, kích thước, mức độ khớp và trạng thái duyệt. Đường dẫn ảnh tính từ thư mục này. View `product_catalog_with_images` dùng để lấy sản phẩm kèm ảnh. Ảnh dòng máy không xác nhận đúng toàn bộ SKU/cấu hình; đọc `match_notes`. Quyền sử dụng thương mại chưa được xác minh.

Tạo lại từ thư mục AI:

```powershell
.\\.venv\\Scripts\\python.exe scripts/export_catalog_sql.py
```
'''
    (OUTPUT/'README.md').write_text(readme,encoding='utf-8')
    db.close()
    print(json.dumps(manifest,ensure_ascii=False),flush=True)

if __name__=='__main__':export()
