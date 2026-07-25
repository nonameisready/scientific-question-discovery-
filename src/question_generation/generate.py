"""Candidate scientific question generation from Evidence Graph signals.

Signal priority (set by the batch 001 tension review — most high-scoring
R4 pairs turned out to be supports/qualifies/challenges_method rather
than direct contradictions, so unreviewed R4 candidates are EXCLUDED):

    P1  human-confirmed observational tension (contradicts, created_by=human)
    P2  challenges_method edges (human)
    P3  qualifies edges between independent datasets (human)
    P4  single-dataset conclusions from trusted claims
        (verification_status human_gold / model_matched_gold)

Each candidate question carries its full evidence trail (claim IDs,
papers, objects) plus an archival-data availability count from MAST
observation metadata — the first falsification screen: a question whose
targets already have archived JWST/HST spectra is immediately testable.

Question texts are phrased by an LLM from the evidence bundle
(deterministic signal assembly, model phrasing only). Requires
OPENAI_API_KEY.

Usage:
    python -m src.question_generation.generate --model gpt-4.1

Output:
    data/processed/questions/candidates.jsonl
    data/processed/questions/candidates.md
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

import duckdb
import pyarrow.parquet as pq
import requests

from src.common import DATA_ROOT, load_dotenv, utc_now_iso

API_URL = "https://api.openai.com/v1/chat/completions"
QGEN_VERSION = "qgen-p1"
TRUSTED = ("human_gold", "model_matched_gold")

PHRASING_PROMPT = """\
You turn evidence signals from a scientific knowledge graph into precise,
falsifiable research questions about exoplanet atmospheres.

Given the signal below, write ONE research question. Requirements:
- Precise enough that a falsification test could be designed against it.
- Grounded strictly in the given evidence — do not invent measurements.
- Prefer "what mechanism / under what conditions / is X robust to Y" forms
  over yes/no phrasings.

Return JSON with exactly these keys:
  question_text   The research question, one sentence.
  rationale       Two sentences: why the evidence makes this worth asking.
  test_sketch     One sentence: how archival or near-term observations
                  could begin to answer it.
