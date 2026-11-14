"""Synthetic regression cases for bound-model retrieval; no evaluation banks."""
import sqlite3
from datetime import date

import pytest

from shopbot import grounded_rag, retrieval
from shopbot.knowledge import KnowledgeStore

TODAY = date(2026, 10, 31)
TITLE = 'Atlas AX123'
TECHNICAL = {'product', 'glossary', 'buying_guide'}


def document(identifier, title, text, kind='glossary', named=False):
    return dict(document_id=identifier, chunk_id=identifier + '-1', title=title,
                text=text, source=identifier + '.md', version=1, section=1,
                heading_path='test', authority='shop_document', audience='customer',
                data_kind='shop', status='approved', effective_from='2026-01-01',
                doc_type=kind, retrieval='explicit named product' if named else 'TF-IDF fallback')


def pipeline(monkeypatch, *, bound=True, types=('product', 'policy'), strict=False):
    calls, offered = [], []
    product = document('catalog-atlas', TITLE, 'Bộ nhớ: cấu hình tiêu chuẩn.', 'product', True)
    policy = document('policy', 'Quy định cửa hàng', 'Điều kiện hỗ trợ cần hóa đơn.', 'policy')
    article = document('memory', 'Bộ nhớ và ứng dụng', 'Bộ nhớ tạm giữ dữ liệu ứng dụng.')

    def search(*_, **kwargs):
        calls.append(kwargs['doc_types'])
        docs = ([product] if bound else []) + [policy]
        return docs + ([article] if TECHNICAL <= set(kwargs['doc_types'] or []) else [])

    def chat(system, payload, schema, **_):
        if 'parts' not in payload:
            return dict(action='answer', query='unused', doc_types=list(types),
                        strict_filters=strict, private_request=False, task='lookup')
        offered.append(payload)
        return dict(action='answer', answers={key: [] for key in payload['parts']},
                    missing=list(payload['parts']), negative=[])

    monkeypatch.setenv('VI_EMBEDDING_URL', '')
    monkeypatch.setenv('VI_UNDERSTANDING_URL', '')
    monkeypatch.setenv('RAG_RERANK', '0')
    monkeypatch.setenv('RAG_EVIDENCE_RERANK', '0')
    monkeypatch.setattr('shopbot.product_lookup.product_names', lambda _: [TITLE] if bound else [])
    monkeypatch.setattr('shopbot.product_lookup.lookup', lambda *_, **__: None)
    monkeypatch.setattr('shopbot.budget_advice.advise', lambda *_, **__: None)
    monkeypatch.setattr('shopbot.route_guard.corpus_words', lambda: frozenset())
    monkeypatch.setattr(grounded_rag, 'search', search)
    monkeypatch.setattr(grounded_rag, 'chat', chat)
    return calls, offered


def test_mixed_route_adds_technical_articles_only_for_bound_model(monkeypatch):
    calls, offered = pipeline(monkeypatch)
    grounded_rag.answer(f'Giải thích cơ chế bộ nhớ của {TITLE}?', 'customer', {}, 'unused', TODAY)
    assert calls == [['product', 'policy'], ['buying_guide', 'glossary', 'policy', 'product']]
    assert any(source['title'] == 'Bộ nhớ và ứng dụng' for p in offered for source in p['sources'])
    assert 'policy' in calls[1]

    # The same mixed route with no explicit named record keeps the previous path.
    calls, _ = pipeline(monkeypatch, bound=False)
    grounded_rag.answer('Giải thích cơ chế bộ nhớ của laptop?', 'customer', {}, 'unused', TODAY)
    assert calls == [['product', 'policy']]


@pytest.mark.parametrize('types,strict', [(('policy',), False), (('product', 'policy'), True)])
def test_pure_policy_and_strict_routes_keep_their_searches(monkeypatch, types, strict):
    calls, _ = pipeline(monkeypatch, types=types, strict=strict)
    grounded_rag.answer(f'Điều kiện hỗ trợ cho {TITLE}?', 'customer', {}, 'unused', TODAY)
    assert calls == [list(types)]


