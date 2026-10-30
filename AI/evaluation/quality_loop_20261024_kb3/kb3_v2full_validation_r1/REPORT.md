# Fine-tuned Qwen v2 — 2026-10-27

Model `shopbot-qwen-sft-20261027-v2` (Kaggle QLoRA on data v2: doc/admin balanced, lr 5e-5, 2 epochs;
GGUF sha256 13df1c93…). Kaggle dev (159): router 47→60/68, admin document routes 9→18/21, no group dropped.

| Round | Config | Baseline | Checks | Answers changed | PASS→FAIL |
|---|---|---|---|---|---|
| kb3_v2sel_validation_r1 (121) | v2 as gated selector | kb3_gated_validation_r1 | 106 / 14 review / 1 fail — same | 1 | 0 |
| kb3_v2sel_dev_r1 (479) | v2 as gated selector | kb3_gated_dev_r1 | 426 / 53 review — same | 1 | 0 |
| kb3_v2full_validation_r1 (121) | v2 as router + every selector | kb3_gated_validation_r1 | 89 / 15 review / 17 fail | 25 | **16** |

Gated selector: the only changes (Q0393, Q0498) list "cáp modular" before "loại" although the question
asks for "loại" first; v1 keeps the asked order. No gain over v1, so `.env` keeps the v1 selector.

Router + selector: all 16 regressions are one admin template, "Đặt cạnh nhau <chỉ số> trong báo cáo
tháng A và tháng B, không tính chênh lệch". v2 routes it to `deferred` ("cần công cụ ngoài RAG");
the base router answers it from the two monthly reports. That template is 132 of the 600 evaluation
questions, so the 479 run was not made with this config.

Cause in the data: every admin `deferred` example is a calculation/action request, and every document
question names a single period; no read-only question over two periods was labelled `answer`.
Fix (data v3, `build_qwen_sft_20261026.py --v3`): two-report read-only questions over all 7 report
metrics and two quarterly plans (labels: `answer` + per-month fragment), in wordings other than the
evaluation template and skipping every (metric, month, month) the evaluation asks; plus 8 contrast
requests that ask to compute a difference/growth/ranking, labelled `deferred` per the router spec.
