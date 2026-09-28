# Exploratory potency appendix

Date: 2026-09-28

## Decision

**Gate P1: APPENDIX — TARGET MISMATCH.** The exploratory correlations are strong,
but the official EPA EC50 is calculated from area under the complete ontogeny
trajectory. The model-derived estimate here uses only predicted DIV12 response by
dose. These are related but non-identical biological targets, so this analysis
cannot support the headline “potency ranking five days earlier.”

## Official EC50 semantics

The bundled EPA R script (`AUC_analysis_Revised_SD_*.R`) normalizes each network
parameter's ontogeny AUC to matched controls and fits a four-parameter
log-logistic curve with fixed lower/upper limits of 0 and 100. It falls back to a
linear crossing estimate when fitting is unstable. It writes `NA` when the two
highest doses do not cross the activity threshold or when the estimate exceeds
the tested range. Therefore missing values are censored/not-estimable outcomes,
not zero potency and not numeric values to impute.

The two official tables contain 2,774 rows, of which 1,190 have numeric EC50s.
For the five primary endpoints, 316 rows are numeric. Six ToxCast raw labels are
absent from the official EC50 table; they remain explicitly marked missing.

## Exploratory method

For each held-out physical well, predictions from the three frozen split/model
seeds are averaged without using DIV12 labels. Dose-level curves are then fitted
per canonical chemical, cohort, and endpoint with a decreasing Hill form fixed at
0/100. A deterministic bounded grid replaces the unavailable native optimizer;
a transparent 50%-crossing interpolation is the fallback. Curves without a
high-dose 50% crossing remain missing.

This DIV12-only estimate is compared only with numeric official AUC EC50s.

| Endpoint | Comparable pairs | Predicted DIV12 vs official AUC Spearman | Observed DIV12 vs official AUC Spearman |
|---|---:|---:|---:|
| Mean firing rate | 58 | 0.773 | 0.910 |
| Bursts/min | 54 | 0.868 | 0.877 |
| Active electrodes | 61 | 0.845 | 0.937 |
| Network spikes | 54 | 0.792 | 0.948 |
| Coordinated activity (`r`) | 61 | 0.820 | 0.950 |

The association is scientifically encouraging and shows that early forecasts
retain chemical potency ordering. It remains an appendix robustness result until
a reference EC50 derived from the same DIV12 endpoint definition is available.
`r` also retains its percent-control extreme-tail limitation.

Machine-readable outputs are `results/potency_detail.csv` and
`results/potency_summary.csv`.
