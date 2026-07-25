# Historical Validation Report (hv-p1)

Questions were generated from Corpus A (evidence up to 2020-12-31)
and judged against 2021-2026 literature the pipeline never saw.
Validation corpus: 1891 post-cutoff papers.

Verdict counts: answered=2, partially_addressed=7, posed_but_open=1

## rank 1 — q_002: posed_but_open

**How does terminator heterogeneity affect the statistical evidence for water and the inferred water abundance and C/O ratio in WASP-12 b?**

- premise: untested  |  top retrieval similarity: 0.5966
- note: Post-2020 literature has engaged with the general problem of terminator heterogeneity and its impact on atmospheric retrievals, but has not specifically addressed or resolved how this affects the statistical evidence for water and the inferred water abundance and C/O ratio in WASP-12 b. The question remains open for WASP-12 b, with only general methodological progress made on the topic in other systems or in synthetic studies.
- [2022ApJ...933...79W] This paper discusses the impact of inhomogeneous terminators on atmospheric retrievals, including biases in inferred abundances, but does not specifically address WASP-12 b or provide a resolution for its water and C/O ratio in light of terminator heterogeneity.

## rank 2 — q_001: partially_addressed

**What causes the roughly factor-of-five discrepancy between the ~8 km/s wind inferred from optical sodium and the ~1.7 km/s wind inferred from near-infrared CO/H2O in HD 189733 b: vertical wind shear between the probed atmospheric layers, temporal variability, line-formation differences, or instrumental and analysis systematics?**

- premise: validated  |  top retrieval similarity: 0.6017
- note: Post-2020 literature has made substantial progress in addressing the wind speed discrepancy in HD 189733 b. Evidence supports the presence of vertical wind shear between atmospheric layers and highlights the role of analysis systematics, but the core question of fully reconciling the sodium and CO/H2O wind measurements remains open.
- [2021PhDT.........4S] This thesis applies resolved line-shape modeling to HD 189733 b, finding evidence for zonal winds in the lower and vertical winds in the intermediate atmosphere, directly addressing vertical wind shear as a cause of wind discrepancies.
- [2021MNRAS.502.4392L] This paper analyzes telluric correction and confirms sodium detection and blueshift in HD 189733 b, discussing instrumental and analysis systematics as a source of discrepancies.
- [2024AJ....167..179B] This work reanalyzes high-resolution near-infrared data for HD 189733 b, finding a significant blueshift in H2O lines, and discusses the impact of analysis pipelines on inferred wind speeds.

## rank 3 — q_004: partially_addressed

**Under what atmospheric conditions does HD 189733 b exhibit subsolar water abundances alongside robust carbon monoxide detection in high-dispersion transmission spectra?**

- premise: validated  |  top retrieval similarity: 0.6896
- note: Post-2020 literature, specifically 2021AJ....162..233B, detected subsolar water vapor in HD 189733 b and noted the context of previously reported super-solar CO abundances, implying a high C/O ratio. However, the study did not directly confirm robust CO detection in the same dataset or fully resolve the atmospheric conditions (e.g., temperature, cloud properties) that enable this abundance pattern, leaving the core question open.
- [2021AJ....162..233B] This study directly detects water vapor in HD 189733 b's atmosphere using high-resolution transmission spectroscopy, finding a slightly subsolar water abundance and referencing previous super-solar CO detections, thus engaging the question's premise.

## rank 4 — q_008: answered

**Is the strongly subsolar terminator water abundance retrieved for HD 209458 b a property of the atmosphere or an artifact of retrieval assumptions, as tested by comparing independent retrieval frameworks on the same and on independent datasets?**

- premise: refuted  |  top retrieval similarity: 0.6487
- note: Multiple independent retrieval frameworks, using both new and archival HST and JWST data as well as ground-based high-resolution spectra, now consistently find that the water abundance at the terminator of HD 209458 b is consistent with solar values. The previously reported strongly subsolar water abundance is now understood to be an artifact of earlier retrieval assumptions and/or data systematics, not a true property of the atmosphere.
- [2025A&A...700A.105B] This study reanalyzes HST and JWST spectra of HD 209458 b with improved systematics treatment and Bayesian model averaging, finding a water abundance consistent with solar, thus refuting the previously reported strongly subsolar value.
- [2025AJ....170...69V] This work applies the new SANSAR retrieval framework to HST and JWST data, showing that retrieval assumptions (free vs. equilibrium chemistry, grid retrievals) can yield both subsolar and solar water abundances, directly addressing the retrieval-dependence of the result.
- [2025AJ....170..223F] High-resolution ground-based spectroscopy and retrievals independently constrain the H2O abundance in HD 209458 b to be at least solar, consistent with recent JWST results and inconsistent with a strongly subsolar value.

