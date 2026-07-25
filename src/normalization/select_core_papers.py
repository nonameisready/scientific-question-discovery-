"""Select the core full-text paper set from the literature metadata.

Implements the manifest's `full_text.selection_method:
citation_and_topic_coverage` using four deterministic criteria:

  citation_count       In-degree within the corpus citation graph
                       (how many corpus papers cite this one).
  keyword_coverage     Hits against the include_keywords in
                       configs/queries/; greedy selection rewards papers
                       that cover keywords not yet represented.
  time_stratification  A per-year quota so no era dominates.
  target_diversity     Planet/host names (from the Exoplanet Archive
                       catalog) mentioned in title+abstract; greedy
                       selection rewards papers introducing new targets.

Outputs:
    data/processed/core_papers.parquet   selected set with score breakdown
    data/processed/paper_objects.parquet paper -> object mentions (ALL papers,
                                         the day-4 cross-layer link table)

Usage:
    python -m src.normalization.select_core_papers
"""

from __future__ import annotations

import argparse
import math
import re
from collections import defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import yaml

from src.common import DATA_ROOT, load_corpus_config

# Greedy score weights: citations anchor quality; unseen keywords and
# targets reward coverage of the topic and object space.
W_CITATIONS = 1.0
W_NEW_KEYWORD = 2.0
W_NEW_TARGET = 0.5

CORE_PAPERS_SCHEMA = pa.schema(
    [
        ("paper_id", pa.string()),
        ("title", pa.string()),
        ("year", pa.int32()),
        ("internal_citations", pa.int32()),
        ("keywords_matched", pa.list_(pa.string())),
        ("targets_matched", pa.list_(pa.string())),
        ("score", pa.float64()),
        ("rank", pa.int32()),
    ]
)

PAPER_OBJECTS_SCHEMA = pa.schema(
    [
        ("paper_id", pa.string()),
        ("object_name", pa.string()),   # canonical catalog planet name
        ("matched_via", pa.string()),   # planet_name | host_star
    ]
)


def _norm(text: str | None) -> str:
    return " ".join((text or "").lower().split())


def _name_pattern(name: str) -> re.Pattern | None:
    """Regex matching an object name in normalized text, tolerant of
    space/hyphen variants ('WASP-39 b' matches 'wasp-39b', 'wasp 39 b',
    'wasp-39 b') and anchored so 'WASP-1' never fires inside 'WASP-12b'."""
    tokens = [t for t in re.split(r"[\s-]+", name.lower()) if t]
    if len("".join(tokens)) < 5:
        return None
    return re.compile(r"[\s-]?".join(map(re.escape, tokens)) + r"(?![a-z0-9])")


def load_inputs(data_root: Path):
    papers = pq.read_table(data_root / "normalized" / "papers.parquet").to_pylist()
    citations = pq.read_table(
        data_root / "normalized" / "paper_citations.parquet"
    ).to_pylist()
    objects = pq.read_table(
        data_root / "normalized" / "celestial_objects.parquet",
        columns=["object_name", "host_star"],
    ).to_pylist()
    return papers, citations, objects


def internal_citation_counts(papers, citations) -> dict[str, int]:
    corpus_ids = {p["paper_id"] for p in papers}
    counts: dict[str, int] = defaultdict(int)
    for edge in citations:
        if edge["cited_paper_id"] in corpus_ids and edge["citing_paper_id"] in corpus_ids:
            counts[edge["cited_paper_id"]] += 1
    return counts


def match_targets(papers, objects) -> dict[str, list[tuple[str, str]]]:
    """Map paper_id -> [(canonical planet name, matched_via)] via name
    matching in title+abstract. Host-star matches attribute the mention to
    the star's planets' host, recorded once per planet name."""
    planet_index = []
    for o in objects:
        regex = _name_pattern(o["object_name"])
        if regex is not None:
            planet_index.append((o["object_name"], regex))

    host_index: dict[str, list[str]] = defaultdict(list)
    host_patterns: dict[str, re.Pattern] = {}
    for o in objects:
        host = o["host_star"]
        if not host:
            continue
        regex = _name_pattern(host)
        if regex is not None:
            host_index[host].append(o["object_name"])
            host_patterns[host] = regex

    hits: dict[str, list[tuple[str, str]]] = {}
    for paper in papers:
        text = _norm(f'{paper["title"] or ""} {paper["abstract"] or ""}')
        found: dict[str, str] = {}
        for name, regex in planet_index:
            if regex.search(text):
                found[name] = "planet_name"
        for host, planets in host_index.items():
            if host_patterns[host].search(text):
                for name in planets:
                    found.setdefault(name, "host_star")
        if found:
            hits[paper["paper_id"]] = sorted(found.items())
    return hits


