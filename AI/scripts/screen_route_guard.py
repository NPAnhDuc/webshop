"""Screen the conservative route guard against the designated dev export."""

import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shopbot.route_guard import corpus_words, guard

CASES = ROOT / "evaluation" / "dev_export_20261031" / "cases.json"
DB = ROOT / "data" / "business_sql" / "scenario_v1" / "shop.sqlite"
BAD_TOPICS = {
    "admin_tool_request": "deferred",
    "admin_clarify": "clarify",
    "customer_clarify": "clarify",
    "customer_permission": "denied",
    "live_boundary": "live_product",
    "unknown_product": "unknown_product",
}


def known_product_names():
    uri = DB.resolve().as_uri() + "?mode=ro"
    with sqlite3.connect(uri, uri=True) as con:
        tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        for table in ("products", "catalog_items", "product_catalog"):
            if table in tables:
                columns = {row[1] for row in con.execute(f'PRAGMA table_info("{table}")')}
                name_col = next((col for col in ("name", "title", "product_name") if col in columns), None)
                if name_col:
                    return [row[0] for row in con.execute(f'SELECT "{name_col}" FROM "{table}" WHERE "{name_col}" IS NOT NULL')]
    raise RuntimeError("No product-name column found in the read-only shop database")


def main():
    rows = json.loads(CASES.read_text(encoding="utf-8"))
    products = known_product_names()
    output = []
    false_positives = []
    fixed = 0
    misses = []
    for row in rows:
        action = guard(row.get("question", ""), row.get("role", "customer"), int(row.get("turn", 0)) > 0, products, corpus_words())
        expected = row.get("expected_behavior")
        actual = "unknown" if action == "unknown_product" else action
        if action is not None and actual != expected:
            false_positives.append(row.get("id", "?"))
        target = BAD_TOPICS.get(row.get("topic"))
        is_bad = row.get("status") == "FAIL_CHECKS" and target is not None and expected == ("unknown" if target == "unknown_product" else target)
        if is_bad:
            output.append(row.get("id", "?"))
            if actual == expected or (target == "unknown_product" and action == "unknown_product"):
                fixed += 1
            else:
                reason = "còn mơ hồ/thiếu tín hiệu an toàn cho luật " + target
                misses.append((row.get("id", "?"), reason))
    print(f"Tổng ca development: {len(rows)}")
    print(f"Bắt nhầm: {len(false_positives)}")
    if false_positives:
        print("ID bắt nhầm: " + ", ".join(false_positives))
    print(f"Sửa ca lỗi mục tiêu: {fixed}/{len(output)}")
    print(f"Đạt ngưỡng 0 bắt nhầm: {not false_positives}")
    print(f"Đạt ngưỡng tối thiểu 16/33: {fixed >= 16 and len(output) == 33}")
    print("Ca còn bỏ sót:")
    for case_id, reason in misses:
        print(f"{case_id}: {reason}")
    if len(rows) != 864 or false_positives or len(output) != 33 or fixed < 16:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
