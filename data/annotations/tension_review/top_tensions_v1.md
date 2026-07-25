# Top Tension Candidates

Top 20 of 161 R4 candidates, ranked by:
shared topics + opposite polarity (2x) + independent datasets (1x) +
gold support on either end (2x) + min claim confidence (tiebreak).
Spot-check before question generation; record verdicts as `relation`
entries in data/annotations/<batch>/contradictions.jsonl.

## 1. score 6.75  [pending]

- objects: HD 209458 b  |  topics: water
- signals: opposite_polarity=True, independent_datasets=True, gold_supported=True
- A `claim_cfab7b1f2bba` (model_matched_gold, 2017MNRAS.469.1979M): The preferred retrieval for HD 209458 b indicates non-uniform cloud coverage, high-altitude haze, and strongly subsolar water abundance at the terminator.
- B `claim_e06bbde77555` (model_only, 2016AJ....152..203L): HST/WFC3 spectroscopy detects water in absorption in the dayside emission spectrum of HD 209458b at 6.2σ confidence, indicating the absence of a thermal inversion.

## 2. score 6.75  [pending]

- objects: HD 209458 b  |  topics: clouds, haze, abundance
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_cfab7b1f2bba` (model_matched_gold, 2017MNRAS.469.1979M): The preferred retrieval for HD 209458 b indicates non-uniform cloud coverage, high-altitude haze, and strongly subsolar water abundance at the terminator.
- B `claim_4a85ddfac48f` (model_only, 2019AJ....157..206W): Broadband transmission spectra from current facilities, analyzed with retrieval models that include variable cloud coverage and prominent opacity sources, enable precise joint constraints on chemical abundances and cloud/haze properties in H2-rich exoplanet atmospheres.

## 3. score 6.75  [pending]

- objects: HD 189733 b  |  topics: clouds
- signals: opposite_polarity=True, independent_datasets=True, gold_supported=True
- A `claim_fbabb7a810d2` (model_matched_gold, 2016ApJ...820...78L): The HST/WFC3 spectra of HD 189733 b and HAT-P-11 b can be explained by solar-composition atmospheres with patchy clouds without requiring high mean molecular weight or globally uniform clouds.
- B `claim_521bba86046c` (model_only, 2016ApJ...827...19F): Despite having a pressure-temperature profile comparable to HD 189733 b and WASP-6 b, WASP-39 b appears to be largely cloud-free, in contrast to the high-altitude clouds or hazes seen in the other two planets.

## 4. score 6.75  [pending]

- objects: HD 189733 b  |  topics: clouds
- signals: opposite_polarity=True, independent_datasets=True, gold_supported=True
- A `claim_fbabb7a810d2` (model_matched_gold, 2016ApJ...820...78L): The HST/WFC3 spectra of HD 189733 b and HAT-P-11 b can be explained by solar-composition atmospheres with patchy clouds without requiring high mean molecular weight or globally uniform clouds.
- B `claim_cb5c7da0849f` (model_only, 2016ApJ...827...19F): These observations emphasize the diversity of cloudy and cloud-free gas giant planets in short-period orbits and highlight the challenges in developing predictive cloud models for exoplanet atmospheres.

## 5. score 6.0  [contradicts]

- objects: HD 189733 b  |  topics: sodium, wind
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_1465e6632000` (model_matched_gold, 2015A&A...577A..62W): The resolved sodium lines in HD 189733 b indicate hotter upper-atmosphere layers and a possible high-altitude wind blueshift.
- B `claim_3240edabe8e5` (model_matched_gold, 2016ApJ...817..106B): The near-infrared data indicate a small day-to-night wind in HD 189733 b and, when compared with a much larger optical sodium blueshift, imply strong vertical wind shear.

## 6. score 5.75  [pending]

- objects: WASP-12 b  |  topics: c/o ratio
- signals: opposite_polarity=True, independent_datasets=False, gold_supported=True
- A `claim_8ff60d8c01cd` (model_matched_gold, 2015ApJ...814...66K): An equilibrium-chemistry retrieval of WASP-12 b favors a near-solar carbon-to-oxygen ratio and rules out a carbon-rich atmosphere.
- B `claim_68b8a8f9a8fb` (model_only, 2019MNRAS.482.1485P): Retrieved H2O abundances suggest subsolar oxygen and/or supersolar C/O ratios in the atmospheres of these hot giant exoplanets.

## 7. score 5.75  [pending]

