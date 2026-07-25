"""Ingest validated annotation batches into the normalized claims table.

Loads every data/annotations/*/claims.jsonl, assigns deterministic claim
IDs, and rebuilds data/normalized/claims.parquet. Run validation first:

    python -m src.extraction.validate_annotations data/annotations/batch_001
    python -m src.extraction.ingest
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.common import DATA_ROOT
from src.extraction.claims import load_claims_jsonl, write_claims


def run(data_root: Path = DATA_ROOT) -> int:
    claims = []
    for path in sorted((data_root / "annotations").glob("*/claims.jsonl")):
        batch_claims = load_claims_jsonl(path)
        print(f"[ingest] {path.parent.name}: {len(batch_claims)} claims")
        claims.extend(batch_claims)

    seen: set[str] = set()
    unique = []
    for claim in claims:
        if claim.claim_id not in seen:
            seen.add(claim.claim_id)
            unique.append(claim)

    out = data_root / "normalized" / "claims.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    n = write_claims(unique, out)
    print(f"[ingest] total: {n} unique claims -> {out}")
    return n


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    run()
