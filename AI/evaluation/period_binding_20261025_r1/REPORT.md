# Explicit period-to-evidence contract frozen

Evaluation-only audit of102development multi_period cases/204parts. Expected period parsed from explicit month/year in each user part using an independent regex, no bot resolver/model. Actual period comes from source document ID in stored trace mapping. Current166exact/34wrong/4overbroad vs baseline168/32/4.19cases include a non-exact slot; all cases and flagged subset preserved in audit.json/frozen_cases.json. Q0244new swap has correct overall sourced May/Aug numbers, so trace misalignment must be distinguished from numeric answer error. No semantic pass rate or training labels inferred. No runtime patch/inference yet.

Next: freeze executable swap/overbroad/missing/identical-value regressions before a source-period rebinding change. Reuse only selected evidence with matching source period, do not fabricate missing facts or silently select unrelated metrics. Preserve original bank/gold/results.
