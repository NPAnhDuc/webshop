"""Deterministic retail scenario. External product facts + explicitly synthetic trade.

No foreign transaction IDs are re-labelled as these products. All trade tables
reference the original catalog IDs. Full inventory/cost accounting is checked by
validate_simulated_shop.py before the scenario is selected in the application.
"""
import calendar
from collections import Counter, defaultdict, deque
import csv
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import random
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data/business_sql/scenario_v1'
START, END = date(2025, 10, 1), date(2026, 9, 30)
SEED = 20261019
SEASON = {1: 1.12, 2: .68, 3: .91, 4: .94, 5: .97, 6: .94,
          7: 1.02, 8: 1.32, 9: 1.14, 10: .98, 11: 1.30, 12: 1.18}
WEIGHTS = {'laptop': .43, 'cpu': .075, 'video-card': .065,
           'motherboard': .055, 'memory': .075, 'internal-hard-drive': .09,
           'power-supply': .035, 'case': .03, 'monitor': .065, 'mouse': .08}
MARGINS = {'laptop': .135, 'cpu': .16, 'video-card': .11,
           'motherboard': .19, 'memory': .23, 'internal-hard-drive': .20,
           'power-supply': .23, 'case': .25, 'monitor': .18, 'mouse': .32}
BOUNDS = {'cpu': (1800000, 15000000), 'video-card': (6500000, 22000000),
          'motherboard': (1800000, 11000000), 'memory': (900000, 6500000),
          'internal-hard-drive': (850000, 6500000), 'power-supply': (950000, 4200000),
          'case': (850000, 3800000), 'monitor': (2100000, 9500000), 'mouse': (450000, 2500000)}
# Scenario prices by exact model/configuration tier, not a current market quote.
# Keep the RNG draws below unchanged so price reviews do not alter demand/events.
LAPTOP_PRICES = {
 'Lenovo LOQ Gaming 15IRH8':17500000, 'Lenovo Legion Slim 5i 16IRH8':26000000,
 'Asus TUF Gaming A15 FA506NF':16500000, 'HP Victus Gaming 15-fa1251TX':19900000,
 'Acer Nitro 5 AN515-58-59JP':18900000, 'Asus VivoBook 15 X1500EA':13900000,
 'Lenovo IdeaPad Slim 3i 15ITL6':13500000, 'Dell Inspiron 15 3520':13900000,
 'Acer Aspire 5 5P-A515-58P':14900000, 'Apple MacBook Air (Late 2020)':18900000,
 'Asus ZenBook 14 UM425UA':14900000, 'MSI Modern 15 B12M':14500000,
 'Acer Swift Go 14 SFG14-41-R5RB':15900000, 'Dell Latitude 3430':15500000,
 'HP 15-fd0202TU':15500000, 'Lenovo ThinkBook 15 G2 ITL':14500000,
 'Dell Vostro 15 3510':13500000, 'Acer Aspire 3 A315-59-56VC':12900000,
 'Gigabyte Gaming G5 MF':21900000}

SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE suppliers(id TEXT PRIMARY KEY,name TEXT,lead_days INTEGER);
CREATE TABLE products(sku TEXT PRIMARY KEY,name TEXT,price INTEGER,stock INTEGER,
 panel TEXT,ram INTEGER,battery REAL,weight REAL,category TEXT);
CREATE TABLE product_facts(sku TEXT PRIMARY KEY REFERENCES products(sku),
 record_json TEXT NOT NULL CHECK(json_valid(record_json)),segment TEXT,
 standard_cost INTEGER,price_basis TEXT NOT NULL,synthetic INTEGER NOT NULL CHECK(synthetic=1));
CREATE TABLE customers(id TEXT PRIMARY KEY,segment TEXT NOT NULL);
CREATE TABLE campaigns(id TEXT PRIMARY KEY,name TEXT,start TEXT,end TEXT,
 budget INTEGER CHECK(budget>=0),discount_bps INTEGER CHECK(discount_bps BETWEEN 0 AND 10000));
