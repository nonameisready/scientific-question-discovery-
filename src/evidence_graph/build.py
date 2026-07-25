"""Build the minimal Evidence Graph tables from normalized claims.

Deterministic construction rules for v1 (each edge records which rule
created it via the `basis` field, so every link is auditable):

  R1  claim --uses_dataset--> dataset      (from claims.datasets)
  R2  claim --measures-->     object       (from claims.objects)
  R3  claim --assumes-->      assumption   (from claims.assumptions)
  R4  Two claims about the same object whose texts are flagged as opposing
      by a reviewer or model become a *candidate* contradiction edge with
      created_by='rule:R4-candidate'. Candidates require human confirmation
      before they count as contradictions in downstream queries.

Usage:
    python -m src.evidence_graph.build
"""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.common import DATA_ROOT
from src.evidence_graph.schema import (
    EVIDENCE_EDGES,
    EVIDENCE_NODES,
    validate_edge_type,
    validate_node_type,
)


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


def build_graph(data_root: Path = DATA_ROOT) -> tuple[int, int]:
    """Build evidence_nodes/evidence_edges from data/normalized/claims.parquet.

    Applies rules R1-R3 automatically. R4 candidates come from a separate
    review file and are merged in a later pass.
    Returns (node_count, edge_count).
    """
    claims_path = data_root / "normalized" / "claims.parquet"
    out_dir = data_root / "processed" / "evidence_graph"
    out_dir.mkdir(parents=True, exist_ok=True)

    nodes: list[dict] = []
    edges: list[dict] = []
    # Shared entity nodes are deduplicated by (type, label).
    entity_index: dict[tuple[str, str], str] = {}

    def entity(node_type: str, label: str) -> str:
        key = (node_type, label)
        if key not in entity_index:
            node = _node(node_type, label)
            nodes.append(node)
            entity_index[key] = node["node_id"]
        return entity_index[key]

    if claims_path.exists():
        for claim in pq.read_table(claims_path).to_pylist():
            claim_node = _node(
                "claim", claim["claim_text"][:120], paper_id=claim["paper_id"],
                payload={"claim_id": claim["claim_id"]},
            )
            nodes.append(claim_node)
            for dataset in claim.get("datasets") or []:
                edges.append(_edge(claim_node["node_id"], entity("dataset", dataset),
                                   "uses_dataset", "rule:R1", "rule:R1"))
            for obj in claim.get("objects") or []:
                edges.append(_edge(claim_node["node_id"], entity("object", obj),
                                   "measures", "rule:R2", "rule:R2"))
            for assumption in claim.get("assumptions") or []:
                edges.append(_edge(claim_node["node_id"], entity("assumption", assumption),
                                   "assumes", "rule:R3", "rule:R3"))

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
