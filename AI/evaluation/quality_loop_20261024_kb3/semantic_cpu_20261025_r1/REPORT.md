# CPU reference lookup review — completed KB3r5

Reviewed all17development product_single questions explicitly asking CPU information. Each now names the correct CPU model according to its cited reference catalog, and selected claims are restricted to CPUmodel/brand/core. Exact claim text is present in the cited bound-product record. This verifies source faithfulness, not manufacturer specifications or live shop configuration.

Old stored KB2rerank replies used81claims across the same17questions; current KB3r5 uses18. Unasked display/OS/GPU/weight fragments are absent from these current replies. This is measured relevance improvement for this selected family, not an increase in overall accuracy17/17→anything or proof all479responses are correct.

Data/runtime revisions differ, including additional schema/field selection changes. Do not attribute all improvement solely to source-frame removal. No new inference batch was run to generate this review, and no validation opened. Completed KB3r5 has479/479integrityunchanged and mechanical368PASS_CHECKS/53NEEDS_REVIEW/58FAIL_CHECKS; those totals remain separate from semantic review.

Admin issues remain: Q0020 still fails to directly disclose unavailable MOQ evidence and adds warranty/simulator information; Q0038 does not qualify the lack of detailed campaign eligibility; Q0102 reports6percent cap while saying cap comparison is not known. No guessed MOQ, eligibility, approval policy or new shop data is added. RAG/source-scope and answer-obligation work remains before acceptance.

Pending preamble unit check finished:51tests passed7.72s in tests-preamble-20261025-r1.log, including9new source-frame cases. This is targeted testing, not fullsuite/model acceptance. No code/model/source/config changes or model batch in this heartbeat. Review is evaluation-only:training_allowed/ingestion_allowed=false.
