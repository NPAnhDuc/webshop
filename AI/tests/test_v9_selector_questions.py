import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS = ROOT / "data/v9_selector/questions.json"
BUSINESS = ROOT / "data/business_sql/scenario_v1/documents"
POLICY_DIR = ROOT / "data/unstructured/managed/e397df083984c120"
OLD_DIRS = ("v6_questions", "v7_selector", "v8_router_questions")
METRIC_COUNTS = {
    "plan_quarter_sales": 8,
    "plan_margin": 6,
    "plan_marketing": 6,
    "plan_month_sales": 10,
    "net_sales": 8,
    "cogs": 5,
    "gross_profit": 6,
    "operating_cost": 5,
    "operating_profit": 5,
    "orders": 6,
    "returns": 5,
}


def normalized(text):
    text = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return " ".join(re.sub(r"[^\w\s]", " ", text).split())


def rows():
    return json.loads(QUESTIONS.read_text(encoding="utf-8"))


def source_for(row):
    filename = row["document_id"]
    path = (POLICY_DIR if filename.startswith("policy-") else BUSINESS) / filename
    return path.read_text(encoding="utf-8")


def bot_quote_units(row):
    from shopbot.chunking import chunk_document
    from shopbot.rag_answer import evidence_fragments

    filename = row["document_id"]
    document = dict(
        text=source_for(row), source=filename, title=filename, document_id=filename,
    )
    fragments = evidence_fragments(chunk_document(document))
    units = set()
    for fragment in fragments.values():
        quotes = fragment["quotes"]
        units.add(quotes[-1] if quotes[0].startswith("|") else quotes[0])
    return units


def test_counts_schema_ids_and_unique_questions():
    data = rows()
    assert Counter(row["kind"] for row in data) == {
        "chi_tieu": 70, "chinh_sach_khong_ghi": 50, "chinh_sach_co_ghi": 30,
    }
    assert [row["id"] for row in data] == [f"S9-{i:03d}" for i in range(1, 151)]
    assert len({normalized(row["question"]) for row in data}) == 150
    for row in data:
        assert row["question"].strip() == row["question"] and len(row["question"]) >= 20
        assert row["role"] == ("admin" if row["kind"] == "chi_tieu" else "customer")
        required = {"id", "kind", "role", "question", "document_id"}
        if row["kind"] == "chi_tieu":
            required.add("quote")
            required.add("metric")
        elif row["kind"] == "chinh_sach_co_ghi":
            required.add("quote")
        else:
            required.add("topic")
        assert set(row) == required
        if row["kind"] == "chinh_sach_khong_ghi":
            assert re.fullmatch(r"[a-z0-9_]{3,32}", row["topic"])


def test_sources_and_quotes_are_real_verbatim_and_approved():
    for row in rows():
        source = source_for(row)
        if row["kind"] != "chinh_sach_khong_ghi":
            assert row["quote"] in bot_quote_units(row), row["id"]
        if row["kind"] == "chi_tieu":
            assert row["document_id"].startswith(("sales-plan-", "monthly-report-"))
            assert "-draft" not in row["document_id"]
        else:
            assert row["document_id"].startswith("policy-")


def test_metric_counts_period_spread_and_month_table_rows():
    data = [row for row in rows() if row["kind"] == "chi_tieu"]
    assert Counter(row["metric"] for row in data) == METRIC_COUNTS
    periods = {}
    by_quote = {}
    for row in data:
        filename = row["document_id"]
        if filename.startswith("sales-plan-"):
            period = filename.removeprefix("sales-plan-").removesuffix("-v1.md")
        else:
            period = filename.removeprefix("monthly-report-").removesuffix("-v1.md")
        periods.setdefault(row["metric"], set()).add(period)
        by_quote.setdefault(row["quote"], set()).add(row["metric"])
        assert row["metric"] in METRIC_COUNTS
    assert all(len(values) >= 3 for values in periods.values())
    assert all(len(metrics) == 1 for metrics in by_quote.values())

    monthly = [row for row in data if row["metric"] == "plan_month_sales"]
    for row in monthly:
        match = re.search(r"(\d{1,2})/(\d{4})", row["question"])
        assert match and row["quote"].startswith("|")
        month, year = int(match.group(1)), match.group(2)
        assert row["quote"].startswith(f"| {year}-{month:02d} |"), row["id"]


def test_metric_question_phrasing_is_not_reused_by_period():
    data = [row for row in rows() if row["kind"] == "chi_tieu"]
    templates = [re.sub(r"\d+", "#", normalized(row["question"])) for row in data]
    assert len(set(templates)) == 70


def test_missing_policy_topics_are_diverse_and_bounded():
    missing = [row for row in rows() if row["kind"] == "chinh_sach_khong_ghi"]
    counts = Counter(row["topic"] for row in missing)
    assert len(counts) >= 14
    assert max(counts.values()) <= 4


def test_questions_do_not_repeat_v6_v7_or_v8():
    old = set()
    for dirname in OLD_DIRS:
        path = ROOT / "data" / dirname / "questions.json"
        old.update(normalized(item["question"]) for item in json.loads(path.read_text(encoding="utf-8")))
    overlap = [(row["id"], row["question"]) for row in rows() if normalized(row["question"]) in old]
    assert not overlap


def test_each_group_has_20_to_50_percent_unaccented_questions():
    for kind, group in _groups().items():
        unaccented = sum(_is_unaccented(row["question"]) for row in group)
        assert 0.20 <= unaccented / len(group) <= 0.50, (kind, unaccented)


def _is_unaccented(text):
    folded = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    folded = "".join(char for char in folded if unicodedata.category(char) != "Mn")
    plain = unicodedata.normalize("NFD", text.casefold().replace("đ", "d"))
    return folded == plain


def _groups():
    return {kind: [row for row in rows() if row["kind"] == kind]
            for kind in ("chi_tieu", "chinh_sach_khong_ghi", "chinh_sach_co_ghi")}


def test_ci_text_checker_reports_clean():
    from scripts.check_vi_text import check_file

    result = check_file(QUESTIONS)
    assert not result
