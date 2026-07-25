"""Offline tests for the corpus manifest and shared schemas."""

import pytest

from src.common import load_corpus_config
from src.evidence_graph.schema import (
    EDGE_TYPES,
    NODE_TYPES,
    validate_edge_type,
    validate_node_type,
)
from src.normalization.schemas import ALL_TABLES, CHUNKS


def test_corpus_v1_manifest_loads_with_required_keys():
    config = load_corpus_config("configs/corpus_v1.yaml")
    assert config["corpus_id"] == "exoplanet_atmospheres_v1"
    assert config["cutoff_date"] == "2020-12-31"
    assert config["observations"]["mast"]["metadata_only"] is True
    assert 0 < config["literature"]["max_records"] <= 5000
    assert config["full_text"]["max_documents"] <= 500


def test_all_eight_normalized_tables_are_defined():
    expected = {
        "papers", "authors", "paper_citations", "celestial_objects",
        "observations", "data_products", "claims", "evidence_links",
    }
    assert set(ALL_TABLES) == expected


def test_chunks_keep_source_traceability_fields():
    required = {
        "paper_id", "section", "page", "paragraph",
        "start_offset", "end_offset", "source_url", "publication_date",
    }
    assert required <= set(CHUNKS.names)


def test_graph_vocabulary():
    assert "claim" in NODE_TYPES and "hypothesis" in NODE_TYPES
    assert "contradicts" in EDGE_TYPES and "fails_to_explain" in EDGE_TYPES
    assert validate_node_type("claim") == "claim"
    assert validate_edge_type("supports") == "supports"
    with pytest.raises(ValueError):
        validate_node_type("planet")
    with pytest.raises(ValueError):
        validate_edge_type("disagrees")