- objects: HD 209458 b  |  topics: water, abundance
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_cfab7b1f2bba` (model_matched_gold, 2017MNRAS.469.1979M): The preferred retrieval for HD 209458 b indicates non-uniform cloud coverage, high-altitude haze, and strongly subsolar water abundance at the terminator.
- B `claim_2de3449c6918` (model_only, 2019AJ....157..114B): Application of the framework to VLT CRIRES K-band spectra of HD 209458 b and HD 189733 b retrieves abundant carbon monoxide but subsolar water abundances, with results largely invariant under different model assumptions.

## 8. score 5.75  [pending]

- objects: HD 209458 b  |  topics: abundance
- signals: opposite_polarity=True, independent_datasets=False, gold_supported=True
- A `claim_cfab7b1f2bba` (model_matched_gold, 2017MNRAS.469.1979M): The preferred retrieval for HD 209458 b indicates non-uniform cloud coverage, high-altitude haze, and strongly subsolar water abundance at the terminator.
- B `claim_2a8b6be51638` (model_only, 2019AJ....157..206W): The degeneracy between planetary radius and reference pressure is well characterized and does not significantly affect chemical abundance estimates, challenging previous results from semi-analytic models.

## 9. score 5.75  [pending]

- objects: WASP-12 b  |  topics: water, abundance
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_0da0d291929b` (human_gold, 2020ApJ...893L..43M): One-dimensional retrievals of heterogeneous terminators can bias retrieved molecular abundances, including water, by more than an order of magnitude.
- B `claim_b4f8dcc2790d` (model_only, 2015ApJ...814...66K): Retrievals using the transmission spectrum yield a 1σ water volume mixing ratio between 10^-5 and 10^-2, which is consistent with a carbon-to-oxygen ratio (C/O) greater than 1 to within 2σ.

## 10. score 5.75  [pending]

- objects: HD 189733 b  |  topics: clouds
- signals: opposite_polarity=True, independent_datasets=False, gold_supported=True
- A `claim_fbabb7a810d2` (model_matched_gold, 2016ApJ...820...78L): The HST/WFC3 spectra of HD 189733 b and HAT-P-11 b can be explained by solar-composition atmospheres with patchy clouds without requiring high mean molecular weight or globally uniform clouds.
- B `claim_c4a6a107230d` (model_only, 2016A&A...594A..48L): 3D radiative-hydrodynamic simulations with kinetic, non-equilibrium cloud formation produce an inhomogeneous, wavelength-dependent mineral cloud structure in the atmosphere of HD 189733b, with properties varying by longitude, latitude, and depth.

## 11. score 5.75  [pending]

- objects: HD 189733 b  |  topics: clouds
- signals: opposite_polarity=True, independent_datasets=False, gold_supported=True
- A `claim_fbabb7a810d2` (model_matched_gold, 2016ApJ...820...78L): The HST/WFC3 spectra of HD 189733 b and HAT-P-11 b can be explained by solar-composition atmospheres with patchy clouds without requiring high mean molecular weight or globally uniform clouds.
- B `claim_6982479b5338` (model_only, 2016A&A...594A..48L): Mean cloud particle sizes in HD 189733b's atmosphere are typically sub-micron (0.01–0.5 μm) at pressures less than 1 bar, with the smallest grains found in hotter equatorial regions and denser cloud structures near terminators and deeper atmospheric layers.

## 12. score 5.75  [pending]

- objects: HD 189733 b  |  topics: clouds
- signals: opposite_polarity=True, independent_datasets=False, gold_supported=True
- A `claim_fbabb7a810d2` (model_matched_gold, 2016ApJ...820...78L): The HST/WFC3 spectra of HD 189733 b and HAT-P-11 b can be explained by solar-composition atmospheres with patchy clouds without requiring high mean molecular weight or globally uniform clouds.
- B `claim_01be704b116b` (model_only, 2016A&A...594A..48L): Elements involved in cloud formation in HD 189733b's atmosphere can be depleted by several orders of magnitude due to cloud processes.

## 13. score 5.75  [pending]

- objects: HD 189733 b  |  topics: clouds
- signals: opposite_polarity=True, independent_datasets=False, gold_supported=True
- A `claim_fbabb7a810d2` (model_matched_gold, 2016ApJ...820...78L): The HST/WFC3 spectra of HD 189733 b and HAT-P-11 b can be explained by solar-composition atmospheres with patchy clouds without requiring high mean molecular weight or globally uniform clouds.
- B `claim_e1bb8bfe897c` (model_only, 2016A&A...594A..48L): The spatially variable cloud properties predicted by the model imply that transit spectroscopy of HD 189733b would sample a variety of cloud particle properties, including sizes, compositions, and densities.

