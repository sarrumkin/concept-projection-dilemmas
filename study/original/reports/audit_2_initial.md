# Audit 2

## Procedure

I performed a masked semantic audit of six input parts sequentially. Each part contained 40 records with fields `id`, `A`, `X`, and `Y`. For every record, I identified the two competing stakes in `A`, then judged whether `X`, `Y`, both candidates, or neither expressed the same central decision conflict. Topic words and surface vocabulary were ignored when they did not carry the underlying conflict. I reasoned about each record individually and wrote the literal judgment for a part before reading the next part.

The six part label files were combined into `notebooks/concept_layers_large_en/data/audit_labels_2.json`. Structural validation confirmed 240 records, 240 unique IDs, exact coverage of the six input parts, the required fields, valid choices and confidence values, and explanations of 15–30 English words.

## Results

| Choice | Count |
|---|---:|
| X | 135 |
| Y | 105 |
| both | 0 |
| neither | 0 |
| Total | 240 |

Confidence was `high` for 239 records and `medium` for 1 record. No confidence value was low.

## Limitations

This audit was produced by an AI system using semantic reading and judgment. It was not independently validated by a human annotator, so the labels and explanations may contain interpretation errors or systematic preference for one candidate. The choice distribution should not be treated as evidence that one side is intrinsically more correct.