CREATE TABLE orders(id TEXT PRIMARY KEY,day TEXT NOT NULL,customer_id TEXT REFERENCES customers(id),
 channel TEXT NOT NULL CHECK(channel IN ('store','website','social')),campaign_id TEXT REFERENCES campaigns(id));
CREATE TABLE order_items(id TEXT PRIMARY KEY,order_id TEXT NOT NULL REFERENCES orders(id),
 sku TEXT NOT NULL REFERENCES products(sku),quantity INTEGER CHECK(quantity>0),
 list_price INTEGER,discount INTEGER,revenue INTEGER CHECK(revenue>=0),cost INTEGER CHECK(cost>=0));
CREATE TABLE purchase_orders(id TEXT PRIMARY KEY,ordered_day TEXT,supplier_id TEXT REFERENCES suppliers(id),due_day TEXT);
CREATE TABLE purchase_lines(id TEXT PRIMARY KEY,po_id TEXT REFERENCES purchase_orders(id),
 sku TEXT NOT NULL REFERENCES products(sku),quantity INTEGER CHECK(quantity>0),unit_cost INTEGER CHECK(unit_cost>0));
CREATE TABLE receipts(id TEXT PRIMARY KEY,line_id TEXT UNIQUE REFERENCES purchase_lines(id),
 day TEXT,sku TEXT NOT NULL REFERENCES products(sku),quantity INTEGER,unit_cost INTEGER);
CREATE TABLE returns(id TEXT PRIMARY KEY,item_id TEXT UNIQUE NOT NULL REFERENCES order_items(id),
 day TEXT,sku TEXT NOT NULL REFERENCES products(sku),quantity INTEGER CHECK(quantity=1),
 refund INTEGER,cost_reversal INTEGER,restock INTEGER CHECK(restock IN (0,1)),reason TEXT);
CREATE TABLE inventory_moves(id INTEGER PRIMARY KEY,day TEXT NOT NULL,sku TEXT NOT NULL REFERENCES products(sku),
 delta INTEGER NOT NULL,cost_delta INTEGER NOT NULL,kind TEXT NOT NULL,source_id TEXT NOT NULL);
CREATE TABLE inventory_daily(day TEXT,sku TEXT NOT NULL REFERENCES products(sku),
 quantity INTEGER CHECK(quantity>=0),value INTEGER CHECK(value>=0),PRIMARY KEY(day,sku));
CREATE TABLE financial_ledger(id TEXT PRIMARY KEY,day TEXT,sku TEXT NOT NULL REFERENCES products(sku),
 quantity INTEGER,revenue INTEGER,cost INTEGER,kind TEXT CHECK(kind IN ('sale','return')),
 CHECK((kind='sale' AND quantity>0 AND revenue>=0 AND cost>=0)
 OR (kind='return' AND quantity<0 AND revenue<=0 AND cost<=0)));
CREATE VIEW sales AS SELECT day,sku,quantity,revenue,cost FROM financial_ledger;
CREATE TABLE operating_expenses(id TEXT PRIMARY KEY,day TEXT,category TEXT,
 amount INTEGER CHECK(amount>=0),campaign_id TEXT REFERENCES campaigns(id));