## 14. score 5.75  [pending]

- objects: HD 189733 b  |  topics: water, carbon monoxide
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_26c21a047230` (model_matched_gold, 2016ApJ...817..106B): High-dispersion transmission spectroscopy detects carbon monoxide and water vapor in HD 189733 b and yields a rotation rate consistent with tidal locking.
- B `claim_2de3449c6918` (model_only, 2019AJ....157..114B): Application of the framework to VLT CRIRES K-band spectra of HD 209458 b and HD 189733 b retrieves abundant carbon monoxide but subsolar water abundances, with results largely invariant under different model assumptions.

## 15. score 5.0  [challenges_method]

- objects: WASP-12 b  |  topics: water
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_41790912efe6` (model_matched_gold, 2015ApJ...814...66K): The HST/WFC3 transmission spectrum of WASP-12 b contains a high-confidence water absorption signal.
- B `claim_0da0d291929b` (human_gold, 2020ApJ...893L..43M): One-dimensional retrievals of heterogeneous terminators can bias retrieved molecular abundances, including water, by more than an order of magnitude.

## 16. score 5.0  [explains_discrepancy]

- objects: HD 189733 b  |  topics: sodium
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_6df6b9a5a7e0` (model_matched_gold, 2015A&A...577A..62W): High-resolution HARPS transmission spectroscopy resolves the sodium D doublet in the atmosphere of HD 189733 b at high significance.
- B `claim_3240edabe8e5` (model_matched_gold, 2016ApJ...817..106B): The near-infrared data indicate a small day-to-night wind in HD 189733 b and, when compared with a much larger optical sodium blueshift, imply strong vertical wind shear.

## 17. score 4.75  [pending]

- objects: HD 209458 b  |  topics: clouds
- signals: opposite_polarity=False, independent_datasets=True, gold_supported=True
- A `claim_72a7eac80d1a` (model_matched_gold, 2017MNRAS.469.1979M): A two-dimensional retrieval with inhomogeneous clouds finds evidence for nitrogen-bearing chemistry in the atmosphere of HD 209458 b.
- B `claim_4a85ddfac48f` (model_only, 2019AJ....157..206W): Broadband transmission spectra from current facilities, analyzed with retrieval models that include variable cloud coverage and prominent opacity sources, enable precise joint constraints on chemical abundances and cloud/haze properties in H2-rich exoplanet atmospheres.

## 18. score 4.75  [pending]

- objects: HD 209458 b  |  topics: water, abundance
- signals: opposite_polarity=False, independent_datasets=False, gold_supported=True
- A `claim_cfab7b1f2bba` (model_matched_gold, 2017MNRAS.469.1979M): The preferred retrieval for HD 209458 b indicates non-uniform cloud coverage, high-altitude haze, and strongly subsolar water abundance at the terminator.
- B `claim_2f8286c3df19` (model_only, 2019MNRAS.482.1485P): The majority of hot Jupiters in the sample have atmospheres consistent with subsolar H2O abundances at their day-night terminators.

## 19. score 4.75  [pending]

- objects: HD 209458 b  |  topics: water, abundance
- signals: opposite_polarity=False, independent_datasets=False, gold_supported=True
- A `claim_cfab7b1f2bba` (model_matched_gold, 2017MNRAS.469.1979M): The preferred retrieval for HD 209458 b indicates non-uniform cloud coverage, high-altitude haze, and strongly subsolar water abundance at the terminator.
- B `claim_68b8a8f9a8fb` (model_only, 2019MNRAS.482.1485P): Retrieved H2O abundances suggest subsolar oxygen and/or supersolar C/O ratios in the atmospheres of these hot giant exoplanets.

## 20. score 4.75  [pending]

- objects: HD 209458 b  |  topics: clouds, haze
- signals: opposite_polarity=False, independent_datasets=False, gold_supported=True
- A `claim_cfab7b1f2bba` (model_matched_gold, 2017MNRAS.469.1979M): The preferred retrieval for HD 209458 b indicates non-uniform cloud coverage, high-altitude haze, and strongly subsolar water abundance at the terminator.
- B `claim_ba109515b7ee` (model_only, 2019MNRAS.482.1485P): Cloud/haze coverage fractions in the atmospheres of these hot Jupiters are statistically constrained to range from 0.18^{+0.26}_{-0.12} to 0.76^{+0.13}_{-0.15}.
