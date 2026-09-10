# Audit 1: semantic side alignment

## Scope

This audit covers 240 fixed records in six 40-record parts from `concept_layers_large_en`. It is a side-alignment pass over the original Luna audit labels: the original confidence and semantic explanation were preserved verbatim for every record. The Sol pass reread each original record and its original explanation, then assigned `X`, `Y`, `both`, or `neither` according to which candidate or candidates actually express the competing stakes described by that explanation.

The pass did not use author labels, answer keys, other audits, protocols, results, or the failed automated first-eight-words/no-changes pass. No paragraph or original explanation was changed. Short exact contiguous quotes from both candidates were added to make every side decision inspectable.

## Results

- Records reviewed: 240
- Side assignments changed: 80
- Alignment unresolved: 1
- Changes by part (0–5): 5, 7, 13, 13, 22, 20
- Unresolved by part (0–5): 0, 1, 0, 0, 0, 0
- Final choices: X 124, Y 115, both 0, neither 1

Most corrections were initial `both` labels whose explanations or candidate text supported only one side, plus several X/Y swaps where the explanation clearly described the opposite candidate. One record remains unresolved because neither candidate aligns with the original explanation; its initial choice was retained as required.

## Validation status

This is model-based semantic side alignment, not human validation. No human reviewer validated these labels. The main experiment has not been scored, and the underlying study data was treated as fixed. No author key or author-label access was used.
