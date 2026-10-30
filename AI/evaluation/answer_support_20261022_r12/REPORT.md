# Broader confirmation r12: combined judge gate rejected

44scenarios/22new questiontexts,68parts;22buyer/22admin,22recorded answers plus22constructed contrasts. Per-part gold fixed by manual reading before inference and separate from legacy whole-QA grades. No r10/r11questiontext reused. Same r11SYSTEM/schema/guard/options, no production changes or training. Balanced pairs are correlated development probes, not independent user accuracy or natural log prevalence.

|Variant|Part agreement|Exact cases|False accepts|False rejects|
|---|---:|---:|---:|---:|
|Raw judge|45/68|25/44|20|3|
|Literal candidate-answer membership guard|53/68|33/44|3|12|

Within these same44outputs the guard removes17wrong approvals but introduces9false rejections. It is unsuitable as production completeness gate. It rejects correct answers from source-only concatenations/reordered sentences, table paraphrases, semicolon-vs-period and initial capitalization changes. Five of eight valid-unknown parts are rejected (shopdays/fees, three channel budgets), while explicit sourceabsence is often misread as candidatefailure. Original general180Hz/FPS principle is rejected for missing specific180/60wording, despite frozen pre-inference rubric accepting it.

Three wrong approvals survive actual literal quotes: OLED conditions-vary clause without answering guaranteed immunity, and both swapped target/actual revenue labels. In the latter case notes even identify correct values/wrong mapping while checks remaintrue. The source/answer distinction is still unreliable. MissingJuly decision is correct but rationale falsely claims July sourceabsent. No gold changed after these outputs; borderline interpretation boundaries were written before inference in REVIEW_PLAN.

Recorded-output cases14/22 exact versus constructed19/22 after guard; buyer16/22/admin17/22. Agreement differs sharply by cohort, so do not use total33/44 as chatbot accuracy. R11smallselected56/57does not generalize here; it is a different cohort, not a measured production regression.

All44completed/integritytrue/stderr empty, done_reasonstop44. Prompt410–1509tokens, output100–283 under900. Total144.814s, median2.5625s; cache/cold not controlled.55proposedquotes,26parts with membership/emptyquote issues across21cases. All decisions, quotes and notes manually reviewed; raw requests/responses retained. No inference-time labels/categories, no validation/reserved use.

Decision: reject installing this combined source+candidate judge. Next bounded design should separate candidate coverage from reference support: coverage can inspect question/history plus candidate text/fragmentIDs without full source facts, distinguish actual answer/explicitunknown/missing, and never pretend to verify factual support. A separate evidence-availability check is needed for unknown validity. Any new coverage labels must be manually defined/frozen in a new revision, not reuse support booleans blindly; false-unknown answers have coverage but fail evidence validity. Fixed answer-owned IDs may avoid quote typography errors, but cannot guarantee semantic relevance. This is design only, no second batch or implementation now. Acceptedpatch9 remains450/479development,87/100legacy,193tests previously passed; no new production result claimed.
