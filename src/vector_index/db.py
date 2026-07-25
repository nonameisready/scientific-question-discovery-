"""PostgreSQL + pgvector connection handling and schema setup.

The connection string is read from the PG_DSN environment variable
(see .env.example). Running this module directly verifies the connection,
enables the pgvector extension, and creates the chunks table:

    python -m src.vector_index.db
"""

from __future__ import annotations

import os
from pathlib import Path

EMBEDDING_DIM = 1024  # adjust to the embedding model chosen for v1

CHUNKS_DDL = f"""
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    chunk_id         TEXT PRIMARY KEY,
    paper_id         TEXT NOT NULL,
    section          TEXT,
    page             INTEGER,
    paragraph        INTEGER,
    start_offset     BIGINT,
    end_offset       BIGINT,
    text             TEXT NOT NULL,
    source_url       TEXT,
    publication_date TEXT,
    embedding        vector({EMBEDDING_DIM})
);

CREATE INDEX IF NOT EXISTS chunks_paper_id_idx ON chunks (paper_id);
"""


def _load_dotenv(path: str | Path = ".env") -> None:
    """Minimal .env loader — sets variables not already in the environment."""
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        # values may be quoted for shell `source` compatibility
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def get_dsn() -> str:
    _load_dotenv()
    dsn = os.environ.get("PG_DSN")
    if not dsn:
        raise EnvironmentError(
            "PG_DSN is not set. Copy .env.example to .env and fill in the "
            "PostgreSQL connection string (postgresql://USER:PASSWORD@HOST:PORT/DB)."
        )
    return dsn


def connect():
    """Return a psycopg connection with pgvector type support registered."""
    try:
        import psycopg
        from pgvector.psycopg import register_vector
    except ImportError as exc:
        raise ImportError(
            'Vector-index dependencies missing. Install with: pip install -e ".[vector]"'
        ) from exc

    conn = psycopg.connect(get_dsn())
    try:
        register_vector(conn)
    except psycopg.ProgrammingError:
        # pgvector extension not enabled yet — ensure_schema() fixes that.
        pass
    return conn


def ensure_schema() -> None:
    """Enable pgvector and create the chunks table (idempotent)."""
    with connect() as conn:
        conn.execute(CHUNKS_DDL)
        conn.commit()


if __name__ == "__main__":
    with connect() as check:
        version = check.execute("SELECT version()").fetchone()[0]
    print(f"[vector_index] connected: {version}")
    ensure_schema()
    print(f"[vector_index] pgvector enabled, chunks table ready (dim={EMBEDDING_DIM})")
