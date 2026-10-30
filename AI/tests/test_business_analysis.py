import pytest
from shopbot.store import initialize, connect
from shopbot.engine import Engine
from shopbot.business_analysis import analyze_business, format_business_report


@pytest.fixture
def ledger(tmp_path, monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER', 'demo')
    monkeypatch.setenv('KEV_BASE_URL', '')
    path = tmp_path / 'shop.db'
    initialize(path)
    with connect(path) as con:
        con.execute('DELETE FROM sales')
        con.executemany('INSERT INTO sales VALUES (?,?,?,?,?)', [
            ('2026-09-01','DEMO-A',2,200,120),
            ('2026-09-02','DEMO-A',1,100,60),
            ('2026-09-03','DEMO-B',1,100,140),
            ('2026-10-01','DEMO-B',1,999,1)])
    return path


def test_accounting_boundaries_weighted_margin_and_loss(ledger):
    report = analyze_business(ledger, '2026-09-01', '2026-10-01')
    assert report['totals'] == dict(units=4, revenue=400, cost=320, gross_profit=80, gross_margin_pct=20)
    assert report['quality']['source_rows'] == 3
    assert report['products'][0]['revenue_share_pct'] == 75
    assert report['products'][1]['gross_profit'] == -40
    assert report['net_profit'] is None
    assert 'DEMO-B' in format_business_report(report)


def test_unknown_versus_zero_revenue(ledger):
    empty = analyze_business(ledger, '2030-01-01', '2031-01-01')
    assert 'chưa thể kết luận' in format_business_report(empty)
    with connect(ledger) as con:
        con.execute('UPDATE sales SET revenue=0 WHERE day<?', ('2026-10-01',))
    report = analyze_business(ledger, '2026-09-01', '2026-10-01')
    assert report['totals']['gross_margin_pct'] is None
    assert report['totals']['gross_profit'] == -320


def test_missing_cost_not_silently_imputed(ledger):
    with connect(ledger) as con:
        con.execute("UPDATE sales SET cost=NULL WHERE sku='DEMO-A'")
    with pytest.raises(ValueError, match='thiếu'):
        analyze_business(ledger, '2026-09-01', '2026-10-01')


def test_engine_access_citations_and_period(ledger):
    engine = Engine(ledger)
    result = engine.ask('Phân tích kinh doanh tháng 9 năm 2026', 'admin')
    assert result['analysis']['totals']['gross_profit'] == 80
    assert result['sources'][0]['source_rows'] == 3
    assert 'Lợi nhuận gộp' in result['answer']
    for question in ('Phân tích kinh doanh tháng 9 năm 2026', 'Lãi lỗ tháng 9', 'Biên gộp'):
        denied = engine.ask(question, 'customer')
        assert denied['intent'] == 'denied' and not denied['rows']
    assert not engine.ask('Phân tích kinh doanh', 'admin')['rows']


def test_streamlit_analysis_charts(monkeypatch):
    from pathlib import Path
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv('ADMIN_PASSWORD', 'test-password-only')
    monkeypatch.setenv('LLM_PROVIDER', 'demo')
    monkeypatch.setenv('KEV_BASE_URL', '')
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / 'app.py').run(timeout=30)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    app.text_input[0].set_value('test-password-only').run(timeout=30)
    app.chat_input[0].set_value('Phân tích kinh doanh quý 3 năm 2026').run(timeout=30)
    assert not app.exception
    assert any('Biên lợi nhuận gộp:' in item.value for item in app.markdown)
    assert len(app.get('vega_lite_chart')) == 2
