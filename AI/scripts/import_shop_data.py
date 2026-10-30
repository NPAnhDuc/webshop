"""Create a NEW validated shop database from JSON; never merge with demo data."""
import argparse
from datetime import date
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shopbot.store import initialize,connect,ROOT


from shopbot.validation import validate, sales_hash


def import_new(source,output):
    output=Path(output).resolve()
    if not output.is_relative_to((ROOT/'data').resolve()): raise ValueError('Output must be inside AI/data')
    if output.exists(): raise ValueError('Output already exists; choose a new versioned path')
    payload=json.loads(Path(source).read_text(encoding='utf-8-sig'))
    products,sales=validate(payload)
    inventory_as_of=payload.get('inventory_as_of')
    if inventory_as_of and date.fromisoformat(inventory_as_of).isoformat()!=inventory_as_of:
        raise ValueError('Use ISO inventory_as_of YYYY-MM-DD')
    temp=output.with_suffix('.importing')
    if temp.exists(): raise ValueError('Staging file exists; inspect it before retry')
    initialize(temp)
    with connect(temp) as con:
        con.execute('DELETE FROM products');con.execute('DELETE FROM sales')
        keys=['sku','name','price','stock','panel','ram','battery','weight','category']
        con.executemany('INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?)',[tuple(p[k] for k in keys) for p in products])
        con.executemany('INSERT INTO sales VALUES (?,?,?,?,?)',[(s['day'],s['sku'],s['quantity'],s['revenue'],s['cost']) for s in sales])
        con.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY,value TEXT)')
        con.execute("INSERT OR REPLACE INTO metadata VALUES ('source',?)",('user-import: '+Path(source).name,))
        con.execute('CREATE TABLE IF NOT EXISTS sales_ingestion (id TEXT PRIMARY KEY,payload_hash TEXT NOT NULL)')
        con.executemany('INSERT INTO sales_ingestion VALUES (?,?)',[(r['id'],sales_hash(r)) for r in sales])
        con.execute("INSERT OR REPLACE INTO metadata VALUES ('catalog_as_of',?)",(inventory_as_of or 'unknown',))
    temp.rename(output)
    return {'products':len(products),'sales':len(sales),'database':str(output)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(import_new(a.source,a.output)))
