from streamlit.testing.v1 import AppTest
from pathlib import Path
APP=Path(__file__).resolve().parents[1]/'app.py'

def test_customer_chat(monkeypatch):
    monkeypatch.setenv('LLM_PROVIDER','demo')
    monkeypatch.setenv('KEV_BASE_URL','')
    app=AppTest.from_file(APP).run(timeout=30)
    assert not app.exception
    app.chat_input[0].set_value('Laptop tầm 20 triệu màn hình đẹp').run(timeout=30)
    assert not app.exception
    assert any('DEMO-A' in item.value for item in app.markdown)

def test_admin_requires_password(monkeypatch):
    monkeypatch.setenv('ADMIN_PASSWORD','')
    app=AppTest.from_file(APP).run(timeout=30)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    assert not app.chat_input
    assert not app.exception

def test_admin_chart(monkeypatch):
    monkeypatch.setenv('ADMIN_PASSWORD','test-password-only')
    monkeypatch.setenv('LLM_PROVIDER','demo')
    app=AppTest.from_file(APP).run(timeout=30)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    app.text_input[0].set_value('test-password-only').run(timeout=30)
    app.chat_input[0].set_value('Doanh thu quý 3 năm 2026').run(timeout=30)
    assert not app.exception
    assert any('Doanh thu:' in item.value for item in app.markdown)




def test_admin_logout_and_customer_isolation(monkeypatch):
    monkeypatch.setenv('ADMIN_PASSWORD','test-password-only')
    monkeypatch.setenv('LLM_PROVIDER','demo')
    monkeypatch.setenv('KEV_BASE_URL','')
    app=AppTest.from_file(APP).run(timeout=30)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    app.text_input[0].set_value('test-password-only').run(timeout=30)
    app.chat_input[0].set_value('Doanh thu tháng 9 năm 2026').run(timeout=30)
    app.radio[0].set_value('Người mua').run(timeout=30)
    assert not any('Doanh thu:' in item.value for item in app.markdown)
    app.radio[0].set_value('Chủ shop').run(timeout=30)
    app.text_input[0].set_value('test-password-only').run(timeout=30)
    next(b for b in app.button if b.label=='Đăng xuất').click().run(timeout=30)
    assert not app.chat_input
    assert not app.exception
