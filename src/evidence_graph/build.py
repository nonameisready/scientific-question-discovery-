"""Build the minimal Evidence Graph tables from normalized claims.

Deterministic construction rules for v1 (each edge records which rule
created it via the `basis` field, so every link is auditable):

  R1  claim --uses_dataset--> dataset      (from claims.datasets)
  R2  claim --measures-->     object       (from claims.objects)
  R3  claim --assumes-->      assumption   (from claims.assumptions)
  R4  Two claims from different papers about the same object whose texts
      share a topic term (species/property vocabulary below) become a
      *candidate* contradiction edge (created_by='rule:R4-candidate',
      low confidence). Candidates are also written to
      contradiction_candidates.jsonl for human review; confirmations
      recorded in data/annotations/*/contradictions.jsonl upgrade them
      (created_by='human', confidence 1.0, origin recorded in basis) and
      rejections remove them.

Usage:
    python -m src.evidence_graph.build
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import uuid
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.common import DATA_ROOT, read_jsonl
from src.extraction.claims import claim_polarity
from src.evidence_graph.schema import (
    EVIDENCE_EDGES,
    EVIDENCE_NODES,
    TENSION_RELATIONS,
    validate_edge_type,
    validate_node_type,
)

# Topic vocabulary for R4: two same-object claims must share one of these
# terms to become a contradiction candidate (same object alone is far too
# weak a signal). Word-boundary regexes; extend as the corpus grows.
R4_TOPIC_TERMS = {
    "water": r"\bwater\b|\bh2o\b",
    "sodium": r"\bsodium\b|\bna\b",
    "potassium": r"\bpotassium\b",
    "carbon monoxide": r"\bcarbon monoxide\b|\bco\b",
    "carbon dioxide": r"\bcarbon dioxide\b|\bco2\b",
    "methane": r"\bmethane\b|\bch4\b",
    "c/o ratio": r"\bc/o\b|carbon-to-oxygen",
    "clouds": r"\bcloud\w*\b",
    "haze": r"\bhaze\w*\b",
    "temperature": r"\btemperature\w*\b|\bthermal\b",
    "wind": r"\bwind\w*\b",
    "metallicity": r"\bmetallicit\w+\b",
    "abundance": r"\babundance\w*\b",
    "stellar contamination": r"stellar contamination|center-to-limb|centre-to-limb|rossiter",
}


def _node(node_type: str, label: str, paper_id: str = "", payload: dict | None = None) -> dict:
    return {
        "node_id": f"{validate_node_type(node_type)}_{uuid.uuid4().hex[:12]}",
        "node_type": node_type,
        "label": label,
        "paper_id": paper_id,
        "payload": json.dumps(payload or {}),
    }


def _edge(from_node: str, to_node: str, edge_type: str, basis: str, created_by: str, confidence: float = 1.0) -> dict:
    return {
        "edge_id": f"edge_{uuid.uuid4().hex[:12]}",
        "from_node": from_node,
        "to_node": to_node,
        "edge_type": validate_edge_type(edge_type),
        "confidence": confidence,
        "basis": basis,
        "created_by": created_by,
    }


def _r4_candidates(claims: list[dict]) -> list[dict]:
    """Cross-paper same-object claim pairs sharing a topic term."""
    compiled = {term: re.compile(rx) for term, rx in R4_TOPIC_TERMS.items()}
    candidates = []
    for a, b in itertools.combinations(claims, 2):
        if a["paper_id"] == b["paper_id"]:
            continue
        shared_objects = set(a.get("objects") or []) & set(b.get("objects") or [])
        if not shared_objects:
            continue
        text_a = f'{a["claim_text"]} {a["uncertainty"]}'.lower()
        text_b = f'{b["claim_text"]} {b["uncertainty"]}'.lower()
        shared_terms = [
            term for term, rx in compiled.items()
            if rx.search(text_a) and rx.search(text_b)
        ]
        if shared_terms:
            candidates.append(
                {
                    "claim_id_a": a["claim_id"],
                    "claim_id_b": b["claim_id"],
                    "paper_a": a["paper_id"],
                    "paper_b": b["paper_id"],
                    "objects": sorted(shared_objects),
                    "topics": shared_terms,
                    "claim_text_a": a["claim_text"],
                    "claim_text_b": b["claim_text"],
                }
            )
    return candidates


TRUSTED_STATUSES = ("human_gold", "model_matched_gold")


def score_candidate(cand: dict, claim_a: dict, claim_b: dict) -> tuple[float, dict]:
    """Rank a tension candidate before it may enter question generation.

    Criteria (per the batch 001 review protocol): shared measurable
    (topic count), opposite conclusion polarity, dataset independence,
    and gold support on at least one end; claim confidence breaks ties.
    Shared object is already required by R4 itself.
    """
    parts = {
        "shared_topics": len(cand["topics"]),
        "opposite_polarity": claim_polarity(claim_a["claim_text"])
        != claim_polarity(claim_b["claim_text"]),
        "independent_datasets": bool(
            (claim_a.get("datasets") and claim_b.get("datasets"))
            and not (set(claim_a["datasets"]) & set(claim_b["datasets"]))
        ),
        "gold_supported": (
            claim_a.get("verification_status") in TRUSTED_STATUSES
            or claim_b.get("verification_status") in TRUSTED_STATUSES
        ),
    }
    score = (
        parts["shared_topics"]
        + 2.0 * parts["opposite_polarity"]
        + 1.0 * parts["independent_datasets"]
        + 2.0 * parts["gold_supported"]
        + min(claim_a.get("confidence", 1.0), claim_b.get("confidence", 1.0))
    )
    return round(score, 3), parts


def write_top_tensions(
    candidates: list[dict], claims_by_id: dict[str, dict], out_dir: Path, top_k: int = 20
) -> Path:
    """Ranked worksheet of the strongest tension candidates for human
    spot-checking — question generation must not consume unranked,
    unreviewed candidates wholesale."""
    scored = []
    for cand in candidates:
        a = claims_by_id[cand["claim_id_a"]]
        b = claims_by_id[cand["claim_id_b"]]
        score, parts = score_candidate(cand, a, b)
        scored.append((score, parts, cand, a, b))
    scored.sort(key=lambda t: -t[0])

    lines = [
        "# Top Tension Candidates",
        "",
        f"Top {min(top_k, len(scored))} of {len(scored)} R4 candidates, ranked by:",
        "shared topics + opposite polarity (2x) + independent datasets (1x) +",
        "gold support on either end (2x) + min claim confidence (tiebreak).",
        "Spot-check before question generation; record verdicts as `relation`",
        "entries in data/annotations/<batch>/contradictions.jsonl.",
        "",
    ]
    for rank, (score, parts, cand, a, b) in enumerate(scored[:top_k], start=1):
        status = cand.get("status", "pending")
        lines += [
            f"## {rank}. score {score}  [{status}]",
            "",
            f"- objects: {', '.join(cand['objects'])}  |  topics: {', '.join(cand['topics'])}",
            f"- signals: opposite_polarity={parts['opposite_polarity']}, "
            f"independent_datasets={parts['independent_datasets']}, "
            f"gold_supported={parts['gold_supported']}",
            f"- A `{cand['claim_id_a']}` ({a.get('verification_status')}, "
            f"{cand['paper_a']}): {a['claim_text']}",
            f"- B `{cand['claim_id_b']}` ({b.get('verification_status')}, "
            f"{cand['paper_b']}): {b['claim_text']}",
            "",
        ]
    path = out_dir / "top_tensions.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _load_reviews(data_root: Path) -> dict[frozenset, dict]:
    """Human verdicts on candidate pairs, keyed by the claim-ID pair.

    Review record format (data/annotations/<batch>/contradictions.jsonl):
      {"claim_id_a": ..., "claim_id_b": ...,
       "relation": one of schema.TENSION_RELATIONS,   # preferred
       "verdict": "confirmed"|"rejected",             # legacy form
       "origin": "data"|"method"|"assumption", "note": "..."}

    `relation` types the tension precisely (a qualifies/challenges_method
    edge is kept in the graph instead of being dropped as a non-
    contradiction). Legacy verdicts map: confirmed -> contradicts,
    rejected -> no edge.
    """
    reviews: dict[frozenset, dict] = {}
    for path in sorted((data_root / "annotations").glob("*/contradictions.jsonl")):
        for rec in read_jsonl(path):
            relation = rec.get("relation")
            if relation is not None and relation not in TENSION_RELATIONS:
                raise ValueError(
                    f"{path}: relation {relation!r} not in {TENSION_RELATIONS}"
                )
            reviews[frozenset((rec["claim_id_a"], rec["claim_id_b"]))] = rec
    return reviews


def build_graph(data_root: Path = DATA_ROOT) -> tuple[int, int]:
    """Build evidence_nodes/evidence_edges from data/normalized/claims.parquet.

    Applies R1-R3 automatically, generates R4 contradiction candidates,
    and merges human verdicts from annotation review files.
    Returns (node_count, edge_count).
    """
    claims_path = data_root / "normalized" / "claims.parquet"
    out_dir = data_root / "processed" / "evidence_graph"
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes: list[dict] = []
    edges: list[dict] = []
    # Shared entity nodes are deduplicated by (type, label).
    entity_index: dict[tuple[str, str], str] = {}
    claim_nodes: dict[str, str] = {}  # claim_id -> node_id

    def entity(node_type: str, label: str) -> str:
        key = (node_type, label)
        if key not in entity_index:
            node = _node(node_type, label)
            nodes.append(node)
            entity_index[key] = node["node_id"]
        return entity_index[key]

    claims: list[dict] = []
    if claims_path.exists():
        claims = pq.read_table(claims_path).to_pylist()
        for claim in claims:
            claim_node = _node(
                "claim", claim["claim_text"][:120], paper_id=claim["paper_id"],
                payload={
                    "claim_id": claim["claim_id"],
                    "verification_status": claim.get("verification_status"),
                    "confidence": claim.get("confidence"),
                },
            )
            nodes.append(claim_node)
            claim_nodes[claim["claim_id"]] = claim_node["node_id"]
            for dataset in claim.get("datasets") or []:
                edges.append(_edge(claim_node["node_id"], entity("dataset", dataset),
                                   "uses_dataset", "rule:R1", "rule:R1"))
            for obj in claim.get("objects") or []:
                edges.append(_edge(claim_node["node_id"], entity("object", obj),
                                   "measures", "rule:R2", "rule:R2"))
            for assumption in claim.get("assumptions") or []:
                edges.append(_edge(claim_node["node_id"], entity("assumption", assumption),
                                   "assumes", "rule:R3", "rule:R3"))

    # R4: contradiction candidates + human verdicts
    candidates = _r4_candidates(claims)
    reviews = _load_reviews(data_root)
    kept = 0
    with open(out_dir / "contradiction_candidates.jsonl", "w", encoding="utf-8") as f:
        for cand in candidates:
            key = frozenset((cand["claim_id_a"], cand["claim_id_b"]))
            review = reviews.get(key)
            relation = None
            if review:
                relation = review.get("relation") or (
                    "contradicts" if review.get("verdict") == "confirmed" else None
                )
            cand["status"] = relation or (review and review.get("verdict")) or "pending"
            f.write(json.dumps(cand, ensure_ascii=False) + "\n")
            if review and relation is None:
                continue  # rejected: no tension edge at all
            if review:
                basis = (
                    f"origin={review.get('origin', 'unresolved')}; "
                    f"{review.get('note', '')}".strip()
                )
                edges.append(_edge(claim_nodes[cand["claim_id_a"]],
                                   claim_nodes[cand["claim_id_b"]],
                                   relation, basis, "human", confidence=1.0))
            else:
                basis = (
                    f"candidate: shared object {cand['objects']} "
                    f"+ topics {cand['topics']} — needs human review"
                )
                edges.append(_edge(claim_nodes[cand["claim_id_a"]],
                                   claim_nodes[cand["claim_id_b"]],
                                   "contradicts", basis, "rule:R4-candidate",
                                   confidence=0.3))
            kept += 1
    reviewed = sum(
        1 for r in reviews.values()
        if r.get("relation") or r.get("verdict") == "confirmed"
    )
    print(f"[graph] R4: {len(candidates)} candidate pairs, {kept} edges "
          f"({reviewed} human-typed)")
    if candidates:
        claims_by_id = {c["claim_id"]: c for c in claims}
        top_path = write_top_tensions(candidates, claims_by_id, out_dir)
        print(f"[graph] top tensions -> {top_path}")

    node_table = (
        pa.Table.from_pylist(nodes, schema=EVIDENCE_NODES) if nodes
        else EVIDENCE_NODES.empty_table()
    )
    edge_table = (
        pa.Table.from_pylist(edges, schema=EVIDENCE_EDGES) if edges
        else EVIDENCE_EDGES.empty_table()
    )
    pq.write_table(node_table, out_dir / "evidence_nodes.parquet")
    pq.write_table(edge_table, out_dir / "evidence_edges.parquet")
    print(f"[graph] {node_table.num_rows} nodes, {edge_table.num_rows} edges -> {out_dir}")
    return node_table.num_rows, edge_table.num_rows


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    build_graph()
