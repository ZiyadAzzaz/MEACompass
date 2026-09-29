# MEACompass

## Team

Ziyad Azzaz; College of Artificial Intelligence; Arab Academy for Science,
Technology & Maritime Transport (AASTMT); Alamein Campus, Egypt.

Team name: **MEACompass**. Solo submission; no additional team members.

## Links

1. Demo video: **VIDEO_URL_TO_BE_ADDED_AFTER_UPLOAD**
2. Public repository: [github.com/ZiyadAzzaz/MEACompass](https://github.com/ZiyadAzzaz/MEACompass)
3. Live demo: [ziyadazzaz.github.io/MEACompass/demo/](https://ziyadazzaz.github.io/MEACompass/demo/) — static and precomputed.

## Project summary

Neural microelectrode-array assays reveal how chemical exposure changes network development, but the functional endpoint used here arrives at day in vitro 12 (DIV12). MEACompass asks a practical, narrower question: can measurements available by DIV7 forecast that endpoint for a chemical the model has never seen, while explicitly refusing uncertain cases?

We built a reliability-aware early-prediction workflow from public EPA rat cortical neural MEA data. Canonical chemical identity—not the individual well—is the unit of separation: all doses, aliases, plates, and replicates for one chemical remain together throughout repeated nested cross-validation. The frozen gradient-boosted model combines DIV5/DIV7 physiology, dose, cohort, missingness, and structure-derived chemical descriptors. Training-fold residuals provide calibrated CV+ intervals, and a frozen policy abstains when uncertainty is high.

Three numbers summarize the locked evidence. First, mean absolute error improved by **14.2–39.0% versus the inner-selected BT+ baseline across all five preregistered endpoints**, with every paired chemical-bootstrap interval excluding zero. Second, nominal 90% intervals achieved **91.0–92.4% empirical coverage** on held-out chemicals. Third, selective prediction cleared the registered risk-reduction threshold on **three of five endpoints**; bursts and network spikes remain explicit limitations.

For accepted cases, a DIV7 forecast is available five days before the DIV12 endpoint. This supports earlier research triage, not autonomous assay termination. The data are rat cortical MEA recordings, not organ-on-chip or human data. Transfer to a new neural organ-on-chip platform is a hypothesis requiring local retraining, recalibration, and prospective validation.

## Technical approach and evidence

### Data and evaluation

The audit identified 136 canonical chemicals, 4,192 complete DIV5/7/9/12 trajectories, and five functional endpoints: firing rate, bursts, active electrodes, network spikes, and coordinated activity. The primary model uses only DIV5 and DIV7 neural measurements; DIV9 appears solely in a declared post-lock ablation. Outer folds evaluate unseen chemical groups. Inner group folds choose model settings and the BT+ comparator. Confidence intervals resample chemicals rather than wells.

Against the stricter post-audit BT++ comparator, the same frozen predictions improved MAE by 12.3–42.9% across all five endpoints, again with paired chemical-bootstrap intervals excluding zero. The full endpoint table and bootstrap intervals are in the [technical report](https://github.com/ZiyadAzzaz/MEACompass/blob/main/docs/MEACompass_Technical_Report.pdf).

<!-- GENERATED_MAIN_RESULTS_START -->
| Endpoint | M1 MAE | BT+ MAE | Gain vs BT+ | ΔMAE vs BT+ [95% CI] | BT++ Gain | ΔMAE vs BT++ [95% CI] |
|---|---:|---:|---:|---:|---:|---:|
| Bursts/min | 27.17 | 32.74 | 17.0% | -5.57 [-7.51, -3.77] | 16.2% | -5.25 [-7.26, -3.41] |
| Mean firing rate | 39.29 | 45.79 | 14.2% | -6.50 [-11.59, -1.50] | 12.3% | -5.49 [-10.48, -0.21] |
| Active electrodes | 20.42 | 33.50 | 39.0% | -13.08 [-17.47, -9.52] | 42.9% | -15.33 [-25.82, -7.75] |
| Network spikes | 40.72 | 48.26 | 15.6% | -7.54 [-10.20, -4.56] | 14.2% | -6.75 [-9.48, -3.76] |
| Coordinated activity (`r`) | 48.61 | 62.91 | 22.7% | -14.30 [-17.56, -11.05] | 26.4% | -17.41 [-24.51, -12.32] |
<!-- GENERATED_MAIN_RESULTS_END -->

### Integrity before momentum

A registered chemical-block permutation control unexpectedly showed a small beneficial bursts result, so the registered gate stopped. We did not erase that outcome. A bounded audit found no future-derived feature, a clean full-target shuffle, no alignment defect, and residual dose/trajectory structure in the original null construction. Real M1 then exceeded every one of 20 independent block-null runs for every endpoint. Continuation was conditional on retaining the failed gate and adding BT++ as a stricter comparator.

### Calibrated uncertainty and abstention

![Calibration](https://raw.githubusercontent.com/ZiyadAzzaz/MEACompass/main/artifacts/reproduce-lite/calibration.png)

![Selective risk](https://raw.githubusercontent.com/ZiyadAzzaz/MEACompass/main/artifacts/reproduce-lite/risk_coverage.png)

Intervals are calibrated from training chemicals only. At the frozen 70% retained-coverage operating point, firing rate, active electrodes, and coordinated activity pass the registered risk-reduction rule. Bursts and network spikes do not. Uncertain cases continue to DIV12; MEACompass is a research decision-support system, not an autonomous assay-termination system.

### Time causality, interpretation, and robustness

![Time ablation](https://raw.githubusercontent.com/ZiyadAzzaz/MEACompass/main/artifacts/reproduce-lite/time_ablation.png)

DIV5 alone is weaker; DIV7 is the earliest window with consistent primary gains. Frozen tree contributions assign 56.9–77.3% of absolute predictive contribution to DIV7 physiology and 11.2–31.8% to chemistry. These are predictive associations, not mechanisms, and the tributyltin chloride failure remains disclosed.

Post-lock secondary analysis retained predictive value under a held-out NTP↔ToxCast cohort shift without model retuning. This is not external laboratory or device transfer. A later refinement release was audited with deterministic final-refit models frozen before access, but external scoring was cut at harmonization: two required inputs were absent and `r` failed the registered compatibility threshold. No external outcomes were scored.

## Use on your own data

MEACompass is an evaluation and adaptation recipe, not a frozen model to deploy directly on a new chip.

1. Map local longitudinal measurements to the declared schema and define local endpoints and controls.
2. Keep every well, concentration, replicate, and alias of one chemical in the same split.
3. Train locally using only measurements available before the target time; never fit preprocessing or selection on the outer test set.
4. Calibrate prediction intervals on local training chemicals and predeclare the acceptance/abstention rule.
5. Validate prospectively on unseen chemicals, plates, dates, and devices with human review before operational use.

The repository provides `make test`, `make reproduce-lite`, and `make demo`. Lightweight reproduction regenerates tables, figures, and the demo from checked saved predictions without retraining.

## Sources, licenses, and AI-tool disclosure

The primary source is the public EPA neural network formation assay catalog recorded with URLs and SHA-256 hashes in `schemas/epa_downloads_v1.json`. It contains animal-derived assay measurements and no human or personal data. Raw source files are not redistributed. Project-authored code and documentation use Apache-2.0; third-party data and dependencies retain their own terms. PubChem supplies public structure lookups. No EPA endorsement is claimed or implied. Full provenance and limitations appear in [Sources and licenses](sources_and_licenses.md).

**AI-tool disclosure.** Codex/the repository coding agent assisted with implementation, experiment execution, testing, reproducibility, result artifacts, documentation, the deck, and subtitles. ChatGPT assisted with planning, strategy, protocol/gate and claim review, prompt drafting, and submission planning. Claude provided independent review, source exploration, strategy/protocol feedback, and critique. Claude and generated prose were not sources of scientific result values. All scientific numbers came from executed code and stored artifacts; automated claim-consistency tests were used, and Ziyad Azzaz manually reviewed the public scientific claims, report, README, presentation, and submission materials.
