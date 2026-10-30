"""Read-only numeric audit of failing document-report cases; not routing acceptance."""
import json,re,sqlite3,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
assert hashlib.sha256(DB.read_bytes()).hexdigest()=='f544a0a0255d78a06f01833275170a6f2eda89f2c9053a923433e420ca365028'
rows=json.loads((ROOT/'evaluation/quality_loop_20261024_kb3/kb3_guards_full_r1/results.json').read_text(encoding='utf-8'))
c=sqlite3.connect(DB.resolve().as_uri()+'?mode=ro',uri=True)
queries=dict(ledger='SELECT COALESCE(SUM(revenue),0), COALESCE(SUM(cost),0) FROM financial_ledger WHERE substr(day,1,7)=?',expenses='SELECT COALESCE(SUM(amount),0) FROM operating_expenses WHERE substr(day,1,7)=?',orders='SELECT COUNT(*) FROM orders WHERE substr(day,1,7)=?')
def oracle(month,metric):
 revenue,cost=c.execute(queries['ledger'],(month,)).fetchone()
 expenses=c.execute(queries['expenses'],(month,)).fetchone()[0]
 orders=c.execute(queries['orders'],(month,)).fetchone()[0]
 return dict(revenue=revenue,cost=cost,gross_profit=revenue-cost,expenses=expenses,operating_profit=revenue-cost-expenses,orders=orders)[metric]
def amount(text):
 m=re.search(r':\s*(-?[\d.]+)',text)
 assert m,text
 return int(m[1].replace('.',''))
audit=[]
for row in rows:
 if row['checks']['status']!='FAIL_CHECKS' or row['topic']!='monthly_single':continue
 assert len(row['result']['rag']['claims'])==1
 claim=row['result']['rag']['claims'][0];ev=claim['evidence'][0]
 month=ev['period'];metric=ev['metric'];value=amount(claim['text']);expected=oracle(month,metric)
 report_quote=row['checks']['issues'][0]['detail']['quote'];report_value=amount(report_quote)
 audit.append(dict(id=row['id'],period=month,metric=metric,actual=value,independent_sql=expected,frozen_report_value=report_value,numeric_match=value==expected==report_value,source_request_honored=False,conclusion='numeric equivalent, but document-reading request answered from SQL rather than requested report'))
assert len(audit)==57 and all(a['numeric_match'] for a in audit)
for month in ['2026-01','2026-09']:assert oracle(month,'revenue') in [1077004000,1189908000]
out=dict(cases=audit,queries=queries,numeric_matches=57,requested_document_source_mismatches=57,source_contract_accepted=False,bot_helpers_imported=False,db_sha256=hashlib.sha256(DB.read_bytes()).hexdigest(),model_calls=0,training_allowed=False,ingestion_allowed=False)
Path(__file__).with_name('numeric_source_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(numeric_matches=57,requested_document_source_mismatches=57,model_calls=0)))
