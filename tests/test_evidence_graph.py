"""Offline tests for claim IDs and R4 contradiction-candidate generation."""

from src.evidence_graph.build import _r4_candidates
from src.extraction.claims import deterministic_claim_id


def test_claim_ids_are_deterministic_and_distinct():
    a = deterministic_claim_id("paperX", "water is detected")
    assert a == deterministic_claim_id("paperX", "water is detected")
    assert a != deterministic_claim_id("paperY", "water is detected")
    assert a.startswith("claim_")


def _claim(cid, paper, text, objects):
    return {
        "claim_id": cid, "paper_id": paper, "claim_text": text,
        "uncertainty": "", "objects": objects,
    }


def test_r4_requires_cross_paper_shared_object_and_topic():
    claims = [
        _claim("c1", "p1", "Strong water absorption detected.", ["WASP-12 b"]),
        _claim("c2", "p2", "Retrievals bias water abundances.", ["WASP-12 b"]),
        _claim("c3", "p2", "Sodium detected in the atmosphere.", ["WASP-12 b"]),
        _claim("c4", "p3", "Water detected here too.", ["GJ 1214 b"]),
        _claim("c5", "p1", "Water abundance is sub-solar.", ["WASP-12 b"]),
    ]
    pairs = {(c["claim_id_a"], c["claim_id_b"]) for c in _r4_candidates(claims)}
    assert ("c1", "c2") in pairs          # cross-paper, same object, both 'water'
    assert ("c1", "c3") not in pairs      # no shared topic term
    assert ("c1", "c4") not in pairs      # no shared object
    assert ("c1", "c5") not in pairs      # same paper
    assert ("c2", "c5") in pairs          # cross-paper water pair
