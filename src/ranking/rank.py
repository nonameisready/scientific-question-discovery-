"""Rank candidate questions on the evaluation rubric dimensions.

Each dimension blends a structural (deterministic, corpus-derived) signal
with an LLM-judge score, and every component is reported so rankings are
auditable:

  novelty       LLM judge + corpus check (1 - max embedding similarity of
                the question against core-paper abstracts: a question the
                literature already discusses is not novel)
  feasibility   LLM judge + archival-data score (log-scaled MAST spectra
                counts for the question's targets)
  significance  LLM judge + impact breadth (papers in the corpus mentioning
                the question's objects) + signal-priority bonus
  clarity       LLM judge only (is it precise enough to design a
                falsification test against?)

Requires OPENAI_API_KEY.

Usage:
    python -m src.ranking.rank --model gpt-4.1

Output:
    data/processed/questions/ranked.jsonl
    data/processed/questions/ranked.md
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from pathlib import Path

import pyarrow.parquet as pq
import requests

from src.common import DATA_ROOT, load_dotenv, utc_now_iso
from src.extraction.merge_claims import cosine, embed

API_URL = "https://api.openai.com/v1/chat/completions"
RANK_VERSION = "rank-p1"

# Final-score weights over the four rubric dimensions.
WEIGHTS = {"significance": 0.30, "novelty": 0.25, "feasibility": 0.25, "clarity": 0.20}
# Blend of LLM judge vs structural signal within each dimension.
LLM_BLEND = {"novelty": 0.5, "feasibility": 0.5, "significance": 0.6, "clarity": 1.0}

JUDGE_PROMPT = """\
You are scoring a candidate research question about exoplanet atmospheres
on four dimensions, each 0-10. Anchors:

  novelty       0 = paraphrases a question the literature already poses;
                10 = a genuinely unposed question opened by the evidence.
  feasibility   0 = unanswerable with existing or near-term observations;
                10 = answerable by reanalysis of archival data alone.
  significance  0 = resolving it changes nothing; 10 = resolving it would
                change the conclusions of many published papers.
  clarity       0 = too vague to test; 10 = a falsification test can be
                designed against it directly.

Judge strictly from the provided question and evidence context.
Return JSON with exactly these keys:
  novelty, feasibility, significance, clarity   (numbers 0-10)
  justification   {dimension: one sentence} for all four dimensions
"""


def _judge(model: str, question: dict) -> dict:
    load_dotenv()
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
    }
    archival = ", ".join(f"{k}={v}" for k, v in question["archival_observations"].items()) or "none"
    user = (
        f"Question: {question['question_text']}\n"
        f"Rationale: {question['rationale']}\n"
        f"Test sketch: {question['test_sketch']}\n"
        f"Signal type: {question['signal_type']} (priority P{question['priority']})\n"
        f"Evidence papers: {', '.join(question['papers'])}\n"
        f"Archival spectra available: {archival}"
    )
    body = {
        "model": model,
        "response_format": {"type": "json_object"},
        "temperature": 0,
        "messages": [
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": user},
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


def corpus_novelty(questions: list[dict], data_root: Path) -> list[float]:
    """1 - max cosine similarity of each question against core abstracts."""
    core_ids = {
        r["paper_id"]
        for r in pq.read_table(data_root / "processed" / "core_papers.parquet").to_pylist()
    }
    abstracts = [
        p["abstract"]
        for p in pq.read_table(data_root / "normalized" / "papers.parquet").to_pylist()
        if p["paper_id"] in core_ids and p["abstract"]
    ]
    vectors = embed([q["question_text"] for q in questions] + abstracts)
    q_vecs, a_vecs = vectors[: len(questions)], vectors[len(questions):]
    scores = []
    for qv in q_vecs:
        max_sim = max(cosine(qv, av) for av in a_vecs)
        scores.append(round(1.0 - max_sim, 4))
    return scores


def archival_score(question: dict) -> float:
    """0-1: log-scaled count of archival spectra for the question's targets."""
    total = sum(question["archival_observations"].values())
    return min(1.0, math.log10(1 + total) / 3.0)


