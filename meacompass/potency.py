"""Exploratory DIV12 potency ranking against official AUC-based EPA EC50 tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from meacompass.data import PRIMARY_ENDPOINTS, build_treatment_crosswalk, normalize_chemical_name
from meacompass.evaluate import safe_spearman


OFFICIAL_FILES = {
    "NTP": "New NTP/Summary Files/ec50_allOntogeny.csv",
    "ToxCast": "New TC/Summary Files/ec50_allOntogeny.csv",
}


def hill_decreasing(dose: np.ndarray, slope: float, ec50: float) -> np.ndarray:
    return 100.0 / (1.0 + np.power(np.maximum(dose, 0) / ec50, slope))


def estimate_div12_ec50(dose: np.ndarray, response: np.ndarray) -> tuple[float, str]:
    """Fit a fixed 0/100 decreasing Hill curve, with transparent interpolation fallback."""
    finite = np.isfinite(dose) & np.isfinite(response)
    dose = np.asarray(dose[finite], dtype=float)
    response = np.asarray(response[finite], dtype=float)
    if len(np.unique(dose)) < 4 or not np.any(dose > 0):
        return float("nan"), "insufficient_doses"
    order = np.argsort(dose)
    dose, response = dose[order], response[order]
    unique_dose = np.unique(dose)
    means = np.asarray([response[dose == value].mean() for value in unique_dose])
    positive = unique_dose[unique_dose > 0]
    max_dose = float(positive.max())
    # EPA's source does not report an estimate unless high doses cross the
    # response threshold. This exploratory DIV12 analogue uses the documented
    # fixed 50% threshold because the AUC-specific 3*MAD limit is unavailable.
    if np.min(means[-2:]) >= 50:
        return float("nan"), "no_high_dose_50pct_crossing"
    slopes = np.geomspace(0.05, 10.0, 80)
    ec50_grid = np.geomspace(float(positive.min()) / 100, max_dose * 100, 240)
    predictions = 100.0 / (
        1.0
        + np.power(
            np.maximum(unique_dose[None, None, :], 0)
            / ec50_grid[None, :, None],
            slopes[:, None, None],
        )
    )
    losses = np.mean((predictions - means[None, None, :]) ** 2, axis=2)
    best_slope, best_ec50 = np.unravel_index(int(np.argmin(losses)), losses.shape)
    del best_slope
    estimate = float(ec50_grid[best_ec50])
    if np.isfinite(estimate) and estimate <= max_dose:
        return estimate, "hill_fixed_0_100_grid"
    crossing = np.flatnonzero(means < 50)
    if len(crossing) == 0:
        return float("nan"), "no_50pct_crossing"
    index = int(crossing[0])
    if index == 0:
        previous_dose, previous_response = 0.0, 100.0
    else:
        previous_dose, previous_response = unique_dose[index - 1], means[index - 1]
    current_dose, current_response = unique_dose[index], means[index]
    if current_response == previous_response:
        return float(current_dose), "first_crossing"
    estimate = previous_dose + (50 - previous_response) * (
        current_dose - previous_dose
    ) / (current_response - previous_response)
    return (float(estimate), "linear_50pct_fallback") if 0 <= estimate <= max_dose else (float("nan"), "outside_tested_range")


def load_official(root: Path) -> pd.DataFrame:
    crosswalk = build_treatment_crosswalk(root)
    crosswalk["normalized_name"] = crosswalk["treatment"].map(normalize_chemical_name)
    crosswalk = crosswalk.loc[crosswalk["casrn"].ne("")]
    frames: list[pd.DataFrame] = []
    for cohort, relative in OFFICIAL_FILES.items():
        official = pd.read_csv(root / relative)
        official["cohort"] = cohort
        official["normalized_name"] = official["Compound"].map(normalize_chemical_name)
        lookup = crosswalk.loc[
            crosswalk["cohort"].eq(cohort), ["normalized_name", "casrn"]
        ].drop_duplicates()
        official = official.merge(
            lookup, on="normalized_name", how="left", validate="many_to_one"
        )
        if official["casrn"].isna().any():
            raise ValueError(f"Official EC50 names failed canonical mapping for {cohort}")
        official["endpoint"] = official["Ontogeny"].str.removesuffix("_AUC")
        official["official_ec50"] = pd.to_numeric(official["ec"], errors="coerce")
        official["official_status"] = np.where(
            official["official_ec50"].notna(), "numeric", "not_estimable_or_above_range"
        )
        frames.append(official)
    return pd.concat(frames, ignore_index=True)


def run_potency(data_root: Path, results_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictions = pd.read_csv(results_dir / "m1_predictions.csv")
    # Average the three independently fitted held-out predictions for each
    # physical well; this uses no target labels and yields one dose curve.
    curves = predictions.groupby(
        ["sample_id", "casrn", "cohort", "endpoint"], as_index=False
    ).agg(dose=("sample_id", "size"), target12=("target12", "first"), prediction=("prediction", "mean"))
    identity = pd.read_csv(results_dir / "demo_predictions.csv")[["sample_id", "dose"]].drop_duplicates()
    curves = curves.drop(columns="dose").merge(identity, on="sample_id", how="left", validate="many_to_one")
    official = load_official(data_root)
    official = official.loc[official["endpoint"].isin(PRIMARY_ENDPOINTS)]
    rows: list[dict[str, object]] = []
    for (cohort, casrn, endpoint), source in curves.groupby(
        ["cohort", "casrn", "endpoint"], sort=True
    ):
        predicted, predicted_method = estimate_div12_ec50(
            source["dose"].to_numpy(), source["prediction"].to_numpy()
        )
        observed, observed_method = estimate_div12_ec50(
            source["dose"].to_numpy(), source["target12"].to_numpy()
        )
        match = official.loc[
            official["cohort"].eq(cohort)
            & official["casrn"].eq(casrn)
            & official["endpoint"].eq(endpoint)
        ]
        if len(match) > 1:
            raise ValueError(f"Expected at most one official row for {cohort}/{casrn}/{endpoint}; got {len(match)}")
        if len(match) == 1:
            record = match.iloc[0]
            compound = record["Compound"]
            official_ec50 = record["official_ec50"]
            official_status = record["official_status"]
        else:
            compound = source["casrn"].iloc[0]
            official_ec50 = float("nan")
            official_status = "chemical_absent_from_official_ec50_table"
        rows.append(
            {
                "cohort": cohort,
                "casrn": casrn,
                "compound": compound,
                "endpoint": endpoint,
                "official_auc_ec50": official_ec50,
                "official_status": official_status,
                "predicted_div12_ec50": predicted,
                "predicted_method": predicted_method,
                "observed_div12_ec50": observed,
                "observed_method": observed_method,
                "target_match": False,
                "target_mismatch_reason": "official is ontogeny-AUC EC50; estimate is DIV12-only EC50",
            }
        )
    detail = pd.DataFrame(rows)
    summaries: list[dict[str, object]] = []
    for endpoint, source in detail.groupby("endpoint", sort=True):
        comparable = source.dropna(subset=["official_auc_ec50", "predicted_div12_ec50"])
        observed_comparable = source.dropna(subset=["official_auc_ec50", "observed_div12_ec50"])
        prediction_spearman = safe_spearman(
            comparable["official_auc_ec50"].to_numpy(),
            comparable["predicted_div12_ec50"].to_numpy(),
        )
        observed_spearman = safe_spearman(
            observed_comparable["official_auc_ec50"].to_numpy(),
            observed_comparable["observed_div12_ec50"].to_numpy(),
        )
        summaries.append(
            {
                "endpoint": endpoint,
                "official_numeric": source["official_auc_ec50"].notna().sum(),
                "predicted_div12_estimable": source["predicted_div12_ec50"].notna().sum(),
                "comparable_pairs": len(comparable),
                "spearman_predicted_div12_vs_official_auc": prediction_spearman,
                "observed_comparable_pairs": len(observed_comparable),
                "spearman_observed_div12_vs_official_auc": observed_spearman,
                "gate_p1_eligible": False,
                "gate_p1_decision": "APPENDIX_TARGET_MISMATCH",
            }
        )
    summary = pd.DataFrame(summaries)
    detail.to_csv(results_dir / "potency_detail.csv", index=False)
    summary.to_csv(results_dir / "potency_summary.csv", index=False)
    return detail, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    _, summary = run_potency(Path(config["data_root"]), Path(config["results_dir"]))
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
