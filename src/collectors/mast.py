"""MAST observation *metadata* collector for JWST and Hubble.

v1 policy: metadata only. We never bulk-download raw FITS images or low-level
products. Once the system has selected a question worth falsifying, the
corresponding high-level products (e.g. 1-D spectra) are fetched on demand
using the product URLs recorded here.

Uses the MAST Mashup API (https://mast.stsci.edu/api/) — no key needed for
public metadata.

Usage:
    python -m src.collectors.mast --config configs/corpus_v1.yaml

Output:
    data/raw/observations/mast/<YYYY-MM-DD>/<mission>_metadata.jsonl
    One provenance envelope per observation; source_id is the MAST obsid.
"""

from __future__ import annotations

import argparse
import json
import time
from typing import Any, Iterator

import requests

from src.common import envelope, load_corpus_config, raw_dir, write_jsonl

API_URL = "https://mast.stsci.edu/api/v0/invoke"

# Metadata columns kept in v1 (see configs/corpus_v1.yaml).
COLUMNS = [
    "obsid",
    "obs_id",
    "obs_collection",
    "target_name",
    "instrument_name",
    "em_min",             # wavelength range (m)
    "em_max",
    "t_exptime",          # exposure time (s)
    "proposal_id",
    "t_min",              # observation start (MJD)
    "calib_level",
    "dataURL",
    "dataproduct_type",
]

PAGE_SIZE = 5000
REQUEST_DELAY_S = 1.0


def query_mission(mission: str, dataproduct_type: str = "spectrum") -> Iterator[dict[str, Any]]:
    """Yield observation metadata rows for one mission, paginating."""
    page = 1
    while True:
        request = {
            "service": "Mast.Caom.Filtered",
            "format": "json",
            "pagesize": PAGE_SIZE,
            "page": page,
            "params": {
                "columns": ",".join(COLUMNS),
                "filters": [
                    {"paramName": "obs_collection", "values": [mission]},
                    {"paramName": "dataproduct_type", "values": [dataproduct_type]},
                ],
            },
        }
        response = requests.post(
            API_URL, data={"request": json.dumps(request)}, timeout=300
        )
        response.raise_for_status()
        rows = response.json().get("data", [])
        if not rows:
            return
        yield from rows
        if len(rows) < PAGE_SIZE:
            return
        page += 1
        time.sleep(REQUEST_DELAY_S)


def collect(config_path: str) -> list[str]:
    config = load_corpus_config(config_path)
    mast = config["observations"]["mast"]
    if not mast.get("metadata_only", True):
        raise ValueError(
            "v1 policy violation: observations.mast.metadata_only must be true. "
            "Raw products are fetched on demand only after question selection."
        )
    out_dir = raw_dir("observations", "mast")

    written: list[str] = []
    for mission in mast["missions"]:
        records = (
            envelope(
                source="MAST",
                query_version=config["corpus_id"],
                source_id=str(row.get("obsid", "")),
                payload=row,
            )
            for row in query_mission(mission)
        )
        path = out_dir / f"{mission.lower()}_metadata.jsonl"
        n = write_jsonl(path, records)
        print(f"[mast] {mission} -> {n} records -> {path}")
        written.append(str(path))
    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/corpus_v1.yaml")
    collect(parser.parse_args().config)
