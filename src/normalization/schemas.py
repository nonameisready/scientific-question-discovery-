"""Table schemas for the normalized layer (data/normalized/*.parquet).

Defined as pyarrow schemas so both the Parquet writers and DuckDB views
share one source of truth.
"""

from __future__ import annotations

import pyarrow as pa

PAPERS = pa.schema(
    [
        ("paper_id", pa.string()),        # ADS bibcode preferred, else arXiv ID
        ("title", pa.string()),
        ("abstract", pa.string()),
        ("authors", pa.list_(pa.string())),
        ("pubdate", pa.string()),         # YYYY-MM or YYYY-MM-DD
        ("doi", pa.string()),
        ("bibcode", pa.string()),
        ("arxiv_id", pa.string()),
        ("keywords", pa.list_(pa.string())),
        ("objects_mentioned", pa.list_(pa.string())),
        ("source", pa.string()),          # NASA_ADS | arXiv
        ("query_version", pa.string()),   # corpus manifest that fetched it
        ("retrieved_at", pa.string()),
    ]
)

AUTHORS = pa.schema(
    [
        ("paper_id", pa.string()),
        ("author_name", pa.string()),
        ("author_position", pa.int32()),
    ]
)

PAPER_CITATIONS = pa.schema(
    [
        ("citing_paper_id", pa.string()),
        ("cited_paper_id", pa.string()),
    ]
)

CELESTIAL_OBJECTS = pa.schema(
    [
        ("object_name", pa.string()),     # planet name (canonical)
        ("host_star", pa.string()),
        ("mass_earth", pa.float64()),
        ("mass_earth_err1", pa.float64()),
        ("mass_earth_err2", pa.float64()),
        ("radius_earth", pa.float64()),
        ("radius_earth_err1", pa.float64()),
        ("radius_earth_err2", pa.float64()),
        ("orbital_period_days", pa.float64()),
        ("equilibrium_temp_k", pa.float64()),
        ("discovery_method", pa.string()),
        ("stellar_type", pa.string()),
        ("reference", pa.string()),
        ("catalog_updated", pa.string()),
        ("source", pa.string()),
        ("query_version", pa.string()),
    ]
)

OBSERVATIONS = pa.schema(
    [
        ("observation_id", pa.string()),  # MAST obsid
        ("mission", pa.string()),         # JWST | HST
        ("target_name", pa.string()),
        ("instrument", pa.string()),
        ("wavelength_min_m", pa.float64()),
        ("wavelength_max_m", pa.float64()),
        ("exposure_time_s", pa.float64()),
        ("proposal_id", pa.string()),
        ("obs_date_mjd", pa.float64()),
        ("calib_level", pa.int32()),
        ("product_url", pa.string()),
        ("dataproduct_type", pa.string()),
        ("source", pa.string()),
        ("query_version", pa.string()),
    ]
)

DATA_PRODUCTS = pa.schema(
    [
        ("product_id", pa.string()),
        ("observation_id", pa.string()),
        ("product_type", pa.string()),    # e.g. x1d spectrum
        ("calib_level", pa.int32()),
        ("url", pa.string()),
        ("downloaded", pa.bool_()),       # v1: on-demand only
    ]
)

CLAIMS = pa.schema(
    [
        ("claim_id", pa.string()),
        ("paper_id", pa.string()),
        ("claim_text", pa.string()),
        ("supporting_evidence", pa.string()),
        ("assumptions", pa.list_(pa.string())),
        ("uncertainty", pa.string()),
        ("objects", pa.list_(pa.string())),
        ("datasets", pa.list_(pa.string())),
        # source location — always keep a pointer back into the document
        ("section", pa.string()),
        ("page", pa.int32()),
        ("paragraph", pa.int32()),
        ("start_offset", pa.int64()),
        ("end_offset", pa.int64()),
        ("extraction_method", pa.string()),  # human | model:<name>
        ("human_verified", pa.bool_()),
    ]
)

EVIDENCE_LINKS = pa.schema(
    [
        ("link_id", pa.string()),
        ("from_id", pa.string()),
        ("to_id", pa.string()),
        ("relation", pa.string()),        # see evidence_graph.schema.EDGE_TYPES
        ("confidence", pa.float64()),
        ("basis", pa.string()),           # why this link exists (free text / rule id)
        ("created_by", pa.string()),      # rule:<id> | model:<name> | human
    ]
)

# Full-text chunks (data/processed/documents/<paper_id>/chunks.parquet).
# Every chunk must remain traceable to its exact location in the source
# document — text is never stored only inside a vector index.
CHUNKS = pa.schema(
    [
        ("chunk_id", pa.string()),
        ("paper_id", pa.string()),
        ("section", pa.string()),
        ("page", pa.int32()),
        ("paragraph", pa.int32()),
        ("start_offset", pa.int64()),
        ("end_offset", pa.int64()),
        ("text", pa.string()),
        ("source_url", pa.string()),
        ("publication_date", pa.string()),
    ]
)

ALL_TABLES: dict[str, pa.Schema] = {
    "papers": PAPERS,
    "authors": AUTHORS,
    "paper_citations": PAPER_CITATIONS,
    "celestial_objects": CELESTIAL_OBJECTS,
    "observations": OBSERVATIONS,
    "data_products": DATA_PRODUCTS,
    "claims": CLAIMS,
    "evidence_links": EVIDENCE_LINKS,
}
