# Additional results

These analyses supplement the full-corpus accuracy comparison in the [README](../README.md). The [notebook](../notebooks/research.ipynb) reproduces both figures from the experiment tables.

## Paired accuracy differences

Concept207 corrects **55** baseline errors and introduces **21** new errors, a net gain of 34 correct preferences out of 240 (+14.17 percentage points). Hybrid50 corrects 36 and introduces 14, a net gain of 22 (+9.17 points).

The points show accuracy differences relative to the embedding baseline; the horizontal segments show 95% descriptive bootstrap intervals. The intervals use 10,000 paired draws over conflicts and topics, retaining both variants in each sampled cell. The Concept207 interval is [+2.50, +27.08] percentage points; the Hybrid50 interval is [+0.42, +19.58]. These intervals describe sensitivity within the fixed synthetic design, not population uncertainty for naturally occurring dilemmas.

![Paired accuracy differences and descriptive intervals](figures/effects.png)

## Random-projection controls

Thirty Gaussian maps and thirty random orientations with the attribute map's singular spectrum are evaluated separately and in 50/50 mixtures. Each grey point represents one random map's accuracy on the same 240 triplets; each coloured line marks the corresponding attribute-based representation.

**Concept207 exceeds all 60 standalone controls**: its accuracy is 60.42%, while the best control reaches 55.83%. One of the 60 random mixtures exceeds Hybrid50. Thus, the selected attribute projection outperforms all tested standalone random alternatives on this corpus, while the hybrid does not outperform every control mixture.

The map comparisons are descriptive. The maps share the same texts and labels and do not constitute additional independent datasets or establish a universal advantage over random projections.

![Random projections and attribute-based representations](figures/random_controls.png)

See the [methods](methods.md) for the representation definitions and [reproduction checks](reproduction.md) for numerical verification.
