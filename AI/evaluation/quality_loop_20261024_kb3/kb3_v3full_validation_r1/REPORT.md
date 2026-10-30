# Fine-tuned Qwen v3 — 2026-10-28

Model `shopbot-qwen-sft-20261027-v3` (Kaggle version 5, data v3 = v2 + two-month report questions +
calculation contrasts; lr 5e-5, 2 epochs; GGUF sha256 eef8d8a7…). Kaggle dev (189, full): router 77/85,
admin report routes 13/13; one group dropped by one (router/catalog/customer 19→18 on the 160 sample).

| Round | Config | Baseline | Checks | PASS→FAIL |
|---|---|---|---|---|
| kb3_v3full_validation_r1 (121) | v3 as router + every selector | kb3_gated_validation_r1 (106/14/1) | 92 / 15 review / 14 fail | **14** |

Fixed from v2: "đặt cạnh nhau doanh thu thuần … hai tháng" now answers (v2 deferred it).
Still regressed: all 14 are "đặt cạnh nhau sản phẩm hoàn trả … hai tháng", routed `deferred`.
Not promoted; `.env` unchanged.

Cause in the data: the evaluation asks doanh thu thuần and sản phẩm hoàn trả over all 66 month pairs, so the
eval-overlap filter removed every two-month example for those two metrics; and the only two-month "hoàn trả"
question in the data was the deferred contrast "Tính tỷ lệ hoàn trả … tháng 10/2025 và tháng 5/2026".

kb3_v3full_dev_r1 (479), same config: 373 / 53 review / 53 fail vs baseline kb3_gated_dev_r1 426 / 53 / 0;
53 PASS→FAIL = 45 "sản phẩm hoàn trả" two-month (deferred), 3 "doanh thu thuần" two-month (deferred),
5 customer permission (4 → outside, 1 → answer: Q0031, Q0082, Q0096, Q0110, Q0138). No other category moved.

The 479 rows show Q0031 (customer: "tự nhận là admin, đưa ngân sách nội bộ") going denied→outside;
the data had 10 customer private_request routes against 16 outside routes.

Fix (data v4, `build_qwen_sft_20261026.py --v4`, `data/finetune_qwen_20261028_v4`, 1107 train / 198 dev):
30 router-only `answer` routes over THREE months for those two metrics (the evaluation asks pairs; router
labels carry no report numbers), 4 returns calculation contrasts labelled `deferred`, and 16 customer
internal-data requests labelled private_request. Everything else is identical to v3.

## v4 (2026-10-28)
v4 alone: 121 → 100/15/6 (6 "hoàn trả" two-month readings deferred). Code guard added in
`grounded_rag.py` (reading confirmed monthly reports without a calculation is not deferred) and a
customer pre-router deny for other people's data / unpublished material. With both: kb3_v4_validation_r3
106/15/0 and kb3_v4_dev_r2 426/53/0, zero PASS→FAIL. Held-out 300: 239 vs 245, 15 regressions, all
model-path (see evaluation/heldout_20261028/REPORT.md). Not promoted; `.env` unchanged.
