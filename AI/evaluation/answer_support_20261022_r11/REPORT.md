# Same-input candidate-answer support diagnostic r11

31 frozen r10 inputs/gold copied byte-for-byte;57parts,44acceptable and13unacceptable. All31 calls completed, integrity unchanged, stderr empty. All31 decisions/57notes and proposed quotes reviewed manually. No production code/data/model/config changes, no training, no reserved24/validation use.

|Protocol|Part agreement|Exact cases|False accepts|False rejects|
|---|---:|---:|---:|---:|
|r10 part flags|50/57|26/31|6|1|
|r11 raw flags|51/57|27/31|6|0|
|r11 with literal-answer membership guard|56/57|30/31|0|1|

Within r11, the guard rejects six incorrect approvals across four cases: Dell cores, G.Skill kit, omitted DDR comparison, and three false-unknown monthly fields. The judge still copies SOURCE facts into answer_quotes despite instructions. Guard also rejects one acceptable ECC answer because judge selected a supporting sentence only present in source. Raw-to-guard difference is a deterministic audit of the same outputs; r10-to-r11 prompt/schema/output-limit changes are not isolated causal effects.

Remaining false reject R9-011 is held to original frozen gold. Other limitations: R9-015 display-port part is accepted with real but generic Thunderbolt4 quotes instead of the available model-specific Apple sentence; membership is not semantic sufficiency. R9-018 supplies a literal numeric-prefix quote missing the final digit, followed by a full correct quote; substring membership does not prove safe standalone numeric interpretation. Valid thread-count unknown R9-001 now accepted. MissingQ2 rationale correctly distinguishes supplied source from omitted answer. No annotation was changed after inference.

All31 calls stop normally. Prompt410–1643tokens; output88–355 (ceiling900 versus r10=500); total126.732s, median3.515s versus r10 96.822s/2.546s. Cold/cache not controlled; this is additional verifier cost, not chatbot speed gain. See summary for quote count, categories/cohorts and raw/guarded errors.

Decision: retain as diagnostic only. Before any production gate, prepare broader frozen development cases with manual relevance/unknown labels, including candidate quotes that are literal but irrelevant, wrong-scope or falsely unknown; preserve correct scoped/implicit answers and multi-part cases. Do not just tune the same31 or change gold. If broader confirmation succeeds, a bounded production proposal still requires latency assessment, same-input regression, old100/full479. Accepted patch9 stays450/479 development,87/100 legacy,193tests last passed. No new production result is claimed.
