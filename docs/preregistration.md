# NeuroChip-Twin Phase 2 pre-registration

Frozen: 2026-09-28, before any predictive model result  
Protocol version: 1.0  
Commit: recorded in `docs/decisions.md` and every subsequent result report

Any change after this document's frozen commit is a deviation. Deviations must be
dated, justified without reference to outer-test improvement, and reported beside
the affected result.

## Scientific question

For chemicals never seen during training, can measurements available at DIV5 and
DIV7 predict DIV12 network function better than carrying DIV7 forward, and does
uncertainty identify cases whose early prediction is unsafe?

The source is a rat cortical neural microelectrode-array assay. It is not described
as organ-on-chip data.

## Units, grouping, and eligibility

- Prediction unit: one `(cohort, plate, well)` longitudinal trajectory.
- Chemical group: canonical cleaned CAS RN.
- All aliases, concentrations, wells, plates, and biological replicates associated
  with one CAS RN remain in one outer fold.
- Primary analysis requires observed DIV5, DIV7, and DIV12 rows.
- An endpoint is eligible when its DIV12 value and matched plate-control median are
  finite and the control median is strictly positive.
- All models for an endpoint are compared on the same eligible outer-test rows.
- No complete-case removal is applied to input features. Missing input values are
  preserved and accompanied by explicit `<feature>_missing` indicators.

## Primary endpoints

The following five columns cover the pre-specified functional families and agree
with the parameters identified in Shafer et al. (2019):

| Family | Raw column |
|---|---|
| Firing | `meanfiringrate` |
| Bursting | `burst.per.min` |
| Active electrodes | `nAE` |
| Network spikes | `ns.n` |
| Coordinated activity | `r` |

The remaining raw parameters are secondary and will appear only in an appendix.

## Control matching and primary target

For each `(cohort, plate, DIV, endpoint)`, the matched control is the median across
all dose-zero wells on that plate at that DIV. The raw files label dose-zero wells
under individual treatments; no literal DMSO treatment is assumed.

Primary target for endpoint `e`:

`target12_e = 100 * raw12_e / plate_zero_median12_e`

The few plate-endpoint cases with a non-positive DIV12 denominator are undefined
and excluded for that endpoint. The exclusion rule is determined before folds and
does not use chemical activity or model output.

The change target is:

`delta_e = target12_e - target7_e`

where `target7_e` is defined analogously. Rows with a non-positive DIV7 control
denominator are excluded from the common comparison set for that endpoint.

Robustness outcomes:

- `log1p(raw12_e)` for nonnegative endpoints;
- raw `r` for coordinated activity;
- percent-control results stratified by cohort.

DIV12 control values define the target/scoring units only. They are never model
features, never used in imputation, and never used to select a prediction.

## Time-causal feature contract

The primary feature view may contain only:

- raw DIV5 and DIV7 values for all 18 network columns;
- a missingness flag for every DIV-feature pair;
- `log10(1 + dose_uM)`;
- cohort encoded from the training data;
- optional chemistry descriptors derived from structure alone.

Forbidden primary inputs include any DIV9 value, DIV12 value, DIV12 control value,
EC50, activity/hit label, viability outcome measured at DIV12, and any summary
computed using future rows. The later time-ablation experiment is a separately
labelled protocol that may add DIV9.

## Splits

- Outer evaluation: five-fold `StratifiedGroupKFold`, grouping by canonical CAS RN
  and stratifying rows by cohort, repeated with seeds 0, 1, and 2.
- Inner selection: three-fold `StratifiedGroupKFold` on each outer-training set,
  grouped by canonical CAS RN with the outer seed.
- Primary estimates aggregate predictions from the five outer held-out folds.
- Every reported fold must pass a zero-overlap assertion on canonical CAS RN.
- Plate-disjoint and Bemis–Murcko-scaffold-disjoint evaluations are secondary
  stress tests, not replacements for chemical-disjoint evaluation.

All transformations, imputation, scaling, hyperparameter selection, calibration,
and conformal residual estimation are fit without access to the corresponding
outer-test chemicals.

## Models fixed before results

- **B0:** training-fold mean target within training-derived dose bins. Dose bins
  are quantiles of `log10(1+dose)` fit on the training fold; empty test bins fall
  back to the training endpoint mean.
- **B1:** DIV7 percent-of-matched-DIV7-control carried forward.
- **B1b:** B1 multiplied by the training-fold median raw zero-dose growth ratio
  from DIV7 to DIV12 for the endpoint. Ratios with non-positive DIV7 controls are
  omitted when fitting this scalar.
