"""Bounded-memory profiling, not cross-source entity matching or shop facts."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics

ROOT=Path(__file__).resolve().parents[1]


def build():
    path=ROOT/'data/structured/raw/mkechinov__ecommerce-events-history-in-electronics-store/original/events.csv'
    events=Counter();categories=Counter();months=Counter();prices=[];purchases=0
    rng=random.Random(42)
    with path.open(encoding='utf-8-sig',newline='') as stream:
        for row in csv.DictReader(stream):
            events[row['event_type']]+=1
            if row['event_type']!='purchase': continue
            purchases+=1
            categories[row['category_code'] or 'unknown']+=1
            months[row['event_time'][:7]]+=1
            price=float(row['price'])
            if len(prices)<10000: prices.append(price)
            else:
                index=rng.randrange(purchases)
                if index<len(prices): prices[index]=price
    path2=ROOT/'data/structured/raw/mkechinov__ecommerce-purchase-history-from-electronics-store/original/kz.csv'
    baskets=Counter()
    with path2.open(encoding='utf-8-sig',newline='') as stream:
        for i,row in enumerate(csv.DictReader(stream)):
            if i>=200000: break
            baskets[row['order_id']]+=1
    report={'source_event_rows':sum(events.values()),'event_counts':dict(events),
            'purchase_event_fraction_not_session_conversion':events['purchase']/sum(events.values()),
            'purchase_category_counts':dict(categories.most_common(30)),
            'purchase_month_counts':dict(sorted(months.items())),
            'source_price_median_not_vnd':statistics.median(prices),
            'purchase_price_reservoir_size':len(prices),
            'purchase_history_head_sample_rows':sum(baskets.values()),
            'sample_order_ids':len(baskets),'head_sample_mean_lines_per_order':statistics.mean(baskets.values()),
            'limitations':['Source price currency is not verified here; no VND conversion.',
                           'Head sample can truncate orders and is not a random or seasonally representative sample.',
                           'These distributions are comparison context. Shop category mix, demand and margins remain explicit assumptions.',
                           'Purchase event fraction is not a conversion rate per user/session.',
                           'No source product IDs mapped to the 67 product IDs.'],
            'source_manifest_paths':[str(path.parent.parent/'manifest.json'),str(path2.parent.parent/'manifest.json')]}
    out=ROOT/'data/business_sql/scenario_v1/source_profile.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__': build()
