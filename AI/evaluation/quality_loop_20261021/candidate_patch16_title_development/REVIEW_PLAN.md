# Patch16: source identity for a referenced document summary

One repair only: when the router says summary and there is a single paired full-title quote with no detected separate request, pass document_title into retrieval. Match it against role-approved current documents, before guessed type/category and incidental SKU-code filters. Keep date/period constraints and routing permissions. Missing exact title yields no substitute source. Multi-quote, comparison, external conjunction/semicolon/product code, or a following question not referring back to the document keeps ordinary search.

This is conservative syntax gating, not proof the router understands every mixed request. Unit tests cover excluded mixed forms, unknown titles, similar SKU names, ACL/current/future/draft/expired/deleted versions, and both retrieval passes. No benchmark ID/name or answer is in production logic. No parser, prompt, schema, fragment cap, model/config or knowledge change. Patch15 parser is not reapplied. Frozen patch9 snapshot at patch16_before_code.

After units, one28quoted-development focus batch, complete groups, same fixed clock and bank/gold. Baseline19PASS/9FAIL. Manually read every answer and relevant source; source focus is not semantic completeness. Answers must preserve SKU/region/capacity and conditions, decline unknowns, and include main requested content. Do not rewrite historical labels or send gold into bot. Any semantic regression => reject and restore snapshot, preserving outputs. If gain without regression, next heartbeat old100 before acceptance; then full479. Reserved24/validation stay unopened for tuning. Do not run another batch this heartbeat.

No r19retry/unload/model swap, service restart, training/Colab, external API, deployment, subagents or messages.
