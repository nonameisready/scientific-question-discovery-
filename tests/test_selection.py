"""Offline tests for core paper selection and cross-source dedup helpers."""

from src.normalization.build_tables import _strip_arxiv_version
from src.normalization.select_core_papers import match_targets, select


def test_strip_arxiv_version():
    assert _strip_arxiv_version("1401.0022v2") == "1401.0022"
    assert _strip_arxiv_version("1401.0022") == "1401.0022"
    assert _strip_arxiv_version("astro-ph/0601001v1") == "astro-ph/0601001"


def test_target_matching_respects_name_boundaries():
    papers = [
        {"paper_id": "p1", "title": "Water in WASP-12b", "abstract": ""},
        {"paper_id": "p2", "title": "Clouds on WASP-1 b today", "abstract": ""},
    ]
    objects = [
        {"object_name": "WASP-1 b", "host_star": "WASP-1"},
        {"object_name": "WASP-12 b", "host_star": "WASP-12"},
    ]
    hits = match_targets(papers, objects)
    # 'wasp-1' must not fire inside 'wasp-12b'
    assert [name for name, _ in hits["p1"]] == ["WASP-12 b"]
    assert [name for name, _ in hits["p2"]] == ["WASP-1 b"]


def test_selection_is_year_stratified_and_capped():
    papers = [
        {"paper_id": f"p{y}{i}", "title": "t", "abstract": "", "pubdate": f"{y}-01"}
        for y in (2015, 2016) for i in range(10)
    ]
    citations = {p["paper_id"]: 1 for p in papers}
    core = select(papers, citations, keyword_hits={}, target_hits={}, max_documents=6)
    assert len(core) == 6
    years = [p["year"] for p in core]
    assert years.count(2015) == 3 and years.count(2016) == 3
    assert [p["rank"] for p in core] == [1, 2, 3, 4, 5, 6]
