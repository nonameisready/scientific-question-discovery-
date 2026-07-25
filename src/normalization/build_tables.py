"""Build the normalized Parquet tables from raw provenance-wrapped files.

Reads:
    data/raw/literature/ads/**/*.jsonl
    data/raw/literature/arxiv/**/*.jsonl
    data/raw/catalogs/exoplanet_archive/**/pscomppars.csv
    data/raw/observations/mast/**/*.jsonl

Writes:
    data/normalized/<table>.parquet   (one file per table, deduplicated)

Usage:
    python -m src.normalization.build_tables
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from src.common import DATA_ROOT, read_jsonl
from src.normalization import schemas


def _empty(schema: pa.Schema) -> pa.Table:
    return schema.empty_table()


def _first_arxiv_id(identifiers: list[str] | None) -> str | None:
    for ident in identifiers or []:
        if ident.startswith("arXiv:"):
            return ident.removeprefix("arXiv:")
    return None


def _strip_arxiv_version(arxiv_id: str) -> str:
    """'1401.0022v2' -> '1401.0022' (version suffix varies between sources)."""
    head, _, tail = arxiv_id.rpartition("v")
    return head if head and tail.isdigit() else arxiv_id


def build_papers(raw_root: Path) -> tuple[pa.Table, pa.Table, pa.Table]:
    """Flatten ADS + arXiv envelopes into papers, authors, paper_citations."""
    papers: list[dict[str, Any]] = []
    authors: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    seen: set[str] = set()

    for path in sorted(raw_root.glob("literature/ads/**/*.jsonl")):
        for rec in read_jsonl(path):
            doc = rec["payload"]
            paper_id = doc.get("bibcode") or rec["source_id"]
            if not paper_id or paper_id in seen:
                continue
            seen.add(paper_id)
            title = doc.get("title")
            papers.append(
                {
                    "paper_id": paper_id,
                    "title": title[0] if isinstance(title, list) else title,
                    "abstract": doc.get("abstract"),
                    "authors": doc.get("author") or [],
                    "pubdate": doc.get("pubdate"),
                    "doi": (doc.get("doi") or [None])[0],
                    "bibcode": doc.get("bibcode"),
                    "arxiv_id": _first_arxiv_id(doc.get("identifier")),
                    "keywords": doc.get("keyword") or [],
                    "objects_mentioned": doc.get("data") or [],
                    "source": rec["source"],
                    "query_version": rec["query_version"],
                    "retrieved_at": rec["retrieved_at"],
                }
            )
            for pos, name in enumerate(doc.get("author") or []):
                authors.append(
                    {"paper_id": paper_id, "author_name": name, "author_position": pos}
                )
            for cited in doc.get("reference") or []:
                citations.append({"citing_paper_id": paper_id, "cited_paper_id": cited})

    # Cross-source dedup: ADS records carry their arXiv ID, so an arXiv
    # record matching one is the same paper under a different identifier.
    ads_arxiv_ids = {
        _strip_arxiv_version(p["arxiv_id"]) for p in papers if p["arxiv_id"]
    }
    for path in sorted(raw_root.glob("literature/arxiv/**/*.jsonl")):
        for rec in read_jsonl(path):
            doc = rec["payload"]
            bare_id = _strip_arxiv_version(doc["arxiv_id"] or "")
            paper_id = f"arXiv:{bare_id}"
            if not bare_id or paper_id in seen or bare_id in ads_arxiv_ids:
                continue
            seen.add(paper_id)
            papers.append(
                {
                    "paper_id": paper_id,
                    "title": doc.get("title"),
                    "abstract": doc.get("abstract"),
                    "authors": doc.get("authors") or [],
                    "pubdate": (doc.get("published") or "")[:10],
                    "doi": doc.get("doi"),
                    "bibcode": None,
                    "arxiv_id": doc.get("arxiv_id"),
                    "keywords": doc.get("categories") or [],
                    "objects_mentioned": [],
                    "source": rec["source"],
                    "query_version": rec["query_version"],
                    "retrieved_at": rec["retrieved_at"],
                }
            )

    return (
        pa.Table.from_pylist(papers, schema=schemas.PAPERS) if papers else _empty(schemas.PAPERS),
        pa.Table.from_pylist(authors, schema=schemas.AUTHORS) if authors else _empty(schemas.AUTHORS),
        pa.Table.from_pylist(citations, schema=schemas.PAPER_CITATIONS)
        if citations
        else _empty(schemas.PAPER_CITATIONS),
    )


def build_celestial_objects(raw_root: Path, con: duckdb.DuckDBPyConnection) -> pa.Table:
    """Normalize the Exoplanet Archive pscomppars CSV via DuckDB."""
    csvs = sorted(raw_root.glob("catalogs/exoplanet_archive/**/pscomppars.csv"))
    if not csvs:
        return _empty(schemas.CELESTIAL_OBJECTS)
    latest = str(csvs[-1])
    return con.execute(
        """
        SELECT
            pl_name          AS object_name,
            hostname         AS host_star,
            pl_bmasse        AS mass_earth,
            pl_bmasseerr1    AS mass_earth_err1,
            pl_bmasseerr2    AS mass_earth_err2,
            pl_rade          AS radius_earth,
            pl_radeerr1      AS radius_earth_err1,
            pl_radeerr2      AS radius_earth_err2,
            pl_orbper        AS orbital_period_days,
            pl_eqt           AS equilibrium_temp_k,
            discoverymethod  AS discovery_method,
            st_spectype      AS stellar_type,
            disc_refname     AS reference,
            CAST(pl_pubdate AS VARCHAR) AS catalog_updated,
            'NASA_Exoplanet_Archive'   AS source,
            ''               AS query_version
        FROM read_csv(?, header=true, delim=',', quote='"', escape='"',
                      strict_mode=false, sample_size=-1, max_line_size=10000000)
        """,
        [latest],
    ).fetch_arrow_table().cast(schemas.CELESTIAL_OBJECTS)


def build_observations(raw_root: Path) -> pa.Table:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in sorted(raw_root.glob("observations/mast/**/*.jsonl")):
        for rec in read_jsonl(path):
            obs = rec["payload"]
            obs_id = str(obs.get("obsid", ""))
            if not obs_id or obs_id in seen:
                continue
            seen.add(obs_id)
            rows.append(
                {
                    "observation_id": obs_id,
                    "mission": obs.get("obs_collection"),
                    "target_name": obs.get("target_name"),
                    "instrument": obs.get("instrument_name"),
                    "wavelength_min_m": obs.get("em_min"),
                    "wavelength_max_m": obs.get("em_max"),
                    "exposure_time_s": obs.get("t_exptime"),
                    "proposal_id": str(obs.get("proposal_id", "")),
                    "obs_date_mjd": obs.get("t_min"),
                    "calib_level": obs.get("calib_level"),
                    "product_url": obs.get("dataURL"),
                    "dataproduct_type": obs.get("dataproduct_type"),
                    "source": rec["source"],
                    "query_version": rec["query_version"],
                }
            )
    return (
        pa.Table.from_pylist(rows, schema=schemas.OBSERVATIONS)
        if rows
        else _empty(schemas.OBSERVATIONS)
    )


def build_all(data_root: Path = DATA_ROOT) -> dict[str, int]:
    """Build every normalized table; returns row counts per table."""
    raw_root = data_root / "raw"
    out_dir = data_root / "normalized"
    out_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect()

    papers, authors, citations = build_papers(raw_root)
    tables: dict[str, pa.Table] = {
        "papers": papers,
        "authors": authors,
        "paper_citations": citations,
        "celestial_objects": build_celestial_objects(raw_root, con),
        "observations": build_observations(raw_root),
        # Populated by later pipeline stages; created empty so the schema
        # is fixed from day one.
        "data_products": _empty(schemas.DATA_PRODUCTS),
        "claims": _empty(schemas.CLAIMS),
        "evidence_links": _empty(schemas.EVIDENCE_LINKS),
    }

    counts: dict[str, int] = {}
    for name, table in tables.items():
        pq.write_table(table, out_dir / f"{name}.parquet")
        counts[name] = table.num_rows
        print(f"[normalize] {name}: {table.num_rows} rows -> {out_dir / f'{name}.parquet'}")
    return counts


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    build_all()
