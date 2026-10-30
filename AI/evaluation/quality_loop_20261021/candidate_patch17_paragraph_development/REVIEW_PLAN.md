# Patch17: evidence units retain the paragraph of a short referenced article

Offline r22 audit:34active public technical notes,34main paragraphs,37chunks; each main paragraph stays inside a single chunk, max85words. All34preserve exact source spans/content; no model calls or production mutation in that audit. Splitting facts and their qualifiers into sentence IDs allows the selector to omit either, as r21/patch16 demonstrated.

One coherent repair: explicit short technical document-summary path combines source identity with paragraph evidence. Uses paired single title plus summary router task/mixed-request guard, upstream ACL/status/date/period checks, and source-identity restriction. Only glossary/buying_guide documents of at most250sourcewords qualify; long/business documents retain established retrieval. Literal paragraphs are offered only for one matching owner/version and total retrieved context<=400words. Keep exact chunk citation; no cross-chunk generated merge, no source rewrite. Table handling remains unchanged. Other tasks retain sentence fragments. Parser/model/prompts/schema/fragment cap/KB/config unchanged.

Patch16 alone is not being reinstalled unchanged. Preserve patch9 snapshot in patch17_before_code and all candidate source/tests on rollback. Unit coverage includes prior title ACL/version/mixed guards, exact paragraph quotation/owners, and long/business fallback.

After units, one frozen28quoted-development batch, full groups. Baseline19PASS/9FAIL. Read all answers/source paragraphs and mark semantic completeness separately from PASS_CHECKS; full-paragraph quotation is not automatic proof the question is fully answered. Missing definitions in original notes (CPU threads, TN/VA detail, potentially explicit CPU/GPU replacement statement) must not be invented or relabeled to claim perfection. Record excess text and unsupported claims. Any semantic regression => rollback. If focused gain without regression, next heartbeat old100 before acceptance, then full479; no second model batch now.

No reserved/validation tuning, no r19retry/unload, model swap, service restart, paid API, training/Colab, deployment, subagents or external messages.
