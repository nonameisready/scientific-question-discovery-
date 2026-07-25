"""NASA ADS literature metadata collector.

ADS is the primary literature entry point for astronomy: it covers journals
and preprint metadata, supports search, citations, metrics, and export.

Requires an API token in the ADS_API_TOKEN environment variable
(get one at https://ui.adsabs.harvard.edu/user/settings/token).

Usage:
    python -m src.collectors.ads --config configs/corpus_v1.yaml

Output:
    data/raw/literature/ads/<YYYY-MM-DD>/query_<NNN>.jsonl
    One provenance envelope per record; source_id is the ADS bibcode.
"""

from __future__ import annotations

import argparse
import os
import time
from typing import Any, Iterator

import requests

from src.common import envelope, load_corpus_config, raw_dir, write_jsonl

API_URL = "https://api.adsabs.harvard.edu/v1/search/query"

# Metadata fields collected in v1 (see configs/corpus_v1.yaml).
FIELDS = [
    "bibcode",
    "title",
    "abstract",
    "author",
    "pubdate",
    "doi",
    "identifier",     # includes arXiv IDs
    "citation",       # bibcodes citing this paper
    "reference",      # bibcodes this paper cites
    "keyword",
    "data",           # linked datasets / archives
]

PAGE_SIZE = 200
REQUEST_DELAY_S = 0.35  # stay well under ADS rate limits


def _headers() -> dict[str, str]:
    token = os.environ.get("ADS_API_TOKEN")
    if not token:
        raise EnvironmentError(
            "ADS_API_TOKEN is not set. Create a token at "
            "https://ui.adsabs.harvard.edu/user/settings/token"
        )
    return {"Authorization": f"Bearer {token}"}


def search(
    query: str,
    year_min: int,
    year_max: int,
    max_records: int,
) -> Iterator[dict[str, Any]]:
    """Yield raw ADS documents for a query, paginating until exhausted."""
    q = f"({query}) AND year:{year_min}-{year_max}"
    start = 0
    fetched = 0
    while fetched < max_records:
        params = {
            "q": q,
            "fl": ",".join(FIELDS),
            "rows": min(PAGE_SIZE, max_records - fetched),
            "start": start,
            "sort": "date asc",
        }
        response = requests.get(API_URL, headers=_headers(), params=params, timeout=60)
        response.raise_for_status()
        docs = response.json()["response"]["docs"]
        if not docs:
            return
        for doc in docs:
            yield doc
            fetched += 1
            if fetched >= max_records:
                return
        start += len(docs)
        time.sleep(REQUEST_DELAY_S)


def collect(config_path: str) -> list[str]:
    """Run all ADS queries from a corpus manifest; return written file paths."""
    config = load_corpus_config(config_path)
    lit = config["literature"]
    years = lit["publication_year"]
    per_query_cap = lit["max_records"] // max(len(lit["ads_queries"]), 1)
    out_dir = raw_dir("literature", "ads")

    written: list[str] = []
    for i, query in enumerate(lit["ads_queries"], start=1):
        records = (
            envelope(
                source="NASA_ADS",
                query_version=config["corpus_id"],
                source_id=doc.get("bibcode", ""),
                payload=doc,
            )
            for doc in search(query, years["min"], years["max"], per_query_cap)
        )
        path = out_dir / f"query_{i:03d}.jsonl"
        n = write_jsonl(path, records)
        print(f"[ads] query {i}: {query!r} -> {n} records -> {path}")
        written.append(str(path))
    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/corpus_v1.yaml")
    collect(parser.parse_args().config)
