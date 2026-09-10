# Reproduction and numerical verification

The executable entry point is `reproduce.py`. It loads the preserved calculation in `study/original/experiment.py`, verifies the 194 public artifact hashes and the frozen input/design manifests, and writes to a separate output directory. Existing nonempty output directories and protected source directories are rejected.

After verifying the original result tables, it computes exploratory nDCG@5 and nDCG@10 with `ndcg.py` from that run's `main_vectors.npz`. Both modes write `retrieval_per_query.csv` (720 rows) and `retrieval_summary.csv` (3 rows); columns `ndcg_at_5` and `ndcg_at_10` contain scores on a 0–1 scale. The protocol and output counts are recorded under `exploratory_retrieval` in `verification.json`. These additional tables are not compared with the frozen experiment. The notebook displays their method means. See the [retrieval methods](methods.md#exploratory-retrieval-ndcg).

| Mode | Text vectors | Attribute prototypes | Recomputed results |
|---|---|---|---|
| `cached` | Supplied 720 × 384 matrix | Supplied 207 × 384 matrix | All primary comparisons, controls, intervals and sensitivity tables |
| `full` | Fresh pinned MiniLM inference | Fresh inference of 2,790 phrases, combined into 207 prototypes | The same calculations |

The raw attribute CSV retains its original `cp1252` encoding. Full inference is performed on CPU with four PyTorch threads, batch size 32, and model revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. Text and phrase lengths are checked before encoding; inputs exceeding the 128-token limit are rejected. No external language-model API or paid inference service is required.

## Completed release checks

The release preparation run used Python 3.12.7 on macOS ARM64. A fresh virtual environment installed only the lightweight requirements and pytest; cached reproduction and all four tests passed with PyTorch, Sentence Transformers and Transformers absent. Both reproduction modes reproduced:

- 720 primary triplet/representation comparisons;
- 28,800 random-map comparisons;
- 18 bootstrap interval records, including the prespecified grouping sensitivities;
- the exact 111, 145 and 133 correct preferences for Embedding, Concept207 and Hybrid50.

The full run performed fresh inference for all 720 texts and all 2,790 attribute phrases. Its embedding, Concept207 and Hybrid50 arrays matched the supplied arrays exactly in this environment. All compared CSV values also matched exactly after serialization.

A separate implementation recomputed the distances with SciPy and checked the random maps and bootstrap calculations. Its largest distance discrepancy was below `5 × 10⁻¹²`, consistent with rounding in the supplied CSV files. This independent check matters because rerunning the original calculation alone would not detect every shared implementation error. Machine-readable evidence is in [reproduction_check.json](reproduction_check.json).

The English notebook executed all five code cells in a fresh kernel without errors and embeds three figures. Its setup supports the public Colab URL, but a Google-hosted runtime was not exercised during release preparation. The cached notebook and both CLI modes were tested locally. A full run on another operating system may differ slightly in floating-point values; primary preference equality is checked explicitly and all deviations are reported in the run's `verification.json`.

## Commands

After the installation described in the [README](../README.md):

```bash
python reproduce.py --mode cached --output artifacts/cached
python scripts/make_figures.py --results artifacts/cached --output artifacts/cached/figures
python study/original/execute_notebook.py notebooks/research.ipynb
```

For full inference:

```bash
python -m pip install -r requirements-full.txt
python reproduce.py --mode full --output artifacts/full
```

On Linux, a CPU-only PyTorch installation can avoid downloading CUDA dependencies:

```bash
python -m pip install torch==2.12.0 --index-url https://download.pytorch.org/whl/cpu
python -m pip install -r requirements-full.txt
```

Additional verification:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python study/original/check_metrics.py
python study/original/reports/independent_recheck.py study/original --output-dir artifacts/independent
python scripts/verify_release.py
```

The release verifier checks the distributed files before modification. Executing a notebook updates its outputs and therefore its file hash; use a fresh clone to check the original release hash again. GitHub Actions runs cached reproduction, tests, metric checks, release verification and the notebook automatically. A full CPU run is available through the workflow's manual `full` input.
