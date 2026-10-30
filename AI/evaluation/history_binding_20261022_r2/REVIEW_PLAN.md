# Controlled history baseline r2

Production remains patch9. No resolver or knowledge changes in this revision.
168 scenarios from all 56 already-opened development product_context groups; 68 distinct current-question texts and 89 distinct profiles. Three variants per target: original recorded patch9 parent history, alternate recorded patch10 parent history, and that alternate history with the confirmed product name substituted for the current anaphor. Each starts from its own copied profile; variants do not form a sequential conversation.

23 parent profiles are byte-equivalent as serialized objects. Alternate assistant text is shorter in 22 groups, equal length in 33, longer in 1; the label brief_history is historical shorthand, not a universal length claim. Correlated scenarios and duplicated inputs must be counted separately from unique questions.

Inputs and exact source gold are frozen in bank/metadata; source provenance includes both original rounds. Gold facts never go to Engine. Parent model answers are untrusted conversation inputs, never knowledge or training data. The current-question substitution inserts a confirmed name only, never the requested answer. Clock remains 2026-10-21, models/config/source snapshots fixed. Shared runner.lock prevents GPU overlap. No reserved revision3 or validation inputs are opened.

## Review after completion

Require 168 outputs and unchanged integrity before scoring. Read answers with their input histories and source-owned required facts. PASS_CHECKS is not semantic PASS. Record main-fact verdict separately from irrelevant additions, model attribution, clarification despite known subject, source correctness, and missing requested attributes. Distinguish infrastructure failures from semantic failures. All changed responses require manual reading; reuse a saved semantic decision only for exact answer/action/source identity with compatible context and explicitly record provenance.

Compare variants within each target, report all 56 triplets and duplicate-input variability. Explicit naming is a diagnostic intervention, not an implemented automatic resolver or production gain. Baseline does not establish generalization. Future resolver repair requires separate frozen round with the same fixtures, plus counterexamples for unknown/multiple subjects, new explicit models and topic changes; never remove assistant history blindly. Preserve all old raw answers, banks, gold and executed scripts.
