# Gate S post-registration integrity audit

Audit date: 2026-09-28

Audit result: **PASS - RESIDUAL STRUCTURE UNDER NULL**

Registered Gate S: **FAIL / STOP - unchanged**

This is a bounded post-registration diagnostic audit. It does not replace, edit,
or invalidate the registered Gate S result. All diagnostic artifacts are under
`results/audit/`; registered data, predictions, results, and checkpoints were not
modified.

## Decision summary

All six audit PASS conditions were met:

1. No feature, target, group, or outer-test leakage path was found.
2. The full well-level shuffle had no beneficial confidence interval on any endpoint.
3. For bursts/min, DOSE-SMOOTH gained 0.99% over BT+ and the registered S2 null
   gained 1.60%; their paired comparison was compatible with no difference
   (S2 minus DOSE-SMOOTH delta MAE -0.182, 95% CI [-0.604, 0.221]).
4. Real M1 beat DOSE-SMOOTH with a beneficial chemical-bootstrap interval on all
   five endpoints.
5. Real M1's gain exceeded every one of 20 repeated M1 chemical-block null runs
   on all five endpoints.
6. There were zero null exceedances for every endpoint. With 20 runs this is
   reported as empirical **p < 0.05**, not p = 0.

The evidence supports retained, expected trajectory structure under the registered
block null rather than implementation leakage. Per the authorized rule, M2/M3 may
resume only after preserving this report and adding the post-hoc BT++ comparator.

## A1 - exact registered S2 mechanism

For each seed-0 outer fold and endpoint, the implementation first filters to rows
with an available endpoint, then sorts canonical CAS groups and creates a seeded
derangement. A recipient chemical A receives donor B's complete outer-training
`target12` block. Both blocks are sorted by `dose`, `Plate.SN`, and `well`; donor
values are mapped to recipient rows by equally spaced rank quantiles using linear
interpolation.

It does **not** match absolute dose, cohort, plate, well, or concentration labels.
It preserves only ordered trajectory position. Replicates are individual sorted
rows. If row counts differ, the donor sequence is linearly resampled to the
recipient count; if dose grids or replicate counts differ, no direct dose/replicate
match is attempted. Endpoint availability determines which rows and chemicals
enter each endpoint-specific mapping. Outer-test targets are never changed.

Concrete fold-0 bursts/min example: recipient `105512-06-9` (24 rows: eight doses
with three replicates each) receives donor `208-96-8` (40 rows: the same eight dose
levels with five replicates each). The 40 donor targets, ordered by dose/plate/well,
are interpolated at 24 evenly spaced positions and assigned to the recipient's 24
ordered rows. Thus dose rank and generic response-curve shape can survive even
though chemical identity and exact row correspondence do not.

## A2 - feature and data-flow audit

The machine-readable lineage is in `results/audit/feature_lineage.csv`:

- B3 has 74 inputs: 36 raw DIV5/DIV7 neural measurements, 36 corresponding
  missingness indicators, log-dose, and a fixed cohort indicator.
- M1 has those 74 inputs plus 16 deterministic RDKit descriptors, a 2,048-bit
  Morgan fingerprint, and one missing-structure indicator: 2,139 inputs total.
- No DIV9/DIV12 measurement, DIV12 control-derived value, EC50/potency, activity
  label, hit call, or late viability value enters `X`.
- There are no learned imputers, scalers, encoders, or plate-level aggregates.
  XGBoost handles missing values natively; dose/cohort encodings and RDKit features
  are fixed row-local or structure-local transforms. No outer-test target statistic
  is computed.
- Canonical CAS is the split group. Automated checks verify chemical disjointness,
  trajectory disjointness, forbidden future-feature rejection, derangement without
  index realignment, and full-shuffle reproducibility.

The residual M1 variant may use a B2 prediction fitted on the corresponding
training fold. B2's prediction is expressed in the registered target units, but no
DIV12 value is placed in `X`; this registered residual target construction is
fold-local and was explicitly audited. No leaking path was found.

