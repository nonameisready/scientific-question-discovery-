"""Competency queries over the Evidence Graph (DuckDB over Parquet).

These four questions define "minimum viable" for the v1 graph:
  1. Which papers conflict with each other?
  2. Does a conflict originate from data, method, or assumptions?
  3. Which conclusions are supported by only a single dataset?
  4. Which targets show unexplained discrepancies?

Usage:
    python -m src.evidence_graph.queries
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

from src.common import DATA_ROOT


def _connect(data_root: Path) -> duckdb.DuckDBPyConnection:
    graph_dir = data_root / "processed" / "evidence_graph"
    con = duckdb.connect()
    con.execute(
        f"CREATE VIEW nodes AS SELECT * FROM read_parquet('{graph_dir / 'evidence_nodes.parquet'}')"
    )
    con.execute(
        f"CREATE VIEW edges AS SELECT * FROM read_parquet('{graph_dir / 'evidence_edges.parquet'}')"
    )
    return con


def conflicting_papers(con: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
    """Q1: pairs of papers linked by a confirmed `contradicts` edge."""
    return con.sql(
        """
        SELECT DISTINCT a.paper_id AS paper_a, b.paper_id AS paper_b,
               e.basis, e.confidence
        FROM edges e
        JOIN nodes a ON e.from_node = a.node_id
        JOIN nodes b ON e.to_node   = b.node_id
        WHERE e.edge_type = 'contradicts'
          AND a.paper_id <> '' AND b.paper_id <> ''
          AND a.paper_id <> b.paper_id
        ORDER BY paper_a, paper_b
        """
    )


def conflict_origins(con: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
    """Q2: classify each contradiction by what the two claims share.

    Same object + different datasets  -> likely data-driven conflict.
    Same datasets + different methods -> likely method-driven.
    Differing assumption sets         -> likely assumption-driven.
    """
    return con.sql(
        """
        WITH contra AS (
            SELECT e.edge_id, e.from_node AS claim_a, e.to_node AS claim_b
            FROM edges e WHERE e.edge_type = 'contradicts'
        ),
        claim_context AS (
            SELECT e.from_node AS claim_id,
                   n.node_type,
                   n.label
            FROM edges e JOIN nodes n ON e.to_node = n.node_id
            WHERE e.edge_type IN ('uses_dataset', 'assumes', 'depends_on')
               OR (e.edge_type = 'measures' AND n.node_type = 'object')
        )
        SELECT c.edge_id,
               CASE
                 WHEN NOT shared.datasets    THEN 'data'
                 WHEN NOT shared.methods     THEN 'method'
                 WHEN NOT shared.assumptions THEN 'assumption'
                 ELSE 'unresolved'
               END AS likely_origin
        FROM contra c
        CROSS JOIN LATERAL (
            SELECT
              (SELECT list(label) FROM claim_context WHERE claim_id = c.claim_a AND node_type='dataset')
                = (SELECT list(label) FROM claim_context WHERE claim_id = c.claim_b AND node_type='dataset')
                AS datasets,
              (SELECT list(label) FROM claim_context WHERE claim_id = c.claim_a AND node_type='method')
                = (SELECT list(label) FROM claim_context WHERE claim_id = c.claim_b AND node_type='method')
                AS methods,
              (SELECT list(label) FROM claim_context WHERE claim_id = c.claim_a AND node_type='assumption')
                = (SELECT list(label) FROM claim_context WHERE claim_id = c.claim_b AND node_type='assumption')
                AS assumptions
        ) AS shared
        """
    )


def single_dataset_conclusions(con: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
    """Q3: claims whose evidence rests on exactly one dataset."""
    return con.sql(
        """
        SELECT n.node_id, n.label AS claim, n.paper_id,
               min(d.label) AS only_dataset
        FROM nodes n
        JOIN edges e ON e.from_node = n.node_id AND e.edge_type = 'uses_dataset'
        JOIN nodes d ON e.to_node = d.node_id
        WHERE n.node_type = 'claim'
        GROUP BY n.node_id, n.label, n.paper_id
        HAVING count(DISTINCT d.node_id) = 1
        ORDER BY n.paper_id
        """
    )


def unexplained_targets(con: duckdb.DuckDBPyConnection) -> duckdb.DuckDBPyRelation:
    """Q4: objects touched by `fails_to_explain` or contradiction edges."""
    return con.sql(
        """
        SELECT o.label AS object_name,
               count(DISTINCT c.paper_id)  AS papers_involved,
               count(DISTINCT e2.edge_id)  AS problem_edges
        FROM nodes o
        JOIN edges m  ON m.to_node = o.node_id AND m.edge_type = 'measures'
        JOIN nodes c  ON m.from_node = c.node_id
        JOIN edges e2 ON (e2.from_node = c.node_id OR e2.to_node = c.node_id)
                     AND e2.edge_type IN ('contradicts', 'fails_to_explain')
        WHERE o.node_type = 'object'
        GROUP BY o.label
        ORDER BY problem_edges DESC, papers_involved DESC
        """
    )


def run_all(data_root: Path = DATA_ROOT) -> None:
    con = _connect(data_root)
    for name, fn in [
        ("Q1 conflicting papers", conflicting_papers),
        ("Q2 conflict origins", conflict_origins),
        ("Q3 single-dataset conclusions", single_dataset_conclusions),
        ("Q4 unexplained targets", unexplained_targets),
    ]:
        print(f"\n=== {name} ===")
        fn(con).show()


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    run_all()
