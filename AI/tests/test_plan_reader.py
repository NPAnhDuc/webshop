from datetime import date
from pathlib import Path

from shopbot.plan_reader import answer_plan, plan_request
from shopbot.rag_scope import resolve_scope
from shopbot.retrieval import normalize

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "data/business_sql/scenario_v1/documents"
TODAY = date(2026, 10, 26)
QUARTERS = ("2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3")


def request(question, role="admin", previous=None):
    return plan_request(question, role, resolve_scope(question, TODAY, previous))


def test_all_approved_quarter_targets_and_month_rows_match_source_files():
    from shopbot.chunking import chunk_document
    from shopbot.rag_answer import evidence_fragments

    for quarter in QUARTERS:
        plan_path = DOCS / f"sales-plan-{quarter}-v1.md"
        source_text = plan_path.read_text(encoding="utf-8")
        plan_request_data = {"metric": "quarter_net_sales", "period": quarter, "month": None}
        for metric, marker in (
            ("quarter_net_sales", "muc tieu doanh thu thuan sau hoan tra"),
            ("gross_margin", "bien loi nhuan gop muc tieu"),
            ("marketing", "marketing thuong xuyen"),
        ):
            result = answer_plan({**plan_request_data, "metric": metric})
            assert result["answerability"] == "full"
            assert result["source"]["document_id"] == f"sales-plan-{quarter}"
            assert result["source"]["status"] == "approved"
            assert result["source"]["source"].endswith("-v1.md")
            assert marker in normalize(result["claim"]["text"])
            assert result["claim"]["text"] in source_text
            assert result["claim"]["evidence"][0]["quotes"]
            assert f"[Nguồn: sales-plan-{quarter}-v1.md," in result["answer"]

        for month in (int(quarter[-1]) * 3 - 2, int(quarter[-1]) * 3 - 1, int(quarter[-1]) * 3):
            year = int(quarter[:4])
            month_id = f"{year:04}-{month:02}"
            result = answer_plan({"metric": "month_sales", "period": quarter, "month": month_id})
            line = next(line for line in source_text.splitlines() if line.startswith(f"| {month_id} |"))
            assert result["answerability"] == "full"
            assert line in result["claim"]["text"]
            assert result["claim"]["evidence"][0]["quotes"][-1] == line
            document = {"text": source_text, "source": plan_path.name,
                        "document_id": f"sales-plan-{quarter}", "title": f"Kế hoạch {quarter}",
                        "version": 1, "doc_type": "sales_plan", "status": "approved",
                        "audience": "admin", "data_kind": "demo"}
            fragments = evidence_fragments(chunk_document(document))
            assert any(line in fragment["quotes"] for fragment in fragments.values())


def test_three_question_phrasings_per_metric_include_unaccented_and_trigger_words():
    variants = {
        "quarter_net_sales": [
            "Mục tiêu doanh thu thuần quý 3/2026 là bao nhiêu?",
            "Doanh thu thuần kế hoạch quý 3 năm 2026 ở mức nào?",
            "Chi tieu doanh so thuan quy 3/2026 co muc nao?",
            "Tính doanh thu thuần mục tiêu quý 3/2026, chưa VAT?",
            "Lấy doanh thu thuần sau hoàn trả quý 3/2026 trong kế hoạch.",
        ],
        "gross_margin": [
            "Biên gộp mục tiêu quý 3/2026 là bao nhiêu?",
            "Biên lợi nhuận gộp trong kế hoạch quý 3/2026 ở mức nào?",
            "Ke hoach bien gop quy 3/2026 la bao nhieu?",
        ],
        "month_sales": [
            "Mục tiêu doanh thu tháng 8/2026 là bao nhiêu?",
            "Lấy doanh thu mục tiêu tháng 8 năm 2026 trong kế hoạch.",
            "Doanh thu kế hoạch tháng 8/2026 đang ghi mức nào?",
        ],
        "marketing": [
            "Ngân sách marketing kế hoạch quý 3/2026 là bao nhiêu?",
            "Marketing thường xuyên theo kế hoạch quý 3/2026 ở mức nào?",
            "Tinh ngan sach marketing ke hoach quy 3/2026 giup minh.",
        ],
    }
    # "lai" without accents is also "lại"; it must not count as a profit target.
    variants["quarter_net_sales"].append("Nhắc lại mục tiêu doanh thu thuần quý 3/2026 giúp mình.")
    variants["month_sales"].append("Lấy lại doanh thu mục tiêu tháng 8/2026 trong kế hoạch.")
    for metric, questions in variants.items():
        assert len(questions) >= 3
        for question in questions:
            req = request(question)
            assert req is not None, question
            assert req["metric"] == metric, (question, req)


