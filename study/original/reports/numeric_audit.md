# Independent numeric audit

Status: **OK**. Read the saved 720 encoder vectors, reconstructed the concept207 and hybrid50 representations, and independently recomputed all 720 main per-triplet rows, 28,800 random-control rows, summaries, transitions, audit sensitivity, leave-one-author-out tables, and the 18 bootstrap intervals from saved artifacts.

Study package: `study/original`

The reference uses `scipy.spatial.distance.cosine` pair by pair. All comparisons tolerate at most 1e-10 absolute error (CSV values are written to 12 significant digits). No encoder, prior study, or experiment module was imported. This is an AI numeric check of saved artifacts, not human semantic validation.
