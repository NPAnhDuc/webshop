from pathlib import Path
from shopbot.business_analysis import analyze_business
from shopbot.business_review import review_business

DB=Path(__file__).resolve().parents[1]/'data/business_sql/scenario_v1/shop.sqlite'


def test_review_reconciles_categories_and_target_without_attribution():
    report=analyze_business(DB,'2026-09-01','2026-10-01')
    result=review_business(DB,report,[])
    assert result['target']==1_539_000_000 and result['variance']==-349_092_000
    assert sum(r['revenue'] for r in result['categories'])==1_189_908_000
    assert sum(r['gross_profit'] for r in result['categories'])==report['totals']['gross_profit']
    assert 'chưa thể quy phần hụt' in result['answer']
    assert '349.092.000' in result['answer'] and result['priorities']
    assert result['inventory_as_of']=='2026-09-30'


def test_future_target_is_unknown_and_document_must_support_target():
    report=analyze_business(DB,'2026-10-01','2026-11-01')
    result=review_business(DB,report,[dict(doc_type='sales_plan',text='mục tiêu tháng khác',source='wrong.md',section=1)])
    assert not result['target'] and result['variance'] is None
    assert 'Chưa có mục tiêu' in result['answer']
    assert all(r.get('source')!='wrong.md' for r in result['sources'])
