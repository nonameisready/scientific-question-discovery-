"""Historical validation pipeline: collect post-cutoff literature, then
judge each ranked question against it.

Stages (run separately or via --all):

    collect     ADS 2021-2026 records under the validation manifest;
                raw files are corpus-prefixed so they can never be
                mistaken for Corpus A collections
    normalize   raw validation envelopes -> papers_validation.parquet
                (kept strictly separate from Corpus A's papers.parquet)
    validate    for each question in ranked.jsonl: embed + retrieve the
                top-k most similar validation abstracts, then an LLM
                judge classifies the question's fate with cited bibcodes

Requires ADS_API_TOKEN (collect) and OPENAI_API_KEY (validate).

Usage:
    python -m src.validation.historical --all
    python -m src.validation.historical --stage validate --top-k 8

Output:
    data/normalized/papers_validation.parquet
    data/processed/validation/verdicts.jsonl
    data/processed/validation/report.md
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests
import yaml

from src.collectors.ads import search as ads_search
from src.common import DATA_ROOT, envelope, load_dotenv, raw_dir, utc_now_iso, write_jsonl
from src.extraction.merge_claims import cosine, embed

API_URL = "https://api.openai.com/v1/chat/completions"
VALIDATION_VERSION = "hv-p1"

VERDICTS = ("answered", "partially_addressed", "posed_but_open", "not_addressed")

JUDGE_PROMPT = """\
You judge whether the post-2020 exoplanet literature engaged with a research
question that was generated from pre-2021 evidence only.

You get the question and candidate abstracts (2021-2026), each with an ADS
bibcode. Classify the question's fate:

  answered              the literature resolved it (state the resolution)
  partially_addressed   substantial directly-relevant progress; core question open
  posed_but_open        the literature poses essentially the same question
                        without resolving it
  not_addressed         none of the abstracts engage the question substantively

Rules:
- Cite ONLY bibcodes from the provided candidates; never invent evidence.
- Similar topic is not engagement: the abstract must bear on the question's
  actual test or premise.
- If the question's premise was refuted (not just unaddressed), use
  partially_addressed and say so.

Return JSON:
  verdict          one of the four labels
  evidence         [{bibcode, relevance: one sentence}] max 5, may be empty
  resolution_note  two sentences: what the post-cutoff literature did
  premise_status   "validated" | "refuted" | "untested"
