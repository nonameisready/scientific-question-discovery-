"""Prepare a manual claim-annotation batch (v1 plan step 5, calibration pass).

Picks papers from the core set by round-robin over publication years in
selection order, so the calibration batch spans the full time window and
inherits the core set's target/keyword diversity. Emits a human-readable
worksheet with titles, links, abstracts, and matched targets, plus an
empty claims file for the annotator to fill (validate it afterwards with
src.extraction.validate_annotations).

Usage:
    python -m src.extraction.prepare_annotation --batch 001 --size 20

Output (committed to git — human annotations are source data, unlike the
regenerable raw/normalized/processed layers):
    data/annotations/batch_<NNN>/papers.md
    data/annotations/batch_<NNN>/selection.jsonl
    data/annotations/batch_<NNN>/claims.jsonl   (empty, to be filled)
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import pyarrow.parquet as pq

from src.common import DATA_ROOT


def ads_link(bibcode: str | None) -> str | None:
    return f"https://ui.adsabs.harvard.edu/abs/{bibcode}/abstract" if bibcode else None


def arxiv_link(arxiv_id: str | None) -> str | None:
    return f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else None


def pick_round_robin(core: list[dict], size: int) -> list[dict]:
    """Round-robin over years; within a year prefer papers that matched
    topic keywords and have high internal citations — a calibration batch
    needs claim-dense, clearly in-scope papers (coverage is already the
    core set's job)."""
    by_year: dict[int, list[dict]] = defaultdict(list)
    order = sorted(
        core,
        key=lambda r: (
            -bool(r["keywords_matched"]),
            -r["internal_citations"],
            r["rank"],
        ),
    )
    for row in order:
        by_year[row["year"]].append(row)
    picked: list[dict] = []
    years = sorted(by_year)
    while len(picked) < size and any(by_year[y] for y in years):
        for year in years:
            if by_year[year] and len(picked) < size:
                picked.append(by_year[year].pop(0))
    return picked


def run(batch: str, size: int, data_root: Path = DATA_ROOT) -> Path:
    core = pq.read_table(data_root / "processed" / "core_papers.parquet").to_pylist()
    papers = {
        p["paper_id"]: p
        for p in pq.read_table(data_root / "normalized" / "papers.parquet").to_pylist()
    }
    picked = pick_round_robin(core, size)

    out_dir = data_root / "annotations" / f"batch_{batch}"
    out_dir.mkdir(parents=True, exist_ok=True)

    selection_rows = []
    lines = [
        f"# Claim Annotation Batch {batch}",
        "",
        f"{len(picked)} papers selected from the core set by round-robin over",
        "publication years in selection order. See ANNOTATION_GUIDE.md for the",
        "claim schema and rules; record claims in claims.jsonl.",
        "",
    ]
    for i, row in enumerate(picked, start=1):
        meta = papers[row["paper_id"]]
        links = [l for l in (ads_link(meta.get("bibcode")), arxiv_link(meta.get("arxiv_id"))) if l]
        selection_rows.append(
            {
                "n": i,
                "paper_id": row["paper_id"],
                "year": row["year"],
                "internal_citations": row["internal_citations"],
                "targets_matched": row["targets_matched"],
                "links": links,
            }
        )
        lines += [
            f"## {i}. {meta['title']}",
            "",
            f"- paper_id: `{row['paper_id']}`",
            f"- year: {row['year']}  |  internal citations: {row['internal_citations']}",
            f"- targets: {', '.join(row['targets_matched']) or '(none matched)'}",
        ]
        lines += [f"- link: {l}" for l in links]
        lines += ["", f"> {meta['abstract'] or '(no abstract)'}", ""]

    (out_dir / "papers.md").write_text("\n".join(lines), encoding="utf-8")
    with open(out_dir / "selection.jsonl", "w", encoding="utf-8") as f:
        for row in selection_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    claims_path = out_dir / "claims.jsonl"
    if not claims_path.exists():
        claims_path.write_text("", encoding="utf-8")

    print(f"[annotation] batch {batch}: {len(picked)} papers -> {out_dir}")
    years = sorted({r['year'] for r in picked})
    print(f"[annotation] year coverage: {years}")
    return out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", default="001")
    parser.add_argument("--size", type=int, default=20)
    args = parser.parse_args()
    run(args.batch, args.size)
