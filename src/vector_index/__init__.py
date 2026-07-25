"""Vector index — semantic search over full-text chunks (v1: PostgreSQL + pgvector).

The vector index stores *embeddings* of chunks, never the only copy of the
text. Chunk text and its source location (paper_id, section, page,
paragraph, offsets, source_url, publication_date) always live in
data/processed/documents/<paper_id>/chunks.parquet, so every retrieval
result can be checked against the original document.

Setup:
    pip install -e ".[vector]"
    cp .env.example .env          # fill in PG_DSN
    python -m src.vector_index.db # verify connection + create schema
"""
