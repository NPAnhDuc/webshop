# Report source intent r1 — candidate replay in progress

Verified baseline runtime against kb3_guards_full_r1 before edit; no batch active. Frozen57document-request failures and3additional report phrasings plus6directSQL controls, source/gold unchanged. Before fix59failed/7passed of66routing assertions (one document paraphrase already bypassed SQL for another reason).

One correction in rag_metrics/grounded_rag: explicit read/quote/according-to-report preference gates the SQL shortcut. A separate rag_metric_source profile field preserves document preference for compatible financial/period follow-ups; a direct new metric request, explicit underlying-data request or changed domain resets it. Role permissions and calendar resolution stay independent. No report values, dates, document IDs or expected answers encoded in the router. Does not rewrite source dates or substitute reports for data-only metrics.

214targeted checks passed13.90s (report-intent, existing metrics and recent guard regressions). Then strengthened two-turn test to assert selected cost1010759000 rather than prior revenue1189908000 with an injected evidence selector:74source-intent checks passed1.72s. These are code/fixture checks, not live-model accuracy or evidence that all57report answers are now correct.

One bounded development replay running: kb3_report_source_intent_r1,81requestedIDs (57knownmonthly cases+24controls, conversation closure handled by runner). Script run_quality_report_source_intent_20261025_r1.py freezes evidence rerank1 and shared locks. Same bank/gold/source/model/config. Next heartbeat checks process FIRST, waits if active, then integrity and per-case report version/period/metric/value/extra-claim semantics against the unchanged gold and prior independentSQL audit. Keep priorMOQ/campaign/discount fixes in controls. No promotion yet; no validation, training, ingestion, paid API, model download, embedding-worker startup or deployment. Candidate sources and before/after tests preserved.

## Completed review

# Report source intent r1 —57source defects corrected in bounded replay

85/85development turns completed, integrity unchanged=true; runtime matches frozen candidate and source equals prior full guards baseline. Mechanical68PASS_CHECKS/17NEEDS_REVIEW/0FAIL_CHECKS; no general semantic accuracy inferred.

Reviewed all57previous document-source defects against unchanged gold and actual cited text/version: exactly one relevant claim per reply, requested metric/value/period correct, requested monthly report document/version cited, quote present verbatim, simulation label retained and no extra claims. Numbers also equal the earlier independent raw SQL audit. This corrects report provenance rather than changing57wrong numbers (numbers were already correct). Other28control answer texts and all85actions remain unchanged, including MOQ, campaign uncertainty and discount comparison fixes.

Report-source path adds retrieval/model latency versus previous near0s SQL shortcut; no speed improvement claim. Existing214unitchecks and strengthened74source-intent checks passed before inference. Compatible source-memory follow-up was verified with injected-selector code tests; this85turn model replay does not independently certify all new follow-up phrasings. DirectSQL behavior is covered by existing unit/control checks, not a claim that all natural language variants are tested.

Retain correction locally and run broad479development regression to detect source-memory/routing side effects outside this subset before validation. Q0055capability refusal and other17review cases remain. No training, validation opening, data ingestion, model/worker startup, deployment or frontend change. Evaluation artifacts remain evaluation-only.
