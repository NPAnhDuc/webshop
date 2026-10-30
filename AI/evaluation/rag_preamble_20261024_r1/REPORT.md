# Source-frame obligation fix — model evaluation pending

Observed root cause from semantic review: “Theo danh mục tham khảo, X có CPU như thế nào?” became two required parts, including a phantom question “Theo danh mục tham khảo”. The selector can then fill that phantom part with unrelated display/GPU facts. Reranking alone does not remove the phantom obligation.

Before runtime edit: baseline_code/grounded_rag.py and12frozen parser cases in check_parts.py.5/12before→12/12after. One code change in question_parts excludes only complete source-framing phrases when there are actual question parts. Full original question still accompanies model evidence selection; factual clauses, decimal comma, distinct requested fields, period/context and lone ambiguous frame are preserved. No prompt/model/source-content change by this fix.

41existing grounded RAG tests passed8,46s before9new tests were added. A later command named nonexistent test_retrieval.py, so NO tests ran in that attempt. The9new tests (including full original-question/context preservation) remain pending. Do not report50tests passed or fullsuite passed.

A bounded24case replay was being prepared:16previously changed development cases plus8controls. Preparation stopped at baselinehash assertion: pre-edit grounded_rag.py is NOT byte-identical to kb2_rag5_rerank_r1 metadata; unrelated runtime changes already exist. ids.json/protocol.json and wrapper are draft, NOT a valid frozen A/B protocol and have made0model calls. Do NOT run this wrapper as-is or attribute future gains solely to preamble removal. Need a new protocol/revision using the actual current snapshot after reviewing current batch.

During preparation another quality batch kb3_final_r4 started at23:56:46 local (metadata16:56:48UTC). Runtime edit timestamp23:55:49 precedes batch; current grounded_rag.py hash matches that batch's frozen metadata. New test-file edit23:57 was after batch started before this run noticed it; tests are not part of its frozen runtime hashes, but no further code/data/model/config writes or competing model/test batches are permitted. Do not edit or roll back runtime during that batch. All original banks/gold/results remain intact; no source embedding-worker startup/retry, fine-tune or paidAPI.

Next: wait for kb3_final_r4 to exit, verify input/runtime integrity and semantic results. Then finish new unit tests against current snapshot, inspect pre-existing changes and choose a comparable source/config baseline before any bounded replay. Current12/12parser probes are logic checks only, not chatbot accuracy or production acceptance.


## Follow-up25/10local

Pending unit run completed:51tests passed7.72s, including9new cases, with correct test filename. No new model replay. Completed KB3finalr5 was reviewed separately for17CPU lookup questions; see ../quality_loop_20261024_kb3/semantic_cpu_20261025_r1. Observed relevance gains cannot be isolated to this patch because knowledge/runtime revisions differ. The24-case wrapper/protocol remains a draft and must not be run as a valid A/B experiment.
