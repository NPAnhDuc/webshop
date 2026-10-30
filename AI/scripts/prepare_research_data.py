"""Prepare source-traceable corpora without inventing shop facts or ID joins."""
import csv
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'structured'/'raw'
OUT=ROOT/'data'/'structured'/'processed'
PLACEHOLDERS={'','not found','undefined','nan','n/a','unknown','none','null'}
PART_SELECTION={
 'cpu':['Ryzen 7 9800X3D','Ryzen 5 7600','Core i5-14400F','Core i5-12400F','Ryzen 5 9600X','Ryzen 7 7700','Core i5-14600KF','Ryzen 7 5700X3D'],
 'video-card':['RTX 5060','RTX 4060','RTX 5070','RX 9060','RTX 4070','RTX 3060','RX 7600','RX 7800'],
 'motherboard':['B650','B760','B550','B850','X870','Z790'],
 'memory':['Vengeance','Fury','Ripjaws','T-Force','Trident Z5','Vengeance LPX 16'],
 'internal-hard-drive':['Samsung 990','WD_BLACK SN850','Crucial P3','Kingston NV2','Samsung 980','Samsung 970','Kingston KC3000','Crucial P5'],
 'power-supply':['Corsair RM750','MSI MAG A650','Corsair RM850','MSI MAG A750'],
 'case':['Corsair 4000D','NZXT H5','Montech AIR 903','Deepcool CH160'],
 'monitor':['AOC 24G','Asus TUF Gaming','MSI G255F','LG UltraGear 27GR75'],
 'mouse':['Logitech G305','Razer DeathAdder','Logitech G502 Hero','Razer Basilisk V3'],
}
LAPTOP_SELECTION=['LOQ','Legion','TUF','Victus','Nitro','VivoBook 15','IdeaPad Slim','Inspiron','Aspire 5','MacBook Air','ThinkPad','ZenBook',
 'MSI Modern 15 B12M','Acer Swift Go 14 SFG14-41-R5RB','Dell Latitude 3430','HP 15-fd0202TU','Lenovo ThinkBook 15 G2 ITL',
 'Dell Vostro 15 3510','Acer Aspire 3 A315-59-56VC','Gigabyte Gaming G5 MF','Asus ExpertBook B1 B1400CEAE']

def select_candidates(rows,patterns,name_key):
    chosen=set()
    for term in patterns:
        for number,row in enumerate(rows,1):
            name=str(row.get(name_key,''))
            if term.lower() in name.lower() and name.lower() not in chosen:
                if name_key=='Model' and memory(row.get('RAM')) is not None and memory(row['RAM'])<8:continue
                chosen.add(name.lower())
                yield number,row,term
                break

def clean(value):
    if isinstance(value,str):
        value=value.strip()
        if value.lower() in PLACEHOLDERS: return None
    return value

def first(row,*keys):
    return next((clean(row[k]) for k in keys if k in row and clean(row[k]) is not None),None)

def numeric(value):
    if value is None:return None
    try:
        result=float(str(value).replace(',',''))
        return result if result>=0 and result<float('inf') else None
    except ValueError:return None

def memory(value):
    if value is None:return None
    match=re.fullmatch(r'(\d+(?:\.\d+)?)\s*(GB)?',str(value),re.I)
    return float(match[1]) if match else None

def catalog_record(row,ref,source_file,line,sha,category):
    # Preserve all original attributes; each optional common field has a literal source column.
    record={'record_id':hashlib.sha256(f'{ref}:{source_file}:{line}'.encode()).hexdigest(),
            'source_dataset':ref,'source_file':source_file,'source_row':line,'source_sha256':sha,
            'category':category,'brand':first(row,'Brand','Company'),
            'model':first(row,'name','Laptop','Product','Model'),'part_number':first(row,'Part No'),
            'cpu':first(row,'Processor Model','CPU','Processor','Cpu Model'),
            'ram_gb':memory(first(row,'RAM','Ram','Ram Size')),
            'gpu':first(row,'Graphics Chipset','GPU','Gpu Model'),
            'screen_inches':numeric(first(row,'Display Size (Inch)','Inches','Screen','Screen Size (inch)')),
            'socket':first(row,'socket'),'form_factor':first(row,'form_factor'),
            'price_original':numeric(first(row,'price','Price_euros','Final Price','Price')),
            'currency': 'EUR' if 'Price_euros' in row else None,
            'currency_raw':first(row,'Currency'),
            'shop_price_vnd':None,'cost_price':None,'stock':None,'supplier':None,
            'provenance_type':'external_observation','approved_for_shop_sales':False,
            'attributes':{k:clean(v) for k,v in row.items() if k}}
    if ref=='docyx/pc-part-dataset':
        record['currency']='USD'
        record['currency_basis']='PCPartPicker dataset; user-provided source description'
    return record

