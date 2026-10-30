import pytest


@pytest.fixture(autouse=True)
def isolated_application_database(monkeypatch):
    # Tests explicitly use the legacy fixture, independent of the user's .env choice.
    monkeypatch.setenv('SHOP_DATABASE','data/structured/shop.db')
    monkeypatch.setenv('CHATBOT_MODE','tools')
    monkeypatch.setenv('CONVERSATION_MODE','legacy')
    monkeypatch.setenv('VI_EMBEDDING_URL','')
    monkeypatch.setenv('VI_UNDERSTANDING_URL','')
