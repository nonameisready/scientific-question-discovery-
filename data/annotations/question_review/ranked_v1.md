# Ranked Scientific Questions

11 questions. final = 0.3*significance + 0.25*novelty + 0.25*feasibility + 0.2*clarity; each dimension blends an LLM judge with structural signals
(corpus-similarity novelty, archival-data feasibility, impact-breadth
+ signal-priority significance). All components shown for audit.

## 1. [7.929] q_003 (P2 — methodological_challenge)

**Under what atmospheric heterogeneity conditions does the one-dimensional retrieval method for WASP-12 b's transmission spectrum yield water volume mixing ratios that are robust to biases exceeding an order of magnitude?**

- scores: novelty 5.628 | feasibility 9.0 | significance 8.24 | clarity 9.0
- structural: corpus-novelty 0.3256, archival 1.0, impact 0.86
- objects: WASP-12 b, WASP-17 b  |  papers: 2015ApJ...814...66K, 2020ApJ...893L..43M
- novelty: The question seeks to quantitatively define the heterogeneity threshold for robust retrievals, which is not directly addressed in the cited literature and represents a new methodological frontier.
- feasibility: Archival HST/WFC3 spectra for WASP-12 b are available, and the test sketch outlines a clear path using both real and synthetic data with existing retrieval tools.
- significance: Resolving this would directly impact the interpretation of many published water abundance and C/O ratio results for WASP-12 b and similar exoplanets, potentially revising key conclusions.
- clarity: The question is precise, specifying the retrieval method, target, parameter of interest, and the bias threshold, allowing for a direct falsification test via comparative retrievals.

## 2. [7.876] q_002 (P2 — methodological_challenge)

**Under what atmospheric heterogeneity conditions do one-dimensional retrievals of WASP-12 b's transmission spectrum yield robust water detection significance, even if the inferred abundance is biased?**

- scores: novelty 5.637 | feasibility 9.5 | significance 7.64 | clarity 9.0
- structural: corpus-novelty 0.3274, archival 1.0, impact 0.86
- objects: WASP-12 b, WASP-17 b  |  papers: 2015ApJ...814...66K, 2020ApJ...893L..43M
- novelty: The question directly addresses a methodological gap—robustness of detection significance under heterogeneity—that is not explicitly posed in the cited literature.
- feasibility: Archival HST/WFC3 spectra for WASP-12 b are available and can be reanalyzed with existing multi-dimensional retrieval tools.
- significance: Resolving this would impact the interpretation of many published water detections in exoplanet atmospheres, especially those relying on 1D retrievals.
- clarity: The question is precise and testable: it asks under what heterogeneity conditions detection significance remains robust, which can be directly assessed by comparative retrieval analyses.

## 3. [7.808] q_001 (P1 — observational_tension)

**Under what atmospheric conditions does HD 189733 b exhibit strong vertical wind shear between the high-altitude sodium-traced layers (showing ~8 km/s blueshift) and the deeper CO/H2O-traced layers (showing ~1.7 km/s wind), as inferred from simultaneous or contemporaneous multi-wavelength spectroscopy?**

- scores: novelty 5.914 | feasibility 7.558 | significance 8.8 | clarity 9.0
- structural: corpus-novelty 0.3828, archival 0.812, impact 1.0
- objects: HD 189733 b  |  papers: 2015A&A...577A..62W, 2016ApJ...817..106B
- novelty: The question targets the specific atmospheric conditions producing observed vertical wind shear between different tracers, a nuance not directly addressed in the literature.
- feasibility: Simultaneous or contemporaneous multi-wavelength spectra exist or can be obtained, and the analysis is feasible with current techniques and available archival data.
- significance: Resolving this would impact the interpretation of wind measurements and atmospheric dynamics in exoplanet studies, affecting many published analyses.
- clarity: The question is precise, specifying the tracers, wind velocities, and the observational approach, allowing for a direct falsification test.

## 4. [7.739] q_007 (P4 — single_dataset_conclusion)

**Under what cloud inhomogeneity conditions does the detection significance of nitrogen-bearing species (NH3 and/or HCN) in the atmosphere of HD 209458 b, as inferred from HST transmission spectra, remain robust above 3 sigma?**

