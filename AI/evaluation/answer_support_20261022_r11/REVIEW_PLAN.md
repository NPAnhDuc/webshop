# Frozen same-input candidate-answer quote diagnostic

31 exact r10 inputs and gold copied byte-for-byte before inference; no new labels. 57 parts (44 acceptable/13 unacceptable), 26 recorded answers and5 intentionally bad constructed contrasts. Gold stays out of prompts. No production verifier, source/data/model/config change.

Hypothesis: raw part flags confuse facts available in reference sources with content actually present in the candidate answer. Require exact candidate-answer quotes for every approval; canonical NFC/whitespace membership guard rejects missing/blank/nonmember quotes. Preserve raw flags separately. This guard cannot establish relevance, unknown validity, or source support; manually inspect all outputs, especially correct/false unknowns and nearby attributes.

Nine offline controls passed before preparation: source-only span, no span, blank span, whitespace normalization, explicit unknown literal, raw false preservation, mixed valid/invalid span, and two intentional membership-only limitations (false unknown and irrelevant nearby attribute pass membership). No production tests rerun because app/shopbot unchanged. Output ceiling900 accommodates additional quotes (r10=500); same model/context/temp. Record actual tokens and stop reasons; no isolated speed-causality claim.

After completion check integrity and read every decision/quote/note. Report raw/guarded confusion and exact cases, category/cohort, all quote errors and same-input differences from r10. Do not change gold after results. A favorable diagnostic is not chatbot improvement nor sufficient to install a gate. No validation/reserved cases used. One batch only this heartbeat.
