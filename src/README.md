# src/ — Pipeline Source Code

Each package is one stage of the architecture in the top-level README:

| Package                | Stage                                                    |
|------------------------|----------------------------------------------------------|
| `collectors/`          | Existing scientific knowledge (ADS, arXiv, Exoplanet Archive, MAST) |
| `normalization/`       | Evidence representation — raw JSONL/CSV → Parquet tables (DuckDB) |
| `extraction/`          | Claims, supporting evidence, assumptions from full text  |
| `evidence_graph/`      | Contradictions, gaps, alternative explanations           |
| `question_generation/` | Candidate scientific questions from graph signals        |
| `falsification/`       | Evidence-based question refinement                       |
| `ranking/`             | Ranked high-value scientific questions                   |

## Running the v1 pipeline

```bash
pip install -e ".[dev]"
export ADS_API_TOKEN=...   # https://ui.adsabs.harvard.edu/user/settings/token

# 1. Collect (raw, immutable, provenance-wrapped)
python -m src.collectors.ads               --config configs/corpus_v1.yaml
python -m src.collectors.arxiv             --config configs/corpus_v1.yaml
python -m src.collectors.exoplanet_archive --config configs/corpus_v1.yaml
python -m src.collectors.mast              --config configs/corpus_v1.yaml

# 2. Normalize (Parquet tables under data/normalized/)
python -m src.normalization.build_tables

# 3. Build the Evidence Graph and run the competency queries
python -m src.evidence_graph.build
python -m src.evidence_graph.queries
```

`extraction/`, `question_generation/`, `falsification/`, and `ranking/`
define their interfaces and protocols in module docstrings; they are
implemented after the manual claim-calibration pass (20 papers by hand,
then model extraction over 100).