- **B2:** `raw7 + alpha * (raw7 - raw5)`, with one `alpha` fit per endpoint by
  least absolute error on the training fold. The predicted raw DIV12 value is
  converted to primary target units using the row's DIV12 target denominator only
  at scoring time. `alpha` candidates are fixed at
  `[-1, -0.5, 0, 0.5, 1, 1.5, 2, 3]`.
- **B3:** XGBoost using DIV5/DIV7 network features, missing flags, dose, and
  cohort.
- **B4:** XGBoost using RDKit descriptors, Morgan fingerprint (2,048 bits),
  missing-structure flag, dose, and cohort.
- **M1:** XGBoost using the union of B3 and B4 inputs. Direct-target and
  best-trivial-residual variants are selected only by inner CV.

The XGBoost grid has at most 16 configurations per endpoint:

- `max_depth`: 2 or 4;
- `learning_rate`: 0.03 or 0.08;
- `min_child_weight`: 1 or 5;
- `subsample`: 0.8;
- `colsample_bytree`: 0.7 or 1.0;
- `n_estimators`: 400 with early stopping decided inside training/validation data;
- objective: squared error;
- `n_jobs`: CPU-limited and recorded.

No MLP, transformer, or test-fold tuning is permitted in Phase 2.

## Best trivial baseline

For each endpoint and outer fold, the best trivial baseline (BT) is selected among
B1, B1b, and B2 using inner-fold MAE only. The selected baseline is then refit on
the complete outer-training set and evaluated once on the outer-test set.

## Metrics

Reported per endpoint:

- MAE and RMSE on `target12`;
- Spearman correlation on `target12`;
- MAE and Spearman correlation on `delta`;
- paired `delta_MAE = MAE(model) - MAE(BT)`;
- relative MAE gain `100 * (MAE(BT)-MAE(model))/MAE(BT)`.

If either vector is constant, Spearman is undefined and remains `NaN`; it is not
changed to zero. Aggregate conclusions count only defined correlations.

Confidence intervals use 1,000 chemical-level bootstrap draws with seed 20260928.
Each draw resamples canonical CAS groups with replacement and retains every row of
each sampled group. Wells are never independently bootstrapped. The interval is
the 2.5th–97.5th percentile.

## Uncertainty and abstention

- Primary interval: group-aware CV+ using residuals generated out-of-fold at the
  chemical level.
- Nominal coverage: 90%.
- Required reporting: overall coverage, NTP coverage, ToxCast coverage, and median
  interval width.
- If overall coverage is outside 85–95% or either cohort is below 80%, one
  pre-specified switch to conformalized quantile regression is allowed.
- Abstention ranks test predictions by interval width. Thresholds are selected
  without outer-test labels.
- Risk–coverage reporting: accepted-case MAE at 100%, 90%, 80%, 70%, and 60%
  coverage, plus area under the risk–coverage curve.

The operational verdict is `EARLY DECISION POSSIBLE` below the selected interval-
width threshold and `CONTINUE TO DIV12` otherwise.

## Gates fixed before results

### B2 — learned signal beyond trivial baselines

- **Strong:** B3 has at least 5% relative MAE gain, paired chemical-bootstrap CI
  for delta-MAE excludes zero in the beneficial direction, and delta Spearman is
  at least 0.20 on at least three of five endpoints.
- **Weak:** positive gain on at least three endpoints but the strong criteria are
  not satisfied. One feature-pack retry is allowed: DIV5→7 slope, same-plate DIV7
  control ratio, within-plate rank, and missing-count features.
- **None:** B3 is not better than BT on at least four endpoints.

### M1 — chemistry value

- Keep M1 if it beats B3 or BT with a paired chemical-bootstrap CI excluding zero
  on at least three endpoints.
- If M1 ties B3, deploy B3 and report no measured chemistry benefit.
- If M1 is worse, chemistry is an ablation only.

### M2 — calibration

- Pass when 90% intervals achieve 85–95% overall coverage and at least 80% in
  each cohort.

### M3 — abstention

- Headline pass when accepted-case MAE at 70% coverage is at least 15% below the
  100% coverage MAE and the paired chemical-bootstrap CI excludes zero.

### Kill condition

If B3 and M1 fail to improve on BT, delta Spearman is below 0.20, classification
AUROC is below 0.60 when a verified official hit label is available, and
abstention does not lower risk, NeuroChip receives a FAIL flag at Gate L1. No
automatic pivot or test-set tuning is allowed.

## Reporting and claims

- Every headline reports skill relative to BT on unseen chemicals.
- “Potentially enabling earlier assay decisions” is allowed only with the measured
  accepted fraction and error beside it.
- No assay-time or cost-saving percentage is claimed without measurement and
  stated assumptions.
- “Digital twin” remains subtitle/future-direction language unless the optional
  trajectory model beats all pre-registered trivial baselines at every horizon.
- Negative findings and deviations are reported.
