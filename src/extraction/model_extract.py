"""Model-based claim extraction over core papers (v1: abstract-only).

Scales the calibration protocol to ~100 papers: the picker returns the
same ordering as the manual batch, so the first 20 papers overlap the
human gold set — that overlap is the evaluation sample for extraction
quality. Full-text extraction replaces this once document ingestion
lands; every record is labeled `model:<name> (abstract-only)` so the
provenance of the shallower source is never lost.

Requires OPENAI_API_KEY in the environment or .env.

Usage:
    python -m src.extraction.model_extract --size 100 --model gpt-4.1

Output:
    data/processed/model_claims/<model>/claims.jsonl   (resumable)
    data/processed/model_claims/<model>/gold_comparison.md
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import pyarrow.parquet as pq
import requests

from src.common import DATA_ROOT, load_dotenv, utc_now_iso
from src.extraction.claims import deterministic_claim_id, load_claims_jsonl
from src.extraction.prepare_annotation import pick_round_robin

API_URL = "https://api.openai.com/v1/chat/completions"
REQUEST_DELAY_S = 0.5

# Prompt revision history (recorded in extraction_method for provenance):
#   p1  initial calibration run (over-split measurements, occasional
#       first-person copying, missed interpretive conclusions)
#   p2  load-bearing-claims revision from the batch 001 gold review:
#       2-6 claims, priority ordering, merge coupled measurements,
#       normalized third person, omission self-check
#   p3  cap tightened to 2-5 (p2 filled the 2-6 headroom, avg 3.9/paper)
#       and standalone system-parameter measurements excluded
PROMPT_VERSION = "p3"

SYSTEM_PROMPT = """\
You extract scientific claims from the title and abstract of research papers
on exoplanet atmospheres. A claim is a substantive assertion the AUTHORS
THEMSELVES make based on their own analysis. Do not extract background
statements attributed to other papers, method-step descriptions, or
speculation flagged as future work.

Extract 2-5 LOAD-BEARING claims per paper — the assertions the paper exists
to make — not an inventory of every result. Most abstracts support only 2-4;
reserve 5 for exceptionally rich abstracts. Never pad to the cap.

Priority order when deciding what to extract:
  1. Main scientific conclusion
  2. Interpretation or mechanism — what the result means or implies
  3. Methodological limitation, or a challenge to prior literature or
     common assumptions
  4. Decisive quantitative result
  5. Secondary descriptive measurement (usually omit)

Rules:
- Merge tightly coupled measurements into ONE claim when they support the
  same conclusion. Example: line contrasts, layer temperatures, and a
  velocity blueshift that jointly establish "hotter upper atmosphere with a
  high-altitude wind" are one claim; put the numbers in
  supporting_evidence and uncertainty, not in separate claims.
- Write claim_text in normalized third-person form: "HARPS transmission
  spectroscopy resolves the sodium doublet ..." — never copy the abstract's
  first person ("we find", "we measure").
- Omit standalone system-parameter measurements (spin-orbit angles, orbital
  elements, stellar parameters, masses, radii) unless that measurement is
  the paper's central result.
- Keep interpretations even when qualitative: what a result implies, what
  mechanism could explain it, or which prior results it calls into question
  are MORE valuable to extract than additional numbers.

Before finalizing, check yourself:
- Did I include the paper's main interpretation, not just its measurements?
- Did I include any claim that challenges prior literature or assumptions?
- Did I let a low-priority numeric detail displace a higher-value
  interpretation? If so, swap it out.

Return JSON: {"claims": [...]} , each object with exactly these keys:
  claim_text            One precise sentence stating the claim.
  supporting_evidence   The observation/analysis offered as support.
  assumptions           List of assumptions the claim depends on ([] if none).
  uncertainty           How the abstract qualifies it (sigmas, caveats); "" if unstated.
  objects               Celestial objects the claim is about, canonical catalog
                        names like "WASP-39 b" (space before the planet letter).
  datasets              Instruments/programs the evidence comes from, e.g.
                        "HST/WFC3", "JWST/NIRSpec"; [] if unstated.

