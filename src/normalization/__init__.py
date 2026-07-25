"""Normalization — raw immutable files -> relational tables (Parquet + DuckDB).

v1 storage decisions:
  * Parquet for table files, DuckDB for local queries and analysis.
  * No PostgreSQL needed at this stage; DuckDB handles thousands to
    millions of rows without a database server.

Tables (see schemas.py):
    papers, authors, paper_citations, celestial_objects,
    observations, data_products, claims, evidence_links
"""
