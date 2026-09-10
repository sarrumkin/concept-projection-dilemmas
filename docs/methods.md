# Methods

## Design

The fixed dataset has 240 triplets (720 unique English texts), balanced as 12 conflict classes × 10 anchor topics × 2 variants. A is the query, B is the same presumed conflict in another topic, and C is another conflict in A’s topic. The primary research comparison is Concept207 versus the original embedding; Hybrid50 versus embedding is secondary.

The encoder is `paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions, revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`. Inputs are whole paragraphs, limited to 128 tokens. Metadata, audit answers, and labels are excluded from encoder input. Attribute definitions and prototypes come from Bhatia et al.; reasons are not extracted from these texts.

The source CSV contains 414 directional rows for 207 attributes. Each row's semicolon-separated phrases are embedded and individually normalized; their mean is normalized to obtain a directional prototype. The positive and negative prototypes for an attribute are added and normalized to form one row of `P`. Attribute names and their ordering are checked against the supplied prototype bank. The full reproduction mode regenerates these prototypes using the same pinned encoder as the texts.

For normalized embedding `z` and prototype matrix `P`, centered attributes are:

`c = norm(z (P − mean_rows(P))ᵀ)`

Concept207 compares cosine distance in `c`. Hybrid50 uses `h = [z/√2; c/√2]`, equivalent to the mean of the embedding and Concept207 cosine distances. Distances are `d = 1 − cosine` in [0, 2]. Accuracy scores 1, 0, or 0.5 for B preferred, C preferred, or a tie.

## Intervals and controls

The reported descriptive intervals use 10,000 two-factor bootstrap reweightings of conflicts and anchor topics, retaining both variants in sampled cells. They describe stability of the selected synthetic grid and are not population confidence intervals. Controls comprise 30 Gaussian maps and 30 spectrum-matched random orientations, each evaluated alone and in the 50/50 mixture.

## Source clarification

Bhatia et al. analyse more than 100,000 Reddit and US-survey dilemmas. Their pipeline uses GPT-derived benefits and costs and SBERT mapping to 207 attributes. Study 4a fits individual models to eight dilemmas per participant; mean R² is 0.24 for the attribute model versus 0.14 for text and random alternatives. That result is model fit, not retrieval accuracy. This repository borrows the attribute bank and applies it to whole-text geometry.

## Audit history

The initial 140/240 joint agreement rose to 225/240 after a separate masked candidate-letter/explanation alignment check. This correction did not change texts, methods, or the primary 240 authored relations. The later check is not an independent third semantic audit.

## Editorial provenance

The author clarified Concept207 as the primary research subject when preparing this public presentation. The historical assistant-written [protocol](../study/original/PROTOCOL.md) designated Hybrid50 − embedding as its principal contrast. That document is preserved unchanged. All three comparisons were computed and remain available, including Hybrid50 − Concept207. The current hierarchy describes the research presentation and is not claimed to be the original protocol priority.

## References

- [Bhatia et al., PNAS (2025)](https://doi.org/10.1073/pnas.2406489122).
- [Original code and data, OSF](https://osf.io/f29be/).
- [MiniLM model card](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2).
