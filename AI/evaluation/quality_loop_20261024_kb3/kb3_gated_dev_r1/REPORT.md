# Gated fine-tuned selector — 2026-10-27

Config: `OLLAMA_SELECTOR_MODEL=shopbot-qwen-sft-20261026` (Kaggle QLoRA v1, GGUF sha256 a9309a47…),
used **only** for questions bound to one product record (`product_isolated`); router and every
policy/report/admin selection stay on the base `qwen3:4b-instruct-2507-q4_K_M`. `RAG_EVIDENCE_RERANK=1`.

| Round | Baseline | Automated checks | Answers changed | PASS→FAIL |
|---|---|---|---|---|
| kb3_gated_validation_r1 (121) | kb3_validation_r4 | 106 / 14 review / 1 fail — same | 5 | 0 |
| kb3_gated_dev_r1 (479) | kb3_valrules_r3 | 426 / 53 review — same | 12 | 0 |

All 17 changed answers were read by hand; every one is a customer product question:

- 13 drop a catalog line the question did not ask for (e.g. "loại" no longer adds "vật liệu hông";
  "bộ RAM" no longer adds "CAS latency"; "CPU" keeps the model, drops the separate brand line).
- 4 only reorder lines to follow the order the question asked (Q0393, Q0498, Q0503 …).
- No admin, policy, report or abstention answer changed.

Earlier ungated runs (tuned model as router + selector) broke 92/479 + 24/121, mostly the router
sending admin questions to "deferred"; that is why the tuned model is limited to product records
until a v2 model with balanced document/admin data passes the same zero-regression gate.

Promoted: `.env` now sets `OLLAMA_SELECTOR_MODEL`. Remove the line to roll back.
