# manifests/ — Frozen Corpus Manifests

Every experiment must know exactly what the system has seen. A corpus
manifest pins the scope, queries, time boundaries, and selection rules that
produced a corpus.

## Workflow

1. Author or edit the working manifest in `configs/` (e.g.
   `configs/corpus_v1.yaml`).
2. When a corpus is actually collected, copy the manifest here as a frozen
   record, suffixed with the collection date:

   ```
   manifests/exoplanet_atmospheres_v1__2026-07-26.yaml
   ```

3. Frozen manifests are immutable. A change in scope means a new
   `corpus_id` (e.g. `exoplanet_atmospheres_v2`), never an edit in place.
4. Every experiment config in `experiments/` references a frozen manifest
   by filename, so results always trace back to an exact corpus definition.

## cutoff_date and historical backtesting

`cutoff_date` is the most important field. It enables historical
validation without letting the system peek at the future:

- **Corpus A** — only data available up to `2020-12-31`.
- **Validation** — discoveries published 2021-2026 are used to check
  whether the questions generated from Corpus A were later answered or
  proven valuable.

See `evaluations/README.md` for the validation protocol.
