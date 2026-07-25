"""Two-stage ranking of curated candidate questions (rank-p2).

Stage A — quality gate (pass / needs_rewrite):
    Structural checks (evidence-grounded, source-traceable; duplicates are
    handled upstream by curation) plus an LLM clarity gate scored against
    six criteria: presupposed conclusions, statistics/physics conflation,
    explicit comparison object, falsifiable outcome, scope, and a
    stateable failure condition. clarity < 7 -> needs_rewrite; clarity is
    a GATE, not a score component (rank-p1 scored it 9.0 uniformly, so as
    a weighted term it only added a constant).

Stage B — value ranking (scientific_priority):
    35%  scientific significance   LLM judge, hard-capped by signal tier:
                                   P1 10 / P2 9 / P3 8.5 / P4 7.5 —
                                   single-dataset robustness checks must
                                   not rank beside confirmed tensions
    25%  evidence tension strength structural: confirmed tension 10,
                                   method challenge 8, independent
                                   qualification 6.5, single-dataset 5
    20%  feasibility               mean of LLM-judged subcomponents
                                   (data_availability blended with the
                                   archival-count signal, data_independence,
                                   analysis_readiness, reanalysis_sufficiency)
    10%  novelty                   down-weighted by design: questions are
                                   deliberately generated from existing
                                   evidence tensions, so surface novelty
                                   is not the point
    10%  expected information gain LLM judge: how much the answer updates
                                   beliefs either way

    execution_priority (= feasibility) is reported SEPARATELY from
    scientific_priority: abundant archives must not outrank a confirmed
    cross-instrument tension, and a question may be scientifically first
    while operationally harder.

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
RANK_VERSION = "rank-p2"

WEIGHTS = {
    "significance": 0.35,
    "tension_strength": 0.25,
    "feasibility": 0.20,
    "novelty": 0.10,
    "information_gain": 0.10,
}
SIGNIFICANCE_CAP = {1: 10.0, 2: 9.0, 3: 8.5, 4: 7.5}
TENSION_STRENGTH = {1: 10.0, 2: 8.0, 3: 6.5, 4: 5.0}
CLARITY_GATE = 7.0

GATE_PROMPT = """\
You are gatekeeping candidate research questions on exoplanet atmospheres
for clarity. Assess the question against six criteria:

  presupposes_conclusion      Does it assume the thing to be proven?
  conflates_stats_physics     Does it mix statistical significance with
                              physical conditions (e.g. "what T-P profile
                              produces a 5-sigma detection")?
  explicit_comparison         Does it name what is compared against what?
  falsifiable_outcome         Is there an outcome that would refute it?
  scope_bounded               Is the scope narrow enough to answer?
  failure_condition_stateable Can you state in one sentence what result
                              would count as "no"?

Return JSON:
Calibration:
- Research questions are normally open-form ("what explains X", "how does
  X affect Y"). falsifiable_outcome means a definable test could return a
  decisive negative result (e.g. "no dependence found", "the discrepancy
  vanishes under a consistent pipeline") — it does NOT require the
  question to be phrased as a yes/no hypothesis.
- A question that asks what explains an observed discrepancy, or names
  competing explanations, has a stateable failure condition.
- Score 8-9 for clean, testable questions; 7 for minor phrasing issues
  that do not obscure the test; 6 and below ONLY for structural flaws:
  presupposing the conclusion, conflating statistics with physics,
  missing comparison object, or unbounded scope.

Return JSON:
  criteria        {name: {"ok": bool, "note": one sentence}} for all six
  clarity_score   0-10 overall per the calibration above
  rewrite_hint    one sentence if clarity_score < 7, else ""
"""

VALUE_PROMPT = """\
You are scoring a candidate research question on exoplanet atmospheres.
Score each 0-10, judging strictly from the given evidence context:

  significance          10 = resolving it would change conclusions of many
                        published papers; 0 = changes nothing.
  novelty               10 = genuinely unposed; 0 = already answered.
  information_gain      10 = any answer (positive or negative) strongly
                        updates beliefs or affects other conclusions;
                        0 = answer changes little either way.
  data_availability     10 = the specific data needed already exists in
                        archives. Judge whether the RIGHT data exists
                        (e.g. simultaneous multi-band spectra if the
                        question needs them), not raw record counts.
  data_independence     10 = testable with datasets independent of those
                        that produced the original claims.
  analysis_readiness    10 = standard tools/pipelines can run the test
                        today; 0 = requires new methodology.
  reanalysis_sufficiency 10 = archival reanalysis alone can answer it;
                        0 = requires substantial new observations.

Return JSON with those seven numeric keys plus:
  justification   {key: one sentence} for each of the seven
"""


def _chat(model: str, system: str, user: str) -> dict:
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
            {"role": "system", "content": system},
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


def _context(question: dict) -> str:
    archival = ", ".join(
        f"{k}={v}" for k, v in question["archival_observations"].items()
    ) or "none"
    parts = [
        f"Question: {question['question_text']}",
        f"Rationale: {question.get('rationale', '')}",
        f"Test sketch: {question.get('test_sketch', '')}",
        f"Signal type: {question['signal_type']} (priority P{question['priority']})",
        f"Evidence papers: {', '.join(question['papers'])}",
        f"Archival spectra counts (raw MAST records, NOT verified as the "
        f"specific data the question needs): {archival}",
    ]
    if question.get("sub_questions"):
        parts.append("Sub-questions: " + " | ".join(question["sub_questions"]))
    return "\n".join(parts)


def stage_a(model: str, question: dict) -> dict:
    """Quality gate: structural traceability + LLM clarity rubric.

    Human-curated questions bypass the LLM gate — human editorial review
    IS the stage-A review; the LLM verdict is recorded as advisory only.
    """
    structural_ok = bool(question.get("claim_ids")) and bool(question.get("papers"))
    gate = _chat(model, GATE_PROMPT, _context(question))
    clarity = float(gate.get("clarity_score", 0.0))
    human_curated = bool(question.get("curation_note"))
    if human_curated:
        status = "pass_human_curated"
    elif structural_ok and clarity >= CLARITY_GATE:
        status = "pass"
    else:
        status = "needs_rewrite"
    return {
        "evidence_grounded": structural_ok,
        "clarity_score": clarity,
        "criteria": gate.get("criteria", {}),
        "rewrite_hint": gate.get("rewrite_hint", ""),
        "status": status,
    }


def corpus_novelty(questions: list[dict], data_root: Path) -> list[float]:
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
    return [round(1.0 - max(cosine(qv, av) for av in a_vecs), 4) for qv in q_vecs]


def archival_score(question: dict) -> float:
    total = sum(question["archival_observations"].values())
    return min(1.0, math.log10(1 + total) / 3.0)


def stage_b(model: str, question: dict, novelty_corpus: float) -> dict:
    judge = _chat(model, VALUE_PROMPT, _context(question))

    def llm(key: str) -> float:
        return float(judge.get(key, 0.0))

    significance = min(llm("significance"), SIGNIFICANCE_CAP[question["priority"]])
    tension = TENSION_STRENGTH[question["priority"]]
    feasibility_parts = {
        "data_availability": 0.5 * llm("data_availability") + 5.0 * archival_score(question),
        "data_independence": llm("data_independence"),
        "analysis_readiness": llm("analysis_readiness"),
        "reanalysis_sufficiency": llm("reanalysis_sufficiency"),
    }
    feasibility = sum(feasibility_parts.values()) / len(feasibility_parts)
    novelty = 0.5 * llm("novelty") + 5.0 * novelty_corpus
    information_gain = llm("information_gain")

    dims = {
        "significance": round(significance, 3),
        "tension_strength": tension,
        "feasibility": round(feasibility, 3),
        "novelty": round(novelty, 3),
        "information_gain": round(information_gain, 3),
    }
    return {
        "scores": dims,
        "scientific_priority": round(sum(WEIGHTS[d] * dims[d] for d in WEIGHTS), 3),
        "execution_priority": round(feasibility, 3),
        "feasibility_parts": {k: round(v, 3) for k, v in feasibility_parts.items()},
        "significance_cap_applied": llm("significance") > SIGNIFICANCE_CAP[question["priority"]],
        "llm_justification": judge.get("justification", {}),
    }


def run(model: str, data_root: Path = DATA_ROOT) -> Path:
    q_dir = data_root / "processed" / "questions"
    source = q_dir / "curated.jsonl"
    if not source.exists():
        source = q_dir / "candidates.jsonl"
    questions = [json.loads(l) for l in open(source, encoding="utf-8") if l.strip()]
    print(f"[rank] input: {source.name} ({len(questions)} questions)")

    novelty_scores = corpus_novelty(questions, data_root)

    ranked, gated_out = [], []
    for i, question in enumerate(questions):
        gate = stage_a(model, question)
        record = {**question, "stage_a": gate, "ranked_by": f"model:{model}/{RANK_VERSION}",
                  "ranked_at": utc_now_iso()}
        if gate["status"] not in ("pass", "pass_human_curated"):
            gated_out.append(record)
            print(f"[rank] {question['question_id']}: GATED "
                  f"(clarity {gate['clarity_score']}) {gate['rewrite_hint'][:70]}")
            continue
        record.update(stage_b(model, question, novelty_scores[i]))
        ranked.append(record)
        print(f"[rank] {question['question_id']}: sci {record['scientific_priority']} "
              f"exec {record['execution_priority']} "
              f"(S {record['scores']['significance']}, T {record['scores']['tension_strength']}, "
              f"F {record['scores']['feasibility']}, N {record['scores']['novelty']}, "
              f"IG {record['scores']['information_gain']})")
        time.sleep(0.4)

    ranked.sort(key=lambda r: -r["scientific_priority"])
    for position, record in enumerate(ranked, start=1):
        record["rank"] = position

    with open(q_dir / "ranked.jsonl", "w", encoding="utf-8") as f:
        for record in ranked + gated_out:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    lines = [
        "# Ranked Scientific Questions (rank-p2, two-stage)",
        "",
        "Stage A: quality gate (evidence grounding + clarity rubric, gate at "
        f"{CLARITY_GATE}). Stage B: scientific_priority = "
        + " + ".join(f"{w}*{d}" for d, w in WEIGHTS.items()) + ".",
        "Significance is hard-capped by signal tier (P1 10 / P2 9 / P3 8.5 / "
        "P4 7.5); execution_priority (feasibility) is reported separately and "
        "does not gate scientific rank.",
        "",
    ]
    for record in ranked:
        s = record["scores"]
        lines += [
            f"## {record['rank']}. [sci {record['scientific_priority']} | "
            f"exec {record['execution_priority']}] {record['question_id']} "
            f"(P{record['priority']} — {record['signal_type']})",
            "",
            f"**{record['question_text']}**",
            "",
        ]
        if record.get("sub_questions"):
            lines += [f"  - sub: {sq}" for sq in record["sub_questions"]] + [""]
        lines += [
            f"- scores: significance {s['significance']}"
            + (" (capped)" if record["significance_cap_applied"] else "")
            + f" | tension {s['tension_strength']} | feasibility {s['feasibility']} "
            f"| novelty {s['novelty']} | info-gain {s['information_gain']}",
            f"- feasibility parts: {record['feasibility_parts']}",
            f"- clarity gate: {record['stage_a']['clarity_score']}",
            f"- objects: {', '.join(record['objects']) or '—'}  |  "
            f"papers: {', '.join(record['papers'])}",
            "",
        ]
    if gated_out:
        lines += ["## Gated out (needs_rewrite)", ""]
        for record in gated_out:
            lines += [
                f"- {record['question_id']} (clarity "
                f"{record['stage_a']['clarity_score']}): {record['question_text']}",
                f"  hint: {record['stage_a']['rewrite_hint']}",
            ]
    (q_dir / "ranked.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[rank] {len(ranked)} ranked, {len(gated_out)} gated -> {q_dir / 'ranked.md'}")
    return q_dir / "ranked.jsonl"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="gpt-4.1")
    args = parser.parse_args()
    run(args.model)
