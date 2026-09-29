# MEACompass: Reliability-Aware Early Prediction of Neural Network Development from Microelectrode-Array Assays

**Toward Functional Digital Twins for Neural Organ-on-Chip Screening**

Target runtime: 4:35–4:50. Final subtitle cues must be retimed against the recorded narration.

## 0:00–0:18 — The decision problem

“A neural assay reaches its functional endpoint at day twelve. MEACompass asks whether day-seven physiology can forecast that endpoint for a chemical the model has never seen—and whether the system can refuse when the forecast is unsafe.”

On screen: title, subtitle, and the line “Forecast early. Quantify uncertainty. Continue when uncertain.”

## 0:18–0:58 — Show the working prototype first

Open the public demo and use the predetermined neutral example listed in the recording checklist.

“Everything shown here is precomputed held-out evidence. **OBSERVED** contains only early measurements. **PREDICTED** shows the later forecast and its calibrated interval. The reliability badge applies a frozen acceptance policy. A wide interval means abstain and continue the assay. **HYPOTHESIS** marks anything this study has not validated, including human organ-on-chip transfer.”

Change the endpoint once. Show the prediction, interval, comparator, and verdict updating together. Do not select a case because it looks favorable.

## 0:58–1:30 — Fair evaluation

Show the chemical-disjoint evaluation design and the main-results figure.

“The study contains 136 chemicals and about 4,200 complete longitudinal trajectories. Every dose, replicate, well, and alias of one chemical stays on one side of each split. Across all five preregistered endpoints—firing, bursts, active electrodes, network spikes, and coordinated activity—the frozen model reduced mean absolute error by 14.2 to 39.0 percent versus the strongest baseline BT+. Against the stricter BT++, gains remained 12.3 to 42.9 percent. Every paired chemical-level confidence interval excluded zero.”

## 1:30–2:05 — Integrity before momentum

Show the audit decision graphic.

“One negative control did not behave as expected, so the registered rule stopped the pipeline. We kept that failure visible. A bounded audit found no future-derived feature, a clean full-target shuffle, no alignment defect, and a dose-plus-trajectory effect in the original null construction. The real model then beat every independent block-null run on every endpoint. Continuation remained conditional, and BT++ stayed as an added safeguard.”

## 2:05–2:45 — Reliability, not automatic stopping

Show calibration and selective-prediction figures.

“Nominal intervals achieved 91.0 to 92.4 percent coverage. At the frozen acceptance level, abstention passed the registered risk threshold on three of five endpoints. Bursts and network spikes did not pass, and we report both as limitations. This is research decision support: uncertainty means continue, not terminate.”

## 2:45–3:20 — Why DIV7 matters

Show the time-causality and interpretability slide.

“The earlier snapshot alone was weaker. Adding day-seven physiology produced the primary gains. For accepted cases, forecasts are available five days before the day-twelve endpoint. Contribution analysis identifies day-seven physiology as the dominant predictive family, while chemistry adds complementary context. These are predictive associations, not mechanisms.”

## 3:20–3:50 — Show failure, not just success

Show one predetermined correct case and the disclosed tributyltin chloride failure.

“A trustworthy system must expose where it breaks. The demo therefore shows an ordinary correct case and a registered failure case, without cherry-picking. The interval and abstention decision remain visible in both.”

## 3:50–4:22 — Robustness and scope

Show the adoption slide.

“Post-lock secondary analysis retained predictive value under a held-out NTP-to-ToxCast and ToxCast-to-NTP cohort shift without model retuning. This is not external laboratory or device transfer. The training data are rat cortical neural microelectrode-array assays, not organ-on-chip data. A new platform requires local retraining, recalibration, and prospective validation.”

## 4:22–4:45 — Close

Show the reproducibility slide and repository commands.

“MEACompass is not an automatic laboratory decision. It is an audited, reproducible path from early neural measurements to a forecast, calibrated uncertainty, and an honest option to wait. Forecast when evidence is strong; continue the assay when it is not.”
