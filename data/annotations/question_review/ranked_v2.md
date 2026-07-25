# Ranked Scientific Questions (rank-p2, two-stage)

Stage A: quality gate (evidence grounding + clarity rubric, gate at 7.0). Stage B: scientific_priority = 0.35*significance + 0.25*tension_strength + 0.2*feasibility + 0.1*novelty + 0.1*information_gain.
Significance is hard-capped by signal tier (P1 10 / P2 9 / P3 8.5 / P4 7.5); execution_priority (feasibility) is reported separately and does not gate scientific rank.

## 1. [sci 8.782 | exec 7.639] q_001 (P1 — observational_tension)

**What causes the order-of-magnitude discrepancy between the ~8 km/s wind inferred from optical sodium and the ~1.7 km/s wind inferred from near-infrared CO/H2O in HD 189733 b - vertical wind shear between the probed atmospheric layers, temporal variability, or instrumental and analysis systematics?**

- scores: significance 9.0 | tension 10.0 | feasibility 7.639 | novelty 6.037 | info-gain 10.0
- feasibility parts: {'data_availability': 6.558, 'data_independence': 10.0, 'analysis_readiness': 8.0, 'reanalysis_sufficiency': 6.0}
- clarity gate: 9.0
- objects: HD 189733 b  |  papers: 2015A&A...577A..62W, 2016ApJ...817..106B

## 2. [sci 8.133 | exec 9.125] q_002 (P2 — methodological_challenge)

**How does terminator heterogeneity affect the statistical evidence for water and the inferred water abundance and C/O ratio in WASP-12 b?**

  - sub: At what degree of terminator heterogeneity does the water detection significance degrade materially?
  - sub: While the detection remains robust, how large can the biases in the inferred water abundance and C/O ratio become?

- scores: significance 8.0 | tension 8.0 | feasibility 9.125 | novelty 6.079 | info-gain 9.0
- feasibility parts: {'data_availability': 9.5, 'data_independence': 10.0, 'analysis_readiness': 8.0, 'reanalysis_sufficiency': 9.0}
- clarity gate: 7.0
- objects: WASP-12 b, WASP-17 b  |  papers: 2015ApJ...814...66K, 2020ApJ...893L..43M

## 3. [sci 7.623 | exec 9.375] q_004 (P3 — independent_qualification)

**Under what atmospheric conditions does HD 189733 b exhibit subsolar water abundances alongside robust carbon monoxide detection in high-dispersion transmission spectra?**

- scores: significance 8.0 | tension 6.5 | feasibility 9.375 | novelty 5.228 | info-gain 8.0
- feasibility parts: {'data_availability': 9.5, 'data_independence': 10.0, 'analysis_readiness': 9.0, 'reanalysis_sufficiency': 9.0}
- clarity gate: 9.0
- objects: HD 189733 b, HD 209458 b  |  papers: 2016ApJ...817..106B, 2019AJ....157..114B

## 4. [sci 7.102 | exec 9.0] q_008 (P4 — single_dataset_conclusion)

**Is the strongly subsolar terminator water abundance retrieved for HD 209458 b a property of the atmosphere or an artifact of retrieval assumptions, as tested by comparing independent retrieval frameworks on the same and on independent datasets?**

- scores: significance 7.5 (capped) | tension 5.0 | feasibility 9.0 | novelty 5.267 | info-gain 9.0
- feasibility parts: {'data_availability': 9.0, 'data_independence': 9.0, 'analysis_readiness': 9.0, 'reanalysis_sufficiency': 9.0}
- clarity gate: 9.0
- objects: HD 209458 b  |  papers: 2017MNRAS.469.1979M

## 5. [sci 7.062 | exec 9.613] q_009 (P4 — single_dataset_conclusion)

**Under what atmospheric conditions do patchy cloud models with solar composition provide robust fits to HST/WFC3 spectra of hot Neptunes and hot Jupiters, without invoking high mean molecular weight or globally uniform clouds?**

