# Typed source-backed discount comparison candidate r1

Baseline runtime hashes verified against kb3_campaign_scope_r1. Frozen integration test failed before implementation: cap quoted but no7% versus6% comparison. Existing20contract cases preserved unchanged in discount_contract_20261025_r1.

Implemented read-only compare_policy_percentage with Decimal operands and source-bound current-policy adapter. Requested percentage comes from one explicit user percentage in a discount/cap comparison; cap comes from a complete unqualified policy quote, never a hard-coded runtime value. Trace records operation, operands, relation, difference in percentage points, quote/evidence ID, date and approval_granted=false/mutation_allowed=false. Conflicting caps, out-of-range inputs, draft/future/expired/quarterly evidence, methodology sources, margin/stacking and historical scopes abstain. Conditional approval is not promoted to universal authority. This is a bounded operation in grounded RAG, not a general arbitrary SQL/Python agent or globally exposed policy tool.

Integration retains unanswered approver while covering only supported comparison parts. Derived claims explicitly cite the source quote and calculation; source quote remains verbatim, arithmetic wording is marked as a calculation. Numeric compliance does not grant permission or prove adequate profit margin.

121 targeted tests passed2.56s: previous83 + integration1 + typed/adapter37. Includes frozen20contracts (8positive numeric outcomes versus independent Fraction gold,12negative-operation boundaries) and cap3.5% counterexample, conflicting evidence and period/source filters. Negative-operation tests certify abstention by this adapter, not the complete chatbot reply. First after-patch integration failed due overly broad quarterly-label filter matching “Quy định”; corrected to explicit quarter/month-number expressions, tests retained. No model acceptance or accuracy claimed from unit checks.

One bounded model batch running: kb3_discount_comparison_r1,24development IDs plus4context=28, baseline campaign guard. Same bank/gold/source/model/config; wrapper freezes evidence rerank1 and takes both locks. No validation/training/ingestion/model download/embedding-worker startup. Do not mutate runtime/data/config/model or start competing batch while active. Next heartbeat: process check, integrity, semantic review Q0102/all controls versus baseline, especially retained missing approver and no authorizations. Candidate not yet accepted or promoted.

## Completed review

28/28complete,integritytrue; Q0102nowcomputes7%-6%=1percentagepoint and retains unknownapprover.27other answer texts/all28actions unchanged. Narrow correction retained pending combined479development regression; see kb3_discount_comparison_r1/REPORT.md and semantic_review.json.
