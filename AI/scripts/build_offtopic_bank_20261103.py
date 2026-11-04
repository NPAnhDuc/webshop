"""Build the off-topic bank: questions outside the shop, plus controls that sound off-topic but belong to the shop."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-11-03"
OUT = ROOT / "evaluation" / "offtopic_20261103"
DB = ROOT / "data/business_sql/scenario_v1/shop.sqlite"
MANAGED = ROOT / "data/unstructured/managed/e397df083984c120"
SQLDOCS = ROOT / "data/business_sql/scenario_v1/documents"
VALIDATION_SHARE = 0.4


def has_diacritic(s: str) -> bool:
    return any(unicodedata.category(c) == "Mn" for c in unicodedata.normalize("NFD", s))


def docs_index() -> dict[str, dict]:
    result = {}
    for base in (MANAGED, SQLDOCS):
        for item in json.loads((base / "manifest.json").read_text(encoding="utf-8")):
            path = base / item.get("source", "")
            if item.get("source") and path.is_file():
                result[item["document_id"]] = dict(item, text=path.read_text(encoding="utf-8"))
    return result


def quotas(sizes: dict[str, int]) -> dict[str, int]:
    """Validation units per group: 40% of the family total, split by largest remainder."""
    exact = {g: n * VALIDATION_SHARE for g, n in sizes.items()}
    result = {g: int(x) for g, x in exact.items()}
    left = round(sum(sizes.values()) * VALIDATION_SHARE) - sum(result.values())
    for g in sorted(exact, key=lambda g: (result[g] - exact[g], g))[:left]:
        result[g] += 1
    return result


def spread(n: int, k: int) -> set[int]:
    """k positions spread evenly over n, so each group has both splits."""
    return {int((i + 0.5) * n / k) for i in range(k)}


def build() -> list[dict]:
    source = json.loads((OUT / "questions.json").read_text(encoding="utf-8"))
    docs = docs_index()
    # Units keep a conversation in one split: (group, [(question, behavior, refs, role, intent)]).
    units: list[tuple[str, list[tuple]]] = []
    for group, questions in source["outside"].items():
        units += [(group, [(q, "outside", [], "customer", group)]) for q in questions]
    units += [(item["group"], [(item["question"], "outside", [], "admin", item["group"])]) for item in source["admin_outside"]]
    units += [("control", [(c["question"], c["behavior"], c.get("refs", []), "customer", "control")]) for c in source["controls"]]
    units += [("multi_turn", [(t["question"], t["behavior"], t.get("refs", []), "customer", t.get("group", "control")) for t in turns])
              for turns in source["conversations"]]

    by_group: dict[str, list[int]] = {}
    for index, (group, _) in enumerate(units):
        by_group.setdefault(group, []).append(index)
    outside = quotas({g: len(ix) for g, ix in by_group.items() if g.startswith("off_")})
    want = outside | quotas({"control": len(by_group["control"])}) | quotas({"multi_turn": len(by_group["multi_turn"])})
    validation = {indexes[p] for g, indexes in by_group.items() for p in spread(len(indexes), want[g])}

    bank = []
    for index, (group, turns) in enumerate(units):
        conversation = f"ot-{index + 1:03}"
        for question, behavior, refs, role, intent in turns:
            required = []
            for doc_id, quote in refs:
                assert doc_id in docs, doc_id
                assert quote in docs[doc_id]["text"], (doc_id, quote)
                required.append({"document_id": doc_id, "version": int(docs[doc_id].get("version", 1)), "quote": quote})
            bank.append({"id": f"OT-{len(bank) + 1:03}", "conversation": conversation, "role": role, "topic": group,
                         "question": question, "expected_behavior": behavior, "required": required, "intent": intent,
                         "expected_values": [], "rubric": f"{behavior}: ngoài phạm vi thì từ chối lịch sự và kéo về việc của shop; việc của shop thì trả lời theo tài liệu.",
                         "gold_document_ids": sorted({r["document_id"] for r in required}), "today": TODAY,
                         "split": "validation" if index in validation else "development"})

    behaviors = Counter(c["expected_behavior"] for c in bank)
    assert len(bank) == 100 and behaviors["outside"] == 80, behaviors
    assert len({c["question"].casefold() for c in bank}) == 100
    assert Counter(c["split"] for c in bank) == Counter(development=60, validation=40), Counter(c["split"] for c in bank)
    assert sum(has_diacritic(c["question"]) for c in bank) >= 80, "questions lost their diacritics"

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "bank.json").write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    used = sorted({(r["document_id"], r["version"]) for c in bank for r in c["required"]})
    gold = [{k: docs[did][k] for k in ("document_id", "version", "title", "source", "text", "audience") if k in docs[did]} for did, _ in used]
    (OUT / "gold_sources.json").write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = MANAGED / "manifest.json"
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    meta = {"created": TODAY, "today": TODAY, "database": DB.relative_to(ROOT).as_posix(),
            "knowledge_manifest": manifest.relative_to(ROOT).as_posix(), "knowledge_sha256": sha(manifest),
            "database_sha256": sha(DB), "bank_sha256": sha(OUT / "bank.json"), "gold_sha256": sha(OUT / "gold_sources.json"),
            "questions_sha256": sha(OUT / "questions.json"),
            "counts": dict(Counter(c["topic"] for c in bank)), "behaviors": dict(behaviors),
            "splits": dict(Counter(c["split"] for c in bank)), "roles": dict(Counter(c["role"] for c in bank)),
            "quality_checks": {"no_diacritic": sum(not has_diacritic(c["question"]) for c in bank),
                               "colloquial_abbreviations": sum(bool(re.search(r"\b(?:ko|k|bh|m|tr|ok)\b", c["question"], re.I)) for c in bank)},
            "note": "Hand-written off-topic bank. Score once before tuning; validation split is for the check after fixes."}
    (OUT / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return bank


if __name__ == "__main__":
    cases = build()
    print(len(cases), dict(Counter(c["expected_behavior"] for c in cases)), dict(Counter(c["split"] for c in cases)))