- scores: novelty 5.136 | feasibility 9.5 | significance 7.6 | clarity 9.0
- structural: corpus-novelty 0.3273, archival 1.0, impact 0.7
- objects: HD 209458 b  |  papers: 2017MNRAS.469.1979M
- novelty: While the sensitivity of molecular detections to cloud assumptions is discussed in the literature, a systematic mapping of detection robustness for NH3/HCN versus cloud inhomogeneity in HD 209458 b is not directly addressed.
- feasibility: The question can be answered by reanalyzing existing HST transmission spectra with varied cloud models, requiring no new observations.
- significance: Resolving this would directly impact the reliability of published nitrogen chemistry detections in HD 209458 b and potentially other exoplanets, affecting interpretations in multiple papers.
- clarity: The question is specific, quantitative (3 sigma threshold), and directly testable by retrieval analysis with falsifiable outcomes.

## 5. [7.611] q_008 (P4 — single_dataset_conclusion)

**Under what atmospheric conditions does HD 209458 b exhibit strongly subsolar water abundance (0.01-0.03 times solar) at the terminator, as inferred from HST transmission spectra with evidence for non-uniform cloud coverage and high-altitude haze?**

- scores: novelty 5.125 | feasibility 9.0 | significance 7.6 | clarity 9.0
- structural: corpus-novelty 0.3251, archival 1.0, impact 0.7
- objects: HD 209458 b  |  papers: 2017MNRAS.469.1979M
- novelty: While subsolar water abundances and cloud/haze effects have been discussed, specifically linking the two and asking under what atmospheric conditions such low water is observed at the terminator is a relatively new angle.
- feasibility: Archival HST spectra exist and comparative retrievals with current models can be performed, making the question answerable with existing data.
- significance: Resolving this would impact the interpretation of many exoplanet spectra and atmospheric retrievals, potentially altering conclusions about atmospheric composition and cloud/haze effects.
- clarity: The question is specific about the planet, spectral features, and atmospheric phenomena, and a direct falsification test (retrievals under varying conditions) can be designed.

## 6. [7.577] q_004 (P3 — independent_qualification)

**Under what atmospheric conditions does HD 189733 b exhibit subsolar water abundances alongside robust carbon monoxide detection in high-dispersion transmission spectra?**

- scores: novelty 5.228 | feasibility 9.0 | significance 7.4 | clarity 9.0
- structural: corpus-novelty 0.3456, archival 1.0, impact 0.8
- objects: HD 189733 b, HD 209458 b  |  papers: 2016ApJ...817..106B, 2019AJ....157..114B
- novelty: The question addresses a specific, underexplored discrepancy in molecular abundance retrievals for HD 189733 b, going beyond standard abundance measurements to probe the conditions yielding this pattern.
- feasibility: The question can be addressed by reanalyzing existing high-resolution spectra with different retrieval models, as described in the test sketch.
- significance: Resolving this would clarify the reliability of molecular abundance inferences from high-dispersion spectra, impacting interpretations in several published studies on exoplanet atmospheres.
- clarity: The question is precise, specifying the molecules, spectral technique, and the nature of the abundance pattern, allowing for a direct falsification test via retrieval analysis.

## 7. [7.298] q_009 (P4 — single_dataset_conclusion)

**Under what atmospheric conditions do patchy cloud models with solar composition provide robust fits to HST/WFC3 spectra of hot Neptunes and hot Jupiters, without invoking high mean molecular weight or globally uniform clouds?**

- scores: novelty 4.642 | feasibility 8.952 | significance 7.0 | clarity 9.0
- structural: corpus-novelty 0.2284, archival 0.99, impact 0.7
- objects: HAT-P-11 b, HD 189733 b  |  papers: 2016ApJ...820...78L
- novelty: While patchy cloud models have been discussed, systematically mapping the atmospheric conditions under which they suffice without high mean molecular weight or uniform clouds is a relatively unposed and specific question.
- feasibility: The question can be addressed with systematic retrievals on existing HST/WFC3 spectra, which are available for several hot Neptunes and hot Jupiters.
- significance: Resolving this would clarify the interpretation of muted spectral features and could shift the consensus away from high mean molecular weight or uniform clouds as default explanations in many published analyses.
- clarity: The question is precise, specifying the models, spectral data, and atmospheric parameters to be tested, allowing for a direct falsification test via retrieval analysis.

## 8. [7.266] q_005 (P4 — single_dataset_conclusion)

**Under what atmospheric temperature and pressure conditions does the water absorption feature observed in the HST/WFC3 transmission spectrum of WASP-12 b remain robust against variations in cloud opacity and composition?**

