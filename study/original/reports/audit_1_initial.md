# Audit 1

This masked semantic audit covered 240 records in six sequential batches of 40. For each record, I read only its `id`, `A`, `X`, and `Y`, identified the two competing stakes in `A`, and judged whether `X`, `Y`, both, or neither expressed the same central decision conflict. Topic words and superficial vocabulary overlap were ignored. Each batch was written to its own JSON file before the next input batch was read; the six files were then combined into `data/audit_labels_1.json`.

The final label counts are:

- X: 105
- Y: 77
- both: 57
- neither: 1

All 240 input IDs are covered exactly once. Every label contains an allowed choice, a high/medium/low confidence value, and a brief explanation of the competing stakes. Explanations were kept between 15 and 30 words.

This is an AI-produced judgment audit. No human validation, adjudication, or inter-rater reliability assessment was performed. Some dilemmas support close structural analogies across multiple candidates, so the labels and confidence values reflect semantic interpretation rather than an objective ground truth.
