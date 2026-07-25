"""Apply human curation decisions to generated candidate questions.

Curation records live in data/annotations/question_review/curation_*.jsonl
(committed — editorial decisions are source data). Supported actions:

  merge    {"action": "merge", "into": id, "members": [ids],
            "question_text": ..., "sub_questions": [...], "note": ...}
           Members become one question family: canonical text replaces the
           primary's, evidence trails union, other members are removed.
  rewrite  {"action": "rewrite", "id": id, "question_text": ..., "note": ...}
           Replaces the question text, preserving the original for audit.
  reject   {"action": "reject", "id": id, "note": ...}
           Drops the question from the ranked set.

Usage:
    python -m src.question_generation.curate

Output:
    data/processed/questions/curated.jsonl
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.common import DATA_ROOT, read_jsonl


def apply_curation(questions: list[dict], records: list[dict]) -> list[dict]:
    by_id = {q["question_id"]: q for q in questions}
    for rec in records:
        if rec["action"] == "merge":
            primary = by_id[rec["into"]]
            primary["original_question_text"] = primary["question_text"]
            primary["question_text"] = rec["question_text"]
            primary["sub_questions"] = rec.get("sub_questions", [])
            primary["curation_note"] = rec.get("note", "")
            for member_id in rec["members"]:
                if member_id == rec["into"]:
                    continue
                member = by_id.pop(member_id, None)
                if member:
                    primary.setdefault("family_members", []).append(
                        {"question_id": member["question_id"],
                         "question_text": member["question_text"]}
                    )
                    for key in ("claim_ids", "papers", "objects"):
                        primary[key] = sorted(set(primary[key]) | set(member[key]))
                    for k, v in member.get("archival_observations", {}).items():
                        primary["archival_observations"].setdefault(k, v)
        elif rec["action"] == "rewrite":
            question = by_id.get(rec["id"])
            if question:
                question["original_question_text"] = question["question_text"]
                question["question_text"] = rec["question_text"]
                question["curation_note"] = rec.get("note", "")
                if rec.get("curated_by"):
                    question["curated_by"] = rec["curated_by"]
        elif rec["action"] == "reject":
            removed = by_id.pop(rec["id"], None)
            if removed:
                print(f"[curate] rejected {rec['id']}: {rec.get('note', '')[:80]}")
        else:
            raise ValueError(f"unknown curation action {rec['action']!r}")
    return list(by_id.values())


def run(data_root: Path = DATA_ROOT) -> Path:
    questions = read_jsonl(data_root / "processed" / "questions" / "candidates.jsonl")
    curation_dir = data_root / "annotations" / "question_review"
    records: list[dict] = []
    for path in sorted(curation_dir.glob("curation_*.jsonl")):
        records.extend(read_jsonl(path))
        print(f"[curate] loaded {path.name}")

    curated = apply_curation(questions, records)
    out = data_root / "processed" / "questions" / "curated.jsonl"
    with open(out, "w", encoding="utf-8") as f:
        for question in curated:
            f.write(json.dumps(question, ensure_ascii=False) + "\n")
    print(f"[curate] {len(questions)} -> {len(curated)} questions -> {out}")
    return out


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    run()