## B - frozen permutation verification

The registered S2 mappings were reconstructed exactly from code and matched all 25
stored tuning records. Every endpoint/fold mapping changed 100% of chemical groups
(96-110 groups depending on fold/endpoint), exceeding the 95% requirement. There
were zero self-maps. Training-target correlations ranged from -0.0036 to 0.3013;
every mapping has a SHA-256 checksum in `results/audit/permutation_mapping.csv`.
Outer-test targets were untouched, and one-to-one key validation prevents a merge
from silently restoring original targets.

## A3 - B3 versus M1 and the `r` endpoint

B3 is direct XGBoost on early neural features, missingness, dose, and cohort. M1
adds chemistry and, inside inner chemical-disjoint CV, selects either direct DIV12
prediction or a residual over B2. Both use the same XGBoost hyperparameter grid;
M1 additionally searches the two target variants. Diagnostics did not retune:
M1 used medians/modes from 75 preserved M1 selections. Because historical original
B3 per-fold selections were not preserved, fixed B3 settings use medians from the
25 preserved registered S2 tuning records; this reproducibility gap is explicit.

For `r`, B3 MAE was 77.49, chemistry-only B4 was 77.64, and M1 was 48.61. All 15
M1 `r` folds selected residual-over-B2, so chemistry alone does not explain the
jump. The percent-control `r` target is highly unstable (median 91.69, maximum
12,452.42), making B2 anchoring especially consequential. The clean feature audit
and full shuffle do not support leakage; the result is best described as a
combination of complementary early/chemistry information and residual anchoring
under a pathological normalization tail. `r` remains an explicit limitation and
was not redefined.

## C - fixed diagnostic models

All diagnostics used the same frozen outer splits and seeds 0/1/2. DOSE-SMOOTH used
only log-dose, cohort, and missing-structure. FULL-SHUFFLE permuted `target12`
across every outer-training well, ignoring chemical, dose, and cohort. Neither was
retuned.

| Endpoint | DOSE-SMOOTH gain vs BT+ | Full-shuffle gain vs BT+ | Full-shuffle delta MAE [95% CI] |
|---|---:|---:|---:|
| mean firing rate | 2.26% | 0.93% | -0.427 [-1.625, 0.724] |
| bursts/min | 0.99% | -4.49% | 1.469 [0.744, 2.216] |
| active electrodes | 6.85% | 5.30% | -1.775 [-11.105, 8.404] |
| network spikes | 1.63% | -1.21% | 0.584 [-0.329, 1.419] |
| coordinated activity (`r`) | -22.37% | -22.26% | 14.002 [-6.076, 38.757] |

The full-shuffle control is clean: no beneficial confidence interval excludes zero.

## C3 - repeated chemical-block null

Twenty documented seeds (`20360931` through `22260988`, step 100,003) were run for
both fixed B3 and fixed M1 across all three split/model seeds. The full per-run
table is `results/audit/block_permutation_null.csv`.

| Model / endpoint | Mean gain | SD | 2.5% | Median | 97.5% | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| B3 / firing | 1.80% | 0.22 | 1.34% | 1.87% | 2.06% | 2.07% |
| B3 / bursts | 0.96% | 0.60 | -0.02% | 1.00% | 2.02% | 2.06% |
| B3 / active electrodes | 6.08% | 0.90 | 4.16% | 6.29% | 7.09% | 7.15% |
| B3 / network spikes | 0.39% | 0.46 | -0.28% | 0.32% | 1.23% | 1.56% |
| B3 / `r` | -11.70% | 2.33 | -16.79% | -11.52% | -7.72% | -7.18% |
| M1 / firing | 3.33% | 2.89 | -3.55% | 3.95% | 6.72% | 7.14% |
| M1 / bursts | -2.85% | 1.03 | -4.67% | -2.80% | -1.37% | -1.25% |
| M1 / active electrodes | 3.91% | 3.45 | -0.74% | 3.47% | 10.56% | 11.49% |
| M1 / network spikes | -2.18% | 1.36 | -4.82% | -1.90% | -0.19% | -0.18% |
| M1 / `r` | -1.49% | 4.27 | -7.19% | -1.52% | 4.36% | 4.62% |

