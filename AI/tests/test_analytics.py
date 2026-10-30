from shopbot.analytics import compare_periods
from shopbot.store import initialize,AdminTools

def test_comparison_exact(tmp_path):
    p=tmp_path/'shop.db';initialize(p);t=AdminTools(p)
    r=compare_periods('Doanh thu quý 3 so với quý 2 năm 2026',t)
    a=sum(v['revenue'] for v in t.revenue('2026-07-01','2026-10-01'))
    b=sum(v['revenue'] for v in t.revenue('2026-04-01','2026-07-01'))
    assert r['difference']==a-b
    assert r['percent']==round((a-b)/b*100,2)
    assert [v['revenue'] for v in r['rows']]==[a,b]