"""


def _chat(model: str, signal_description: str) -> dict:
    load_dotenv()
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model,
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "messages": [
            {"role": "system", "content": PHRASING_PROMPT},
            {"role": "user", "content": signal_description},
        ],
    }
    for attempt in range(4):
        response = requests.post(API_URL, headers=headers, json=body, timeout=120)
        if response.status_code == 429 or response.status_code >= 500:
            time.sleep(2 ** (attempt + 1))
            continue
        response.raise_for_status()
        return json.loads(response.json()["choices"][0]["message"]["content"])
    response.raise_for_status()
    return {}


def _load_graph(data_root: Path):
    graph_dir = data_root / "processed" / "evidence_graph"
    nodes = pq.read_table(graph_dir / "evidence_nodes.parquet").to_pylist()
    edges = pq.read_table(graph_dir / "evidence_edges.parquet").to_pylist()
    claims = {
        c["claim_id"]: c
        for c in pq.read_table(data_root / "normalized" / "claims.parquet").to_pylist()
    }
    node_claim: dict[str, dict] = {}
    for node in nodes:
        if node["node_type"] == "claim":
            payload = json.loads(node["payload"] or "{}")
            claim = claims.get(payload.get("claim_id"))
            if claim:
                node_claim[node["node_id"]] = claim
    return edges, claims, node_claim


def _planet_letter_stripped(name: str) -> str:
    return re.sub(r"\s+[a-h]$", "", name.strip())


def archival_counts(objects: list[str], data_root: Path) -> dict[str, int]:
    """JWST/HST spectral observations on record for these targets (via
    host-star name match against MAST metadata)."""
    obs_path = data_root / "normalized" / "observations.parquet"
    if not obs_path.exists() or not objects:
        return {}
    hosts = sorted({_planet_letter_stripped(o).upper().replace(" ", "") for o in objects})
    con = duckdb.connect()
    counts: dict[str, int] = {}
    for host in hosts:
        row = con.execute(
            f"""
            SELECT mission, count(*) FROM read_parquet('{obs_path}')
            WHERE upper(replace(target_name, ' ', '')) LIKE ? || '%'
            GROUP BY mission
            """,
            [host],
        ).fetchall()
        for mission, n in row:
            counts[f"{host}:{mission}"] = n
    return counts


def edge_signals(edges: list[dict], node_claim: dict[str, dict]) -> list[dict]:
    """P1-P3 signals from human-reviewed tension edges."""
    signals = []
    for edge in edges:
        if edge["created_by"] != "human":
            continue
        claim_a = node_claim.get(edge["from_node"])
        claim_b = node_claim.get(edge["to_node"])
        if not claim_a or not claim_b:
            continue
        if edge["edge_type"] == "contradicts":
            priority, kind = 1, "observational_tension"
        elif edge["edge_type"] == "challenges_method":
            priority, kind = 2, "methodological_challenge"
        elif edge["edge_type"] == "qualifies":
            datasets_a, datasets_b = set(claim_a["datasets"]), set(claim_b["datasets"])
            if not (datasets_a and datasets_b and not datasets_a & datasets_b):
                continue  # P3 requires independent datasets
            priority, kind = 3, "independent_qualification"
        else:
            continue
        signals.append(
            {
                "priority": priority,
                "signal_type": kind,
                "claims": [claim_a, claim_b],
                "basis": edge["basis"],
            }
        )
    return signals


def single_dataset_signals(claims: dict[str, dict]) -> list[dict]:
    """P4: trusted claims resting on exactly one dataset."""
    signals = []
    for claim in claims.values():
        if claim.get("verification_status") not in TRUSTED:
            continue
        if len(set(claim.get("datasets") or [])) == 1 and claim.get("objects"):
            signals.append(
                {
                    "priority": 4,
                    "signal_type": "single_dataset_conclusion",
                    "claims": [claim],
                    "basis": f"only dataset: {claim['datasets'][0]}",
                }
            )
    return signals


def describe(signal: dict) -> str:
    lines = [f"Signal type: {signal['signal_type']}", f"Basis: {signal['basis']}", ""]
    for i, claim in enumerate(signal["claims"]):
        lines += [
            f"Claim {chr(65 + i)} (paper {claim['paper_id']}, "
            f"status {claim.get('verification_status')}):",
            f"  {claim['claim_text']}",
            f"  evidence: {claim['supporting_evidence']}",
            f"  datasets: {claim.get('datasets')}  objects: {claim.get('objects')}",
        ]
    return "\n".join(lines)


def run(model: str, data_root: Path = DATA_ROOT) -> Path:
    edges, claims, node_claim = _load_graph(data_root)
    signals = edge_signals(edges, node_claim) + single_dataset_signals(claims)
    signals.sort(key=lambda s: s["priority"])

    out_dir = data_root / "processed" / "questions"
    out_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for i, signal in enumerate(signals, start=1):
        phrased = _chat(model, describe(signal))
        objects = sorted({o for c in signal["claims"] for o in (c.get("objects") or [])})
        record = {
            "question_id": f"q_{i:03d}",
            "priority": signal["priority"],
            "signal_type": signal["signal_type"],
            "question_text": phrased.get("question_text", ""),
            "rationale": phrased.get("rationale", ""),
            "test_sketch": phrased.get("test_sketch", ""),
            "objects": objects,
            "papers": sorted({c["paper_id"] for c in signal["claims"]}),
            "claim_ids": [c["claim_id"] for c in signal["claims"]],
            "evidence_basis": signal["basis"],
            "archival_observations": archival_counts(objects, data_root),
            "generated_by": f"model:{model}/{QGEN_VERSION}",
            "generated_at": utc_now_iso(),
        }
        records.append(record)
        print(f"[qgen] P{record['priority']} {record['question_id']}: "
              f"{record['question_text'][:90]}")
        time.sleep(0.4)

    jsonl_path = out_dir / "candidates.jsonl"
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    lines = [
        "# Candidate Scientific Questions",
        "",
        f"{len(records)} candidates. Signal priority: P1 confirmed observational",
        "tension, P2 methodological challenge, P3 qualification across",
        "independent datasets, P4 single-dataset conclusion (trusted claims).",
        "Unreviewed R4 pairs are excluded by design.",
        "",
    ]
    for record in records:
        archival = ", ".join(f"{k}={v}" for k, v in record["archival_observations"].items()) or "none found"
        lines += [
            f"## {record['question_id']} (P{record['priority']} — {record['signal_type']})",
            "",
            f"**{record['question_text']}**",
            "",
            f"- rationale: {record['rationale']}",
            f"- test sketch: {record['test_sketch']}",
            f"- objects: {', '.join(record['objects']) or '—'}",
            f"- papers: {', '.join(record['papers'])}",
            f"- archival spectra: {archival}",
            "",
        ]
    (out_dir / "candidates.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[qgen] {len(records)} candidates -> {jsonl_path}")
    return jsonl_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-4.1")
    args = parser.parse_args()
    run(args.model)