If the abstract makes no extractable claim, return {"claims": []}.
"""


def _as_list(value) -> list[str]:
    """The model occasionally returns a bare string where a list is
    expected; coerce so records always satisfy the claims schema."""
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value]


def _headers() -> dict[str, str]:
    load_dotenv()
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise EnvironmentError("OPENAI_API_KEY is not set (env var or .env).")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def extract_one(model: str, title: str, abstract: str) -> list[dict]:
    body = {
        "model": model,
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Title: {title}\n\nAbstract: {abstract}"},
        ],
    }
    for attempt in range(4):
        response = requests.post(API_URL, headers=_headers(), json=body, timeout=120)
        if response.status_code == 429 or response.status_code >= 500:
            time.sleep(2 ** (attempt + 1))
            continue
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content).get("claims", [])
    response.raise_for_status()
    return []


def _gold_paper_ids(data_root: Path) -> set[str]:
    ids: set[str] = set()
    for batch in sorted((data_root / "annotations").glob("*/claims.jsonl")):
        ids |= {c.paper_id for c in load_claims_jsonl(batch)}
    return ids


def run(
    size: int,
    model: str,
    only_overlap: bool = False,
    data_root: Path = DATA_ROOT,
) -> Path:
    core = pq.read_table(data_root / "processed" / "core_papers.parquet").to_pylist()
    papers = {
        p["paper_id"]: p
        for p in pq.read_table(data_root / "normalized" / "papers.parquet").to_pylist()
    }
    picked = pick_round_robin(core, size)
    if only_overlap:
        gold_ids = _gold_paper_ids(data_root)
        picked = [r for r in picked if r["paper_id"] in gold_ids]

    out_dir = data_root / "processed" / "model_claims" / f"{model}_{PROMPT_VERSION}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "claims.jsonl"

    done: set[str] = set()
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            done = {json.loads(l)["paper_id"] for l in f if l.strip()}

    extracted = 0
    with open(out_path, "a", encoding="utf-8") as f:
        for i, row in enumerate(picked, start=1):
            pid = row["paper_id"]
            if pid in done:
                continue
            meta = papers[pid]
            claims = extract_one(model, meta["title"] or "", meta["abstract"] or "")
            for c in claims:
                record = {
                    "claim_id": deterministic_claim_id(pid, c["claim_text"]),
                    "paper_id": pid,
                    "claim_text": c.get("claim_text", ""),
                    "supporting_evidence": c.get("supporting_evidence", ""),
                    "assumptions": _as_list(c.get("assumptions")),
                    "uncertainty": c.get("uncertainty", "") or "",
                    "objects": _as_list(c.get("objects")),
                    "datasets": _as_list(c.get("datasets")),
                    "location": {"section": "Abstract", "page": -1, "paragraph": 0,
                                 "start_offset": -1, "end_offset": -1},
                    "extraction_method": f"model:{model}/{PROMPT_VERSION} (abstract-only)",
                    "human_verified": False,
                    "extracted_at": utc_now_iso(),
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                extracted += 1
            f.flush()
            print(f"[extract] {i}/{len(picked)} {pid}: {len(claims)} claims")
            time.sleep(REQUEST_DELAY_S)

    write_gold_comparison(out_path, out_dir, data_root)
    print(f"[extract] wrote {extracted} new claims -> {out_path}")
    return out_path


def write_gold_comparison(model_claims_path: Path, out_dir: Path, data_root: Path) -> None:
    """Side-by-side of gold vs model claims on overlap papers, for review."""
    gold_by_paper: dict[str, list] = {}
    for batch in sorted((data_root / "annotations").glob("*/claims.jsonl")):
        for claim in load_claims_jsonl(batch):
            gold_by_paper.setdefault(claim.paper_id, []).append(claim)

    model_by_paper: dict[str, list[dict]] = {}
    with open(model_claims_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                model_by_paper.setdefault(rec["paper_id"], []).append(rec)

    overlap = sorted(set(gold_by_paper) & set(model_by_paper))
    lines = [
        "# Gold vs Model Claim Comparison",
        "",
        f"Overlap papers: {len(overlap)}. For each paper, compare whether the",
        "model recovered the human claims (coverage) and asserted anything the",
        "human did not (precision). Judgments are manual; record them in the",
        "annotation batch NOTES.md.",
        "",
    ]
    for pid in overlap:
        lines += [f"## {pid}", "", "**Gold (human):**"]
        lines += [f"- {c.claim_text}" for c in gold_by_paper[pid]]
        lines += ["", f"**Model:**"]
        lines += [f"- {r['claim_text']}" for r in model_by_paper[pid]]
        lines += [""]
    (out_dir / "gold_comparison.md").write_text("\n".join(lines), encoding="utf-8")
    counts = [
        (len(gold_by_paper[p]), len(model_by_paper[p])) for p in overlap
    ]
    if counts:
        g = sum(c[0] for c in counts)
        m = sum(c[1] for c in counts)
        print(f"[extract] overlap eval: {len(overlap)} papers, "
              f"{g} gold vs {m} model claims -> {out_dir / 'gold_comparison.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=100)
    parser.add_argument("--model", default="gpt-4.1")
    parser.add_argument(
        "--only-overlap", action="store_true",
        help="extract only papers that have gold annotations (prompt eval)",
    )
    args = parser.parse_args()
    run(args.size, args.model, args.only_overlap)
