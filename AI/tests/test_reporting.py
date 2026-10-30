from io import BytesIO
from pathlib import Path
import pytest
from PIL import Image
from shopbot.business_analysis import analyze_business
from shopbot.engine import Engine
from shopbot.reporting import render_report_png, report_fingerprint, explain_visual

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'


@pytest.mark.parametrize('kind',['overview','financial_flow'])
def test_png_provenance_and_dimensions(kind):
    report=analyze_business(DB,'2026-07-01','2026-10-01')
    png=render_report_png(report,kind)
    with Image.open(BytesIO(png)) as image:
        assert image.format=='PNG'
        assert min(image.size)>=750
        assert image.info['ReportSHA256']==report_fingerprint(report)
        assert image.info['DataSource']=='demo'
        image.verify()


def test_no_invented_empty_chart():
    report=analyze_business(DB,'2030-01-01','2031-01-01')
    with pytest.raises(ValueError,match='Không có dữ liệu'):
        render_report_png(report)


def test_visual_explanation_uses_exact_report_values():
    report=analyze_business(DB,'2026-07-01','2026-10-01')
    explanation=explain_visual(report)
    value=report['financial']['operating_profit_before_interest_tax']
    assert f'{abs(value):,}'.replace(',','.') in explanation
    assert 'kết luận nguyên nhân' in explanation


def test_diagram_routing_and_acl(monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER','demo');monkeypatch.setenv('KEV_BASE_URL','')
    engine=Engine(DB)
    result=engine.ask('Vẽ sơ đồ lợi nhuận quý 3 năm 2026 và phân tích','admin')
    assert result['intent']=='business_analysis' and result['visualization']=='financial_flow'
    assert engine.ask('Vẽ sơ đồ lợi nhuận quý 3 năm 2026','customer')['intent']=='denied'
    missing=engine.ask('Vẽ sơ đồ báo cáo','admin')
    assert 'analysis' not in missing and not missing['rows']


def test_ui_export_choices_and_repeated_reports(monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv('SHOP_DATABASE','data/business_sql/scenario_v1/shop.sqlite')
    monkeypatch.setenv('ADMIN_PASSWORD','test-password-only')
    monkeypatch.setenv('LLM_PROVIDER','demo');monkeypatch.setenv('KEV_BASE_URL','')
    app=AppTest.from_file(ROOT/'app.py').run(timeout=30)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    app.text_input[0].set_value('test-password-only').run(timeout=30)
    question='Vẽ sơ đồ lợi nhuận quý 3 năm 2026 và phân tích'
    app.chat_input[0].set_value(question).run(timeout=30)
    assert not app.exception
    assert app.selectbox[0].value=='Sơ đồ lời/lỗ'
    assert len(app.get('download_button'))==1
    app.selectbox[0].set_value('Báo cáo tổng quan').run(timeout=30)
    assert not app.exception
    app.chat_input[0].set_value(question).run(timeout=30)
    assert not app.exception and len(app.get('download_button'))==2
