# Method review: `concept_layers_large_en`

Scope: read-only review before scoring of `PROTOCOL.md`, `PRE_SCORE_AMENDMENT.md`,
`experiment.py`, `check_metrics.py`, `build_notebook.py`, `write_report.py`, and the
frozen assignment/label/topic inputs. No experiment, encoder run, or audit-file edit
was performed.

## Findings

1. **The bootstrap implementation matches the stated paired design.** `paired_intervals`
   computes method differences before resampling, samples conflict and anchor-topic
   indices independently with replacement, retains both variants in each selected
   cell, and averages the resulting 12×10 grid. Since every cell has exactly two
   triplets, this preserves the intended equal weighting of the 240 cases. The
   conflict-only, topic-only, and leave-one-author-out sensitivities use the same
   paired differences. This is a descriptive percentile bootstrap over the constructed
   factor grid, not a confidence interval for a population of natural-language
   dilemmas; the protocol and report state that limitation correctly.

2. **The random-map controls implement the specified families.** Gaussian maps use
   `N(0,1/207)` entries. Spectrum-matched maps use the 207 singular values of the
   centered anchor matrix and a QR-generated 384-dimensional orthonormal basis; the
   sign adjustment gives the intended positive-diagonal orientation convention.
   Each control is normalized after projection and is evaluated on the same triplets.
   Seeds are deterministic and maps are not selected by their scores.

3. **The 95th-percentile control comparison is necessarily coarse.** Each family has
   only 30 maps, so the empirical p95 is effectively determined by the top one or two
   observations and is not a calibrated tail probability. The current report calls
   this comparison descriptive and explicitly says it is not a p-value or evidence
   of mechanism; that wording is scientifically appropriate. It would be useful to
   retain the exact per-map control table (which the run does) alongside the summary
   whenever this criterion is discussed.

4. **Corpus-quality checks are upstream rather than part of scoring.** `make_corpus.py`
   checks the 40–70 word range, English-only text, question endings, uniqueness,
   5-gram overlap, assignment consistency, and the 128-token limit. `experiment.py`
   verifies uniqueness, counts, audit schema, and token length, but does not repeat
   those corpus checks or recompute the assignment formulas. This is acceptable only
   because the pre-score audit and frozen manifest are treated as authoritative and
   hashed. For a standalone rerun or independent import of `experiment.run`, adding
   assertions that the pre-score audit exists and matches the data would reduce the
   chance of scoring a malformed but otherwise hash-consistent input.

5. **One defensive report check is missing.** `write_report.py` computes the random
   specificity statement with `.all()` over the hybrid-control rows. If that table
   were empty, `.all()` would be true by vacuous truth. A simple assertion that the
   distribution table contains exactly four rows (two families × two uses, each
   summarizing 30 maps), with both hybrid families present, before computing `specific` would
   prevent an empty-control artifact from producing a positive-sounding claim.
   Under the current `run()` path, four distribution rows and 120 map/use summary
   rows are expected, and the claim is otherwise
   correctly qualified.

## Scientific claim review

The protocol/report distinguish baseline improvement from concept-specific advantage,
describe AI audits as agreement rather than human ground truth, preserve the original
author relations for the primary outcome, and avoid interpreting margins as calibrated
confidence. The fixed 50/50 mixture and centered 207-coordinate transform are
implemented as described; no new fitting or result-dependent selection is visible in
the reviewed code.

This is an AI code/method review, not an independent semantic audit of the generated
English paragraphs or a human relevance judgment. Numerical correctness still depends
on the later score run and independent numeric audit.

Root resolution before scoring: added explicit four-row distribution and 120-row
per-map/use checks to the report generator. Corrected the original review's mistaken
60-row expectation for the distribution table; 60 is the number of random maps.
Upstream corpus checks remain protected by the final input hashes, without changing
any data after audit initiation.
