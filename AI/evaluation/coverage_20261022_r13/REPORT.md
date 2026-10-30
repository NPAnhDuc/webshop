# Candidate-only coverage diagnostic r13

44preserved r12candidate answers/questions,68parts; source bodies withheld, candidate paragraphs assigned local IDs. New manual three-state COVERAGE gold frozen before inference:35answered,9explicit_unknown,24missing. Original r12source-support gold untouched. Same local model/options, no production changes/training. Answered coverage deliberately does not establish correct numeric values/year; false unknown has response coverage but lacks factual validity.

|Variant|Three-state part agreement|Exact cases|False covered|Missed covered|
|---|---:|---:|---:|---:|
|Raw|45/68|25/44|20|0|
|With answer-ID guard|56/68|35/44|7|2|

Binary covered includes answered or explicit_unknown. Guarded binarycaseagreement38/44, but the seven false-covered parts are missing responses mislabeled explicit_unknown using real irrelevant paragraphs: generic DDRgeneration, Hzdefinition, PDmax, OLEDconditionsvary and threechannelbudgets. Both shopreturn unknowns have correct rawstatus but omit available A1 IDs, so guard wrongly downgrades them. Correct study60Hz, actualreportedrevenue and bare-yearlessnumeric assertion classifiedunknown rather than answered. All labels and interpretation boundaries remain as frozen; no gold rewrite.

All returned IDs exist (schema constrains them);15parts/12cases lack required IDs, not invalidforeignIDs. Membership eliminates quote typography failures but does not prove semantic status or relevance. Some selectedblocks are citations or redundant advice; when alongside real answer they are noise, not evidence of additional knowledge. All44statuses/68notes and selectedparagraphs manually read. Notes often describe absence of an answer while emitting explicit_unknown, so explanations are untrusted.

Exploratory answered-only threshold gives32correctanswered,33correctnotanswered,3missedanswered,0falseanswered among this selected cohort. This is post-inference analysis, NOT acceptance of a new gate: correct substantive answers are still lost; explicitunknown must never be treated as healthy completion merely because classifier says so. Production already has structured unanswered/part_evidence metadata; inspect that contract before another verifier change, and freeze a broader generation-level confirmation if pursuing answered-only evaluation. Source availability/truth/year remains a separate untested task.

All44completed/integritytrue/stderr empty, stop44. Prompt354–918tokens,output60–243under900; total98.453s,median1.5625s(cold/cacheuncontrolled). This is additional checker latency, not end-user speed improvement. Do not compare coverage56/68 to r12support53/68 as causal accuracy gain: labels/task changed. Balanced pairs correlated; not independent user accuracy.

Decision: not accepted as standalone coverage/completeness gate; no production implementation. Acceptedpatch9 unchanged450/479development,87/100legacy,193tests previously passed. No reserved/validation/Colab/deployment/paidAPI/subagents/messages. One diagnostic protocol change and one44callbatch only.
