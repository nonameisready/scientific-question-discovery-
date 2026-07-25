# data/ — Storage Layers

Four-layer storage, from external sources to queryable evidence:

```
External Sources
      ↓
Raw immutable files          data/raw/         (JSONL / verbatim files)
      ↓
Normalized relational tables data/normalized/  (Parquet, queried with DuckDB)
      ↓
Evidence Graph + Vector Index data/processed/  (graph tables, documents, chunks)
```

## What is (and is not) in git

`data/raw/`, `data/normalized/`, and `data/processed/` are **gitignored**.
The repository keeps only what makes them reproducible:

- Download scripts (`src/collectors/`)
- Query definitions (`configs/`)
- Schemas (`src/normalization/schemas.py`, `src/evidence_graph/schema.py`)
- Corpus manifests (`configs/corpus_v1.yaml`, frozen copies in `manifests/`)
- A few sample records (`data/samples/`)
- Small processed benchmark subsets, when published

> Data does not have to live in the repository — but the queries, versions,
> time boundaries, and processing code that produce it must.

## Layout

```
data/
├── raw/                      # verbatim API responses, never overwritten
│   ├── literature/
│   │   ├── ads/<YYYY-MM-DD>/query_NNN.jsonl
│   │   └── arxiv/<YYYY-MM-DD>/query_NNN.jsonl
│   ├── catalogs/
│   │   └── exoplanet_archive/<YYYY-MM-DD>/pscomppars.csv (+ .provenance.json)
│   └── observations/
│       └── mast/<YYYY-MM-DD>/<mission>_metadata.jsonl
├── normalized/               # papers, authors, celestial_objects, ... (Parquet)
├── processed/
│   ├── documents/<paper_id>/ # metadata.json, fulltext.txt, chunks.parquet
│   └── evidence_graph/       # evidence_nodes.parquet, evidence_edges.parquet
└── samples/                  # tiny committed examples of each format
```

## Rules

1. **Raw files are immutable.** Every collection run writes into a new dated
   directory; nothing is ever overwritten. Each record carries a provenance
   envelope (`source`, `retrieved_at`, `query_version`, `source_id`, `payload`)
   so past experiments can be reconstructed after upstream APIs change.
2. **Metadata before bulk data.** Observation collection is metadata-only in
   v1; raw FITS and low-level products are fetched on demand only after a
   question has been selected for falsification.
3. **Full text is never vector-only.** Document text lives as files under
   `data/processed/documents/` with a chunks table carrying `paper_id`,
   `section`, `page`, `paragraph`, `start_offset`, `end_offset`,
   `source_url`, `publication_date` — the vector index (PostgreSQL +
   pgvector in v1) stores embeddings of those chunks, never the only copy.
4. **Watch data contamination.** Every corpus has a `cutoff_date`; record
   retrieval dates so they can be compared against model training cutoffs.
