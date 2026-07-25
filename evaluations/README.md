# evaluations/ — Evaluation & Historical Validation

How we measure whether the system discovers scientific questions that are
actually worth asking.

## Scoring dimensions

Shared with `src/ranking/`:

| Dimension    | Question it answers                                           |
|--------------|---------------------------------------------------------------|
| Novelty      | Is it more than a paraphrase of a question already in print?   |
| Feasibility  | Could existing or near-term observations answer it?            |
| Significance | Would resolving it change the conclusions of multiple papers?  |
| Clarity      | Is it precise enough to design a falsification test against?   |

Scoring methods: a documented human evaluation protocol plus automated
evaluation (LLM-as-judge), with rubrics written down explicitly so the
evaluation is reproducible.

## Historical validation (the core protocol)

The corpus manifest's `cutoff_date` makes backtesting possible:

1. **Corpus A** — build the corpus using only data available up to
   `2020-12-31` (literature, catalog snapshots, observation metadata).
2. **Generate** — run the full pipeline on Corpus A to produce ranked
   questions.
3. **Validate** — check the 2021-2026 literature: which generated questions
   were subsequently posed, answered, or shown to be high-value by the
   community? Which were dead ends?

Leakage rules:
- Nothing dated after the cutoff may enter Corpus A — including catalog
  rows whose `rowupdate` postdates the cutoff.
- Retrieval dates and model training cutoffs are recorded so contamination
  can be audited.

## Minimum viable scale (v1)

| Data                        | v1 scale            |
|-----------------------------|---------------------|
| Literature metadata         | 2,000-5,000 papers  |
| Core full text              | 300-500 papers      |
| Catalog objects             | thousands           |
| Observation metadata        | thousands-tens of thousands |
| Human-verified claims       | 200-500             |
| Candidate questions         | 50-200              |
| Top-K ranked questions      | 10-20               |

This is sufficient to validate the framework; scale comes later.
