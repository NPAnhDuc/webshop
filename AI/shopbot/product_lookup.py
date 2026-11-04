"""Price and stock of one named product, read straight from the shop database.

"MSI Modern 15 B12M giá bao nhiêu, còn hàng không?" has a single exact answer in
`products`. The router sent it to a refusal even though the shop holds the number.
Nothing is generated; two products, an order or a discount stay on the normal path.
"""
import re
import sqlite3
from .budget_advice import NOTE, vnd
from .retrieval import normalize
from .store import connect

PRICE = re.compile(r'\b(?:gia|bao nhieu tien|het bao nhieu|ban bao nhieu)\b')
STOCK = re.compile(r'\b(?:con hang|het hang|co hang|co san|ton kho|con khong|con bao nhieu)\b')
# Same word, another meaning: "giá vốn", "đánh giá", "tham gia", "hàng giả".
NOT_PRICE = re.compile(r'\bgia (?:von|nhap|si|tri|su|dinh|dung|do|canh|thanh|goc|treo)\b|\b(?:danh|tham|hang|quoc|ngoai) gia\b')
# The shop can read a price; it cannot promise, reserve or discount through this path.
OUT_OF_SCOPE = re.compile(r'\b(?:dat|giu|chot don|mua giup|len don|giao|ship|thanh toan|tra gop|bao hanh|doi tra|'
                          r'nhap|giam gia|khuyen mai|voucher|uu dai|so voi|so sanh)\b')
ANAPHORA = re.compile(r'\b(?:no|may (?:nay|do|vua noi)|con (?:nay|do)|san pham (?:nay|do|vua noi))\b')


def _key(name):
    return normalize(re.sub(r'\s*\([^)]*\)', '', name)).strip()


def _named(text, rows):
    """Rows whose name is in the text; "X Pro" hides "X" when both match."""
    found = [r for r in rows if re.search(r'(?<!\w)' + re.escape(_key(r[0])) + r'(?!\w)', text)]
    return [r for r in found if not any(o is not r and _key(r[0]) in _key(o[0]) for o in found)]


def product_names(db_path):
    """Every product the shop sells; empty when the database cannot be read."""
    try:
        with connect(db_path, readonly=True) as con:
            return [row[0] for row in con.execute('SELECT name FROM products WHERE price > 0')]
    except sqlite3.Error:
        return []


def lookup(question, role, db_path, subject=''):
    """A reply dict (answer, rows, name) for one product's price or stock, else None."""
    q = normalize(question)
    asks_price = bool(PRICE.search(NOT_PRICE.sub(' ', q)))
    asks_stock = bool(STOCK.search(q))
    if not (asks_price or asks_stock) or OUT_OF_SCOPE.search(q):
        return None
    try:
        with connect(db_path, readonly=True) as con:
            rows = con.execute('SELECT name, price, stock FROM products WHERE price > 0').fetchall()
    except sqlite3.Error:
        return None
    named = _named(q, rows)
    if not named and subject and ANAPHORA.search(q):
        named = _named(normalize(subject), rows)
    if len(named) != 1:
        return None
    name, price, stock = named[0]
    state = 'hết hàng' if stock <= 0 else f'còn {stock} sản phẩm' if role == 'admin' else 'còn hàng'
    return dict(answer=f'{name}: giá {vnd(int(price))}, {state}.\n\n{NOTE}',
                rows=[dict(name=name, price=int(price), stock=int(stock))], name=name)
