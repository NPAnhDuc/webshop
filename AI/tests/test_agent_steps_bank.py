import json
import re
import sqlite3
import sys
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AI_ROOT / "scripts"))
import build_agent_steps_bank_20261031 as builder

BANK = AI_ROOT / "evaluation/agent_steps_20261031/bank.json"
ZERO_IDS = builder.ZERO_IDS


def load_rows():
    return json.loads(BANK.read_text(encoding="utf-8"))


def test_builder_reproduces_bank_and_gold_sql_is_read_only():
    expected = builder.build()
    actual = load_rows()
    assert actual == expected
    db = builder.DB_PATH.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(db, uri=True) as conn:
        for item in actual:
            rows = conn.execute(item["expected_sql"]).fetchall()
            assert rows and all(value is not None for row in rows for value in row)
            if item["kind"] == "months":
                assert all(len(row) == 1 and isinstance(row[0], str) for row in rows)
            else:
                assert len(rows) == 1 and len(rows[0]) == 1


def test_counts_splits_groups_and_allowed_kinds():
    rows = load_rows()
    assert len(rows) == 40
    assert len({r["id"] for r in rows}) == 40
    assert {r["split"] for r in rows} == {"dev", "test"}
    assert sum(r["split"] == "dev" for r in rows) == 20
    assert sum(r["split"] == "test" for r in rows) == 20
    assert {r["kind"] for r in rows} <= {"int", "pct", "months"}
    assert sum(r["id"][-2:] in {"01", "02", "03", "04"} for r in rows) == 8
    assert sum(r["id"][-2:] in {"05", "06", "07", "08"} for r in rows) == 8
    assert sum(r["id"][-2:] in {"09", "10", "11", "12"} for r in rows) == 8
    assert sum(r["id"][-2:] in {"13", "14", "15", "16", "17"} for r in rows) == 10
    assert sum(r["id"][-2:] in {"18", "19", "20"} for r in rows) == 6


def test_only_zero_group_is_zero_and_comparison_signs_match_questions():
    rows = {r["id"]: r for r in load_rows()}
    with sqlite3.connect(builder.DB_PATH.resolve().as_uri() + "?mode=ro", uri=True) as conn:
        for item in rows.values():
            if item["kind"] == "months":
                continue
            value = conn.execute(item["expected_sql"]).fetchone()[0]
            assert (value == 0) == (item["id"] in ZERO_IDS)
        checks = {
            "d01": ("giảm", -1),
            "d03": ("nhiều hơn", 1),
            "d04": ("tăng", 1),
            "t04": ("tăng", 1),
        }
        for item_id, (word, sign) in checks.items():
            row = rows[item_id]
            value = conn.execute(row["expected_sql"]).fetchone()[0]
            assert word in row["question"].casefold()
            assert (value > 0) - (value < 0) == sign
        assert "hay" in rows["t01"]["question"].casefold()
        assert "hay" in rows["t03"]["question"].casefold()


def test_net_revenue_and_gross_profit_questions_include_returns():
    for row in load_rows():
        q = row["question"].casefold()
        if "ròng" in q or "thuần" in q or "lãi gộp" in q or "lg " in q:
            assert "financial_ledger" in row["expected_sql"]
            assert not re.search(r"(?:WHERE|AND)\s+(?:\w+\.)?kind\s*=\s*'sale'", row["expected_sql"], re.I)


def test_categorical_filters_are_real_outside_zero_group():
    db = builder.DB_PATH.resolve().as_uri() + "?mode=ro"
    patterns = [
        (re.compile(r"\bo\.channel\s*=\s*'([^']+)'", re.I), "SELECT 1 FROM orders WHERE channel=? LIMIT 1"),
        (re.compile(r"\bc\.segment\s*=\s*'([^']+)'", re.I), "SELECT 1 FROM customers WHERE segment=? LIMIT 1"),
        (re.compile(r"\bp\.category\s*=\s*'([^']+)'", re.I), "SELECT 1 FROM products WHERE category=? LIMIT 1"),
        (re.compile(r"\br\.reason\s*=\s*'([^']+)'", re.I), "SELECT 1 FROM returns WHERE reason=? LIMIT 1"),
    ]
    with sqlite3.connect(db, uri=True) as conn:
        for row in load_rows():
            if row["id"] in ZERO_IDS:
                continue
            for pattern, query in patterns:
                for value in pattern.findall(row["expected_sql"]):
                    assert conn.execute(query, (value,)).fetchone(), (row["id"], value)


def test_every_multi_step_filter_reduces_the_candidate_set_and_is_documented():
    # Candidate rows before and after the decisive filter, independently counted in shop.sqlite.
    before_after = {
        "d13": (10, 1), "d14": (6, 3), "d15": (3, 1), "d16": (2, 1),
        "d17": (9, 2), "t13": (10, 1), "t14": (62, 3), "t15": (3, 2),
        "t16": (3, 1), "t17": (3, 1),
    }
    source = Path(builder.__file__).read_text(encoding="utf-8")
    for item_id, (before, after) in before_after.items():
        assert before > after
        assert re.search(rf"#\s*{item_id}:.*\b{before}\b.*\b{after}\b", source, re.I)


