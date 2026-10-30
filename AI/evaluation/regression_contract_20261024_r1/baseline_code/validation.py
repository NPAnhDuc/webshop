from datetime import date
import hashlib
import math
import json

def validate(payload):
    products=payload.get('products',[])
    sales=payload.get('sales',[])
    if not products: raise ValueError('products must not be empty')
    skus=set()
    for p in products:
        required={'sku','name','price','stock','panel','ram','battery','weight','category'}
        if set(p)!=required: raise ValueError('Product fields must be exactly '+str(sorted(required)))
        if not isinstance(p['sku'],str) or not p['sku'].strip() or p['sku'] in skus: raise ValueError('SKU missing/duplicate')
        skus.add(p['sku'])
        for key in ('price','stock','ram','battery'):
            if type(p[key]) is not int or p[key]<0: raise ValueError('Invalid '+key)
        if type(p['weight']) not in (int,float) or (not math.isfinite(p['weight']) or p['weight']<0): raise ValueError('Invalid weight')
        for key in ('name','panel','category'):
            if not isinstance(p[key],str): raise ValueError('Invalid '+key)
    ids=set()
    for s in sales:
        if set(s)!={'id','day','sku','quantity','revenue','cost'}: raise ValueError('Invalid sales fields')
        if not isinstance(s['id'],str) or not s['id'] or s['id'] in ids: raise ValueError('Sale ID missing/duplicate')
        ids.add(s['id'])
        d=date.fromisoformat(s['day'])
        if d.isoformat()!=s['day']: raise ValueError('Use ISO dates YYYY-MM-DD')
        if s['sku'] not in skus: raise ValueError('Unknown SKU '+s['sku'])
        for key in ('quantity','revenue','cost'):
            if type(s[key]) is not int or s[key]<0: raise ValueError('Invalid '+key)
        if s['quantity']==0 and (s['revenue'] or s['cost']): raise ValueError('Money without quantity')
    return products,sales


def sales_hash(record):
    return hashlib.sha256(json.dumps(record,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
