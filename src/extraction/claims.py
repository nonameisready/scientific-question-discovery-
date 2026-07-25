"""Claim extraction: schema, validation, and the LLM extraction interface.

A claim is the atomic unit of the Evidence Graph. Each one records what a
paper asserts, on what evidence, under which assumptions, with what
uncertainty — and exactly where in the document it came from.
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.normalization.schemas import CLAIMS


@dataclass
class SourceLocation:
    section: str = ""
    page: int = -1
    paragraph: int = -1
    start_offset: int = -1
    end_offset: int = -1


@dataclass
class Claim:
    paper_id: str
    claim_text: str
    supporting_evidence: str = ""
    assumptions: list[str] = field(default_factory=list)
    uncertainty: str = ""
    objects: list[str] = field(default_factory=list)
    datasets: list[str] = field(default_factory=list)
    location: SourceLocation = field(default_factory=SourceLocation)
    extraction_method: str = "human"
    human_verified: bool = False
    verification_status: str = "human_gold"
    confidence: float = 1.0
    provenance: list[str] = field(default_factory=list)
    claim_id: str = field(default_factory=lambda: f"claim_{uuid.uuid4().hex[:12]}")

    def to_row(self) -> dict:
        row = asdict(self)
        loc = row.pop("location")
        row.update(loc)
        return row


NEGATION_PATTERN = re.compile(
    r"\b(no|not|non-detection|nondetection|rules?\s+out|ruled\s+out|absence|"
    r"without|lack(?:s|ing)?|cannot|fails?\s+to|inconsistent\s+with)\b",
    re.IGNORECASE,
)


def claim_polarity(claim_text: str) -> bool:
    """True if the claim asserts a negative/absence result. Used by the
    dedup matcher (same polarity required) and tension ranking (opposite
    polarity is a conflict signal)."""
    return bool(NEGATION_PATTERN.search(claim_text))


EXTRACTION_PROMPT = """\
You are extracting scientific claims from a research paper on exoplanet
atmospheres. For each substantive claim the paper makes, return a JSON object
with the fields:

  claim_text            The claim, stated precisely in one sentence.
  supporting_evidence   The observation/analysis the paper offers as support.
  assumptions           List of assumptions the claim depends on
                        (e.g. "cloud-free atmosphere", "equilibrium chemistry").
  uncertainty           How the paper qualifies the claim (error bars,
                        significance level, stated caveats).
  objects               Celestial objects the claim is about (canonical names).
  datasets              Datasets or instruments the evidence comes from.
  section               Section of the paper containing the claim.
  paragraph             Paragraph index within that section (0-based).

Only extract claims actually asserted by the authors. Do not extract
background statements attributed to other papers. Return a JSON array.

Paper ID: {paper_id}

Text:
{text}
"""


def extract_claims_with_model(paper_id: str, text: str) -> list[Claim]:
    """Extract claims from one document using an LLM.

    Not wired to a model provider yet — v1 begins with a manual pass over
    ~20 papers (see module docstring) before automating. Plug in a client
    here and parse its JSON output into Claim objects.
    """
    raise NotImplementedError(
        "Model extraction is intentionally unimplemented until the manual "
        "calibration pass over ~20 papers is complete."
    )


def write_claims(claims: list[Claim], out_path: str | Path) -> int:
    """Validate claims against the shared schema and write claims.parquet."""
    table = pa.Table.from_pylist([c.to_row() for c in claims], schema=CLAIMS)
    pq.write_table(table, Path(out_path))
    return table.num_rows


def deterministic_claim_id(paper_id: str, claim_text: str) -> str:
    """Stable content-derived ID so review files (e.g. contradiction
    confirmations) can reference claims across re-ingestions."""
    digest = hashlib.sha1(f"{paper_id}\x1f{claim_text}".encode()).hexdigest()
    return f"claim_{digest[:12]}"


def load_claims_jsonl(path: str | Path) -> list[Claim]:
    """Load manually-authored claims from a JSONL review file. Records
    without an explicit claim_id get a deterministic content-derived one."""
    claims = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            loc = SourceLocation(**data.pop("location", {}))
            data.setdefault(
                "claim_id", deterministic_claim_id(data["paper_id"], data["claim_text"])
            )
            claims.append(Claim(location=loc, **data))
    return claims
