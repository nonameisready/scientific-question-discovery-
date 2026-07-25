# datasets/ — Datasets

Datasets, construction scripts, and documentation.

## Planned Contents

- Scientific literature corpora (input background for question discovery)
- Annotated sets of known "good questions" (for evaluation and rubric calibration)
- Data construction and cleaning scripts

## Conventions

- No large files committed directly: provide download scripts or links, and use Git LFS when necessary
- Each dataset ships with documentation: source, license, size, field descriptions, construction method
- Watch for data contamination: record data cutoff dates so they can be compared against model training cutoffs
