# Patch15 quote-aware question clauses

Only parser change from frozen r20v2 candidate. Same production Qwen3 model, prompts, retrieval, KB and config. This is not a retry of denied Qwen3.5 r19 action: no evaluation alias unload or CPU/GPU canary.

Before model batch: full offline unit checks. One development batch of all28quoted-title questions, complete conversation groups. Compare against patch9 raw outputs; manually review all19PASScontrols and9FAIL. Inference never receives labels or gold. Record omissions, extra-source noise and wrong topic separately from PASS_CHECKS. Any semantic regression => restore frozen patch9. Improvement with no regression still provisional until old100 next heartbeat; no second batch now. Six prior FAIL questions have no parser change; do not expect this one repair to fix all. Max3fragment/part remains a known limit.

Do not use reserved24 or opened121validation to tune. No knowledge revision, model download, services restart, deployment, training or paid API.
