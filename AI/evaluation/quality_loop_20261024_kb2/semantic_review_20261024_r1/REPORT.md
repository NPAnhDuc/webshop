# Rerank: partial semantic review after479 development turns

Batch kb2_rag5_rerank_r1 completed479/479, integrityunchanged. Mechanical368PASS_CHECKS/53NEEDS_REVIEW/58FAIL_CHECKS matches r5 totals; this is NOT semantic acceptance or proof outputs equivalent.

Read first8 changed IDs from changed_vs_rag5.json in stored order, old/new answers and cited source chunks.6 meet their factual request (2 still have irrelevant material),2 incomplete: Q0020 does not explicitly address unavailable MOQ evidence; Q0038 gives campaign title/table without clarifying unknown detailed eligibility. No overall479 semantic score or promotion inferred. No validation opened.

Changes mostly reduce duplicate/unasked excerpts. They do not supply new knowledge, live catalog or analysis tools. CPU/RAM values are supported by the cited reference catalog only; not independently verified manufacturer specifications. All shop targets/campaigns remain simulated.

Next diagnosis: answer obligation/completeness for two-part or yes/no questions. Need explicit statement of missing evidence (retrieved supplier excerpt has lead time, not MOQ; campaign name does not prove precise eligible products). This is synthesis/scope, not automatically lack of more training text. Do not invent MOQ, business policy, campaign eligibility or upgrade negative retrieval into proof of absence across all documents.

Read-only model/runtime/data; no code/config edit, extra model batch, source ingestion or training. review.json is evaluation only (training_allowed/ingestion_allowed=false), separate from old bank/gold/results.573unit tests seen in tests-rag4-full.log remain code checks, not an AI semantic score. Continue reviewing remaining changed/failed cases and resume from current runtime hashes before code changes.
