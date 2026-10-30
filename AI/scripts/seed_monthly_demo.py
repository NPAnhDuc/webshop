"""Publish existing demo rows as a monthly batch; the ledger prevents recounting."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shopbot.layout import STRUCTURED,UNSTRUCTURED
from shopbot.store import DB,connect,dataset_source
from shopbot.monthly import atomic_json,atomic_text


def main():
    if dataset_source(DB)!='demo':raise ValueError('Demo database required')
    month='2026-09'
    with connect(DB,readonly=True) as con:
        products=[dict(r) for r in con.execute('SELECT * FROM products')]
        rows=[dict(r) for r in con.execute("SELECT * FROM sales WHERE substr(day,1,7)=?",(month,))]
    sales=[dict(r,id=f"demo:{r['day']}:{r['sku']}") for r in rows]
    target=STRUCTURED/'monthly'/month/'shop.json'
    if not target.exists():
        atomic_json(target,{'ready':True,'complete':True,'data_kind':'demo','month':month,'inventory_as_of':'2026-09-30','products':products,'sales':sales})
    folder=UNSTRUCTURED/'monthly'/month
    manifest=folder/'manifest-demo.json'
    if not manifest.exists():
        entries=[]
        for audience,name in [('customer','chinh-sach-mau'),('admin','chien-luoc-mau')]:
            original=UNSTRUCTURED/('public' if audience=='customer' else 'admin')/(name+'.md')
            atomic_text(folder/(name+'.md'),original.read_text(encoding='utf-8-sig'))
            entries.append({'document_id':name,'file':name+'.md','version':1,'audience':audience,'status':'approved',
                            'effective_from':'2026-09-01','effective_to':None})
        atomic_json(manifest,{'ready':True,'data_kind':'demo','documents':entries})
    print(f'Prepared {len(sales)} existing demo rows and versioned documents for {month}')


if __name__=='__main__':main()
