from datetime import date

import pytest

from shopbot import grounded_rag
from scripts.probe_bound_generic import FIELD_TRACE, probe_case, summarize

TODAY = date(2026, 10, 31)
TITLE = "Laptop Atlas A123"


def document(identifier, title, text, kind="glossary", named=False):
    return dict(document_id=identifier, chunk_id=identifier + "-1", title=title,
                text=text, source=identifier + ".md", version=1, section=1,
                heading_path="test", authority="shop_document", audience="customer",
                doc_type=kind, retrieval="explicit named product" if named else "TF-IDF fallback")


def setup_pipeline(monkeypatch, extra=(), second_product=False):
    catalog = document("product-atlas", TITLE,
                       f"{TITLE}: RAM: 16 GB. {TITLE}: Installed SSD Type: NVMe PCIe.",
                       kind="product", named=True)
    second_title = "Laptop Vega V789"
    second = document("product-vega", second_title,
                      f"{second_title}: RAM: 32 GB.", kind="product", named=True)
    docs = [catalog, *([second] if second_product else []), *extra]
    captured, offered = [], []
    real_fragments = grounded_rag.evidence_fragments

    def search(*args, **kwargs):
        return [d for d in docs if d["doc_type"] == "product"] if kwargs.get("doc_types") == ["product"] else docs

    def fragments(items):
        captured.append(list(items))
        return real_fragments(items)

    def chat(system, payload, schema, **kwargs):
        if "parts" not in payload:
            return dict(action="answer", query="unused", doc_types=["product"],
                        strict_filters=False, task="lookup", private_request=False)
        offered.append(payload)
        parts = list(payload["parts"])
        return dict(action="answer", answers={key: [] for key in parts},
                    missing=parts, negative=[])

    monkeypatch.setenv("VI_EMBEDDING_URL", "")
    monkeypatch.setenv("RAG_RERANK", "0")
    monkeypatch.setenv("RAG_EVIDENCE_RERANK", "0")
    monkeypatch.setattr("shopbot.product_lookup.product_names", lambda db: [TITLE, second_title, "Lenovo ThinkBook 15 G2 ITL"])
    monkeypatch.setattr("shopbot.product_lookup.lookup", lambda *args, **kwargs: None)
    monkeypatch.setattr("shopbot.budget_advice.advise", lambda *args, **kwargs: None)
    monkeypatch.setattr("shopbot.route_guard.guard", lambda *args, **kwargs: None)
    monkeypatch.setattr(grounded_rag, "search", search)
    monkeypatch.setattr(grounded_rag, "evidence_fragments", fragments)
    monkeypatch.setattr(grounded_rag, "chat", chat)
    return catalog, captured, offered


@pytest.mark.parametrize("question", [
    f"RAM c\u1ee7a {TITLE} gi\u1eef d\u1eef li\u1ec7u l\u00fac m\u1edf \u1ee9ng d\u1ee5ng theo c\u01a1 ch\u1ebf n\u00e0o?",
    f"{TITLE} d\u00f9ng RAM kh\u00e1c SSD \u1edf \u0111i\u1ec3m g\u00ec l\u00fac ch\u1ea1y \u1ee9ng d\u1ee5ng?",
    f"Ch\u1ecdn lo\u1ea1i RAM cho {TITLE} c\u1ea7n ki\u1ec3m tra g\u00ec tr\u01b0\u1edbc?",
    f"RAM tr\u00ean {TITLE} n\u00ean \u0111\u01b0\u1ee3c hi\u1ec3u theo c\u00e1ch n\u00e0o?",
])
def test_concept_questions_never_answer_with_catalog_values(monkeypatch, question):
    setup_pipeline(monkeypatch)
    result = grounded_rag.answer(question, "customer", {}, "unused", TODAY)
    assert FIELD_TRACE not in result["trace"]
    assert result["basic_action"] == "answer"


