# F3b Amendment B: final-refit external-validation preregistration

Registered on 2026-09-29 before fetching, opening, harmonizing, or scoring any
refinement-release file under Amendment B. This protocol supersedes only the old
prohibition on refitting. F3b remains post-lock secondary evidence and cannot
change the locked primary analysis, endpoints, splits, predictions, or claims.

## Data firewall and registration commit

No refinement bytes may be fetched until this document, the deterministic final
settings, source manifest, harmonization contract, and executable final-model
code are committed. The registration commit SHA is recorded here immediately
after that commit. External outcomes never select a feature, parameter, model,
comparator, residual, interval, threshold, mapping, or endpoint.

Registration commit: **PENDING THIS COMMIT**

## Deterministic final M1

For each endpoint, the 15 locked outer-fit configurations (five outer folds ×
seeds 0/1/2) in `results/m1_tuning.json` are aggregated without external data:

- registered-grid numeric parameters: median, then nearest allowed grid value;
  an exact-distance tie chooses the smaller value;
- `n_estimators`: median, then `floor(x + 0.5)`, minimum one;
- categorical parameters (`variant`, residual baseline): mode; a count tie uses
  lexical JSON order;
- final training uses every eligible 2019 development chemical and seeds 0, 1,
  and 2; the external prediction is the arithmetic mean of the three seed
  predictions.

The frozen settings in `schemas/final_model_hyperparameters.json` are:

| Endpoint | Variant | Residual baseline | Depth | Learning rate | Min child | Column sample | Trees |
|---|---|---|---:|---:|---:|---:|---:|
| Bursts/min | direct | B2 | 4 | 0.08 | 1 | 0.7 | 100 |
| Mean firing rate | BT residual | B2 | 4 | 0.03 | 1 | 1.0 | 87 |
| Active electrodes | BT residual | B2 | 4 | 0.03 | 1 | 0.7 | 47 |
| Network spikes | direct | B2 | 4 | 0.03 | 1 | 1.0 | 86 |
| Coordinated activity (`r`) | BT residual | B2 | 4 | 0.03 | 1 | 1.0 | 33 |

The feature contract is unchanged: DIV5/DIV7 neural measurements and missingness
flags, log10(1+dose), cohort, 16 RDKit descriptors, 2,048 Morgan bits at radius
two, and a structure-missing flag. DIV9/DIV12 measurements, late viability,
potency, and outcome-derived features are forbidden. `make final-model` saves the
feature order, descriptor configuration, seed metadata, training chemical list,
models, baseline parameters, package versions, and SHA-256 hashes.

## Final BT+, BT++, calibration, and abstention

For each endpoint and seed, BT+ is selected from B0/B1/B1b/B2 by three-fold
chemical-group validation on all eligible 2019 data, then fitted on all eligible
2019 rows. BT++ compares that BT+ with the fixed dose-smooth candidate by the
registered three-fold chemical-group validation rule on 2019 data only. Ties
select BT+. The external set never selects or fits a comparator. Three seed
predictions are averaged for each final comparator.

The external zero-shot calibration pool is the 2019 locked chemical-disjoint
outer-fold M1 prediction set, averaged across seeds per sample. For each endpoint,
the absolute-residual quantile uses the finite-sample rank
`ceil((n + 1) × 0.90)`, capped at `n`. The external nominal-90% interval is the
final three-seed mean prediction plus/minus that frozen residual quantile. This is
a grouped out-of-fold conformal residual pool derived from the locked CV design;
it is not recalibrated on external outcomes.

The frozen abstention uncertainty is the standard deviation across the three
final seed predictions. The endpoint threshold is the 70th percentile (`higher`
quantile) of seed disagreement in the 2019 out-of-fold ensemble. External cases
at or below that threshold are accepted. Any recalibration is a separately
labelled secondary analysis and requires a chemical-disjoint external calibration
partition that does not overlap final external test chemicals.

## Source and reuse boundary

- Repository: `USEPA/CompTox-DNT-NFA-Refinement`.
- Pinned commit: `01adf3e1a0068c87fe221d60df36b9f96c4b4b1d`.
- Only files explicitly marked `allowed_for_analysis=YES` in
  `results/f3b/source_manifest.csv` may be fetched.
- Eligibility requires the official USEPA repository, README/manuscript
  attribution to EPA NFA data or analysis output, EPA-affiliated authorship or
  EPA-team attribution, and no stated third-party dataset license.
- Repository ownership is not a blanket license. The 17 U.S.C. §105 rationale is
  used only where file-level EPA/U.S. Government provenance supports it.
- The permission clarification requested by email and GitHub issue on
  2026-09-29 remains recorded. If EPA later denies the intended use, F3b is
  removed from public materials.
- Raw refinement files remain ignored and are never committed or redistributed.

## Controlled fetch and integrity

The fetcher uses the pinned commit and explicit manifest allowlist only. It does
not clone or ingest the repository recursively. The first authorized fetch
records SHA-256 for every file. Subsequent bytes must match; a mismatch fails
closed and never overwrites the local file automatically.

## External inclusion and independence

CAS identifiers are normalized conservatively and aliases require an explicit
mapping. The final external test set contains only chemicals absent from the
entire 2019 development release and conditions from experiment dates absent from
that release. Rows are excluded for any CAS, plate, date, batch, well, or record
overlap. The audit reports total chemicals and rows, development overlaps,
duplicate records, excluded plates/dates/batches, and external-only chemicals and
rows remaining. Overlap recordings may be used for harmonization only and never
for scoring.

## Frozen harmonization contract

`schemas/f3b_harmonization_v1.yaml` fixes the expected identity mapping for all
18 neural measurements and the five endpoints. Inputs use DIV5 and DIV7; targets
use DIV12. Values use the same-plate, same-DIV zero-dose percent-control transform.
No test-outcome-aware normalization, imputation, or mapping is allowed.

For recordings present in both releases, every required input and endpoint is
classified using Spearman correlation, median new/old ratio, and missingness:

- `EXACT`: same declared name, semantics, units/scale, and transform;
- `COMPATIBLE_WITH_FROZEN_TRANSFORM`: Spearman ≥0.95 and ratio 0.9–1.1 after the
  frozen transform;
- `MAPPED`: only a predeclared monotone mapping fitted on overlap recordings;
- `NOT_COMPARABLE`: thresholds or semantics fail and no defensible overlap-only
  mapping exists.

An endpoint is scored only when every feature required by its final M1 input and
the endpoint itself is comparable. Equivalence is never forced.

## Scoring, confidence intervals, and classification

For every comparable endpoint report M1 MAE, RMSE, Spearman, BT+ MAE, BT++ MAE,
relative gains, paired ΔMAE, and a 1,000-draw paired chemical bootstrap 95% CI
using seed 20260928. Also report nominal-90% zero-shot coverage and the frozen
70%-policy risk/coverage result when valid. Results are shown by experiment date
when sample size permits.

- **STRONG:** significant gain versus BT++ on at least three comparable
  endpoints, chemical independence, acceptable zero-shot calibration, and no
  provenance or validity defect.
- **MIXED:** some predictive value remains but effects vary or coverage degrades.
- **FAIL:** frozen external performance does not establish useful transfer.
- **CUT:** provenance, final-model construction, harmonization, or data validity
  prevents a defensible test.

The strongest allowed wording is: “Post-lock external evaluation on chemically
non-overlapping refinement data retained predictive value on X of Y comparable
endpoints.” No outcome establishes human, neural organ-on-chip, external-
laboratory/device, or deployment validation.
