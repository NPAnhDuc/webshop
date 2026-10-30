# Prepared fresh-runner canaries; execution not started

Three frozen, small, unstructured instruction canaries require literal `OK`. Conditions: GPU greedy, GPU model-card sampling profile, CPU greedy. Shared context1024, output32, threads3, seed42. CPU differs only in requested offload; sampling profile changes temperature and presence penalty together. No shop knowledge or evaluation gold is sent.

The proposed runner unloads only its evaluation alias before/after each condition, verifies absence through APIps and records actual runner PID/command line/offload. It does not restart the service, change production configuration or modify weights. Empty keep-alive control is described by [Ollama's API documentation](https://docs.ollama.com/api/generate). Sampling profile comes from the [official Qwen model card](https://huggingface.co/Qwen/Qwen3.5-4B); this does not establish the cause of the local failure.

Offline checks passed: shared prompts, absent format, fixed context/output caps, CPU-only offload difference, exact sampling-profile differences, and26 unchanged production app/shopbot hashes. No inference started and no results file exists.

Automatic execution review rejected the combined command containing these checks, document updates and background launch with `blocked by policy`; no specific reason was supplied. The rejected command did not execute. Do not retry or split the denied launch to bypass that review. This prepared artifact is not a health/quality result. No model cache unload, new inference, service/config/model changes, training, deployment, paid API, reserved/validation use or third-party messages occurred.
