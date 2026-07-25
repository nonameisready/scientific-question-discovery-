# paper/ — Manuscript

- `main.tex` — LaTeX main file (article class, natbib)
- `sections/` — one file per section:
  `introduction`, `related_work`, `framework`, `benchmark` (corpus
  discipline + evaluation protocol), `experiments`, `discussion`,
  `conclusion`
- `references.bib` — generated from the corpus metadata tables so every
  citation traces to an ADS bibcode (see below)
- `outline.md` — original outline and idea notes

## Building

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

or upload the `paper/` directory to Overleaf.

## Conventions

- All experimental numbers in `sections/experiments.tex` come from the
  committed pipeline outputs; when re-running the pipeline changes a
  number, update the section in the same commit.
- `\todo{...}` marks unfinished spots (author list, architecture figure,
  related-work citations).
- Figures are referenced from the repository-level `figures/` directory.

## Regenerating references.bib

Citations are emitted from `data/normalized/papers.parquet` (title,
authors, year, DOI, ADS bibcode) for the bibcodes cited in the text —
never hand-typed from memory. To add a citation: add its bibcode to the
`CITED` list in the snippet stored in the repo history (commit that
introduced `references.bib`) and re-run it, or extend it into a small
script under `src/` if this becomes frequent.