## rank 5 — q_007: partially_addressed

**Do patchy-cloud, solar-composition models remain the preferred explanation of the HST/WFC3 transmission spectra of HD 189733 b and HAT-P-11 b when tested with independent retrieval frameworks and broader-wavelength or independent observations?**

- premise: untested  |  top retrieval similarity: 0.6739
- note: Recent literature has made substantial progress by applying independent retrieval frameworks and broader-wavelength observations to the transmission spectra of HD 189733 b and similar planets. However, the specific question of whether patchy-cloud, solar-composition models remain the preferred explanation for HD 189733 b and HAT-P-11 b, when tested with independent retrievals and broader or independent data, remains open due to ongoing issues with stellar contamination and parameter degeneracies, and a lack of direct, comprehensive model comparison in the cited works.
- [2024MNRAS.528.3354F] This study applies three independent retrieval codes to HAT-P-18 b (not HAT-P-11 b), using HST/WFC3, Spitzer, and JWST data, and finds agreement on a sub-solar H2O abundance and the presence of clouds, but also highlights the importance of stellar heterogeneity and the need for further investigation into CO2 abundances.
- [2024AJ....167..179B] This paper presents a new retrieval framework applied to high-resolution transmission spectra of HD 189733 b, finding subsolar metallicity and placing upper limits on several molecules, but does not directly test patchy-cloud, solar-composition models against broader-wavelength data.
- [2024AJ....167..107N] This work investigates the impact of stellar heterogeneity on the transmission spectra of HD 189733 b, showing that unocculted spots can mimic atmospheric features, complicating the interpretation of cloud and haze signatures.

## rank 6 — q_010: partially_addressed

**How sensitive is the reported WASP-121 b water detection to cloud opacity, stellar contamination, baseline offsets, retrieval priors, and the selected null model?**

- premise: untested  |  top retrieval similarity: 0.664
- note: Post-2020 literature has made progress in retrieval methodology for WASP-121b, specifically addressing how data-processing and model-filtering affect atmospheric abundance constraints. However, the abstracts do not report a comprehensive sensitivity analysis of the WASP-121b water detection to all the factors in the question (cloud opacity, stellar contamination, baseline offsets, retrieval priors, and null model selection), so the core question remains open.
- [2022MNRAS.512.4618G] This work presents retrievals on WASP-121b's transmission spectra, directly addressing the impact of data-processing methods (which can include baseline offsets and stellar contamination) on atmospheric abundance constraints.

## rank 7 — q_005: answered

**Do the HST transmission data independently support NH3 or HCN in HD 209458 b, and how does the evidence for each species change under cloud-free, patchy-cloud, and fully cloudy retrieval scenarios?**

- premise: validated  |  top retrieval similarity: 0.6382
- note: Post-2020 literature, particularly 2025AJ....170..223F and 2024A&A...690A..63B, used high-resolution transmission spectroscopy to place stringent upper limits on both NH3 and HCN in HD 209458 b, with no significant detections in HST or ground-based data. These results hold across retrieval scenarios, indicating that HST transmission data do not independently support the presence of NH3 or HCN in this planet's atmosphere under cloud-free or cloudy models.
- [2025AJ....170..223F] This study provides upper limits on NH3 and HCN abundances in HD 209458 b using high-resolution transmission spectroscopy, consistent with recent JWST results, and explicitly states these limits for both species.
- [2024A&A...690A..63B] This work reports a non-detection of HCN in recent space-based transmission data for HD 209458 b, directly addressing the question of HCN detectability.

## rank 8 — q_009: partially_addressed

**Under what atmospheric conditions do patchy cloud models with solar composition provide robust fits to HST/WFC3 spectra of hot Neptunes and hot Jupiters, without invoking high mean molecular weight or globally uniform clouds?**