def test_limit_is_explicit_or_answers_a_named_extreme():
    for row in load_rows():
        limits = re.findall(r"\bLIMIT\s+(\d+)", row["expected_sql"], re.I)
        if not limits:
            continue
        q = row["question"].casefold()
        assert any(word in q for word in ("cao nhất", "thấp nhất", "đứng đầu", "thứ hai", "nhiều nhất", "ít nhất", "nhieu nhat", "it nhat", "lon nhat", "cao nhat")), row["id"]
        for n in limits:
            if int(n) > 1:
                assert str(n) in q or {2: "hai", 3: "ba"}.get(int(n), "__missing__") in q, row["id"]


RANKING_METRICS = {
    "d05": ("SELECT COUNT(*) FROM orders WHERE day BETWEEN '2026-01-01' AND '2026-06-30' GROUP BY substr(day,1,7)", "DESC", 3),
    "d06": ("SELECT SUM(l.revenue) FROM financial_ledger l LEFT JOIN returns r ON l.kind='return' AND r.id=l.id JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END JOIN orders o ON o.id=i.order_id WHERE o.channel='social' AND l.day BETWEEN '2026-04-01' AND '2026-06-30' GROUP BY substr(l.day,1,7)", "ASC", 1),
    "d07": ("SELECT SUM(ABS(refund)) FROM returns WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY substr(day,1,7)", "DESC", 3),
    "d08": ("SELECT COUNT(*) FROM receipts GROUP BY substr(day,1,7)", "DESC", 2),
    "t05": ("SELECT SUM(revenue-cost) FROM financial_ledger WHERE day BETWEEN '2026-01-01' AND '2026-03-31' GROUP BY substr(day,1,7)", "DESC", 3),
    "t06": ("SELECT SUM(quantity*unit_cost) FROM receipts WHERE day BETWEEN '2026-04-01' AND '2026-09-30' GROUP BY substr(day,1,7)", "ASC", 1),
    "t07": ("SELECT SUM(l.revenue) FROM financial_ledger l JOIN products p ON p.sku=l.sku WHERE p.category='laptop' AND l.day BETWEEN '2026-01-01' AND '2026-09-30' GROUP BY substr(l.day,1,7)", "DESC", 3),
    "t08": ("SELECT COUNT(*) FROM orders GROUP BY substr(day,1,7)", "DESC", 2),
    "d17": ("SELECT SUM(revenue-cost) FROM financial_ledger WHERE day BETWEEN '2026-01-01' AND '2026-09-30' AND substr(day,1,7) IN (SELECT substr(day,1,7) FROM operating_expenses WHERE day BETWEEN '2026-01-01' AND '2026-09-30' GROUP BY substr(day,1,7) HAVING SUM(amount)>120000000) GROUP BY substr(day,1,7)", "DESC", None),
    "t17": ("SELECT SUM(revenue) FROM financial_ledger WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY substr(day,1,7) HAVING SUM(quantity)>(SELECT AVG(units) FROM (SELECT SUM(quantity) units FROM financial_ledger WHERE day BETWEEN '2026-07-01' AND '2026-09-30' GROUP BY substr(day,1,7)))", "DESC", None),
}


def test_ranked_months_have_no_ties_at_or_before_the_returned_positions():
    db = builder.DB_PATH.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(db, uri=True) as conn:
        for item_id, (sql, direction, limit) in RANKING_METRICS.items():
            values = [r[0] for r in conn.execute(sql).fetchall()]
            values.sort(reverse=direction == "DESC")
            returned = len([r for r in load_rows() if r["id"] == item_id][0]["expected_sql"] and conn.execute(
                [r for r in load_rows() if r["id"] == item_id][0]["expected_sql"]
            ).fetchall())
            n = limit if limit is not None else returned
            selected = values[:n]
            assert len(selected) == n
            assert len(set(selected)) == n, item_id
            if n < len(values):
                assert values[n - 1] != values[n], item_id


def test_questions_include_plain_voice_unaccented_text_and_abbreviations():
    rows = load_rows()
    old = json.loads(builder.OLD_BANK.read_text(encoding="utf-8"))
    old_questions = {item["question"].strip().casefold() for item in old}
    assert not any(item["question"].strip().casefold() in old_questions for item in rows)
    assert sum(not re.search(r"[à-ỹÀ-ỸđĐ]", row["question"]) for row in rows) >= 5
    corpus = " ".join(row["question"].casefold() for row in rows)
    assert len(re.findall(r"\bdt\b", corpus)) >= 1
    assert len(re.findall(r"\blg\b", corpus)) >= 1
    assert len(re.findall(r"\bq[1-4]\b", corpus)) >= 1
    assert all("làm tròn 2 chữ số thập phân" in row["question"].casefold() for row in rows if row["kind"] == "pct")
