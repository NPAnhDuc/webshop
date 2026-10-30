# Campaign eligibility table coverage — candidate r1

Frozen actual Q0038 source/case before runtime edit. Existing answer treated the campaign name/schedule/budget table as complete evidence for gaming eligibility. Initial regression3failed/6passed; no new knowledge or eligibility policy was invented.

One conservative coverage check: if a product eligibility question is supported only by selected marketing table fragments without populated scope/condition/product-group columns, preserve the cited table as context and mark that requested part unanswered. Campaign-name wording alone does not prove eligible SKUs. Tables with populated scope fields, selected prose, ordinary date/budget/name questions are left to existing evidence selection. This is a narrow missing-field guard, not universal semantic validation. It does not validate product entity alignment or infer scope from a title.

83 targeted tests passed2.43s, including existing supplier/grounded regressions, explicit prose/scope-column positives, empty scope negative and date query control. The first9 frozen tests exposed3failures; two additional boundary tests were added before final patch evaluation. Unit checks do not certify model answers.

One bounded model replay now running: kb3_campaign_scope_r1,24development IDs plus4context=28. Baseline kb3_supplier_fields_r2, same bank/gold/source/model/config and explicit evidence rerank1; wrapper takes both shared runner locks. No validation, training, data ingestion, worker startup or deployment. Results pending; next heartbeat must check process then integrity and semantic effect on Q0038 and all controls. Do not modify runtime/data/model/config or start competing batch while active.

## Completed semantic review

28/28 complete, integritytrue; Q0038 is the sole answer change, now candid about missing eligibility evidence.27other answers/all28actions unchanged. Guard retained locally with limits; see kb3_campaign_scope_r1/REPORT.md and semantic_review.json. No speed or full-system accuracy claim.