@pytest.mark.parametrize("question", [
    f"Nh\u1edd xem {TITLE} c\u00f3 RAM bao nhi\u00eau GB?",
    f"{TITLE} lo\u1ea1i SSD g\u00ec v\u1eady?",
])
def test_attribute_value_questions_still_skip_selector(monkeypatch, question):
    _, _, offered = setup_pipeline(monkeypatch)
    result = grounded_rag.answer(question, "customer", {}, "unused", TODAY)
    assert FIELD_TRACE in result["trace"]
    assert not offered
    assert result["rag"]["claims"]


def test_generic_technology_reaches_selector_but_foreign_model_does_not(monkeypatch):
    generic = document("article-memory", "RAM ph\u1ee5c v\u1ee5 \u1ee9ng d\u1ee5ng nh\u01b0 th\u1ebf n\u00e0o?",
                       "B\u1ed9 nh\u1edb t\u1ea1m gi\u1eef d\u1eef li\u1ec7u c\u1ee7a \u1ee9ng d\u1ee5ng \u0111ang ho\u1ea1t \u0111\u1ed9ng.")
    foreign = document("article-other", "Laptop Orion B456: RAM",
                       "M\u00e1y Orion c\u00f3 b\u1ed9 nh\u1edb g\u1eafn ch\u1ebft.")
    other_family = document("article-thinkbook", "ThinkBook: RAM h\u00e0n",
                            "ThinkBook c\u00f3 b\u1ed9 nh\u1edb h\u00e0n.")
    _, captured, offered = setup_pipeline(monkeypatch, [generic, foreign, other_family])
    result = grounded_rag.answer(f"Gi\u1eef d\u1eef li\u1ec7u trong RAM c\u1ee7a {TITLE} ho\u1ea1t \u0111\u1ed9ng ra sao?",
                                 "customer", {}, "unused", TODAY)
    assert FIELD_TRACE not in result["trace"]
    assert {d["document_id"] for d in captured[0]} == {"product-atlas", "article-memory"}
    assert len(offered) == 2
    assert "RAM ph\u1ee5c v\u1ee5 \u1ee9ng d\u1ee5ng nh\u01b0 th\u1ebf n\u00e0o?" in {s["title"] for s in offered[-1]["sources"]}
    assert all("Orion" not in s["title"] and "ThinkBook" not in s["title"]
               for payload in offered for s in payload["sources"])
    assert result["profile"]["rag_product_subject"] == TITLE


def test_protocol_codes_are_not_mistaken_for_other_product_models():
    article = document("article-ddr", "DDR5: c\u00e1ch t\u1ed5 ch\u1ee9c b\u1ed9 nh\u1edb",
                       "B\u1ed9 nh\u1edb m\u1edbi thay \u0111\u1ed5i t\u1ed5 ch\u1ee9c truy c\u1eadp.")
    assert grounded_rag.generic_product_article(article, "Gi\u1ea3i th\u00edch RAM", [dict(title=TITLE)])
    foreign = document("article-other", "M\u00e1y B456: t\u1ed5 ch\u1ee9c b\u1ed9 nh\u1edb", "M\u1ed9t model kh\u00e1c.")
    assert not grounded_rag.generic_product_article(foreign, "Gi\u1ea3i th\u00edch RAM", [dict(title=TITLE)])


