# Audit 1

This masked semantic audit covered 240 records in six sequential batches of 40. For each record, I read only its `id`, `A`, `X`, and `Y`, identified the two competing stakes in `A`, and judged whether `X`, `Y`, both, or neither expressed the same central decision conflict. Topic words and superficial vocabulary overlap were ignored. Each batch was written to its own JSON file before the next input batch was read; the six files were then combined into `data/audit_labels_1.json`.

The final label counts are:

- X: 105
- Y: 77
- both: 57
- neither: 1

All 240 input IDs are covered exactly once. Every label contains an allowed choice, a high/medium/low confidence value, and a brief explanation of the competing stakes. Explanations were kept between 15 and 30 words.

This is an AI-produced judgment audit. No human validation, adjudication, or inter-rater reliability assessment was performed. Some dilemmas support close structural analogies across multiple candidates, so the labels and confidence values reflect semantic interpretation rather than an objective ground truth.

## Alignment pass

The alignment pass preserved each original explanation verbatim and checked its relationship to the selected side. Each record now also contains short exact contiguous quotes from both X and Y, plus `alignment_changed`, `alignment_note`, and `alignment_unresolved`. No choice was changed in this pass (`changed count: 0`). The 57 records originally labeled `both` were retained with `alignment_unresolved: true`, because resolving whether both candidates independently fit would require a new semantic judgment beyond spelling and side alignment. The remaining 183 records were retained with `alignment_unresolved: false`. Initial labels remain preserved under `data/audit_initial/`.
