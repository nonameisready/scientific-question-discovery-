"""Evidence Graph — plain tables first, graph database later (if ever).

v1 represents the graph as two Parquet tables (evidence_nodes,
evidence_edges) queried with DuckDB. Migrating to Neo4j is deferred until
complex graph queries are genuinely needed; a graph database on day one adds
engineering burden without improving the paper.

The minimum viable graph must be able to answer:
  1. Which papers conflict with each other?
  2. Does a conflict originate from data, method, or assumptions?
  3. Which conclusions are supported by only a single dataset?
  4. Which targets show unexplained discrepancies?
"""