def test_catalog_name_gives_context_to_guard_but_unknown_name_does_not(monkeypatch):
    question = f'Nhờ tư vấn tốc độ của {TITLE} có phụ thuộc dung lượng không?'
    from shopbot.route_guard import guard
    assert guard(question, 'customer', known_products=[TITLE]) == 'outside'
    calls, offered = pipeline(monkeypatch, types=('product',))
    result = grounded_rag.answer(question, 'customer', {}, 'unused', TODAY)
    assert calls and offered
    assert 'route guard: outside reconsidered for named catalog product' in result['trace']
    calls, _ = pipeline(monkeypatch, bound=False, types=('product',))
    result = grounded_rag.answer(question, 'customer', {}, 'unused', TODAY)
    assert result['basic_action'] == 'outside' and not calls


@pytest.mark.parametrize('suffix,keep_variant', [('', True), ('-Z9', True), ('-K8', False)])
def test_scoped_search_keeps_hyphenated_family_article_without_other_skus(monkeypatch, tmp_path, suffix, keep_variant):
    db = tmp_path / 'shop.sqlite'
    with sqlite3.connect(db) as con:
        con.execute('CREATE TABLE metadata (key TEXT, value TEXT)')
    docs = [
        document('catalog', TITLE, 'memory sockets standard', 'product'),
        document('variant', TITLE + '-Z9: memory sockets', 'memory sockets regional details'),
        document('foreign', 'Vega VX456: memory sockets', 'memory sockets unrelated machine'),
        document('prefix', 'Atlas AX1234: memory sockets', 'memory sockets other generation'),
        document('other-sku', TITLE + '-Z9', 'memory sockets regional catalog', 'product'),
    ]
    monkeypatch.setenv('VI_EMBEDDING_URL', '')
    monkeypatch.setenv('RAG_RERANK', '0')
    monkeypatch.setattr(retrieval, 'ROOT', tmp_path)
    monkeypatch.setattr(retrieval, 'dataset_source', lambda _: 'shop')
    monkeypatch.setattr(retrieval, 'read_json', lambda *args: {'documents': docs})
    monkeypatch.setattr(KnowledgeStore, 'records', lambda _: [])
    monkeypatch.setattr('shopbot.dense_retrieval.dense_scores', lambda *_: None)
    found = retrieval.search(f'{TITLE}{suffix} memory sockets', 'customer', db_path=db, as_of=TODAY,
                             doc_types=['product', 'glossary'], top_k=12,
                             scope={'months': [], 'quarters': []})
    ids = {d['document_id'] for d in found}
    assert 'catalog' in ids
    assert ('variant' in ids) is keep_variant
    assert not ids & {'foreign', 'prefix'}
    # Only an explicitly requested variant may bind its own catalog record.
    assert ('other-sku' in ids) is (suffix == '-Z9')


def test_family_reference_survives_isolation_without_confirming_variant_catalog():
    question = f'{TITLE} memory sockets'
    products = [dict(title=TITLE)]
    variant = document('variant', TITLE + '-Z9: memory sockets',
                       'Only the Z9 variant has these sockets; other variants require checking.')
    assert retrieval.about_model(variant, retrieval.normalize(question), products)
    assert 'other variants require checking' in variant['text']
    assert not retrieval.about_model(dict(variant, doc_type='product'), retrieval.normalize(question), products)
    assert not retrieval.about_model(dict(variant, title='Atlas AX1234: memory sockets'),
                                     retrieval.normalize(question), products)


@pytest.mark.parametrize('suffix,kept', [('', True), ('-Z9', True), ('-K8', False)])
def test_about_model_keeps_only_the_requested_variant_or_general_family(suffix, kept):
    article = document('variant', TITLE + '-Z9: memory sockets', 'Z9 regional details.')
    question = retrieval.normalize(f'{TITLE}{suffix} memory sockets')
    assert retrieval.about_model(article, question, [dict(title=TITLE)]) is kept
