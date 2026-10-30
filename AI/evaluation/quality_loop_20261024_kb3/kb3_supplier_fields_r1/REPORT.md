# Supplier-field guard — rejected after same-case regression

One proposed fix: bind selected evidence to an explicitly requested supplier attribute, rejecting lead time or warranty as MOQ, and methodology examples as actual shop supplier data. No new facts, prompt rewrite, model change, knowledge ingestion, startup or training.

Before edits: snapshot and8source-field probes with deliberately wrong injected selections;3/8before→8/8after.66targeted tests passed2.39s. These fixtures incorrectly assumed a procedural source is typed procedure/policy. They did NOT establish real-corpus compatibility.

One bounded model batch requested24same development cases, automatically expanded by select_cases to28to include4conversation prerequisites. Same KB3bank/gold/database/knowledge and model. Legacy baseline did not record RAG_EVIDENCE_RERANK but its trace confirms it was active; new wrapper froze1explicitly. No worker startup/bypass. Batch completed28/28, integrityunchanged; mechanical11PASS_CHECKS/17NEEDS_REVIEW, no automaticFAIL. Mechanical checks did not catch the semantic regression.

Only2answer texts changed;26unchanged were not regraded into an accuracy score. Q0020 now loses the valid lead-time half and returns none; Q0187 regresses from supported4/3day lead times to none. Cause: actual procurement source is doc_type=strategy,authority=synthetic_shop_document. It is a valid role-filtered procedural source despite the broad retrieval type. The whitelist dropped it. This candidate fixes no complete task and must not be promoted.

Candidate rejected, source frozen before rollback, then grounded_rag.py restored BYTE-EXACT baseline. New helper and tests archived under evaluation, candidate code preserved.51grounded tests passed7.09s after rollback; all runtime hashes listed in KB3r5metadata match again. No bank/gold/source/model/config edits or second model batch. Old integrity refers to the evaluated candidate, not the restored runtime.

Next: source-domain contract with real metadata fixtures before another repair. Do not use coarse doc_type as the sole proof of field semantics. Supplier field identity still matters; do not accept a methodology example or customer delivery time as actual supplier terms. Add actual strategy/synthetic_shop_document regression and no-source/partial-coverage cases. MOQ, campaign scope and approval issues remain open; data crawling/fine-tuning does not resolve them.