"""


def load_validation_config(path: str | Path = "configs/corpus_validation_v1.yaml") -> dict:
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    for key in ("corpus_id", "validates", "validation_window", "literature"):
        if key not in config:
            raise KeyError(f"validation manifest missing {key}")
    return config


def collect(config: dict) -> None:
    window = config["validation_window"]
    lit = config["literature"]
    per_query = lit["max_records"] // len(lit["ads_queries"])
    out_dir = raw_dir("literature", "ads")
    for i, query in enumerate(lit["ads_queries"], start=1):
        records = (
            envelope("NASA_ADS", config["corpus_id"], doc.get("bibcode", ""), doc)
            for doc in ads_search(query, window["min"], window["max"], per_query)
        )
        path = out_dir / f"{config['corpus_id']}__query_{i:03d}.jsonl"
        n = write_jsonl(path, records)
        print(f"[hv-collect] query {i}: {query!r} -> {n} records")


def normalize(config: dict, data_root: Path = DATA_ROOT) -> int:
    rows, seen = [], set()
    for path in sorted((data_root / "raw" / "literature" / "ads").glob(
        f"**/{config['corpus_id']}__*.jsonl"
    )):
        for line in open(path, encoding="utf-8"):
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec["query_version"] != config["corpus_id"]:
                continue
            doc = rec["payload"]
            bibcode = doc.get("bibcode")
            if not bibcode or bibcode in seen or not doc.get("abstract"):
                continue
            seen.add(bibcode)
            title = doc.get("title")
            rows.append(
                {
                    "paper_id": bibcode,
                    "title": title[0] if isinstance(title, list) else title,
                    "abstract": doc.get("abstract"),
                    "pubdate": doc.get("pubdate"),
                    "query_version": rec["query_version"],
                }
            )
    table = pa.Table.from_pylist(rows)
    out = data_root / "normalized" / "papers_validation.parquet"
    pq.write_table(table, out)
    print(f"[hv-normalize] {len(rows)} validation papers -> {out}")
    return len(rows)


def _embeddings_cached(papers: list[dict], cache: Path) -> list[list[float]]:
    if cache.exists():
        cached = pq.read_table(cache).to_pylist()
        if len(cached) == len(papers) and all(
            c["paper_id"] == p["paper_id"] for c, p in zip(cached, papers)
        ):
            print(f"[hv] using cached embeddings ({len(cached)})")
            return [c["embedding"] for c in cached]
    vectors = embed([f'{p["title"]} {p["abstract"]}'[:6000] for p in papers])
    cache.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        pa.Table.from_pylist(
            [{"paper_id": p["paper_id"], "embedding": v} for p, v in zip(papers, vectors)]
        ),
        cache,
    )
    return vectors


def _judge(model: str, question: dict, candidates: list[dict]) -> dict:
    load_dotenv()
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
    }
    blocks = [
        f"[{c['paper_id']}] ({c['pubdate']}) {c['title']}\n{c['abstract'][:1500]}"
        for c in candidates
    ]
    user = (
        f"Question (generated from pre-2021 evidence): {question['question_text']}\n\n"
        f"Candidate post-cutoff abstracts:\n\n" + "\n\n".join(blocks)
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
        response = requests.post(API_URL, headers=headers, json=body, timeout=180)
        if response.status_code == 429 or response.status_code >= 500:
            time.sleep(2 ** (attempt + 1))
            continue
        response.raise_for_status()
        return json.loads(response.json()["choices"][0]["message"]["content"])
    response.raise_for_status()
    return {}


def validate(model: str, top_k: int, data_root: Path = DATA_ROOT) -> Path:
    papers = pq.read_table(
        data_root / "normalized" / "papers_validation.parquet"
    ).to_pylist()
    questions = [
        json.loads(l)
        for l in open(data_root / "processed" / "questions" / "ranked.jsonl", encoding="utf-8")
        if l.strip()
    ]
    questions = [q for q in questions if "rank" in q]

    out_dir = data_root / "processed" / "validation"
    out_dir.mkdir(parents=True, exist_ok=True)
    paper_vecs = _embeddings_cached(papers, out_dir / "abstract_embeddings.parquet")
    question_vecs = embed([q["question_text"] for q in questions])

    verdicts = []
    for question, q_vec in zip(questions, question_vecs):
        sims = [(cosine(q_vec, pv), p) for pv, p in zip(paper_vecs, papers)]
        sims.sort(key=lambda t: -t[0])
        candidates = [p for _, p in sims[:top_k]]
        judged = _judge(model, question, candidates)
        verdict = judged.get("verdict", "not_addressed")
        if verdict not in VERDICTS:
            verdict = "not_addressed"
        record = {
            "question_id": question["question_id"],
            "rank": question["rank"],
            "question_text": question["question_text"],
            "verdict": verdict,
            "premise_status": judged.get("premise_status", "untested"),
            "evidence": judged.get("evidence", []),
            "resolution_note": judged.get("resolution_note", ""),
            "retrieval_top_similarity": round(sims[0][0], 4),
            "validated_by": f"model:{model}/{VALIDATION_VERSION}",
            "validated_at": utc_now_iso(),
        }
        verdicts.append(record)
        print(f"[hv] {question['question_id']} (rank {question['rank']}): "
              f"{verdict} ({len(record['evidence'])} refs)")
        time.sleep(0.4)

    with open(out_dir / "verdicts.jsonl", "w", encoding="utf-8") as f:
        for record in verdicts:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    counts: dict[str, int] = {}
    for record in verdicts:
        counts[record["verdict"]] = counts.get(record["verdict"], 0) + 1
    lines = [
        "# Historical Validation Report (hv-p1)",
        "",
        "Questions were generated from Corpus A (evidence up to 2020-12-31)",
        "and judged against 2021-2026 literature the pipeline never saw.",
        f"Validation corpus: {len(papers)} post-cutoff papers.",
        "",
        "Verdict counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
        "",
    ]
    for record in verdicts:
        lines += [
            f"## rank {record['rank']} — {record['question_id']}: {record['verdict']}",
            "",
            f"**{record['question_text']}**",
            "",
            f"- premise: {record['premise_status']}  |  "
            f"top retrieval similarity: {record['retrieval_top_similarity']}",
            f"- note: {record['resolution_note']}",
        ]
        for ev in record["evidence"]:
            lines.append(f"- [{ev.get('bibcode')}] {ev.get('relevance')}")
        lines.append("")
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"[hv] report -> {out_dir / 'report.md'}")
    return out_dir / "verdicts.jsonl"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["collect", "normalize", "validate"])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--model", default="gpt-4.1")
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--config", default="configs/corpus_validation_v1.yaml")
    args = parser.parse_args()
    config = load_validation_config(args.config)
    if args.all or args.stage == "collect":
        collect(config)
    if args.all or args.stage == "normalize":
        normalize(config)
    if args.all or args.stage == "validate":
        validate(args.model, args.top_k)
