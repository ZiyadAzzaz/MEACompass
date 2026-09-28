# Phase 3 reliability results: M2, M3, and L1

Date: 2026-09-28

The post-registration integrity audit passed as **RESIDUAL STRUCTURE UNDER NULL**.
The registered Gate S remains **FAIL / STOP** historically and its result files
remain unchanged. This report follows the audit-authorized continuation and shows
both the original BT+ and post-hoc BT++ comparators.

## BT++

BT++ is the better of BT+ and fixed DOSE-SMOOTH, selected only with
chemical-disjoint inner-validation rows. Outer-test outcomes never choose the
comparator. M1 remained significantly better on all five endpoints.

| Endpoint | M1 MAE | BT++ MAE | M1 gain vs BT++ | Delta MAE [95% CI] |
|---|---:|---:|---:|---:|
| Mean firing rate | 39.295 | 44.786 | 12.26% | -5.491 [-10.484, -0.212] |
| Bursts/min | 27.171 | 32.416 | 16.18% | -5.245 [-7.259, -3.406] |
| Active electrodes | 20.423 | 35.748 | 42.87% | -15.325 [-25.819, -7.751] |
| Network spikes | 40.724 | 47.473 | 14.22% | -6.750 [-9.484, -3.756] |
| Coordinated activity (`r`) | 48.615 | 66.025 | 26.37% | -17.410 [-24.507, -12.319] |

BT++ chose DOSE-SMOOTH in all 15 burst and network-spike tasks, 12/15 firing
tasks, 7/15 active-electrode tasks, and 1/15 `r` tasks. The mixed held-out
comparator can be worse than either aggregate candidate because selection is
strictly fold-local and never corrected using outer-test results.

## Gate M2 - calibration

Intervals use nested group-aware CV+: within each outer-training fold, three
chemical-disjoint inner models generate out-of-fold absolute residuals and
fold-specific predictions for the untouched outer test rows. Nominal coverage is
90%. No CQR switch was needed.

| Endpoint | Overall | NTP | ToxCast | Median width | Gate |
|---|---:|---:|---:|---:|---|
| Mean firing rate | 91.53% | 91.31% | 91.64% | 128.80 | PASS |
| Bursts/min | 91.08% | 91.98% | 90.62% | 108.91 | PASS |
| Active electrodes | 92.13% | 93.51% | 91.42% | 70.09 | PASS |
| Network spikes | 91.03% | 92.17% | 90.39% | 162.63 | PASS |
| Coordinated activity (`r`) | 92.40% | 96.38% | 90.36% | 136.40 | PASS |

**Gate M2: PASS (5/5 endpoints).** Every overall coverage lies inside 85-95%,
and every cohort is above 80%.

## Gate M3 - abstention

Predictions are ranked only by interval width; no DIV12 label is used to choose
acceptance. At 70% coverage, the narrowest 70% receive `EARLY DECISION POSSIBLE`;
the remainder receive `CONTINUE TO DIV12`. Confidence intervals resample complete
canonical chemical groups.

| Endpoint | Full MAE | 70% MAE | Risk reduction | Delta MAE [95% CI] | Endpoint result |
|---|---:|---:|---:|---:|---|
| Mean firing rate | 39.295 | 31.868 | 18.90% | -7.427 [-12.670, -3.369] | PASS |
| Bursts/min | 27.171 | 25.919 | 4.61% | -1.252 [-2.317, -0.422] | below 15% |
| Active electrodes | 20.423 | 16.750 | 17.98% | -3.672 [-5.352, -2.297] | PASS |
| Network spikes | 40.724 | 38.582 | 5.26% | -2.142 [-4.868, 0.034] | below 15%; CI crosses 0 |
| Coordinated activity (`r`) | 48.615 | 34.814 | 28.39% | -13.801 [-27.235, -4.592] | PASS with normalization caveat |

**Gate M3: PASS, mixed by endpoint (3/5 meet the full criterion).** Bursts show
a smaller statistically supported reduction; network spikes do not establish a
70%-coverage reduction. `r` passes the reliability criterion but retains the
pre-registered percent-control extreme-tail limitation, so it is not presented
without that caveat.

## Gate L1

**LOCK.** M1 is frozen as the main model. The project headline is
reliability-aware DIV7-to-DIV12 forecasting with calibrated abstention. The lock
does not rewrite the historical Gate S failure; it records the separately
authorized integrity-audit resolution.

## Section 9 report

PHASE: Reliability | GATE: M2 -> PASS; M3 -> PASS (3/5); L1 -> LOCK

HEADLINE NUMBER: at 70% accepted coverage, MAE falls 18.90% for firing rate,
17.98% for active electrodes, and 28.39% for `r`, with chemical-bootstrap CIs
excluding zero. Bursts and network spikes do not meet the 15% threshold.

COVERAGE / ABSTENTION: nominal-90% coverage is 91.03-92.40% overall across the
five endpoints; all cohort coverages exceed 90%. Accepted fraction is 70%.

DECISION: freeze M1 and the reliability protocol. Preserve BT+, BT++, all five
endpoints, the registered Gate S failure, and the `r` normalization limitation.

NEXT: required post-lock time ablation and practical-value artifacts, followed by
the offline Streamlit demo and reproduction gate.

NEED FROM YOU: none.