CREATE TABLE monthly_targets(month TEXT PRIMARY KEY,revenue INTEGER,gross_margin_bps INTEGER);
CREATE INDEX items_sku ON order_items(sku);
CREATE INDEX ledger_day ON financial_ledger(day);
CREATE INDEX moves_sku_day ON inventory_moves(sku,day);
CREATE VIEW monthly_pnl AS
 WITH s AS (SELECT substr(day,1,7) month,SUM(revenue) net_revenue,
 SUM(cost) net_cogs,SUM(quantity) net_units FROM financial_ledger GROUP BY month),
 e AS (SELECT substr(day,1,7) month,SUM(amount) operating_expenses FROM operating_expenses GROUP BY month),
 o AS (SELECT substr(day,1,7) month,COUNT(*) order_count FROM orders GROUP BY month),
 r AS (SELECT substr(day,1,7) month,SUM(quantity) return_units,SUM(refund) refunds FROM returns GROUP BY month),
 p AS (SELECT substr(day,1,7) month,SUM(quantity*unit_cost) purchases_received FROM receipts GROUP BY month)
 SELECT s.*,s.net_revenue-s.net_cogs gross_profit,
 COALESCE(e.operating_expenses,0) operating_expenses,
 s.net_revenue-s.net_cogs-COALESCE(e.operating_expenses,0) operating_profit_before_interest_tax,
 o.order_count,COALESCE(r.return_units,0) return_units,COALESCE(r.refunds,0) refunds,
 COALESCE(p.purchases_received,0) purchases_received,
 s.net_revenue-COALESCE(p.purchases_received,0)-COALESCE(e.operating_expenses,0) operating_cash_flow_assuming_cash_settlement,
 t.revenue target_revenue FROM s LEFT JOIN e USING(month) LEFT JOIN o USING(month)
 LEFT JOIN r USING(month) LEFT JOIN p USING(month) LEFT JOIN monthly_targets t USING(month);
