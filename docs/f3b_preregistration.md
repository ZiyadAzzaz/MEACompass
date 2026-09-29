# F3b frozen external-validation preregistration

Registered 2026-09-29 before acquisition, harmonization, or scoring of external
outcomes. This is a post-lock secondary analysis and cannot change the locked
primary result.

## Source and permission boundary

- Source: `USEPA/CompTox-DNT-NFA-Refinement` at commit
  `01adf3e1a0068c87fe221d60df36b9f96c4b4b1d`.
- Only the explicit files in `results/f3b/source_manifest.csv` are eligible.
- A file is eligible only when it is in the official USEPA repository, the
  repository description or readme identifies it as NFA manuscript data or an
  analysis output, the commit author is EPA-affiliated or the repository
  attributes the work to the EPA manuscript team, and no third-party dataset
  with a separate stated license is included.
- Repository visibility is not a blanket reuse grant. Permission clarification
  was requested by email and GitHub issue on 2026-09-29.
- Raw files remain untracked and are never redistributed.

## Frozen model definition and availability gate

For each endpoint, an eligible external prediction is the arithmetic mean of
the 15 locked outer-fold M1 models: five folds for each of seeds 0, 1, and 2.
No model may be refit, reconstructed, retuned, or selected using the external
release. Before acquisition, every required serialized model must exist and its
SHA-256 must be recorded in a model manifest.

The current repository contains 75 endpoint/fold/seed tuning records and locked
out-of-fold predictions, but no serialized M1 model artifacts. Therefore the
availability gate currently fails. F3b scoring is **CUT** unless the exact
historical model artifacts are supplied and verified. Retraining an equivalent
model is not an acceptable substitute.

## Frozen comparators

BT+ and BT++ candidate definitions and their final selection rule are fixed from
the 2019 development release only. If F3b becomes eligible, candidate selection
is applied using all 2019 development data and no external values. No baseline
component is fitted, selected, or recalibrated on the external test set.

## Frozen intervals

The primary external interval uses the frozen 2019 CV+ residual pool and reports
zero-shot coverage. Any later local recalibration is labeled secondary, uses a
separate calibration subset, and is never mixed with zero-shot results.

## Inclusion and chemical independence

External test conditions must have both an experiment date absent from the 2019
release and a canonical CAS RN absent from all 2019 development data. Conditions
are excluded by CAS and by plate/date. The audit must report total external
conditions, CAS overlaps excluded, plate/date overlaps excluded, and unique
eligible chemicals remaining.

## Time, endpoint, and control mapping

- Inputs are the same DIV5 and DIV7 variables used by locked M1; DIV9 and DIV12
  inputs remain forbidden.
- Targets are the same five DIV12 endpoints: mean firing rate, bursts per minute,
  active electrodes, network spikes, and coordinated activity (`r`).
- Values use the locked percent-of-same-plate, same-DIV zero-dose-control
  transform. No external normalization change is permitted without a declared
  overlap-only mapping.
- Chemical identifiers are canonicalized to CAS RN before overlap exclusion.
- Missing values follow the locked M1 missingness-indicator contract. No external
  outcome-based imputation is permitted.

## Harmonization gate

Recordings present in both releases are matched by plate, well, and DIV and are
used only for harmonization, never as external test observations. For every
required M1 input feature and each endpoint, report Spearman correlation, median
new/old ratio, and missingness rates in both releases.

- `EXACT/COMPATIBLE`: Spearman at least 0.95 and median ratio from 0.9 to 1.1.
- `MAPPED`: a prespecified monotone mapping is fitted only on overlapping
  recordings and logged as a deviation.
- `NOT COMPARABLE`: thresholds fail and no defensible overlap-only mapping exists.

If any required input is `NOT COMPARABLE`, the affected endpoint is not scored.
No mapping may use new-chemical test conditions.

## Metrics and uncertainty

Eligible endpoints report MAE, RMSE, Spearman correlation, paired gain versus
BT+ and BT++, and a 95% paired chemical-level bootstrap confidence interval.
Zero-shot interval coverage and width are reported at nominal 90% coverage.
M3 risk reduction is evaluated at the frozen 70% retained coverage rule. Results
are also reported by experiment date where sample size permits.

## Interpretation rule

- **STRONG:** gain versus BT++ has a confidence interval excluding zero on at
  least three comparable endpoints, with no material provenance, leakage, or
  calibration problem.
- **MIXED:** some endpoints retain value while others degrade, or interval
  calibration shifts.
- **FAIL:** little or no predictive value is retained.
- **CUT:** provenance, model availability, or harmonization prevents a valid
  evaluation.

No outcome can support claims of human transfer, direct organ-on-chip validation,
new-laboratory/device transfer, or deployment readiness.
