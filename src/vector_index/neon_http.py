"""Neon SQL-over-HTTPS client — fallback when raw TCP 5432 is unreachable.

Sandboxed environments (e.g. Claude Code on the web) route all outbound
traffic through an HTTP/HTTPS proxy, which blocks the native PostgreSQL
wire protocol. Neon exposes a SQL-over-HTTPS endpoint at
https://<endpoint-host>/sql that works through such proxies.

This client covers schema setup and simple queries. For bulk embedding
inserts, prefer the native driver (src/vector_index/db.py) from an
unrestricted machine.

Usage:
    python -m src.vector_index.neon_http            # verify + create schema
    python -m src.vector_index.neon_http "SELECT 1" # run a single statement
"""

from __future__ import annotations

import sys
from typing import Any
from urllib.parse import urlparse

import requests

from src.vector_index.db import CHUNKS_DDL, EMBEDDING_DIM, get_dsn


def _http_endpoint(dsn: str) -> str:
    host = urlparse(dsn).hostname
    if not host or "neon.tech" not in host:
        raise ValueError(
            f"SQL-over-HTTPS is a Neon-specific fallback; host {host!r} "
            "does not look like a Neon endpoint."
        )
    return f"https://{host}/sql"


def execute(query: str, params: list[Any] | None = None) -> dict[str, Any]:
    """Run a single SQL statement over HTTPS; returns the Neon JSON response."""
    dsn = get_dsn()
    response = requests.post(
        _http_endpoint(dsn),
        headers={"Neon-Connection-String": dsn, "Content-Type": "application/json"},
        json={"query": query, "params": params or []},
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def ensure_schema() -> None:
    """Enable pgvector and create the chunks table (idempotent), one
    statement per request — the HTTP endpoint executes single statements."""
    statements = [s.strip() for s in CHUNKS_DDL.split(";") if s.strip()]
    for statement in statements:
        execute(statement)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        result = execute(sys.argv[1])
        print(result.get("rows", result))
    else:
        version = execute("SELECT version()")["rows"][0]["version"]
        print(f"[neon_http] connected: {version}")
        ensure_schema()
        tables = execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = 'chunks' ORDER BY ordinal_position"
        )["rows"]
        print(f"[neon_http] pgvector enabled, chunks table ready (dim={EMBEDDING_DIM})")
        for col in tables:
            print(f"  {col['column_name']}: {col['data_type']}")