## D - baseline asymmetry

For the exact registered seed-0 burst rows, permuted B3's delta MAE was -0.525
against both B0 and BT+ because inner validation selected B0 there. It also beat
B1 (-35.060), B1b (-163.163), and B2 (-13.447), with beneficial intervals. Against
DOSE-SMOOTH it was only -0.182 with CI [-0.604, 0.221]. Therefore the 1.60% result
is not a BT+ selection artifact or outer-test selection advantage. BT+ provenance
remains `inner_validation_mae_only`; outer-test results never select it.

## E - bursts/min residual-signal decomposition

These fixed B3 diagnostics used the registered block mapping. P1 was early neural
features only; P2 dose+cohort; P3 early+dose; P4 early+cohort; P5 full B3.

| Variant | Gain vs BT+ | Delta MAE [95% CI] |
|---|---:|---:|
| P1 early neural only | 2.45% | -0.803 [-1.597, -0.031] |
| P2 dose + cohort only | -0.13% | 0.044 [-0.183, 0.277] |
| P3 early + dose | 1.46% | -0.478 [-0.783, -0.202] |
| P4 early + cohort | 2.22% | -0.726 [-1.510, 0.039] |
| P5 full B3 | 1.27% | -0.416 [-0.718, -0.131] |

The retained null signal is primarily carried by early neural trajectory structure.
Because donor targets are assigned by ordered trajectory rank, generic dose-response
shape remains learnable even without an explicit dose column. Cohort alone is not
required, and explicit dose does not increase the early-only effect.

## F - real effect versus null

Negative M1-minus-DOSE-SMOOTH delta MAE is beneficial.

| Endpoint | Real B3 gain vs BT+ | Real M1 gain vs BT+ | M1 - DOSE-SMOOTH delta MAE [95% CI] | Registered S2 null gain | M1 block-null 97.5% / max | Full-shuffle gain | Empirical p |
|---|---:|---:|---:|---:|---:|---:|---:|
| mean firing rate | 11.51% | 14.19% | -5.463 [-10.551, -0.215] | 0.30% | 6.72% / 7.14% | 0.93% | <0.05 |
| bursts/min | 18.43% | 17.01% | -5.245 [-7.259, -3.406] | 1.60% | -1.37% / -1.25% | -4.49% | <0.05 |
| active electrodes | 13.65% | 39.04% | -10.788 [-22.173, -1.337] | 2.78% | 10.56% / 11.49% | 5.30% | <0.05 |
| network spikes | 17.68% | 15.62% | -6.750 [-9.484, -3.756] | 0.31% | -0.19% / -0.18% | -1.21% | <0.05 |
| coordinated activity (`r`) | -23.17% | 22.72% | -28.368 [-52.988, -8.621] | -24.03% | 4.36% / 4.62% | -22.26% | <0.05 |

Real M1 is separated from exposure-only, repeated chemical-block, and full-shuffle
controls on all five endpoints. This supports the audit classification; it does
not erase the registered failure or the stated `r` limitation.

## Reproduction

The audit implementation is `meacompass/integrity_audit.py`; regression tests are
in `tests/test_integrity_audit.py`. Required outputs are:

- `results/audit/feature_lineage.csv`
- `results/audit/permutation_mapping.csv`
- `results/audit/full_shuffle.csv`
- `results/audit/dose_smooth.csv`
- `results/audit/block_permutation_null.csv`
- `results/audit/real_vs_null.csv`

Supporting diagnostics are `baseline_asymmetry.csv` and `decomposition.csv` in the
same directory. Large per-task audit checkpoints remain ignored and reproducible.
