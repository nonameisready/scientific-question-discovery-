"""arXiv preprint metadata collector (supplement to ADS).

ADS is the primary literature entry point; arXiv fills the gap for the very
latest preprints not yet indexed. Uses the public Atom API — no key needed.

Usage:
    python -m src.collectors.arxiv --config configs/corpus_v1.yaml

Output:
    data/raw/literature/arxiv/<YYYY-MM-DD>/query_<NNN>.jsonl
    One provenance envelope per record; source_id is the arXiv ID.
"""

from __future__ import annotations

import argparse
import time
import xml.etree.ElementTree as ET
from typing import Any, Iterator

import requests

from src.common import envelope, load_corpus_config, raw_dir, write_jsonl

API_URL = "https://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"

PAGE_SIZE = 100
REQUEST_DELAY_S = 3.0  # arXiv asks for no more than 1 request / 3 s


def _parse_entry(entry: ET.Element) -> dict[str, Any]:
    doi_el = entry.find(f"{ARXIV}doi")
    return {
        "arxiv_id": (entry.findtext(f"{ATOM}id") or "").rsplit("/abs/", 1)[-1],
        "title": " ".join((entry.findtext(f"{ATOM}title") or "").split()),
        "abstract": " ".join((entry.findtext(f"{ATOM}summary") or "").split()),
        "authors": [
            a.findtext(f"{ATOM}name") for a in entry.findall(f"{ATOM}author")
        ],
        "published": entry.findtext(f"{ATOM}published"),
        "doi": doi_el.text if doi_el is not None else None,
        "categories": [
            c.get("term") for c in entry.findall(f"{ATOM}category")
        ],
    }


def search(query: str, max_records: int, category: str = "astro-ph.EP") -> Iterator[dict[str, Any]]:
    """Yield parsed arXiv entries for a query, paginating until exhausted."""
    start = 0
    while start < max_records:
        params = {
            "search_query": f'all:{query} AND cat:{category}',
            "start": start,
            "max_results": min(PAGE_SIZE, max_records - start),
            "sortBy": "submittedDate",
            "sortOrder": "ascending",
        }
        response = requests.get(API_URL, params=params, timeout=60)
        response.raise_for_status()
        entries = ET.fromstring(response.text).findall(f"{ATOM}entry")
        if not entries:
            return
        for entry in entries:
            yield _parse_entry(entry)
        start += len(entries)
        time.sleep(REQUEST_DELAY_S)


def collect(config_path: str) -> list[str]:
    """Run supplement queries from the corpus manifest; return written paths."""
    config = load_corpus_config(config_path)
    lit = config["literature"]
    per_query_cap = lit["max_records"] // max(len(lit["ads_queries"]), 1)
    out_dir = raw_dir("literature", "arxiv")

    written: list[str] = []
    for i, query in enumerate(lit["ads_queries"], start=1):
        plain = query.replace('"', "").replace(" AND ", " ")
        records = (
            envelope(
                source="arXiv",
                query_version=config["corpus_id"],
                source_id=doc["arxiv_id"],
                payload=doc,
            )
            for doc in search(plain, per_query_cap)
        )
        path = out_dir / f"query_{i:03d}.jsonl"
        n = write_jsonl(path, records)
        print(f"[arxiv] query {i}: {plain!r} -> {n} records -> {path}")
        written.append(str(path))
    return written


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/corpus_v1.yaml")
    collect(parser.parse_args().config)
