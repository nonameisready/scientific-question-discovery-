# Scientific Question Discovery

> Research on automated scientific question discovery toward AGI — exploring how intelligent agents can ask good questions like scientists do.

## Overview

This repository is the research workspace for the paper *Scientific Question Discovery*. We argue that one of the key capabilities on the path to AGI is not answering questions, but **discovering scientific questions worth investigating**. This project is organized around that core idea:

- Propose a formal framework for scientific question discovery (`framework/`)
- Design reproducible experiments (`experiments/`)
- Build an evaluation benchmark (`benchmark/`) and datasets (`datasets/`)
- Write and iterate on the paper (`paper/`)

## Repository Structure

```
scientific-question-discovery/
├── README.md          # Project overview (this file)
├── paper/             # Paper manuscript, LaTeX sources, references
├── framework/         # Core framework: formal definitions and method implementations
├── experiments/       # Experiment code, configs, and results
├── benchmark/         # Evaluation benchmark: task definitions, rubrics, baselines
├── datasets/          # Datasets, construction scripts, and documentation
├── figures/           # Figures for the paper and experiments
└── LICENSE            # Open-source license (MIT)
```

## Roadmap

- [ ] Define the research question and survey related work (`paper/outline.md`)
- [ ] Formalize the scientific question discovery framework
- [ ] Build the datasets and evaluation benchmark
- [ ] Run core experiments and ablation studies
- [ ] Write the first draft of the paper and iterate

## Getting Started

```bash
git clone <repo-url>
cd scientific-question-discovery
```

Each subdirectory contains its own README describing its purpose and conventions.

## Citation

A BibTeX entry will be provided here once the paper is complete.

## License

This project is licensed under the [MIT License](LICENSE).
