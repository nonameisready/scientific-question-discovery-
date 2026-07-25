# experiments/ — Experiments

Experiment code, configurations, and results.

## Planned Contents

- Main experiments: comparing question discovery capability across methods on the benchmark
- Ablation studies: contribution of each framework component (novelty metrics, value function, etc.)
- Case studies: human evaluation of generated scientific questions

## Conventions

- One subdirectory per experiment, containing `config`, `run` scripts, and `results/`
- Figures produced by experiments are written to the repository-level `figures/` directory
- Reproducibility: fix random seeds, record model versions and hyperparameters
