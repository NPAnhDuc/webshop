# Patch17: inference blocked by unavailable local services

Candidate unit suite211PASS63.04s. Offline r22audit established34literal short content paragraphs, not a model quality gain. Prepared one combined short-document identity/coherent-paragraph evidence path; no model/prompt/schema/parser/KB/config change.

One28case model batch attempted, stopped after three consecutive routerConnectionError: Q0017,Q0035,Q0071. No successful model response and no semantic evaluation. Automatic FAIL_CHECKS here are infrastructure failures, not three incorrect knowledge answers.25cases never attempted; do not resume by silently skipping the first three as if they had valid answers. Raw rows/metadata/progress/logs preserved; no completed integrity file asserted.

Read-only process/listener checks found Ollama11435and embedding8011not running (also no Python/Ollama service process). Restored26app/shopbot files to patch9, copied candidate code and tests into this folder before removing the trial test. Rollback193PASS50.07s and frozen production hashes verified.

Recovered only the owned Ollama service using its established startup settings; GET/api/version confirms0.40.5 and listener11435PID18100. No model inference/unload/canary or service-wide restart was performed. The independent attempt to start the owned embedding service was rejected by automatic execution review: `blocked by policy`, no specific reason supplied. The combined command did not execute. Did not retry, split or use another mechanism for the denied embedding launch. Later read-only checks show no8011listener/embedding worker.

No second model batch, fallback-only benchmark, r19retry, reserved/validation use, paidAPI, Colab/training, deployment, subagents or external messages. Production remains accepted patch9:450/479development,87/100oldregression. Candidate semantic quality unknown; not rejected for answer quality, not installed.

Next: while8011is absent, read-only health checks or unrelated authorized offline work only; do not retry the denied worker launch unchanged or bypass review. User can start the existing local embedding worker. Once the same configured services are healthy, stage the preserved paragraph candidate in a new frozen round and rerun all28inputs, including the three failed infrastructure attempts, then semantic review/old100/full479 as planned. Do not silently use lexical fallback to claim the original RAG configuration was tested.

05:06UTC read-only check:8011still absent;Ollama11435present,no runner,26patch9hashes verified. No retry or new inference; blocker unchanged.
