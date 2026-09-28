# Sanity Gate S results

Run date: 2026-09-28  
Original preregistration: `8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0`  
Gate S deviation: `0623e48`  
Frozen Gate S implementation: `038afcb`  
Selected main model from Gate M1: M1

All confidence intervals use 1,000 canonical-chemical bootstrap draws. Negative
delta MAE is beneficial. BT+ is selected from B0/B1/B1b/B2 using inner validation
folds only.

## S1 — strongest-baseline comparison

| Model | Endpoint | MAE | BT+ MAE | Delta MAE vs BT+ [95% CI] | Gain vs BT+ |
|---|---|---:|---:|---:|---:|
| B3 | Bursts/min | 26.704 | 32.739 | -6.035 [-7.783, -4.243] | 18.43% |
| B3 | Mean firing rate | 40.519 | 45.792 | -5.273 [-7.584, -3.190] | 11.51% |
| B3 | Active electrodes | 28.930 | 33.504 | -4.574 [-12.623, 4.916] | 13.65% |
| B3 | Network spikes | 39.728 | 48.259 | -8.531 [-11.005, -5.844] | 17.68% |
| B3 | Coordinated activity (`r`) | 77.489 | 62.910 | 14.579 [-5.279, 40.208] | -23.17% |
| M1 | Bursts/min | 27.171 | 32.739 | -5.568 [-7.511, -3.769] | 17.01% |
| M1 | Mean firing rate | 39.295 | 45.792 | -6.497 [-11.589, -1.505] | 14.19% |
| M1 | Active electrodes | 20.423 | 33.504 | -13.082 [-17.472, -9.516] | 39.04% |
| M1 | Network spikes | 40.724 | 48.259 | -7.536 [-10.195, -4.558] | 15.62% |
| M1 | Coordinated activity (`r`) | 48.615 | 62.910 | -14.295 [-17.565, -11.049] | 22.72% |

The corresponding original-BT comparisons are preserved in
`results/gate_s_main.csv`; they are not substituted for the stronger headline
comparator.

## S2 — chemical-group permutation negative control

The seed-0 control permuted complete chemical target blocks inside each outer
training fold. Wells, doses, and replicates were not independently shuffled.

| Endpoint | Permuted B3 MAE | BT+ MAE | Delta MAE vs BT+ [95% CI] | Gain |
|---|---:|---:|---:|---:|
| Bursts/min | 32.318 | 32.843 | **-0.525 [-0.969, -0.136]** | 1.60% |
| Mean firing rate | 45.117 | 45.255 | -0.138 [-1.014, 0.753] | 0.30% |
| Active electrodes | 30.982 | 31.869 | -0.886 [-11.981, 11.358] | 2.78% |
| Network spikes | 48.224 | 48.375 | -0.151 [-0.816, 0.503] | 0.31% |
| Coordinated activity (`r`) | 78.028 | 62.910 | 15.118 [-5.434, 40.664] | -24.03% |

Bursts/min violates the registered negative-control rule. The magnitude is small,
but the beneficial interval excludes zero; therefore this gate stops immediately
with suspected leakage or residual confounding. Possible explanations must be
audited without changing the registered result: retained dose/cohort signal,
block-interpolation behavior, baseline-selection asymmetry, or an actual data-flow
leak. No explanation is assumed here.

## S3 — dose-stratified evaluation

Positive-dose tertiles were learned independently from each endpoint's outer
training fold and applied unchanged to that fold's test rows.

### M1 gain versus BT+

| Endpoint | Zero | Low | Mid | High |
|---|---:|---:|---:|---:|
| Bursts/min | -11.50% | 9.22% | 14.40% | 34.94% |
| Mean firing rate | -23.72% | 18.46% | 9.37% | 30.55% |
| Active electrodes | 33.40% | 43.10% | 40.31% | 34.41% |
| Network spikes | -8.16% | 8.12% | 11.65% | 38.31% |
| Coordinated activity (`r`) | 25.53% | 25.12% | 22.38% | 13.74% |

M1 has low/mid-dose signal; active electrodes and `r` have beneficial CIs in
both strata, while bursts/min has beneficial CIs in low and mid and network
spikes in mid. Firing has positive low/mid point estimates but intervals cross
zero. Full B3 and M1 stratum counts, errors, and CIs are in
`results/dose_strata.csv`.

## S4 — descriptive cohort robustness

| Model | Endpoint | NTP gain [CI status] | ToxCast gain [CI status] |
|---|---|---:|---:|
| B3 | Bursts/min | 18.99% beneficial | 18.17% beneficial |
| B3 | Mean firing rate | 17.57% beneficial | 9.37% beneficial |
| B3 | Active electrodes | 54.03% beneficial | -3.16% inconclusive |
| B3 | Network spikes | 18.24% beneficial | 17.41% beneficial |
| B3 | Coordinated activity (`r`) | 7.83% inconclusive | -31.98% inconclusive |
| M1 | Bursts/min | 18.13% beneficial | 16.48% beneficial |
| M1 | Mean firing rate | 15.33% beneficial | 13.78% inconclusive |
| M1 | Active electrodes | 48.18% beneficial | 35.24% beneficial |
| M1 | Network spikes | 16.33% beneficial | 15.28% beneficial |
| M1 | Coordinated activity (`r`) | 37.85% beneficial | 18.43% beneficial |

“Beneficial” means the corresponding delta-MAE CI in
`results/cohort_results.csv` excludes zero below zero. This is descriptive
within-cohort performance, not evidence of cross-cohort transfer.

## S5 — DIV5-only ablation

| Endpoint | DIV5-only MAE | Standard B3 MAE | DIV5-only gain vs BT+ [95% CI] |
|---|---:|---:|---:|
| Bursts/min | 30.923 | 26.704 | 5.55% [-2.571, -1.053 delta MAE] |
| Mean firing rate | 43.633 | 40.519 | 4.71% [-3.693, -0.757 delta MAE] |
| Active electrodes | 33.364 | 28.930 | 0.42% [-8.803, 9.742 delta MAE] |
| Network spikes | 44.761 | 39.728 | 7.25% [-4.704, -2.202 delta MAE] |
| Coordinated activity (`r`) | 78.325 | 77.489 | -24.50% [-4.357, 40.814 delta MAE] |

DIV5-only inputs retain modest signal for three endpoints, while DIV5+DIV7 is
better in point MAE for every endpoint. No DIV9 input was used.

## Gate decision

**FAIL / STOP — suspected leakage or residual confounding.** The real M1 clears
the fair-gain and low/mid-dose conditions, but the bursts/min permutation control
has a beneficial confidence interval excluding zero. Under the registered rule,
M2 and M3 must not start. No validated early-stop, calibration, or abstention
claim is made.
