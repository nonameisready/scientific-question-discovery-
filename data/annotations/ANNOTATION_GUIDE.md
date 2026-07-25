# Claim Annotation Guide

Manual annotation calibrates the claim schema before any model extraction
runs (v1 protocol: ~20 papers by hand, then model extraction over ~100 with
human review). Your annotations become the gold standard that model
extraction is judged against — precision matters more than volume.

## What counts as a claim

A claim is a substantive assertion **the authors themselves make** based on
their own analysis. Extract 2–6 claims per paper: the headline results and
the load-bearing intermediate conclusions.

Do **not** extract:
- Background statements attributed to other papers
- Descriptions of method steps (unless the paper's claim *is* methodological)
- Speculation clearly flagged as such ("future observations may show...")

## Record format

Append one JSON object per line to the batch's `claims.jsonl`:

```json
{"paper_id": "2014Natur.505...69K", "claim_text": "The transmission spectrum of GJ 1214b is featureless, which rules out cloud-free high-mean-molecular-weight atmospheres and requires high-altitude clouds.", "supporting_evidence": "15 HST/WFC3 transit observations combined into a 1.1-1.7 micron transmission spectrum with sub-30 ppm precision.", "assumptions": ["stellar activity does not mimic a flat spectrum", "limb-darkening model is accurate"], "uncertainty": "Cloud-free water-dominated atmosphere ruled out at 16.1 sigma.", "objects": ["GJ 1214 b"], "datasets": ["HST/WFC3 GO-13021"], "location": {"section": "Results", "page": 2, "paragraph": 3, "start_offset": -1, "end_offset": -1}, "extraction_method": "human", "human_verified": true}
```

Field-by-field:

| Field                 | Rule |
|-----------------------|------|
| `paper_id`            | Exactly as listed in `papers.md` / `selection.jsonl`. |
| `claim_text`          | One precise sentence, in your own words if the original is diffuse. |
| `supporting_evidence` | The observation/analysis the authors offer as support. |
| `assumptions`         | List every assumption the claim depends on (e.g. "equilibrium chemistry", "cloud-free limb"). Empty list only if genuinely none. |
| `uncertainty`         | How the paper qualifies it: error bars, significance, stated caveats. |
| `objects`             | Canonical catalog names (`WASP-39 b`, not `WASP39b`). |
| `datasets`            | Instruments/programs the evidence comes from (`HST/WFC3`, `JWST/NIRSpec`, proposal IDs when given). |
| `location.section`    | Section name where the claim is stated (usually Results/Discussion). |
| `location.paragraph`  | Paragraph index within that section, 0-based. |
| `location.page`       | Page in the published PDF; `-1` if unpaginated. |
| `start_offset`/`end_offset` | Character offsets once full text is ingested; `-1` for now. |
| `extraction_method`   | Always `"human"` in calibration batches. |
| `human_verified`      | Always `true` for your own annotations. |

## Working procedure

1. Open the paper via the ADS/arXiv link in `papers.md`.
2. Read abstract + results + discussion; skim the rest.
3. Write claims as you go; when unsure whether something is one claim or
   two, split it — smaller claims link more precisely in the graph.
4. If two of the paper's claims depend on each other, still record them
   separately; dependency edges are added at graph construction.
5. Validate before committing:

   ```bash
   python -m src.extraction.validate_annotations data/annotations/batch_001
   ```

## Calibration notes

Keep a running list of schema pain points (fields that feel ambiguous,
claim types that don't fit) in the batch directory as `NOTES.md` — those
observations drive schema revisions before model extraction begins.