def test_missing_approved_periods_never_fall_back_to_draft():
    for period in ("2026-Q4", "2027-Q1", "2025-Q2"):
        result = answer_plan({"metric": "quarter_net_sales", "period": period, "month": None})
        assert "Chưa có kế hoạch đã duyệt" in result["answer"]
        assert period in result["answer"]
        assert result["answerability"] == "none"
        assert result["source"] is None and result["claim"] is None
        assert not (DOCS / f"sales-plan-{period}-v1.md").exists()
        assert not (DOCS / f"sales-plan-{period}-draft-v1.md").exists()


def test_plan_request_returns_none_for_non_single_target_questions():
    none_cases = [
        ("Mục tiêu doanh thu thuần quý 3/2026 là bao nhiêu?", "customer"),
        ("So sánh doanh thu mục tiêu quý 1 và quý 2/2026.", "admin"),
        ("Doanh thu thuần quý 3/2026 vượt kế hoạch bao nhiêu?", "admin"),
        ("Biên gộp trong bản nháp kế hoạch quý 3/2026 là bao nhiêu?", "admin"),
        ("Doanh thu thực hiện quý 3/2026 là bao nhiêu?", "admin"),
        ("Mục tiêu doanh thu thuần quý 3/2026 và biên gộp là bao nhiêu?", "admin"),
        ("Doanh thu mục tiêu đang ghi mức nào?", "admin"),
        ("Mục tiêu tháng 8 và tháng 9/2026 doanh thu ra sao?", "admin"),
        # Monthly-report questions that list several metrics are not plan targets.
        ("Từ báo cáo 4/2026, trả riêng từng chỉ tiêu: doanh thu thuần; giá vốn; lợi nhuận gộp.", "admin"),
        ("bao cao thang 2/2026 cho tung chi tieu doanh thu, gia von, don hang", "admin"),
        ("Báo cáo tháng 8/2026 ghi chỉ tiêu doanh thu thuần là bao nhiêu?", "admin"),
        ("Chỉ tiêu doanh thu và lợi nhuận gộp tháng 5/2026 là bao nhiêu?", "admin"),
        ("Kế hoạch quý 2/2026 đặt mục tiêu doanh thu và số đơn hàng thế nào?", "admin"),
    ]
    for question, role in none_cases:
        assert request(question, role) is None, question


def test_unnamed_quarter_target_defaults_to_net_sales_only_when_unambiguous():
    positives = [
        "Mục tiêu quý 2/2026 là bao nhiêu?",
        "Lấy chỉ tiêu quý 4/2026 trong kế hoạch.",
        "chi tieu quy 1 nam 2026 la bao nhieu?",
        "Tính mục tiêu quý 2/2026 sau hoàn trả, chưa VAT.",
        "Mục tiêu quý 4/2026 là bao nhiêu?",
    ]
    for question in positives:
        req = request(question)
        assert req == {"metric": "quarter_net_sales", "period": resolve_scope(question, TODAY)["quarters"][0], "month": None}
    missing = request("Lấy chỉ tiêu quý 4/2026 trong kế hoạch.")
    result = answer_plan(missing)
    assert result["answerability"] == "none"
    assert "2026-Q4" in result["answer"]

    negatives = [
        ("Mục tiêu biên lợi nhuận quý 2/2026 là bao nhiêu?", "admin"),
        ("Mục tiêu số đơn hàng quý 2/2026 là bao nhiêu?", "admin"),
        ("Mục tiêu tháng 8/2026 là bao nhiêu?", "admin"),
        ("Mục tiêu quý 2/2026 là bao nhiêu?", "customer"),
    ]
    for question, role in negatives:
        assert request(question, role) is None, question