- scores: significance 7.5 (capped) | tension 5.0 | feasibility 9.613 | novelty 4.642 | info-gain 8.0
- feasibility parts: {'data_availability': 9.452, 'data_independence': 9.0, 'analysis_readiness': 10.0, 'reanalysis_sufficiency': 10.0}
- clarity gate: 9.0
- objects: HAT-P-11 b, HD 189733 b  |  papers: 2016ApJ...820...78L

## 6. [sci 6.92 | exec 9.607] q_010 (P4 — single_dataset_conclusion)

**How sensitive is the reported WASP-121 b water detection to cloud opacity, stellar contamination, baseline offsets, retrieval priors, and the selected null model?**

- scores: significance 7.0 | tension 5.0 | feasibility 9.607 | novelty 4.985 | info-gain 8.0
- feasibility parts: {'data_availability': 9.429, 'data_independence': 10.0, 'analysis_readiness': 9.0, 'reanalysis_sufficiency': 10.0}
- clarity gate: 6.0
- objects: WASP-121 b  |  papers: 2016ApJ...822L...4E

## 7. [sci 6.881 | exec 9.625] q_005 (P4 — single_dataset_conclusion)

**How does the assumed cloud inhomogeneity affect the retrieved evidence for nitrogen-bearing species (NH3 and/or HCN) in HD 209458 b's HST transmission spectrum, and does the detection remain above 3 sigma under cloud-free, patchy, and fully cloudy retrieval scenarios?**

- scores: significance 7.0 | tension 5.0 | feasibility 9.625 | novelty 4.561 | info-gain 8.0
- feasibility parts: {'data_availability': 9.5, 'data_independence': 10.0, 'analysis_readiness': 9.0, 'reanalysis_sufficiency': 10.0}
- clarity gate: 6.0
- objects: WASP-12 b  |  papers: 2015ApJ...814...66K

## 8. [sci 6.803 | exec 9.25] q_006 (P4 — single_dataset_conclusion)

**Does the >3-sigma exclusion of a carbon-rich (C/O > 1) atmosphere for WASP-12 b survive relaxing the equilibrium-chemistry assumption in retrievals of the same HST/WFC3 transmission spectrum?**

- scores: significance 7.0 | tension 5.0 | feasibility 9.25 | novelty 4.531 | info-gain 8.0
- feasibility parts: {'data_availability': 10.0, 'data_independence': 8.0, 'analysis_readiness': 9.0, 'reanalysis_sufficiency': 10.0}
- clarity gate: 6.0
- objects: WASP-12 b  |  papers: 2015ApJ...814...66K

## 9. [sci 6.728 | exec 8.875] q_007 (P4 — single_dataset_conclusion)

**Do patchy-cloud, solar-composition models remain the preferred explanation of the HST/WFC3 transmission spectra of HD 189733 b and HAT-P-11 b when re-evaluated with retrieval frameworks and datasets independent of the original analysis?**

- scores: significance 7.0 | tension 5.0 | feasibility 8.875 | novelty 4.534 | info-gain 8.0
- feasibility parts: {'data_availability': 9.5, 'data_independence': 8.0, 'analysis_readiness': 9.0, 'reanalysis_sufficiency': 9.0}
- clarity gate: 9.0
- objects: HD 209458 b  |  papers: 2017MNRAS.469.1979M

## 10. [sci 6.37 | exec 6.352] q_011 (P4 — single_dataset_conclusion)

**To what extent have actual JWST observations validated pre-launch predictions that aerosol-free TRAPPIST-1 CO2 atmospheres would be detectable within ten NIRSpec Prism transits?**

- scores: significance 7.5 (capped) | tension 5.0 | feasibility 6.352 | novelty 4.249 | info-gain 8.0
- feasibility parts: {'data_availability': 3.408, 'data_independence': 9.0, 'analysis_readiness': 9.0, 'reanalysis_sufficiency': 4.0}
- clarity gate: 9.0
- objects: TRAPPIST-1 b, TRAPPIST-1 c, TRAPPIST-1 d, TRAPPIST-1 e, TRAPPIST-1 f, TRAPPIST-1 g, TRAPPIST-1 h  |  papers: 2019AJ....158...27L
