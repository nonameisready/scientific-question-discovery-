"""Offline tests for provenance envelopes and immutable raw storage."""

import pytest

from src.common import envelope, read_jsonl, write_jsonl


def test_envelope_has_required_provenance_fields():
    record = envelope(
        source="NASA_ADS",
        query_version="exoplanet_atmospheres_v1",
        source_id="2024ApJ...",
        payload={"title": "example"},
    )
    assert set(record) == {"source", "retrieved_at", "query_version", "source_id", "payload"}
    assert record["retrieved_at"].endswith("Z")
    assert record["payload"] == {"title": "example"}


def test_write_jsonl_refuses_to_overwrite(tmp_path):
    path = tmp_path / "query_001.jsonl"
    records = [envelope("NASA_ADS", "v1", "id1", {})]
    assert write_jsonl(path, records) == 1
    with pytest.raises(FileExistsError):
        write_jsonl(path, records)
    # append is allowed only when explicit
    assert write_jsonl(path, records, append=True) == 1
    assert len(read_jsonl(path)) == 2
