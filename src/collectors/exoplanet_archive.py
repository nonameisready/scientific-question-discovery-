"""NASA Exoplanet Archive catalog collector (TAP).

Fetches structured planet/star properties so the system can verify whether a
trend claimed in a paper is a general phenomenon or an artifact of a few
special targets. Uses the public TAP endpoint — no key needed.

Usage:
    python -m src.collectors.exoplanet_archive --config configs/corpus_v1.yaml

Output:
    data/raw/catalogs/exoplanet_archive/<YYYY-MM-DD>/<table>.csv
    data/raw/catalogs/exoplanet_archive/<YYYY-MM-DD>/<table>.provenance.json
    The CSV is the verbatim API response; the sidecar records provenance.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

from src.common import load_corpus_config, raw_dir, utc_now_iso

TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"


def fetch_table(table: str, out_dir: Path, query_version: str) -> Path:
    """Download one catalog table as CSV, verbatim, with a provenance sidecar."""
    adql = f"select * from {table}"
    response = requests.get(
        TAP_URL, params={"query": adql, "format": "csv"}, timeout=300
    )
    response.raise_for_status()

    csv_path = out_dir / f"{table}.csv"
    if csv_path.exists():
        raise FileExistsError(f"{csv_path} already exists; raw files are immutable.")
    csv_path.write_text(response.text, encoding="utf-8")

    sidecar = {
        "source": "NASA_Exoplanet_Archive",
        "retrieved_at": utc_now_iso(),
        "query_version": query_version,
        "source_id": table,
        "query": adql,
        "endpoint": TAP_URL,
        "rows": max(response.text.count("\n") - 1, 0),
    }
    sidecar_path = out_dir / f"{table}.provenance.json"
    sidecar_path.write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    return csv_path


def collect(config_path: str) -> list[str]:
    config = load_corpus_config(config_path)
    archive = config["catalogs"]["nasa_exoplanet_archive"]
    out_dir = raw_dir("catalogs", "exoplanet_archive")

    written: list[str] = []
    for table in archive["tables"]:
        path = fetch_table(table, out_dir, config["corpus_id"])
        print(f"[exoplanet_archive] {table} -> {path}")
        written.append(str(path))
    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/corpus_v1.yaml")
    collect(parser.parse_args().config)
