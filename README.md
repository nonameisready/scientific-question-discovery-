# Scientific Question Discovery

> Research on automated scientific question discovery toward AGI — exploring how intelligent agents can ask good questions like scientists do.

## Overview

This repository is the research workspace for the paper *Scientific Question Discovery*. We argue that one of the key capabilities on the path to AGI is not answering questions, but **discovering scientific questions worth investigating**.

**First study domain: exoplanet atmospheres.** It uniquely combines papers, structured catalogs, and JWST/Hubble observations, making it the easiest domain in which to run the full loop — *evidence → questions → falsification → ranking* — end to end. The v1 corpus is traceable, reproducible, and scope-controlled by design.

## Architecture Overview

```
                Existing Scientific Knowledge
     (Literature · Observations · Catalogs · Data)
                            │
                            ▼
                   Evidence Representation
                            │
                            ▼
                Scientific Reasoning Engine
             ┌─────────┬──────────┬─────────┐
             │         │          │
      Contradictions  Gaps   Alternative Explanations
             └─────────┴──────────┘
                            │
                            ▼
              Evidence-based Question Refinement
                            │
                            ▼
         Ranked High-value Scientific Questions
```

## Data Architecture (v1)

Three source layers, collected in order of increasing cost — never bulk-download raw telescope files up front:

1. **Literature** — what humans have claimed. NASA ADS is the primary entry point (search, citations, metrics, export across astronomy journals and preprints); arXiv supplements it for the newest preprints. v1 collects 2,000–5,000 metadata records (2015–2026), of which 300–800 core papers get full text.
2. **Catalogs** — what objects exist. NASA Exoplanet Archive via TAP: planet/star properties with uncertainties. Used to verify whether a claimed trend is general or an artifact of a few special targets.
3. **Observations** — where the real data lives. MAST metadata for JWST/HST only (target, instrument, wavelength range, exposure, proposal, calibration level, product URL). High-level products such as 1-D spectra are fetched **on demand**, only after a question is selected for falsification.

Four storage layers:

```
External Sources
      ↓
Raw immutable files            data/raw/         JSONL + provenance envelopes
      ↓
Normalized relational tables   data/normalized/  Parquet, queried with DuckDB
      ↓
Evidence Graph + Vector Index  data/processed/   graph tables; pgvector for chunks
```

`data/raw/`, `data/normalized/`, and `data/processed/` are gitignored. The repository keeps download scripts, query definitions, schemas, sample records, corpus manifests, and reproducible experiment configs.

> **Core principle:** the data itself does not have to live in the repository — but the queries, versions, time boundaries, and processing code that produce it must.

## Repository Structure

```
scientific-question-discovery/
├── README.md
├── LICENSE
├── pyproject.toml
├── paper/                 # Manuscript, outline, references
├── src/
│   ├── collectors/        # ads.py · arxiv.py · exoplanet_archive.py · mast.py
│   ├── normalization/     # raw → Parquet tables (DuckDB), shared schemas
│   ├── extraction/        # claims + evidence + assumptions from full text
│   ├── evidence_graph/    # nodes/edges tables + competency queries
│   ├── question_generation/
│   ├── falsification/
│   └── ranking/
├── configs/
│   ├── corpus_v1.yaml     # corpus manifest (scope, queries, cutoff_date)
│   └── queries/           # search keywords and exclusion rules
├── data/
│   ├── raw/               # gitignored — immutable API responses
│   ├── normalized/        # gitignored — Parquet tables
│   ├── processed/         # gitignored — evidence graph, documents, chunks
│   └── samples/           # tiny committed examples of each format
├── manifests/             # frozen corpus manifests (immutable, dated)
├── experiments/           # experiment configs and results
├── evaluations/           # rubrics + historical validation protocol
├── figures/               # figures for the paper
└── tests/                 # offline tests (schemas, manifests, provenance)
```

## The Corpus Manifest

The most important artifact is not the downloaded data but the manifest (`configs/corpus_v1.yaml`): every experiment must know exactly what the system has seen. Its `cutoff_date` enables **historical backtesting**:

- **Corpus A** — only data available up to 2020-12-31.
- **Validation** — discoveries from 2021–2026 verify whether the questions generated from Corpus A were later posed, answered, or proven valuable.

This prevents the system from peeking at the future and is the foundation of the Historical Validation protocol (see `evaluations/README.md`).

## Getting Started

```bash
git clone <repo-url> && cd scientific-question-discovery
pip install -e ".[dev]"
export ADS_API_TOKEN=...   # https://ui.adsabs.harvard.edu/user/settings/token

python -m src.collectors.ads               --config configs/corpus_v1.yaml
python -m src.collectors.arxiv             --config configs/corpus_v1.yaml
python -m src.collectors.exoplanet_archive --config configs/corpus_v1.yaml
python -m src.collectors.mast              --config configs/corpus_v1.yaml
python -m src.normalization.build_tables
python -m src.evidence_graph.build
python -m src.evidence_graph.queries

pytest   # offline tests: schemas, manifest, provenance rules
```

## V1 Build Plan

1. **Fix the scope** — one concrete problem: atmospheric composition interpretation in exoplanet transmission spectra, cloud/haze degeneracies, and instrument systematics. Keywords and exclusion rules live in `configs/queries/`.
2. **Collect literature metadata only** — 2,000–5,000 ADS records, deduplicated, stored as JSONL and Parquet.
3. **Build the core paper set** — filter to ~500 papers by citation count, keyword coverage, time stratification, and target diversity.
4. **Connect catalogs and MAST metadata** — link planet names in papers to NASA Exoplanet Archive rows and MAST observation records.
5. **Extract the first claims** — manually review 20 papers, then run model extraction over 100 (claim, supporting evidence, assumptions, uncertainty, objects, source location).
6. **Build the minimal Evidence Graph** — prove the system can answer: Which papers conflict? Does a conflict come from data, method, or assumptions? Which conclusions rest on a single dataset? Which targets show unexplained discrepancies?

### Minimum viable scale

| Data                    | v1 scale                     |
|-------------------------|------------------------------|
| Literature metadata     | 2,000–5,000 papers           |
| Core full text          | 300–500 papers               |
| Catalog objects         | thousands                    |
| Observation metadata    | thousands–tens of thousands  |
| Human-verified claims   | 200–500                      |
| Candidate questions     | 50–200                       |
| Top-K ranked questions  | 10–20                        |

This is already enough to validate the framework.

## Infrastructure Requirements

| Component      | v1 choice                                | Needed when |
|----------------|-------------------------------------------|-------------|
| ADS API token  | `ADS_API_TOKEN` env var (free)            | Before literature collection |
| Tables/queries | DuckDB + Parquet (no server)              | Nothing to provision |
| Vector index   | PostgreSQL + pgvector via `PG_DSN` env var | Before full-text semantic search |
| Graph database | Not yet — plain tables until complex graph queries are truly needed | Deferred |

Secrets are configured through environment variables or a local `.env` file
(gitignored): copy `.env.example` to `.env` and fill in the values. For the
vector index, install the extras and verify the connection with:

```bash
pip install -e ".[vector]"
python -m src.vector_index.db   # connects, enables pgvector, creates chunks table
```

## Citation

A BibTeX entry will be provided here once the paper is complete.

## License

This project is licensed under the [MIT License](LICENSE).
