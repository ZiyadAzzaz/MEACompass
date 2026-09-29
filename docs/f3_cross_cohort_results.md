# F3 held-out cohort-shift results

## Gate report

**GATE: PASS**

F3 is a post-lock secondary analysis. With hyperparameters frozen before this
run, M1 retained predictive value under both held-out NTP↔ToxCast cohort shifts
without model retuning. This is not external laboratory/device transfer.

## Independence audit

| Direction | Source rows / chemicals | Target before exclusion | Shared chemicals excluded | Eligible target rows / chemicals |
|---|---:|---:|---:|---:|
| ToxCast → NTP | 2,832 / 97 | 1,440 / 50 | 11 | 1,032 / 39 |
| NTP → ToxCast | 1,440 / 50 | 2,832 / 97 | 11 | 2,496 / 86 |

All target conditions belonging to a CAS RN seen in the source cohort were
excluded before scoring. The endpoint-specific eligible counts are smaller where
the locked endpoint-construction rules remove incomplete records.

## Results versus source-selected BT++

Delta is `MAE(M1) − MAE(BT++)`; negative values favor M1. Confidence intervals
use the target chemical as the bootstrap unit.

| Direction | Endpoint | M1 MAE | BT++ MAE | Gain | Paired delta 95% CI |
|---|---|---:|---:|---:|---:|
| ToxCast → NTP | Firing rate | 30.60 | 46.69 | 34.5% | [−19.73, −12.55] |
| ToxCast → NTP | Bursts/min | 26.36 | 29.40 | 10.3% | [−5.25, −0.87] |
| ToxCast → NTP | Active electrodes | 20.28 | 30.39 | 33.3% | [−15.44, −4.67] |
| ToxCast → NTP | Network spikes | 38.04 | 42.78 | 11.1% | [−6.57, −2.74] |
| ToxCast → NTP | Coordinated activity (`r`) | 29.10 | 42.48 | 31.5% | [−18.24, −9.30] |
| NTP → ToxCast | Firing rate | 42.71 | 52.78 | 19.1% | [−19.35, −3.91] |
| NTP → ToxCast | Bursts/min | 28.42 | 33.84 | 16.0% | [−7.86, −3.12] |
| NTP → ToxCast | Active electrodes | 20.97 | 42.20 | 50.3% | [−38.27, −6.71] |
| NTP → ToxCast | Network spikes | 45.97 | 54.16 | 15.1% | [−11.74, −4.92] |
| NTP → ToxCast | Coordinated activity (`r`) | 59.31 | 92.35 | 35.8% | [−72.22, −1.80] |

All ten directional endpoint comparisons meet the preregistered win definition.
The smallest gain is 10.3%; the largest is 50.3%. These ranges are secondary and
must not replace the locked primary headline.

## Scientific status

The evidence supports only this wording:

> Retained predictive value under a held-out NTP↔ToxCast cohort shift without
> model retuning.

The two cohorts belong to the same 2019 EPA NFA release. The analysis does not
establish performance on new experiment dates, laboratories, recording devices,
species, human tissue, or organ-on-chip systems. F3b was later resumed under
Amendment B with deterministic final-refit models, but remained CUT because the
refinement release omitted required inputs and `r` failed its compatibility
threshold. No external refinement outcomes were scored.

## Reproduction

Run `make f3-cross-cohort PYTHON=<environment-python>`. Aggregate evidence is in
`results/f3_cross_cohort/`. Row-level secondary predictions remain ignored to
avoid publishing derived per-well data.