def test_probe_observes_expansion_isolation_and_actual_selector_sources(monkeypatch):
    article = document("article-memory", "RAM ph\u1ee5c v\u1ee5 \u1ee9ng d\u1ee5ng nh\u01b0 th\u1ebf n\u00e0o?",
                       "B\u1ed9 nh\u1edb t\u1ea1m gi\u1eef d\u1eef li\u1ec7u c\u1ee7a \u1ee9ng d\u1ee5ng \u0111ang ho\u1ea1t \u0111\u1ed9ng.")
    catalog, _, _ = setup_pipeline(monkeypatch, [article])
    row = dict(id="synthetic", kind="thieu", role="customer",
               question=f"RAM trong {TITLE} ho\u1ea1t \u0111\u1ed9ng ra sao khi m\u1edf \u1ee9ng d\u1ee5ng?",
               catalog_document_id="product-atlas", tech_document_id="article-memory")
    record = probe_case(row, [catalog, article], db="unused", today=TODAY)
    assert not record["fields_picked"]
    assert "article-memory" not in record["after_search"]
    assert "article-memory" in record["after_expansion"]
    assert "article-memory" in record["after_isolation"]
    assert "article-memory" in record["selector"]
    summary = summarize([record])["thieu"]
    assert summary["fields_picked"] == 0 and summary["selector"] == 1
    assert summary["dropped_at_isolation"] == 0


def test_general_article_does_not_need_to_repeat_the_query_vocabulary():
    article = document("article-general", "B\u1ed9 nh\u1edb \u0111a nhi\u1ec7m", "\u1ee8ng d\u1ee5ng gi\u1eef d\u1eef li\u1ec7u t\u1ea1m.")
    assert grounded_rag.generic_product_article(
        article, "RAM d\u00f9ng l\u00e0m g\u00ec?", [dict(title=TITLE)])


def test_family_article_requires_its_generation_to_be_supported_by_bound_source():
    owner = dict(title="NovaBook Air (2024)", text="Processor Model: N1.")
    matching = document("article-family", "NovaBook Air N1 2024: c\u1ed5ng", "C\u1ed5ng c\u1ee7a b\u1ea3n n\u00e0y.")
    foreign = document("article-family-other", "NovaBook Air N2 2024: c\u1ed5ng", "M\u1ed9t b\u1ea3n kh\u00e1c.")
    assert grounded_rag.generic_product_article(matching, "Gi\u1ea3i th\u00edch c\u1ed5ng", [owner])
    assert not grounded_rag.generic_product_article(foreign, "Gi\u1ea3i th\u00edch c\u1ed5ng", [owner])


@pytest.mark.parametrize("question", [
    f"Thông số RAM bên {TITLE} ra sao?",
    f"Thong so RAM ben {TITLE} ra sao?",
    f"Shop ơi, RAM của {TITLE} thế nào?",
    f"Cho mình hỏi RAM của {TITLE}.",
    f"{TITLE} dùng RAM gì vậy shop?",
    f"{TITLE} có RAM là gì vậy?",
    f"Đặt {TITLE} cạnh Laptop Vega V789 thì RAM mỗi máy thế nào?",
    f"{TITLE} ghi RAM dung lượng nào?",
    f"RAM của {TITLE} theo danh mục là gì?",
    f"RAM cua {TITLE} tn",
])
def test_value_phrasings_default_to_catalog_fields(monkeypatch, question):
    _, _, offered = setup_pipeline(monkeypatch, second_product=True)
    result = grounded_rag.answer(question, "customer", {}, "unused", TODAY)
    assert FIELD_TRACE in result["trace"]
    assert not offered
    assert result["rag"]["claims"]
    if "Vega" in question:
        claims = str(result["rag"]["claims"])
        assert "16 GB" in claims and "32 GB" in claims


def test_unmatched_value_field_keeps_general_article_for_selector(monkeypatch):
    article = document("article-battery", "Pin và thời lượng sử dụng",
                       "Thời lượng pin phụ thuộc tải của ứng dụng.")
    _, captured, offered = setup_pipeline(monkeypatch, [article])
    question = f"Shop ơi, pin của {TITLE} thế nào?"
    assert grounded_rag.catalog_value_request(question, [TITLE])
    result = grounded_rag.answer(question, "customer", {}, "unused", TODAY)
    assert FIELD_TRACE not in result["trace"]
    assert {d["document_id"] for d in captured[0]} == {"product-atlas", "article-battery"}
    assert offered
    assert article["title"] in {source["title"] for payload in offered
                                for source in payload["sources"]}
