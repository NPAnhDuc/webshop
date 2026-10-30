from datetime import date
import importlib.util
import json
from pathlib import Path
import sqlite3
from shopbot.engine import Engine
from shopbot.retrieval import search
from shopbot.chunking import chunk_document

ROOT=Path(__file__).resolve().parents[1]
SCENARIO=ROOT/'data/business_sql/scenario_v1'


def test_full_reconciliation():
    spec=importlib.util.spec_from_file_location('reconcile',ROOT/'scripts/validate_simulated_shop.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    report=module.validate(SCENARIO)
    assert report['passed'] and report['products']==67 and report['products_with_sales']==67


def test_simulation_engine_includes_returns_expenses_and_matching_plan(monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER','demo');monkeypatch.setenv('KEV_BASE_URL','')
    engine=Engine(SCENARIO/'shop.sqlite')
    r=engine.ask('Phân tích kinh doanh quý 3 năm 2026','admin')
    with sqlite3.connect(SCENARIO/'shop.sqlite') as con:
        expected=con.execute("SELECT SUM(net_revenue),SUM(operating_profit_before_interest_tax) FROM monthly_pnl WHERE month>='2026-07'").fetchone()
    assert r['analysis']['totals']['revenue']==expected[0]
    assert r['analysis']['financial']['operating_profit_before_interest_tax']==expected[1]
    assert sum(c['net_revenue'] for c in r['analysis']['financial']['channels'])==expected[0]
    assert any('sales-plan-2026-Q3' in d['source'] for d in r['sources'])
    assert 'mô phỏng' in r['answer']
    assert 'DEMO-' not in engine.ask('Laptop dưới 20 triệu')['answer']
    named=engine.ask('Lenovo LOQ Gaming 15IRH8 còn hàng không?')
    assert len(named['rows'])==1 and named['rows'][0]['name']=='Lenovo LOQ Gaming 15IRH8'


def test_version_acl_and_no_future_reports():
    path=SCENARIO/'shop.sqlite'
    first=search('biên lợi nhuận tối thiểu laptop','admin',db_path=path,as_of=date(2026,2,15),doc_types={'policy'})
    second=search('biên lợi nhuận tối thiểu laptop','admin',db_path=path,as_of=date(2026,8,15),doc_types={'policy'})
    assert any('pricing-policy-v1' in d['source'] for d in first)
    assert all('pricing-policy-v2' not in d['source'] for d in first)
    assert any('pricing-policy-v2' in d['source'] for d in second)
    public=search('mục tiêu doanh thu kế hoạch biên lợi nhuận','customer',db_path=path)
    assert all(d['audience']=='customer' for d in public)
    early=search('báo cáo tháng doanh thu lợi nhuận','admin',db_path=path,as_of=date(2025,10,15),doc_types={'monthly_report'})
    assert not early


def test_historical_policy_routing_and_version(monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER','demo');monkeypatch.setenv('KEV_BASE_URL','')
    engine=Engine(SCENARIO/'shop.sqlite')
    r=engine.ask('Biên lợi nhuận tối thiểu laptop theo chính sách tháng 2 năm 2026','admin')
    assert r['intent']=='documents'
    assert any('pricing-policy-v1' in d['source'] for d in r['sources'])
    assert all('pricing-policy-v2' not in d['source'] for d in r['sources'])


def test_table_headers_and_sentences_are_retained():
    text='# Kế hoạch\n\n## Mục tiêu\n\nDoanh thu là 100 đồng. Biên gộp là 10 phần trăm.\n\n'
    text+='| Tháng | Mục tiêu |\n|---|---:|\n'+'\n'.join(f'| {i} | {i*100} |' for i in range(1,12))
    chunks=chunk_document({'source':'test.md','text':text},max_words=25)
    assert any('Doanh thu là 100 đồng.' in c['text'] for c in chunks)
    tables=[c for c in chunks if '| 1 |' in c['text'] or '| 10 |' in c['text']]
    assert tables and all('| Tháng | Mục tiêu |' in c['text'] for c in tables)
    assert all('Kế hoạch > Mục tiêu'==c['heading_path'] for c in chunks)


def test_v2_splits_preserve_frozen_groups_and_periods():
    folder=ROOT/'training'
    old=[json.loads(s) for s in (folder/'data/corpus.jsonl').read_text(encoding='utf-8').splitlines()]
    new={r['id']:r for r in [json.loads(s) for s in (folder/'v2/data/corpus.jsonl').read_text(encoding='utf-8').splitlines()]}
    assert all(new[r['id']]['split']==r['split'] for r in old)
    cases=[json.loads(s) for s in (folder/'v2/data/tool_cases.jsonl').read_text(encoding='utf-8').splitlines()]
    assert all(c['split']=='test' for c in cases if c['group_id']>='2026-08')
    assert all(c['split']!='train' for c in cases if c['group_id']>='2026-06')
    corpus_text=' '.join(r['text'] for r in new.values())
    assert 'unfilled_attempts' not in corpus_text and 'planted_events' not in corpus_text


def test_new_simulation_streamlit(monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv('SHOP_DATABASE','data/business_sql/scenario_v1/shop.sqlite')
    monkeypatch.setenv('ADMIN_PASSWORD','test-password-only')
    monkeypatch.setenv('LLM_PROVIDER','demo');monkeypatch.setenv('KEV_BASE_URL','')
    app=AppTest.from_file(ROOT/'app.py').run(timeout=30)
    assert not app.exception
    assert any('67 SKU' in item.value for item in app.caption)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    app.text_input[0].set_value('test-password-only').run(timeout=30)
    app.chat_input[0].set_value('Phân tích kinh doanh quý 3 năm 2026').run(timeout=30)
    assert not app.exception and len(app.get('vega_lite_chart'))==2
    assert any('Lợi nhuận hoạt động' in item.value for item in app.markdown)