def products():
    OUT.mkdir(parents=True,exist_ok=True)
    stage=OUT/'research_catalog.building.sqlite'
    if stage.exists(): stage.unlink()
    con=sqlite3.connect(stage)
    con.execute('CREATE TABLE products(record_id TEXT PRIMARY KEY, source_dataset TEXT, category TEXT, brand TEXT, model TEXT, ram_gb REAL, screen_inches REAL, currency TEXT, price_original REAL, record_json TEXT NOT NULL)')
    counts=Counter()
    fingerprints=set()
    duplicate=0
    output=OUT/'product_catalog.jsonl'
    with output.with_suffix('.jsonl.part').open('w',encoding='utf-8') as target:
        def emit(record):
            nonlocal duplicate
            fingerprint=hashlib.sha256(json.dumps(record['attributes'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            key=(record['source_dataset'],record['category'],fingerprint)
            if key in fingerprints:
                duplicate+=1
                return
            fingerprints.add(key)
            record.update(selection_status='representative_candidate_not_sales_ranking',
                          bestseller_verified=False,needs_current_vietnam_sku_validation=True)
            body=json.dumps(record,ensure_ascii=False,allow_nan=False)
            target.write(body+'\n')
            con.execute('INSERT INTO products VALUES(?,?,?,?,?,?,?,?,?,?)',
                        tuple(record[k] for k in ('record_id','source_dataset','category','brand','model','ram_gb','screen_inches','currency','price_original'))+(body,))
            counts[record['source_dataset']]+=1
        repo=ROOT/'references'/'pc-part-dataset'
        revision=subprocess.run(['git','-c','safe.directory='+str(repo),'-C',str(repo),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
        (OUT/'pc-parts-source.json').write_text(json.dumps({'repo':'https://github.com/docyx/pc-part-dataset','commit':revision,
            'repository_license':'MIT; see original LICENSE','data_rights':'Underlying PCPartPicker terms require separate review before redistribution',
            'observed_snapshot':'2025-07-23 according to README','not_current_shop_inventory':True},indent=2),encoding='utf-8')
        for path in sorted((repo/'data'/'json').glob('*.json')):
            if path.stem not in PART_SELECTION:continue
            sha=hashlib.sha256(path.read_bytes()).hexdigest()
            for line,row,term in select_candidates(json.loads(path.read_text(encoding='utf-8')),PART_SELECTION[path.stem],'name'):
                record=catalog_record(row,'docyx/pc-part-dataset',str(path.relative_to(repo)),line,sha,path.stem)
                record['selection_term']=term
                emit(record)
        for manifest in sorted(RAW.glob('msjahid__ryans-laptop*/manifest.json')):
            meta=json.loads(manifest.read_text(encoding='utf-8'))
            if meta.get('status')!='downloaded':continue
            for item in meta.get('files',[]):
                path=manifest.parent/item['file']
                if path.suffix.lower()!='.csv' or 'Unclean' in path.name:continue
                sha=hashlib.sha256(path.read_bytes()).hexdigest()
                with path.open(encoding='utf-8-sig',newline='') as stream:
                    rows=list(csv.DictReader(stream))
                for line,row,term in select_candidates(rows,LAPTOP_SELECTION,'Model'):
                    record=catalog_record(row,meta['dataset'],item['file'],line+1,sha,'laptop')
                    record['selection_term']=term
                    emit(record)
    output.with_suffix('.jsonl.part').replace(output)
    con.execute('CREATE INDEX products_category ON products(category)')
    con.execute('CREATE INDEX products_model ON products(model)')
    con.commit()
    con.close()
    stage.replace(OUT/'research_catalog.sqlite')
    report={'records_by_source':dict(counts),'records':sum(counts.values()),'exact_duplicates_removed':duplicate,
            'curation':'Compact selection requested by user; not the entire downloaded catalog.',
            'bestseller_claim':'Not established. Current Vietnamese family presence is not evidence of SKU sales rank.',
            'no_cross_source_entity_resolution':True,'missing_fields':'null, never inferred',
            'limitations':['No live Vietnam shop price, inventory or warranty claims.',
              'A dollar symbol alone is not mapped to USD. Unknown currency remains null.',
              'eBay rows are listings; not verified completed sales.',
              'CPU socket is absent in many source rows; do not infer Build PC compatibility.',
              'Clean/unclean eBay are alternate versions; only clean version in normalized catalog.',
              'REES46 product IDs have no verified mapping to this catalog; never join by brand alone.']}
    (OUT/'catalog-quality.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False),flush=True)

def inventory():
    records=[]
    for path in sorted(RAW.glob('*/manifest.json')):
        m=json.loads(path.read_text(encoding='utf-8'))
        records.append({'manifest':str(path.relative_to(ROOT)),**m})
    strategy=ROOT/'data'/'unstructured'/'reference'/'retail_strategy'/'manifest.json'
    docs=json.loads(strategy.read_text(encoding='utf-8')) if strategy.exists() else []
    record={'structured_sources':records,'unstructured_sources':docs,
            'combination_policy':'Evidence joined by topic/category and period only. No fabricated product-ID mapping or shop financial facts.',
            'synthetic_data_included_in_research_corpus':False}
    (OUT/'source_catalog.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':
    products()
    inventory()
