# Per-part monthly metric evidence binding candidate r1

Baseline runtime verified against kb3_report_source_full_r1. Frozen injected-selector swap test fails before edit; original102case/204part contract and all prior gold/results unchanged.

One correction: bind typed monthly metric fragments to explicit period in EACHuser part before render. Reuse only IDs already selected somewhere in this answer, with matching source month and requested metric; never search or synthesize a missing fact. A bare month inherits a unique confirmed query year. Conflicting source period/document ID, wrong metrics and absent selected period do not supply evidence. Model-declared missing remains missing. Definitions/causal explanations/targets bypass numeric rebinding. Quarter, ambiguous-year and complex multi-metric parts are not newly certified.

Trace records part, expected month, metric, original/bound/rejected/transferred IDs. Evidence may move between requested parts when the same shared metric is unambiguous; a cost fragment cannot become revenue. Existing source/version-based dedup retains identical numeric values from distinct periods.

227targeted tests passed3.06s, including swapped/overbroad/missing/wrong-metric/year/source-conflict boundaries, same-value integration and previous guards/SQL/report-source tests. Offline reconstruction of ONLYselected source-owned numeric claims across102storedcases yields204/204period-aligned parts versus previous166exact;0modelcalls and no new facts. This is deterministic controller verification, not an end-to-end AI pass rate.

One model replay running: kb3_period_binding_r1, 183requested developmentIDs (102multi-period plus prior report/guard controls; runner adds conversation prefixes). Baseline kb3_report_source_full_r1; same bank/gold/source/model/config, evidence rerank1/two locks. No promotion yet. Next heartbeat FIRSTchecks process, then integrity, per-part metric/period/evidence alignment, response values/sources/missing, control regressions and latency. Do not edit runtime/data/model/config or run competing batch while active. No validation, training, ingestion, frontend/deployment, paidAPI, model download or embedding-worker startup.

## Completed review

# Monthly period binding r1 —204part alignment verified

187/187development turns completed, integrity unchanged=true; runtime matches frozen candidate and source equals broad report-source baseline. Mechanical170PASS_CHECKS/17NEEDS_REVIEW is not overall semantic accuracy.

All102multi-period answers checked against explicit user part month/year and unchanged gold:204/204parts select exactly the requested period and correct metric quote/version, versus baseline166exact/34wrong/4overbroad. No new numbers or claims: each two-claim set equals baseline, no unrequested claims or missing periods.19replies now order their same facts according to the correct user parts. Other85control replies and all187actions unchanged, including57report-source fixes and3earlier guards.

This verifies exposed102case family alignment, not chatbot-wide accuracy or quarters/ambiguous years/complex clauses.227unitchecks passed previously. First review script failed before output due requiring a leading space before “tháng”; corrected independent regex handles beginning of part. Saved verify_model_replay.py completes all assertions; no runtime or model change caused by review repair.

Narrow correction retained pending broad479development regression. No runtime edit this heartbeat. Q0055unsupported-update explanation and wider53review cases remain. Validation121unopened, no training or ingestion. No source/data/model/config change, deployment, frontend, paidAPI or embedding-worker startup. No speed claim.
