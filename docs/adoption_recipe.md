# Local MEA evaluation and adaptation recipe

This is a schema and evaluation recipe for longitudinal MEA tables. It is not
evidence that the frozen EPA model can be deployed directly on a new chip. A new
laboratory, cell source, device, protocol, or endpoint definition requires local
validation and recalibration.

## 1. Map the local table

Map one row per plate, well, and DIV to `schemas/mea_input_v1.yaml`. Required
identity fields are chemical ID, dose, plate, well, and DIV. The five reference
endpoint fields are `burst.per.min`, `meanfiringrate`, `nAE`, `ns.n`, and `r`.
SMILES, cohort, and replicate are optional. Record dose units and local endpoint
definitions alongside the mapped table.

Do not silently rename a biologically different endpoint to match the schema. If
an endpoint cannot be harmonized, mark it not comparable and omit that endpoint
from claims.

## 2. Validate before modeling

Fail closed if plate/well/DIV keys are duplicated, required time points are
missing, dose units are mixed, or a plate/DIV lacks a zero-dose control. Inspect
missingness by endpoint, plate, DIV, chemical, and cohort. Confirm that every
feature available to the model existed at the intended decision time.

## 3. Normalize locally

Apply same-plate, same-DIV zero-dose percent-control normalization using only the
controls on that plate and DIV. Preserve raw values and normalization metadata.
If a control denominator is zero or invalid, stop for that endpoint rather than
inventing a replacement. Treat zero-dose performance as a separate diagnostic;
do not describe underperformance there as expected.

## 4. Evaluate chemical-disjoint generalization

Canonicalize aliases first. Use chemical ID as the group for every outer split,
inner split, and bootstrap. All concentrations, plates, wells, and replicates for
one chemical must remain together. Fit preprocessing, BT+/BT++ selection, model
settings, calibration residuals, and any acceptance threshold on outer-training
groups only. Outer-test labels are evaluation only.

Report every locally defined endpoint, including failures. At minimum report MAE,
the paired gain versus a locally selected simple baseline, a chemical-bootstrap
confidence interval, interval coverage, and a risk–coverage curve.

## 5. Calibrate and assess drift

Calibrate intervals from local training chemicals. Check empirical coverage by
plate, acquisition date, device, cohort, dose stratum, and endpoint. A coverage
shortfall requires local recalibration; it is not permission to widen or tune an
interval on the test labels. Compare feature ranges and missingness with the
training folds and flag extrapolation.

## 6. Validate prospectively

Freeze the full pipeline before the prospective run: mappings, exclusions,
features, baselines, model settings, intervals, acceptance policy, metrics, and
failure rules. Evaluate unseen chemicals and new acquisition batches without
retuning. A human reviews every proposed operational decision.

MEACompass remains a research decision-support workflow, not an autonomous
assay-termination system. Prospective validation is required before real
laboratory deployment.

## Minimum handoff artifacts

- the mapped table plus a data dictionary and source license;
- the validated schema version and mapping log;
- chemical-disjoint split assignments;
- training-only preprocessing and baseline-selection records;
- held-out predictions in `schemas/prediction_schema_v1.yaml` format;
- chemical-bootstrap and calibration diagnostics;
- a limitations log covering missingness, drift, and non-comparable endpoints;
- a frozen prospective-validation protocol.

