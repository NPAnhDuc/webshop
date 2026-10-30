# R21 observational document-summary inputs

Unchanged restored patch9. Twelve already-opened single-turn development cases: six FAIL and six PASS controls, including title-split cases and titles missing from selected/available evidence. This is one observational batch, not a new candidate, independent validation or retry of denied r19 GPU/CPU canaries. No alias unload, service restart or model/config/data mutation.

Capture exact router and selector `/api/chat` JSON request/response, and unmodified search results. No headers/auth/environment dump. Gold/manual reviews are never sent to Engine or model. Shared runner lock and code/config/source hashes checked per input; stop three consecutive infrastructure errors.

Review each case against raw patch9 and approved source. Distinguish: title owner missing from search; retrieved owner lost before selector; owner present but needed sentence missing; needed sentence present yet omitted by selector. Inspect question parts, source ownership, total payload/token context, finish reason and actual selected IDs. Source fields/content alone do not prove semantic correctness. Do not infer max3fragments is sole cause or publish a quality gain for unchanged code.

One batch only. After capture, report facts and choose a subsequent distinct repair. No generic judge prompt variant, no gold rewrites, no extra model batch or production change during this capture. Keep reserved24 and validation untouched. Accepted baseline stays450/479 and87/100,193rollback unit tests passed.
