"""Validate a manually annotated claims file and report coverage.

Checks every record against the Claim schema, verifies paper_ids belong to
the batch selection, and reports per-paper claim counts so calibration
gaps are visible. On success the claims can be merged into the normalized
layer with src.extraction.claims.write_claims.

Usage:
    python -m src.extraction.validate_annotations data/annotations/batch_001
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.extraction.claims import load_claims_jsonl

REQUIRED_NONEMPTY = ("paper_id", "claim_text", "supporting_evidence")


def validate(batch_dir: str | Path) -> int:
    batch_dir = Path(batch_dir)
    selection_ids = set()
    with open(batch_dir / "selection.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                selection_ids.add(json.loads(line)["paper_id"])

    claims = load_claims_jsonl(batch_dir / "claims.jsonl")
    errors: list[str] = []
    for i, claim in enumerate(claims, start=1):
        for field_name in REQUIRED_NONEMPTY:
            if not getattr(claim, field_name).strip():
                errors.append(f"claim {i}: empty {field_name}")
        if claim.paper_id not in selection_ids:
            errors.append(f"claim {i}: paper_id {claim.paper_id!r} not in this batch")
        if claim.location.section == "" and claim.location.paragraph < 0:
            errors.append(f"claim {i}: missing source location (section/paragraph)")

    counts = Counter(c.paper_id for c in claims)
    print(f"[validate] {len(claims)} claims across {len(counts)} papers")
    for pid in sorted(selection_ids):
        print(f"  {pid}: {counts.get(pid, 0)} claims")
    if errors:
        print(f"[validate] {len(errors)} errors:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[validate] OK")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch_dir")
    raise SystemExit(validate(parser.parse_args().batch_dir))
