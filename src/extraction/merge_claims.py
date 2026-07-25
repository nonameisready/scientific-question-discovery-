"""Merge gold and model claims into the canonical claims table with
semantic deduplication and provenance tiers.

Duplicate rule (all four conditions required):
    same paper + shared object (or both object-less)
    + embedding cosine similarity >= threshold
    + same conclusion polarity (both assert, or both negate)

A duplicate does NOT become a second claim node. The canonical claim
keeps the human's text and carries both provenances:

    canonical claim
    ├── human annotation provenance
    └── model extraction provenance

Provenance tiers and default confidences:
    human_gold          1.00   human annotation, no model duplicate
    model_matched_gold  1.00   human + model agree (human_verified=true;
                               the 0.95 table default applies if a
                               standalone model record is ever kept)
    model_only          0.75   model extraction, unreviewed

Requires OPENAI_API_KEY (embeddings: text-embedding-3-small).

Usage:
    python -m src.extraction.merge_claims --model-run gpt-4.1_p3 --threshold 0.62

Output:
    data/normalized/claims.parquet
    data/processed/model_claims/<run>/merge_report.jsonl
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import requests

from src.common import DATA_ROOT, load_dotenv
from src.extraction.claims import claim_polarity, load_claims_jsonl
from src.normalization.schemas import CLAIMS

EMBEDDINGS_URL = "https://api.openai.com/v1/embeddings"
EMBEDDING_MODEL = "text-embedding-3-small"

CONFIDENCE = {"human_gold": 1.0, "model_matched_gold": 1.0, "model_only": 0.75}


def embed(texts: list[str]) -> list[list[float]]:
    load_dotenv()
    headers = {
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
    }
    vectors: list[list[float]] = []
    for start in range(0, len(texts), 100):
        batch = texts[start:start + 100]
        response = requests.post(
            EMBEDDINGS_URL, headers=headers,
            json={"model": EMBEDDING_MODEL, "input": batch}, timeout=120,
        )
        response.raise_for_status()
        vectors.extend(item["embedding"] for item in response.json()["data"])
    return vectors


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def objects_compatible(gold_objects: list[str], model_objects: list[str]) -> bool:
    if not gold_objects and not model_objects:
        return True
    return bool(set(gold_objects) & set(model_objects))


def run(model_run: str, threshold: float, data_root: Path = DATA_ROOT) -> dict:
    gold = []
    for batch in sorted((data_root / "annotations").glob("*/claims.jsonl")):
        gold.extend(c.to_row() for c in load_claims_jsonl(batch))
    for row in gold:
        row["verification_status"] = "human_gold"
        row["confidence"] = CONFIDENCE["human_gold"]
        row["provenance"] = [f"human:{row['claim_id']}"]

    model_path = data_root / "processed" / "model_claims" / model_run / "claims.jsonl"
    model_rows = []
    with open(model_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                loc = rec.pop("location")
                rec.pop("extracted_at", None)
                rec.update(loc)
                rec["verification_status"] = "model_only"
                rec["confidence"] = CONFIDENCE["model_only"]
                rec["provenance"] = [f"model:{model_run}:{rec['claim_id']}"]
                model_rows.append(rec)

    texts = [r["claim_text"] for r in gold] + [r["claim_text"] for r in model_rows]
    vectors = embed(texts)
    gold_vecs, model_vecs = vectors[: len(gold)], vectors[len(gold):]

    gold_by_paper: dict[str, list[int]] = {}
    for i, row in enumerate(gold):
        gold_by_paper.setdefault(row["paper_id"], []).append(i)

    merged_report = []
    kept_model: list[dict] = []
    for j, model_row in enumerate(model_rows):
        best_i, best_sim = None, 0.0
        for i in gold_by_paper.get(model_row["paper_id"], []):
            if not objects_compatible(gold[i]["objects"], model_row["objects"]):
                continue
            if claim_polarity(gold[i]["claim_text"]) != claim_polarity(model_row["claim_text"]):
                continue
            sim = cosine(gold_vecs[i], model_vecs[j])
            if sim > best_sim:
                best_i, best_sim = i, sim
        if best_i is not None and best_sim >= threshold:
            gold[best_i]["verification_status"] = "model_matched_gold"
            gold[best_i]["confidence"] = CONFIDENCE["model_matched_gold"]
            gold[best_i]["provenance"].append(f"model:{model_run}:{model_row['claim_id']}")
            merged_report.append(
                {
                    "gold_claim_id": gold[best_i]["claim_id"],
                    "model_claim_id": model_row["claim_id"],
                    "similarity": round(best_sim, 4),
                    "gold_text": gold[best_i]["claim_text"],
                    "model_text": model_row["claim_text"],
                }
            )
        else:
            kept_model.append(model_row)

    all_rows = gold + kept_model
    table = pa.Table.from_pylist(all_rows, schema=CLAIMS)
    out = data_root / "normalized" / "claims.parquet"
    pq.write_table(table, out)

    report_path = model_path.parent / "merge_report.jsonl"
    with open(report_path, "w", encoding="utf-8") as f:
        for rec in merged_report:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    stats = {
        "gold": len(gold),
        "model_total": len(model_rows),
        "model_matched_gold": len(merged_report),
        "model_only_kept": len(kept_model),
        "canonical_total": len(all_rows),
    }
    for key, value in stats.items():
        print(f"[merge] {key}: {value}")
    print(f"[merge] report -> {report_path}")
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-run", default="gpt-4.1_p3")
    parser.add_argument("--threshold", type=float, default=0.62)
    args = parser.parse_args()
    run(args.model_run, args.threshold)
