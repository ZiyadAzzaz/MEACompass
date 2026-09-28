# Post-lock time ablation and practical value

Date: 2026-09-28

This is a post-L1 analysis. The DIV9 branch does not alter Gate S, M1, M2, or M3.
All three windows use frozen M1 task settings and chemical-disjoint outer folds;
the DIV5 and DIV9 intervals repeat the same nested group-CV+ procedure used at
DIV7.

## Accuracy gained per observation day

| Endpoint | DIV5 MAE / gain vs BT+ | DIV7 MAE / gain | DIV9 MAE / gain |
|---|---:|---:|---:|
| Mean firing rate | 46.364 / -1.25% | 39.295 / 14.19% | 34.410 / 24.86% |
| Bursts/min | 32.391 / 1.06% | 27.171 / 17.01% | 23.583 / 27.97% |
| Active electrodes | 27.659 / 17.45% | 20.423 / 39.04% | 16.672 / 50.24% |
| Network spikes | 45.779 / 5.14% | 40.724 / 15.62% | 37.282 / 22.75% |
| Coordinated activity (`r`) | 58.826 / 6.49% | 48.615 / 22.72% | 48.736 / 22.53% |

Waiting from DIV7 to DIV9 improves MAE for four endpoints; `r` does not improve.
DIV7 is the earliest window with substantial gain across all five endpoints.

## Calibration and fixed-threshold abstention

All windows retain nominal-90% interval coverage near 91-93%. To make abstention
rates comparable, each endpoint's DIV7 70th-percentile width is frozen as the
threshold and applied unchanged to DIV5 and DIV9.

| Endpoint | DIV5 abstain | DIV7 abstain | DIV9 abstain | DIV9 accepted MAE |
|---|---:|---:|---:|---:|
| Mean firing rate | 100.00% | 29.97% | 7.10% | 27.280 |
| Bursts/min | 100.00% | 30.00% | 2.74% | 22.502 |
| Active electrodes | 100.00% | 30.00% | 4.51% | 13.470 |
| Network spikes | 93.65% | 30.00% | 6.66% | 35.278 |
| Coordinated activity (`r`) | 100.00% | 30.00% | 29.29% | 35.241 |

The day-5 result is an honest negative finding: under the reliability threshold
chosen for day 7, almost every day-5 prediction is too uncertain. DIV9 sharply
widens eligibility for four endpoints but not `r`.

## Practical value at DIV7

At the frozen 70%-coverage operating point, approximately 70% of held-out
prediction instances receive `EARLY DECISION POSSIBLE`; approximately 30% receive
`CONTINUE TO DIV12`. Accepted-case MAE is reported separately for every endpoint:

| Endpoint | Accepted | Accepted MAE | Full MAE |
|---|---:|---:|---:|
| Mean firing rate | 70.03% | 31.862 | 39.295 |
| Bursts/min | 70.00% | 25.919 | 27.171 |
| Active electrodes | 70.00% | 16.750 | 20.423 |
| Network spikes | 70.00% | 38.583 | 40.724 |
| Coordinated activity (`r`) | 70.00% | 34.814 | 48.615 |

For an accepted prediction, a DIV7 decision is five calendar assay days earlier
than DIV12, or 5/12 = 41.7% of the stated assay duration. Averaged over the 70%
accepted fraction, that is approximately 3.5 decision-days per prediction. This
is not a measured monetary saving and no cost claim is made.

This remains a research decision-support result, not an autonomous termination
rule. Prospective validation is required before a laboratory changes an assay.
The source data are rat cortical neural MEA assays, not organ-on-chip experiments.

Machine-readable results are `results/time_ablation.csv` and
`results/practical_value.csv`.