- scores: novelty 4.636 | feasibility 9.5 | significance 6.44 | clarity 9.0
- structural: corpus-novelty 0.3273, archival 1.0, impact 0.56
- objects: WASP-12 b  |  papers: 2015ApJ...814...66K
- novelty: While the robustness of water features to clouds and temperature has been discussed, a systematic mapping of the precise T/P/cloud regimes preserving the feature for WASP-12 b is not directly addressed in the cited literature.
- feasibility: The question can be answered by reanalyzing existing HST/WFC3 spectra with retrieval models, as described in the test sketch.
- significance: Resolving this would refine interpretations of water detections in exoplanet spectra and could impact atmospheric retrievals for WASP-12 b and similar planets.
- clarity: The question is specific and testable: it asks for the T/P/cloud parameter space consistent with the observed water feature, which can be directly constrained by retrieval analysis.

## 9. [7.262] q_006 (P4 — single_dataset_conclusion)

**Under what conditions does the equilibrium-chemistry retrieval of WASP-12 b's HST/WFC3 spectrum robustly exclude a carbon-to-oxygen ratio (C/O) greater than 1 at more than 3 sigma confidence?**

- scores: novelty 4.62 | feasibility 9.5 | significance 6.44 | clarity 9.0
- structural: corpus-novelty 0.3239, archival 1.0, impact 0.56
- objects: WASP-12 b  |  papers: 2015ApJ...814...66K
- novelty: While the exclusion of high C/O in WASP-12 b has been discussed, systematically mapping the retrieval conditions under which this exclusion is robust is a less explored, nuanced question.
- feasibility: The question can be addressed by reanalyzing existing HST/WFC3 data with different retrieval models and priors, all of which are feasible with current tools and archival spectra.
- significance: Clarifying the robustness of C/O exclusion impacts the interpretation of WASP-12 b's atmospheric composition and could affect comparative studies of exoplanet atmospheres.
- clarity: The question is precise, specifying the dataset, retrieval approach, statistical threshold, and the parameter of interest, allowing for a direct falsification test.

## 10. [7.184] q_010 (P4 — single_dataset_conclusion)

**Under what atmospheric temperature and pressure conditions does the 1.4 micron water absorption band produce a 5.4 sigma signal in HST/WFC3 transmission spectra of WASP-121 b?**

- scores: novelty 4.522 | feasibility 9.429 | significance 6.32 | clarity 9.0
- structural: corpus-novelty 0.3044, archival 0.986, impact 0.53
- objects: WASP-121 b  |  papers: 2016ApJ...822L...4E
- novelty: While water detection in hot Jupiter atmospheres is well-studied, quantitatively linking a specific sigma-level detection to precise temperature and pressure regimes for WASP-121 b is a more targeted and less commonly posed question.
- feasibility: The question can be addressed by reanalyzing existing HST/WFC3 spectra with atmospheric models, making it highly feasible with archival data.
- significance: Resolving this would refine our understanding of atmospheric retrievals and the interpretation of water features, impacting the conclusions of several studies on exoplanet atmospheres, though not overturning the field.
- clarity: The question is specific and testable: it asks for the temperature and pressure conditions that reproduce a measured 5.4 sigma water signal, which can be directly falsified by model-data comparison.

## 11. [6.461] q_011 (P4 — single_dataset_conclusion)

**Under what atmospheric compositions and temperature-pressure profiles are carbon-dioxide absorption features in TRAPPIST-1 planets robustly detectable by JWST/NIRSpec Prism transmission spectroscopy within ten transits, assuming aerosol-free conditions?**

- scores: novelty 4.835 | feasibility 5.408 | significance 7.0 | clarity 9.0
- structural: corpus-novelty 0.2671, archival 0.282, impact 0.7
- objects: TRAPPIST-1 b, TRAPPIST-1 c, TRAPPIST-1 d, TRAPPIST-1 e, TRAPPIST-1 f, TRAPPIST-1 g, TRAPPIST-1 h  |  papers: 2019AJ....158...27L
- novelty: While the general detectability of CO2 in TRAPPIST-1 planets has been discussed, systematically mapping the atmospheric composition and T-P profile space for robust detection within a fixed number of JWST/NIRSpec Prism transits is a more specific and less explored question.
- feasibility: The question can be addressed with simulated spectra and existing or soon-available JWST/NIRSpec Prism data, requiring no new technology or unattainable observations.
- significance: Resolving this would directly inform observing strategies and atmospheric retrievals for TRAPPIST-1 and similar systems, impacting the interpretation of many published and forthcoming studies.
- clarity: The question is precise, specifying the instrument, observing mode, number of transits, and the conditions (aerosol-free), allowing for a direct falsification test via model-data comparison.
