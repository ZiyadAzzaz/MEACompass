# MEACompass

## Team

Ziyad Azzaz; College of Artificial Intelligence; Arab Academy for Science,
Technology & Maritime Transport (AASTMT); Alamein Campus, Egypt.

Team name: **USER CONFIRMATION REQUIRED**.

## Links

1. Demo video: **VIDEO_URL_TO_BE_ADDED_AFTER_UPLOAD**
2. Public repository: [github.com/ZiyadAzzaz/MEACompass](https://github.com/ZiyadAzzaz/MEACompass) — reserved publication URL; human publication is pending.
3. Live demo: [ziyadazzaz.github.io/MEACompass/demo/](https://ziyadazzaz.github.io/MEACompass/demo/) — static, precomputed, and activated with the public repository.

## Project summary

Neural microelectrode-array assays reveal how chemical exposure changes network development, but the functional endpoint used here arrives at day in vitro 12 (DIV12). MEACompass asks a practical, narrower question: can measurements available by DIV7 forecast that endpoint for a chemical the model has never seen, while explicitly refusing uncertain cases?

We built a reliability-aware early-prediction workflow from public EPA rat cortical neural MEA data. Canonical chemical identity—not the individual well—is the unit of separation: all doses, aliases, plates, and replicates for one chemical remain together throughout repeated nested cross-validation. The frozen gradient-boosted model combines DIV5/DIV7 physiology, dose, cohort, missingness, and structure-derived chemical descriptors. Training-fold residuals provide calibrated CV+ intervals, and a frozen policy abstains when uncertainty is high.

Three numbers summarize the locked evidence. First, mean absolute error improved by **14.2–39.0% versus the inner-selected BT+ baseline across all five preregistered endpoints**, with every paired chemical-bootstrap interval excluding zero. Second, nominal 90% intervals achieved **91.0–92.4% empirical coverage** on held-out chemicals. Third, selective prediction cleared the registered risk-reduction threshold on **three of five endpoints**; bursts and network spikes remain explicit limitations.

For accepted cases, a DIV7 forecast is available five days before the DIV12 endpoint. This supports earlier research triage, not autonomous assay termination. The data are rat cortical MEA recordings, not organ-on-chip or human data. Transfer to a new neural organ-on-chip platform is a hypothesis requiring local retraining, recalibration, and prospective validation.

## Technical approach and evidence

### Data and evaluation

The audit identified 136 canonical chemicals, 4,192 complete DIV5/7/9/12 trajectories, and five functional endpoints: firing rate, bursts, active electrodes, network spikes, and coordinated activity. The primary model uses only DIV5 and DIV7 neural measurements; DIV9 appears solely in a declared post-lock ablation. Outer folds evaluate unseen chemical groups. Inner group folds choose model settings and the BT+ comparator. Confidence intervals resample chemicals rather than wells.

Against the stricter post-audit BT++ comparator, the same frozen predictions improved MAE by 12.3–42.9% across all five endpoints, again with paired chemical-bootstrap intervals excluding zero. The full endpoint table and bootstrap intervals are in the [technical report](MEACompass_Technical_Report.pdf).

### Integrity before momentum

A registered chemical-block permutation control unexpectedly showed a small beneficial bursts result, so the registered gate stopped. We did not erase that outcome. A bounded audit found no future-derived feature, a clean full-target shuffle, no alignment defect, and residual dose/trajectory structure in the original null construction. Real M1 then exceeded every one of 20 independent block-null runs for every endpoint. Continuation was conditional on retaining the failed gate and adding BT++ as a stricter comparator.

### Calibrated uncertainty and abstention

![Calibration](../artifacts/reproduce-lite/calibration.png)

![Selective risk](../artifacts/reproduce-lite/risk_coverage.png)

Intervals are calibrated from training chemicals only. At the frozen 70% retained-coverage operating point, firing rate, active electrodes, and coordinated activity pass the registered risk-reduction rule. Bursts and network spikes do not. Uncertain cases continue to DIV12; MEACompass is a research decision-support system, not an autonomous assay-termination system.

### Time causality, interpretation, and robustness

![Time ablation](../artifacts/reproduce-lite/time_ablation.png)

DIV5 alone is weaker; DIV7 is the earliest window with consistent primary gains. Frozen tree contributions assign 56.9–77.3% of absolute predictive contribution to DIV7 physiology and 11.2–31.8% to chemistry. These are predictive associations, not mechanisms, and the tributyltin chloride failure remains disclosed.

Post-lock secondary analysis retained predictive value under a held-out NTP↔ToxCast cohort shift without model retuning. This is not external laboratory or device transfer. Frozen external scoring on the later refinement release was cut before data acquisition because the exact serialized locked model ensemble was unavailable; it was not reconstructed or tuned.

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

**AI-tool disclosure — USER CONFIRMATION REQUIRED BEFORE PUBLICATION.** The final entry will name only the assistants and services the team confirms were actually used, their roles in code/writing/figures/translation, and the human verification performed. Every scientific number above comes from executed, tested result artifacts; no number is accepted from generated prose.
