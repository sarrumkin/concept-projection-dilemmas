# Audit 2: semantic side alignment

This audit covers 240 records in six 40-record parts. The original Luna audit supplied the semantic explanations and confidence values. This Sol pass independently read each original A/X/Y record together with that original explanation and checked which candidate side actually expresses the competing stakes described by the explanation.

The pass preserved every original explanation verbatim. It corrected 17 choice labels whose letters contradicted their explanations: 0 in part 0, 0 in part 1, 1 in part 2, 5 in part 3, 8 in part 4, and 3 in part 5. The remaining 223 labels were retained. No case required `alignment_unresolved`; all 240 explanations could be aligned semantically to a candidate. Each output record also contains short exact support quotes from both X and Y and a specific note for every changed label.

This was a model-based semantic side-alignment pass, not human validation. No author labels, answer keys, protocols, other audits, or experiment results were accessed. The main experiment was not scored during this work, and the underlying input data and original Luna explanations were not changed.