- premise: validated  |  top retrieval similarity: 0.7192
- note: Post-2020 literature has made substantial progress in modeling and simulating patchy cloud distributions in hot Jupiter and hot Neptune atmospheres, demonstrating that such models can naturally arise from atmospheric dynamics and can explain some observed spectral features. However, the literature has not fully resolved under exactly which atmospheric conditions patchy cloud models with solar composition alone provide robust fits to HST/WFC3 spectra, as degeneracies with other scenarios (e.g., high mean molecular weight, globally uniform clouds) remain in some cases.
- [2021ApJ...908..101R] This study uses 3D GCMs with temperature-dependent clouds to explore how patchy clouds affect the observable properties of hot Jupiters, showing that partial cloud coverage is a natural outcome and can explain some spectral features without invoking high mean molecular weight or globally uniform clouds.
- [2022ApJ...934...79K] This work demonstrates that patchy cloud distributions are a ubiquitous result of atmospheric dynamics in ultra-hot Jupiters, supporting the plausibility of patchy cloud models with solar composition.
- [2021ApJ...909...85H] This paper models the impact of inhomogeneous (patchy) clouds on hot Jupiter emission spectra, showing that such models produce distinct spectral signatures and emphasizing the importance of radiative feedback.
- [2021ApJ...923...62M] This study finds that cloud coverage intensifies spatial variations in emission spectra, supporting the relevance of patchy cloud models for interpreting observations of hot Jupiters.
- [2024MNRAS.530.3100D] This observational study of a warm Neptune finds that solar-abundance models with a high cloud deck are among the plausible explanations for the observed spectra, but does not definitively resolve the degeneracy between patchy clouds and other scenarios.

## rank 9 — q_006: partially_addressed

**Does the >3-sigma exclusion of a carbon-rich (C/O > 1) atmosphere for WASP-12 b survive relaxing the equilibrium-chemistry assumption in retrievals of the same HST/WFC3 transmission spectrum?**

- premise: untested  |  top retrieval similarity: 0.7005
- note: Post-2020 literature (2025MNRAS.538.2521N) directly engages the question by re-examining WASP-12b's HST/WFC3 transmission spectrum with retrievals that consider parameter degeneracies and the limitations of equilibrium-chemistry assumptions. While the study highlights the importance of these degeneracies and advocates for caution in interpreting previous C/O constraints, it does not definitively resolve whether the >3-sigma exclusion of a carbon-rich atmosphere survives when relaxing equilibrium chemistry, leaving the core question open but substantially advanced.
- [2025MNRAS.538.2521N] This study performs atmospheric retrievals on WASP-12b's HST/WFC3 transmission spectrum, specifically investigating parameter degeneracies and the impact of retrieval assumptions, including equilibrium chemistry.

## rank 10 — q_011: partially_addressed

**To what extent have actual JWST observations validated pre-launch predictions that aerosol-free TRAPPIST-1 CO2 atmospheres would be detectable within ten NIRSpec Prism transits?**

- premise: untested  |  top retrieval similarity: 0.7314
- note: Post-2020 JWST observations have begun to address the detectability of CO2 atmospheres on TRAPPIST-1 planets using NIRSpec PRISM, but stellar contamination has proven a major obstacle, preventing a definitive test of pre-launch predictions. While some CO2-rich atmospheres are weakly disfavored, the literature has not yet validated the prediction that aerosol-free CO2 atmospheres would be detectable within ten transits, leaving the core question open.
- [2024ESS.....562518R] Reports on JWST/NIRSpec PRISM transmission spectra of TRAPPIST-1c, finding that stellar contamination limits the precision needed to probe for CO2 atmospheres and that substantial CO2-dominated atmospheres are unlikely for TRAPPIST-1c.
- [2026ASTCS..1160070G] Presents JWST/NIRSpec PRISM transmission spectra of TRAPPIST-1e, finding significant stellar contamination and only weakly disfavors CO2-rich atmospheres at Venus/Mars-like pressures, but does not obtain strong evidence for or against an atmosphere.
- [2026AJ....171..105A] Describes a JWST program targeting TRAPPIST-1e with the explicit goal of detecting a CO2 atmosphere, noting that stellar contamination is a major challenge and that initial observations demonstrate the difficulty of correcting for it.
- [2025ApJ...990L..52E] Presents four JWST/NIRSpec PRISM transmission spectra of TRAPPIST-1e, rules out H2-dominated atmospheres, and discusses the challenge of stellar contamination, with constraints on secondary atmospheres given in a companion paper.
