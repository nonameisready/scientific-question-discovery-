"""Node and edge vocabulary for the Evidence Graph."""

from __future__ import annotations

import pyarrow as pa

NODE_TYPES = (
    "claim",
    "observation",
    "assumption",
    "method",
    "object",
    "dataset",
    "hypothesis",
    "uncertainty",
)

EDGE_TYPES = (
    "supports",
    "contradicts",
    "measures",
    "depends_on",
    "uses_dataset",
    "assumes",
    "refines",
    "fails_to_explain",
)

EVIDENCE_NODES = pa.schema(
    [
        ("node_id", pa.string()),
        ("node_type", pa.string()),       # one of NODE_TYPES
        ("label", pa.string()),           # short human-readable label
        ("paper_id", pa.string()),        # provenance (empty for objects/datasets)
        ("payload", pa.string()),         # JSON blob with type-specific fields
    ]
)

EVIDENCE_EDGES = pa.schema(
    [
        ("edge_id", pa.string()),
        ("from_node", pa.string()),
        ("to_node", pa.string()),
        ("edge_type", pa.string()),       # one of EDGE_TYPES
        ("confidence", pa.float64()),
        ("basis", pa.string()),           # rule id / model name / human note
        ("created_by", pa.string()),
    ]
)


def validate_node_type(node_type: str) -> str:
    if node_type not in NODE_TYPES:
        raise ValueError(f"unknown node type {node_type!r}; expected one of {NODE_TYPES}")
    return node_type


def validate_edge_type(edge_type: str) -> str:
    if edge_type not in EDGE_TYPES:
        raise ValueError(f"unknown edge type {edge_type!r}; expected one of {EDGE_TYPES}")
    return edge_type