def impact_breadth(questions: list[dict], data_root: Path) -> list[float]:
    """0-1 per question: fraction of corpus papers touching its objects
    (capped at 50 papers = 1.0)."""
    links = pq.read_table(data_root / "processed" / "paper_objects.parquet").to_pylist()
    papers_by_object: dict[str, set[str]] = {}
    for link in links:
        papers_by_object.setdefault(link["object_name"], set()).add(link["paper_id"])
    scores = []
    for question in questions:
        papers: set[str] = set()
        for obj in question["objects"]:
            papers |= papers_by_object.get(obj, set())
        scores.append(min(1.0, len(papers) / 50.0))
    return scores


PRIORITY_BONUS = {1: 1.0, 2: 0.8, 3: 0.6, 4: 0.4}


def run(model: str, data_root: Path = DATA_ROOT) -> Path:
    q_path = data_root / "processed" / "questions" / "candidates.jsonl"
    questions = [json.loads(l) for l in open(q_path, encoding="utf-8") if l.strip()]

    novelty_corpus = corpus_novelty(questions, data_root)
    breadth = impact_breadth(questions, data_root)

    ranked = []
    for i, question in enumerate(questions):
        judge = _judge(model, question)
        structural = {
            "novelty": novelty_corpus[i],
            "feasibility": archival_score(question),
            "significance": 0.5 * breadth[i] + 0.5 * PRIORITY_BONUS[question["priority"]],
            "clarity": 0.0,  # no structural signal; LLM only
        }
        dims = {}
        for dim, blend in LLM_BLEND.items():
            llm_score = float(judge.get(dim, 0.0))
            dims[dim] = round(blend * llm_score + (1 - blend) * structural[dim] * 10.0, 3)
        final = round(sum(WEIGHTS[d] * dims[d] for d in WEIGHTS), 3)
        ranked.append(
            {
                **question,
                "scores": dims,
                "structural": structural,
                "llm_justification": judge.get("justification", {}),
                "final_score": final,
                "ranked_by": f"model:{model}/{RANK_VERSION}",
                "ranked_at": utc_now_iso(),
            }
        )
        print(f"[rank] {question['question_id']}: final {final} "
              f"(N {dims['novelty']}, F {dims['feasibility']}, "
              f"S {dims['significance']}, C {dims['clarity']})")
        time.sleep(0.4)

    ranked.sort(key=lambda r: -r["final_score"])
    for position, record in enumerate(ranked, start=1):
        record["rank"] = position

    out_dir = q_path.parent
    with open(out_dir / "ranked.jsonl", "w", encoding="utf-8") as f:
        for record in ranked:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    lines = [
        "# Ranked Scientific Questions",
        "",
        f"{len(ranked)} questions. final = "
        + " + ".join(f"{w}*{d}" for d, w in WEIGHTS.items())
        + "; each dimension blends an LLM judge with structural signals",
        "(corpus-similarity novelty, archival-data feasibility, impact-breadth",
        "+ signal-priority significance). All components shown for audit.",
        "",
    ]
    for record in ranked:
        s = record["scores"]
        lines += [
            f"## {record['rank']}. [{record['final_score']}] {record['question_id']} "
            f"(P{record['priority']} — {record['signal_type']})",
            "",
            f"**{record['question_text']}**",
            "",
            f"- scores: novelty {s['novelty']} | feasibility {s['feasibility']} | "
            f"significance {s['significance']} | clarity {s['clarity']}",
            f"- structural: corpus-novelty {record['structural']['novelty']}, "
            f"archival {round(record['structural']['feasibility'], 3)}, "
            f"impact {round(record['structural']['significance'], 3)}",
            f"- objects: {', '.join(record['objects']) or '—'}  |  "
            f"papers: {', '.join(record['papers'])}",
        ]
        for dim, note in record["llm_justification"].items():
            lines.append(f"- {dim}: {note}")
        lines.append("")
    (out_dir / "ranked.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[rank] -> {out_dir / 'ranked.md'}")
    return out_dir / "ranked.jsonl"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-4.1")
    args = parser.parse_args()
    run(args.model)
