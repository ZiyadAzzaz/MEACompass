# Saved-result artifact contracts

`make reproduce-lite` is deliberately unable to train a model. It requires these
saved files in `results/` and fails explicitly if any is absent.

| File | Required columns | Consumer |
|---|---|---|
| `standardized_predictions.csv` | prediction schema v1 | validation and demo |
| `main_results.csv` | `model`, `endpoint`, `mae_y12_mean`, `spearman_y12_mean`, `spearman_delta_mean` | main table |
| `risk_coverage.csv` | `endpoint`, `model`, `coverage`, `mae` | risk–coverage plot |
| `time_ablation.csv` | `endpoint`, `input_window`, `decision_day`, `mae`, `coverage`, `abstention_rate` | time plot |
| `dose_strata.csv` | `endpoint`, `model`, `dose_stratum`, `relative_gain_percent` | dose-strata plot |
| `calibration.csv` | `endpoint`, `cohort`, `nominal_coverage`, `observed_coverage` | calibration plot |

The complete prediction contract is frozen in
`schemas/prediction_schema_v1.yaml`. Required columns may not be renamed or
reinterpreted to accommodate later results. A technically necessary change must
create a new schema version and be documented in `docs/decisions.md`.

Nullability is intentional for legacy artifacts: `dose` and uncertainty fields
must exist but may be null until standardized dose and calibrated interval results
are produced. `y_true`, `y_pred`, identifiers, fold, and seed are never nullable.

The five plotting scripts consume tables only. They do not import XGBoost, raw
data builders, splitters, tuners, or training entry points.
