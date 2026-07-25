"""Shared utilities: provenance envelopes, immutable raw storage, config loading.

Core principles enforced here:
  * Every raw API response is stored verbatim, wrapped in a provenance
    envelope, and never overwritten.
  * All paths are derived from the data root so the layout stays uniform:
        data/raw/<layer>/<source>/<YYYY-MM-DD>/<name>
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

DATA_ROOT = Path(os.environ.get("SQD_DATA_ROOT", "data"))

RAW_LAYERS = ("literature", "catalogs", "observations")


def load_dotenv(path: str | Path = ".env") -> None:
    """Minimal .env loader — sets variables not already in the environment.
    Values may be quoted for shell `source` compatibility."""
    path = Path(path)
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def utc_now_iso() -> str:
    """Current UTC time in ISO-8601 with a Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def raw_dir(layer: str, source: str, date: str | None = None) -> Path:
    """Return (and create) the dated raw directory for a source.

    Example: raw_dir("literature", "ads") -> data/raw/literature/ads/2026-07-26/
    """
    if layer not in RAW_LAYERS:
        raise ValueError(f"layer must be one of {RAW_LAYERS}, got {layer!r}")
    path = DATA_ROOT / "raw" / layer / source / (date or today_utc())
    path.mkdir(parents=True, exist_ok=True)
    return path


def envelope(
    source: str,
    query_version: str,
    source_id: str,
    payload: dict[str, Any],
    retrieved_at: str | None = None,
) -> dict[str, Any]:
    """Wrap a raw API record in the standard provenance envelope.

    The envelope makes every record reconstructible later, even after the
    upstream API content changes.
    """
    return {
        "source": source,
        "retrieved_at": retrieved_at or utc_now_iso(),
        "query_version": query_version,
        "source_id": source_id,
        "payload": payload,
    }


def write_jsonl(path: Path, records: Iterable[dict[str, Any]], append: bool = False) -> int:
    """Write records to a JSONL file. Raw files are immutable: refuses to
    overwrite an existing file unless append=True is passed explicitly.
    Returns the number of records written."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not append:
        raise FileExistsError(
            f"{path} already exists; raw files are immutable. "
            "Use a new dated directory or append=True."
        )
    n = 0
    with open(path, "a" if append else "x", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            n += 1
    return n


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def load_corpus_config(path: str | Path = "configs/corpus_v1.yaml") -> dict[str, Any]:
    """Load a corpus manifest and validate its required keys."""
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    required = ("corpus_id", "cutoff_date", "literature", "catalogs", "observations")
    missing = [key for key in required if key not in config]
    if missing:
        raise KeyError(f"corpus manifest {path} is missing required keys: {missing}")
    return config
