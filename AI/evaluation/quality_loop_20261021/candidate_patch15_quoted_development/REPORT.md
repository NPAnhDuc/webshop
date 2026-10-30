# Provisional patch15 quoted-clause focus run

Full offline candidate units:197PASS in52.84s. Model batch completed28/28, integritytrue, no automated infrastructure/source-integrity issue. All28 require manual semantic review, not automatic PASS.

Manual read of all answers and exact source texts: **13/28 PASS versus19/28 patch9**. No prior FAIL fully fixed. Six regressions: Q0071 loses DDR4/DDR5 incompatibility; Q0128 loses WiFi6 versus6E/7 bands; Q0166 loses Ryzen core/thread/boost/TDP facts; Q0257 loses OLED scope/condition; Q0281 replaces RAM task guidance with unrelated material; Q0288 loses M2 slot compatibility condition.

Some shorter answers remove noise (CPU, OLED static content, RAM upgrade), but CPU still misses the GHz performance limit and does not become PASS. Correctly protecting the title alone does not make the selected answer complete. One merged part allows only3fragments; answers often spend them on repetition or generic conditions. This batch does not isolate fragment cap from selector competence, so raising the cap is not automatically justified.

Rejected candidate. Restored all26app/shopbot files and original grounded tests from patch15_before_code; verified frozen patch9 hashes. No model/prompt/retrieval/config/KB change accepted. Candidate source/tests, raw outputs, metadata and labels preserved. Rollback offline suite pending in AI/runtime/tests-quality-patch15-rollback.log. No second model batch or old100/full479 on rejected code.

Total202.314s including first request40.391s; median5.4375s. Cold/warm/request-payload differences prevent a speed-improvement claim. Last accepted production remains450/479development and87/100 old regression. Reserved/validation untouched; no r19 retry, unload, paid API, deployment, training or external messages.

Next evidence-based work: capture exact selector inputs for existing document-summary failures and controls without another production change; inspect requested-title identity, available owner/fragments and budget before choosing a document-binding repair. Avoid further generic answer-judge tuning. Keep this parser experiment rejected unless a distinct complete approach survives semantic controls.

Rollback verification complete:193testsPASS in56.71s,26production hashes matchpatch9. Candidate rejected and fully removed.
