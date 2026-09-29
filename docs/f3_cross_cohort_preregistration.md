# F3 directional cross-cohort preregistration

Registered 2026-09-29 before running the post-lock secondary analysis. F3 is the
predeclared fallback because F3b was cut at the frozen-model availability gate.
It does not alter or replace the locked chemical-disjoint primary result.

## Question and directions

Train on one 2019 EPA NFA screening cohort and evaluate on the other:

1. ToxCast → NTP;
2. NTP → ToxCast.

This is a held-out cohort shift inside one EPA assay release. It is not external
laboratory, device, species, human, or organ-on-chip validation.

## Independence

Canonical CAS RN remains the chemical group. Any chemical appearing in both
cohorts is excluded from the target test cohort for that direction. All source
cohort rows remain eligible for training. The report must state source and target
row counts, source and target chemical counts, overlap chemicals excluded, and
eligible target chemicals.

## Frozen M1 settings

No hyperparameter search or target-cohort selection is allowed. The aggregation
rule already used by the bounded integrity audit is frozen: take the median of
the 15 preserved M1 tuning records for numeric parameters and the most frequent
variant and residual-baseline model, with deterministic lexical tie handling.

| Endpoint | Variant | BT component | Depth | Rate | Child weight | Column sample | Trees |
|---|---|---|---:|---:|---:|---:|---:|
| bursts/min | direct | B2 | 4 | 0.08 | 1 | 0.7 | 100 |
| firing rate | BT residual | B2 | 4 | 0.03 | 1 | 1.0 | 87 |
| active electrodes | BT residual | B2 | 4 | 0.03 | 1 | 0.7 | 47 |
| network spikes | direct | B2 | 4 | 0.03 | 1 | 1.0 | 86 |
| coordinated activity (`r`) | BT residual | B2 | 4 | 0.03 | 1 | 1.0 | 33 |

Three models are fitted per endpoint and direction using the locked random seeds
0, 1, and 2. Their target-cohort predictions are averaged before evaluation.
Model fitting uses only the source cohort.

## Features and targets

Inputs, targets, normalization, missingness handling, and feature-causality rules
are identical to locked M1. Inputs stop at DIV7; no DIV9 or DIV12 input is used.
The cohort indicator is retained for schema identity but is constant during
source-cohort fitting and therefore cannot be a learned split.

## Comparators

BT+ is the best of B0, B1, B1b, and B2 selected using three chemical-disjoint
folds inside the source cohort only. BT++ is the better of source-selected BT+
and fixed DOSE-SMOOTH, again selected using source-only chemical-disjoint folds.
Both selected comparators are fit on the full source cohort and applied unchanged
to the target. Target labels never select a model or parameter.

## Metrics and decision

For every direction and all five endpoints report target MAE, RMSE, Spearman,
BT+ and BT++ MAE, paired gain, relative gain, and 95% chemical-bootstrap intervals
for M1 minus each comparator. A directional endpoint win requires a negative
paired delta whose confidence interval excludes zero.

Classification:

- **PASS:** M1 beats BT++ on at least three endpoints in both directions.
- **MIXED:** at least one endpoint wins but PASS is not reached.
- **FAIL:** no endpoint wins in either direction, or a validity defect is found.

Allowed successful wording is limited to: “Retained predictive value under a
held-out NTP↔ToxCast cohort shift without model retuning.” This is not external
laboratory/device transfer.
