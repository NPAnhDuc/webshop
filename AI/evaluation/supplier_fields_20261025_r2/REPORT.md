# Supplier field revision r2 — evaluation in progress

Frozen real-source metadata regression exposes r1 failure: 1 failed/20 passed before correction. Authority plus field/domain binding replaces broad doc_type whitelist; strategy/synthetic_shop_document procurement evidence remains eligible. This does not establish that every shop source has complete supplier terms, and absence is limited to selected evidence.

After patch: first test invocation had 70 passes and two temporary-directory permission errors. Dedicated basetemp rerun: 72 passed (supplier + grounded). No semantic model acceptance from unit checks.

Baseline runtime files verified against kb3_final_r5 before inference. One bounded development replay started: kb3_supplier_fields_r2, 24 requested /28 including conversation context. Wrapper freezes RAG_EVIDENCE_RERANK=1 and takes both runner locks. Bank/gold/source/model/config unchanged. No validation, training, source ingestion or embedding worker startup. Existing r1 remains rejected and archived.

Batch still running at checkpoint; do not edit runtime, data, model or config or start a competing batch. Next: verify integrity, review Q0020/Q0187 against cited evidence, compare all remaining answers with r5/r1; reject and preserve candidate if regression remains. No promotion yet.

## Completed review

Batch completed28/28, integritytrue. See ../quality_loop_20261024_kb3/kb3_supplier_fields_r2/REPORT.md and semantic_review.json. Q0020 improved;27answer texts unchanged, including correct Q0187. Narrow runtime fix retained; no full semantic accuracy or speed claim. No additional batch.