def match_keywords(papers, keywords: list[str]) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    normalized = [(kw, _norm(kw)) for kw in keywords]
    for paper in papers:
        text = _norm(f'{paper["title"] or ""} {paper["abstract"] or ""}')
        matched = [kw for kw, nkw in normalized if nkw in text]
        if matched:
            hits[paper["paper_id"]] = matched
    return hits


def select(
    papers,
    citation_counts: dict[str, int],
    keyword_hits: dict[str, list[str]],
    target_hits: dict[str, list[tuple[str, str]]],
    max_documents: int,
) -> list[dict]:
    """Greedy, year-stratified selection with global coverage state."""
    by_year: dict[int, list[dict]] = defaultdict(list)
    for paper in papers:
        year = int((paper["pubdate"] or "0")[:4] or 0)
        if year:
            by_year[year].append(paper)

    years = sorted(by_year)
    base_quota = max_documents // len(years)
    # distribute the remainder to the years with the most candidates
    remainder = max_documents - base_quota * len(years)
    quotas = {y: base_quota for y in years}
    for y in sorted(years, key=lambda y: -len(by_year[y]))[:remainder]:
        quotas[y] += 1

    seen_keywords: set[str] = set()
    seen_targets: set[str] = set()
    selected: list[dict] = []

    for year in years:
        pool = {p["paper_id"]: p for p in by_year[year]}
        for _ in range(min(quotas[year], len(pool))):
            best_id, best_score, best_parts = None, -1.0, None
            for pid in pool:
                kws = set(keyword_hits.get(pid, []))
                tgts = {name for name, _ in target_hits.get(pid, [])}
                score = (
                    W_CITATIONS * math.log1p(citation_counts.get(pid, 0))
                    + W_NEW_KEYWORD * len(kws - seen_keywords)
                    + W_NEW_TARGET * len(tgts - seen_targets)
                )
                if score > best_score:
                    best_id, best_score = pid, score
                    best_parts = (kws, tgts)
            paper = pool.pop(best_id)
            seen_keywords |= best_parts[0]
            seen_targets |= best_parts[1]
            selected.append(
                {
                    "paper_id": paper["paper_id"],
                    "title": paper["title"],
                    "year": year,
                    "internal_citations": citation_counts.get(paper["paper_id"], 0),
                    "keywords_matched": sorted(best_parts[0]),
                    "targets_matched": sorted(best_parts[1]),
                    "score": round(best_score, 4),
                    "rank": len(selected) + 1,
                }
            )
    return selected


def run(
    config_path: str = "configs/corpus_v1.yaml",
    queries_path: str = "configs/queries/ads_queries_v1.yaml",
    data_root: Path = DATA_ROOT,
) -> dict:
    config = load_corpus_config(config_path)
    with open(queries_path, encoding="utf-8") as f:
        keywords = yaml.safe_load(f)["include_keywords"]

    papers, citations, objects = load_inputs(data_root)
    citation_counts = internal_citation_counts(papers, citations)
    keyword_hits = match_keywords(papers, keywords)
    target_hits = match_targets(papers, objects)

    out_dir = data_root / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    object_rows = [
        {"paper_id": pid, "object_name": name, "matched_via": via}
        for pid, pairs in target_hits.items()
        for name, via in pairs
    ]
    pq.write_table(
        pa.Table.from_pylist(object_rows, schema=PAPER_OBJECTS_SCHEMA)
        if object_rows
        else PAPER_OBJECTS_SCHEMA.empty_table(),
        out_dir / "paper_objects.parquet",
    )

    core = select(
        papers, citation_counts, keyword_hits, target_hits,
        config["full_text"]["max_documents"],
    )
    pq.write_table(
        pa.Table.from_pylist(core, schema=CORE_PAPERS_SCHEMA),
        out_dir / "core_papers.parquet",
    )

    stats = {
        "candidates": len(papers),
        "selected": len(core),
        "papers_with_targets": len(target_hits),
        "paper_object_links": len(object_rows),
        "distinct_targets_in_core": len(
            {t for p in core for t in p["targets_matched"]}
        ),
        "keywords_covered_in_core": len(
            {k for p in core for k in p["keywords_matched"]}
        ),
    }
    for key, value in stats.items():
        print(f"[select] {key}: {value}")
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/corpus_v1.yaml")
    parser.add_argument("--queries", default="configs/queries/ads_queries_v1.yaml")
    args = parser.parse_args()
    run(args.config, args.queries)