'''


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def poisson(rng, mean):
    count, product = 0, 1.
    while product > math.exp(-mean):
        count += 1
        product *= rng.random()
    return count - 1


def first_number(value):
    match = re.search(r'\d+(?:\.\d+)?', str(value or ''))
    return float(match[0]) if match else None


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    records = [json.loads(line) for line in (ROOT/'data/structured/processed/product_catalog.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(records) >= 60
    rng = random.Random(SEED)
    stage = OUT/'shop.building.sqlite'
    if stage.exists():
        stage.unlink()
    con = sqlite3.connect(stage)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    con.executemany('INSERT INTO metadata VALUES (?,?)', [
        ('source','demo'), ('scenario_id','retail_sim_v1'),('data_kind','synthetic'),
        ('period_start',str(START)),('period_end',str(END)),('currency','VND'),
        ('knowledge_dir','data/business_sql/scenario_v1/documents'),
        ('accounting_basis','FIFO, accrual revenue; all values exclude VAT; no interest or income-tax model'),
        ('seed',str(SEED))])
    con.executemany('INSERT INTO suppliers VALUES (?,?,?)', [
        ('SUP-LAP','Nhà phân phối laptop giả lập',4),('SUP-PC','Nhà phân phối linh kiện giả lập',3)])
    by_category = defaultdict(list)
    state = {}
    for record in records:
        sku, category, name = record['record_id'], record['category'], record['model']
        gaming = category == 'laptop' and any(t in name.lower() for t in ('loq','legion','tuf','victus','nitro','gaming'))
        if category == 'laptop':
            price = rng.randrange(1900, 3100, 50)*10000 if gaming else rng.randrange(1150, 2100, 50)*10000
            if 'macbook' in name.lower(): price = 24500000
            price = LAPTOP_PRICES.get(name,price)
        else:
            low, high = BOUNDS[category]
            # Fixed scenario multiplier, NOT a verified live exchange rate or VN price.
            estimate = (record['price_original'] or (low+high)/2/26000)*26000
            price = round(max(low,min(high,estimate*rng.uniform(.92,1.08)))/10000)*10000
        cost = round(price*(1-MARGINS[category])/1000)*1000
        attrs = record['attributes']
        panel = attrs.get('Display Type') or ''
        weight = first_number(attrs.get('Weight (Kg)'))
        con.execute('INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?)',
                    (sku,name,price,0,panel,record['ram_gb'],None,weight,category))
        segment = 'gaming' if gaming else ('office' if category=='laptop' else category)
        con.execute('INSERT INTO product_facts VALUES (?,?,?,?,?,1)',
                    (sku,json.dumps(record,ensure_ascii=False),segment,cost,'Explicit scenario assumption; no live VN quote'))
        state[sku] = dict(record=record,price=price,cost=cost,segment=segment,lots=deque(),stock=0,
                          popularity=rng.lognormvariate(0,.65),reorder=1 if category=='laptop' else 3)
        by_category[category].append(sku)
    gaming_skus = [s for s,v in state.items() if v['segment']=='gaming'][:2]
    slow_skus = [s for s,v in state.items() if v['segment']=='office'][:3]
    pending = defaultdict(list)
    planned_returns = defaultdict(list)
    events = []
    counter = Counter()
    def move(day,sku,delta,cost_delta,kind,source):
        con.execute('INSERT INTO inventory_moves(day,sku,delta,cost_delta,kind,source_id) VALUES (?,?,?,?,?,?)',
                    (str(day),sku,delta,cost_delta,kind,source))
    def receive_lot(sku,quantity,cost):
        state[sku]['lots'].append([quantity,cost])
        state[sku]['stock'] += quantity
    def consume(sku):
        lot = state[sku]['lots'][0]
        cost = lot[1]
        lot[0] -= 1
        state[sku]['stock'] -= 1
        if not lot[0]: state[sku]['lots'].popleft()
        return cost
    for sku,v in state.items():
        quantity = 0 if sku in gaming_skus else (6 if sku in slow_skus else (2 if v['record']['category']=='laptop' else 5))
        if quantity:
            receive_lot(sku,quantity,v['cost'])
            move(START,sku,quantity,quantity*v['cost'],'opening',sku)
    customers = [(f'CUST-{i:04d}',rng.choices(['one_off','loyal','deal_seeker','business'],[.55,.2,.2,.05])[0]) for i in range(1,1201)]
    con.executemany('INSERT INTO customers VALUES (?,?)',customers)
    campaigns = [('C-BUNDLE','Bundle laptop và chuột','2025-11-01','2025-11-30',24000000,200),
                 ('C-TET','Ưu đãi trước Tết','2026-01-15','2026-02-10',18000000,300),
                 ('C-BTS','Tựu trường laptop văn phòng','2026-08-01','2026-08-31',28000000,600)]
    con.executemany('INSERT INTO campaigns VALUES (?,?,?,?,?,?)',campaigns)
    cats = list(WEIGHTS)
    first_purchase = {}
    lost = Counter()
    for offset in range((END-START).days+1):
        day = START+timedelta(days=offset)
        for line_id,sku,qty,cost in pending.pop(day,[]):
            counter['receipt'] += 1
            rid = f'GR-{counter["receipt"]:06d}'
            con.execute('INSERT INTO receipts VALUES (?,?,?,?,?,?)',(rid,line_id,str(day),sku,qty,cost))
            receive_lot(sku,qty,cost)
            move(day,sku,qty,qty*cost,'receipt',rid)
        for item_id,sku,revenue,cost,restock,reason in planned_returns.pop(day,[]):
            counter['return'] += 1
            rid = f'RET-{counter["return"]:06d}'
            reversal = cost if restock else 0
            con.execute('INSERT INTO returns VALUES (?,?,?,?,?,?,?,?,?)',(rid,item_id,str(day),sku,1,revenue,reversal,int(restock),reason))
            con.execute('INSERT INTO financial_ledger VALUES (?,?,?,?,?,?,?)',(rid,str(day),sku,-1,-revenue,-reversal,'return'))
            if restock:
                receive_lot(sku,1,cost)
                move(day,sku,1,cost,'return',rid)
        active = next((c for c in campaigns if c[2]<=str(day)<=c[3]),None)
        mean = 3.8*SEASON[day.month]*(1.22 if day.weekday()>=5 else 1.)
        if date(2026,2,15)<=day<=date(2026,2,20): mean *= .30
        if day.month == 8: mean *= 1.10
        for _ in range(poisson(rng,mean)):
            category = rng.choices(cats,[WEIGHTS[c] for c in cats])[0]
            pool = by_category[category]
            popularity = [state[s]['popularity']*(.15 if s in slow_skus else 1.) for s in pool]
            sku = rng.choices(pool,popularity)[0]
            if state[sku]['stock'] <= 0:
                lost[(str(day),sku)] += 1
                continue
            basket = [sku]
            if category=='laptop' and rng.random() < (.70 if active and active[0]=='C-BUNDLE' else .33):
                basket.append(rng.choice(by_category['mouse']))
            if category in ('cpu','motherboard') and rng.random()<.35:
                basket.append(rng.choice(by_category['memory']))
            if category=='memory' and rng.random()<.27:
                basket.append(rng.choice(by_category['internal-hard-drive']))
            basket = [s for s in dict.fromkeys(basket) if state[s]['stock']>0]
            counter['order'] += 1
            oid = f'ORD-{counter["order"]:06d}'
            customer = rng.choice(customers if rng.random()<.75 else customers[:150])[0]
            first_purchase.setdefault(customer,str(day))
            channel = rng.choices(['store','website','social'],[.55,.3,.15])[0]
            con.execute('INSERT INTO orders VALUES (?,?,?,?,?)',(oid,str(day),customer,channel,active[0] if active else None))
            for sku in basket:
                v = state[sku]
                counter['item'] += 1
                iid = f'ITEM-{counter["item"]:06d}'
                bps = active[5] if active and (active[0]!='C-BTS' or v['segment']=='office') else 0
                discount = round(v['price']*bps/10000/1000)*1000
                revenue = v['price']-discount
                cost = consume(sku)
                con.execute('INSERT INTO order_items VALUES (?,?,?,?,?,?,?,?)',(iid,oid,sku,1,v['price'],discount,revenue,cost))
                con.execute('INSERT INTO financial_ledger VALUES (?,?,?,?,?,?,?)',(iid,str(day),sku,1,revenue,cost,'sale'))
                move(day,sku,-1,-cost,'sale',iid)
                probability = .018 if v['record']['category']=='laptop' else .012
                defect = v['record']['category']=='internal-hard-drive' and day.month==6
                if defect: probability = .18
                if rng.random()<probability:
                    rday = day+timedelta(days=rng.randint(2,14))
                    restock = not defect and rng.random()<.80
                    if rday<=END:
                        planned_returns[rday].append((iid,sku,revenue,cost,restock,'lỗi lô SSD giả lập' if defect else 'đổi trả giả lập'))
        if day.weekday()==0:
            already_pending = {s for batch in pending.values() for _,s,_,_ in batch}
            for sku,v in state.items():
                if v['stock']>=v['reorder'] or sku in already_pending: continue
                if sku in gaming_skus and day<date(2025,10,19): continue
                supplier = 'SUP-LAP' if v['record']['category']=='laptop' else 'SUP-PC'
                lead = 4 if supplier=='SUP-LAP' else 3
                due = day+timedelta(days=lead)
                counter['purchase'] += 1
                po = f'PO-{counter["purchase"]:06d}'
                line = po+'-1'
                qty = (4 if supplier=='SUP-LAP' else 8)-v['stock']
                cost = round(v['cost']*rng.uniform(.985,1.015)/1000)*1000
                con.execute('INSERT INTO purchase_orders VALUES (?,?,?,?)',(po,str(day),supplier,str(due)))
                con.execute('INSERT INTO purchase_lines VALUES (?,?,?,?,?)',(line,po,sku,qty,cost))
                pending[due].append((line,sku,qty,cost))
        for sku,v in state.items():
            value = sum(q*c for q,c in v['lots'])
            con.execute('INSERT INTO inventory_daily VALUES (?,?,?,?)',(str(day),sku,v['stock'],value))
        if day.day == calendar.monthrange(day.year,day.month)[1]:
            month = str(day)[:7]
            target = round(1350000000*SEASON[day.month]/1000000)*1000000
            con.execute('INSERT INTO monthly_targets VALUES (?,?,?)',(month,target,1450))
            fixed = {'rent':22000000,'payroll_including_owner':52000000,'utilities':3500000,
                     'software':1800000,'administration':3500000,'depreciation':3000000}
            for category,amount in fixed.items():
                con.execute('INSERT INTO operating_expenses VALUES (?,?,?,?,?)',(month+'-'+category,str(day),category,amount,None))
            sales = con.execute('SELECT SUM(revenue) FROM financial_ledger WHERE substr(day,1,7)=?',(month,)).fetchone()[0] or 0
            for category,amount in [('payment_and_delivery',round(sales*.011)),('always_on_marketing',12000000)]:
                con.execute('INSERT INTO operating_expenses VALUES (?,?,?,?,?)',(month+'-'+category,str(day),category,amount,None))
            for campaign in campaigns:
                if campaign[2][:7] == month:
                    con.execute('INSERT INTO operating_expenses VALUES (?,?,?,?,?)',(month+'-'+campaign[0],str(day),'campaign_marketing',campaign[4],campaign[0]))
    for sku,v in state.items(): con.execute('UPDATE products SET stock=? WHERE sku=?',(v['stock'],sku))
    con.commit()
    summary = [dict(r) for r in con.execute('SELECT * FROM monthly_pnl ORDER BY month')]
    counts = {table:con.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0] for table in
              ['products','orders','order_items','purchase_orders','receipts','returns','inventory_daily','operating_expenses']}
    opening = con.execute("SELECT SUM(cost_delta) FROM inventory_moves WHERE kind='opening'").fetchone()[0]
    closing = con.execute('SELECT SUM(value) FROM inventory_daily WHERE day=?',(str(END),)).fetchone()[0]
    assumptions = {'scenario_id':'retail_sim_v1','synthetic':True,'seed':SEED,'period_start':str(START),'period_end':str(END),
        'store':{'locations':1,'staff_including_owner':5,'channels':['store','website','social']},
        'expected_monthly_revenue_reference_vnd':[1000000000,1500000000],
        'base_purchase_attempts_per_day':3.8,'monthly_seasonality':SEASON,'category_demand_weights':WEIGHTS,
        'gross_margin_before_promotions_by_category':MARGINS,'opening_inventory_value_vnd':opening,
        'pricing':'Explicit simulation price bands; parts use source USD price x assumed 26000 and bounded scenario multiplier. Not live prices or an observed FX rate.',
        'laptop_model_price_assumptions_vnd':LAPTOP_PRICES,
        'cost_method':'FIFO with ±1.5% synthetic purchase cost variation; returns restore original item cost only if saleable.',
        'accounting':'All prices exclude VAT; no income tax or interest model. Output is operating profit before interest/tax, not net profit.',
        'cash_flow':'Immediate customer/supplier cash settlement assumed; depreciation excluded from cash flow in export view.',
        'calibration':'REES46 category/price/event/basket statistics exported separately. No ID join, no direct scaling of a national chain into this shop.',
        'source_context':[{'url':'https://acbs.com.vn/Files/Domains/ACBS/WFL-1585/250508065942-1015-1015000001.pdf',
                           'use':'Context only: FPT Shop revenue growth can coexist with losses; no copying chain financial ratios into this scenario.'}],
        'not_proven':['current market prices','bestseller rank','real shop turnover','real forecast accuracy','causal campaign incrementality']}
    # Depreciation is a noncash expense: add it back only for the cash-flow measure.
    con.execute('DROP VIEW monthly_pnl')
    # Keep accounting logic explicit and exported in the SQL, not patched in report values.
    view = SCHEMA[SCHEMA.index('CREATE VIEW monthly_pnl'):]
    view = view.replace('s.net_revenue-COALESCE(p.purchases_received,0)-COALESCE(e.operating_expenses,0) operating_cash_flow',
                        "s.net_revenue-COALESCE(p.purchases_received,0)-COALESCE(e.operating_expenses,0)+COALESCE((SELECT SUM(amount) FROM operating_expenses WHERE category='depreciation' AND substr(day,1,7)=s.month),0) operating_cash_flow")
    con.executescript(view)
    summary = [dict(r) for r in con.execute('SELECT * FROM monthly_pnl ORDER BY month')]
    # Only completed receipts represent inventory/purchase cash. Outstanding POs are commitments.
    manifest = {'synthetic':True,'scenario_id':'retail_sim_v1','period':[str(START),str(END)],'counts':counts,
                'catalog_sha256':hashlib.sha256((ROOT/'data/structured/processed/product_catalog.jsonl').read_bytes()).hexdigest(),
                'opening_inventory_value':opening,'closing_inventory_value':closing,
                'net_revenue':sum(r['net_revenue'] for r in summary),
                'gross_profit':sum(r['gross_profit'] for r in summary),
                'operating_profit_before_interest_tax':sum(r['operating_profit_before_interest_tax'] for r in summary),
                'monthly_revenue_min':min(r['net_revenue'] for r in summary),'monthly_revenue_max':max(r['net_revenue'] for r in summary)}
    write_json(OUT/'assumptions.json',assumptions)
    write_json(OUT/'monthly_summary.json',summary)
    write_json(OUT/'manifest.json',manifest)
    evaluation = OUT/'evaluation_only'
    evaluation.mkdir(exist_ok=True)
    write_json(evaluation/'planted_events.json',[
        {'event_id':'E-STOCKOUT','period':['2025-10-01','2025-10-23'],'skus':gaming_skus,'mechanism':'Opening=0, delay initial purchase; inspect actual receipts/snapshots before explaining observed sales.'},
        {'event_id':'E-RETURNS','period':['2026-06-01','2026-06-30'],'category':'internal-hard-drive','return_probability':.18,'baseline_return_probability':.012},
        {'event_id':'E-OVERSTOCK','skus':slow_skus,'mechanism':'Opening=6 each, demand weight x0.15.'},
        {'event_id':'E-BUNDLE','campaign_id':'C-BUNDLE','mechanism':'Laptop mouse attachment probability .70 vs baseline .33; observational comparison alone not causal proof.'}])
    write_json(evaluation/'latent_demand_not_observed_sales.json',[
        {'day':d,'sku':s,'unfilled_attempts':n} for (d,s),n in sorted(lost.items())])
    csv_dir = OUT/'csv'
    csv_dir.mkdir(exist_ok=True)
    for table in ['products','orders','order_items','purchase_orders','purchase_lines','receipts','returns','inventory_moves','inventory_daily','operating_expenses','monthly_pnl']:
        cursor = con.execute(f'SELECT * FROM {table}')
        with (csv_dir/(table+'.csv')).open('w',encoding='utf-8-sig',newline='') as stream:
            writer=csv.writer(stream);writer.writerow([v[0] for v in cursor.description]);writer.writerows(cursor)
    sql = '-- SYNTHETIC SCENARIO ONLY. INTEGER VND EXCLUDING VAT. NOT REAL SHOP SALES.\nPRAGMA foreign_keys=OFF;\n'+'\n'.join(con.iterdump())+'\nPRAGMA foreign_keys=ON;\n'
    (OUT/'shop.sqlite.sql').write_text(sql,encoding='utf-8')
    con.close()
    stage.replace(OUT/'shop.sqlite')
    print(json.dumps(manifest,ensure_ascii=False))


if __name__=='__main__': build()