def test_quarter_and_month_use_month_sales_only_when_month_is_inside_quarter():
    positives = [
        "Kế hoạch 2026-Q2 đặt doanh thu tháng 5 là bao nhiêu?",
        "Mục tiêu quý 2/2026, lấy doanh thu tháng 5 trong kế hoạch.",
        "Ke hoach quy 2 nam 2026 dat muc tieu doanh thu thang 5 la bao nhieu?",
        "Kế hoạch quý 2/2026, tính mục tiêu doanh thu tháng 5 sau hoàn trả.",
    ]
    for question in positives:
        req = request(question)
        assert req is not None, question
        assert req["metric"] == "month_sales"
        assert req["period"] == "2026-Q2" and req["month"] == "2026-05"
        result = answer_plan(req)
        assert result["answerability"] == "full"
        expected = next(line for line in (DOCS / "sales-plan-2026-Q2-v1.md").read_text(encoding="utf-8").splitlines()
                        if line.startswith("| 2026-05 |"))
        assert expected in result["claim"]["text"]

    negatives = [
        ("Mục tiêu quý 2/2026, doanh thu tháng 7 là bao nhiêu?", "admin"),
        ("Mục tiêu quý 2/2026, biên gộp tháng 5 là bao nhiêu?", "admin"),
        ("Mục tiêu quý 2/2026, doanh thu tháng 5 là bao nhiêu?", "customer"),
    ]
    for question, role in negatives:
        assert request(question, role) is None, question


def test_grounded_answer_short_circuits_router_and_selector(monkeypatch):
    from shopbot import grounded_rag, rag_answer

    def forbidden(*args, **kwargs):
        raise AssertionError("plan read must not call a model")

    monkeypatch.setattr(grounded_rag, "chat", forbidden)
    monkeypatch.setattr(rag_answer, "chat", forbidden)
    question = "Tính doanh thu thuần mục tiêu quý 3/2026, chưa VAT?"
    result = grounded_rag.answer(
        question, "admin", {}, DOCS.parent / "shop.sqlite", TODAY,
    )
    assert result["basic_action"] == "answer"
    assert result["rag"]["answerability"] == "full"
    assert result["rag"]["method"] == "deterministic approved-plan lookup"
    assert result["trace"][-1] == "plan: target read by code (no router, no model selection)"
    assert len(result["sources"]) == 1
    source = result["sources"][0]
    assert source["source"] == "sales-plan-2026-Q3-v1.md"
    assert source["doc_type"] == "sales_plan" and source["status"] == "approved"
    assert f"[Nguồn: {source['source']}, mục {source['heading_path']}, đoạn {source['section']}, phiên bản 1]" in result["answer"]
    claim = result["rag"]["claims"][0]
    assert claim["text"] in result["answer"]
    assert claim["evidence"][0]["chunk_id"] == source["chunk_id"]
    assert claim["evidence"][0]["quotes"]


def test_grounded_answer_for_missing_plan_also_skips_models(monkeypatch):
    from shopbot import grounded_rag

    monkeypatch.setattr(grounded_rag, "chat", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("router called")))
    result = grounded_rag.answer(
        "Mục tiêu doanh thu thuần quý 4/2026 là bao nhiêu?", "admin", {},
        DOCS.parent / "shop.sqlite", TODAY,
    )
    assert result["rag"]["answerability"] == "none"
    assert "Chưa có kế hoạch đã duyệt cho kỳ 2026-Q4." == result["answer"]
    assert not result["sources"] and not result["rag"]["claims"]
    assert result["trace"][-1] == "plan: target read by code (no router, no model selection)"
