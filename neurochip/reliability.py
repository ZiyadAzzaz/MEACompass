"""Post-audit BT++, nested CV+ calibration, and abstention evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error

from neurochip.baselines import endpoint_frame, fit_baseline, predict_baseline
from neurochip.chem import attach_chemistry
from neurochip.data import PRIMARY_ENDPOINTS, build_longitudinal_table, primary_feature_columns
from neurochip.evaluate import bootstrap_paired_mae
from neurochip.integrity_audit import fit_fixed, load_fixed_settings
from neurochip.sanity_gate import KEYS, attach_identity
from neurochip.splits import outer_folds
from neurochip.train_baselines import feature_matrix, make_xgb
from neurochip.train_m1 import compose_m1_prediction, m1_training_target


ALPHA = 0.10
COVERAGE_LEVELS = (1.0, 0.9, 0.8, 0.7, 0.6)


def load_m1_settings(results_dir: Path) -> dict[tuple[int, int, str], dict[str, object]]:
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((results_dir / "m1_tuning_checkpoints").glob("*.json"))
    ]
    if len(records) != 75:
        raise RuntimeError(f"M2 requires 75 preserved M1 tuning records; found {len(records)}")
    return {
        (int(record["seed"]), int(record["outer_fold"]), str(record["endpoint"])): record
        for record in records
    }


def bt_plus_model_for_task(results_dir: Path, seed: int, fold: int, endpoint: str) -> str:
    path = results_dir / "bt_plus_checkpoints" / f"seed{seed}_fold{fold}_{endpoint}.csv"
    values = pd.read_csv(path, usecols=["bt_plus_model"])["bt_plus_model"].unique()
    if len(values) != 1:
        raise ValueError(f"BT+ task has {len(values)} selected models: {path}")
    return str(values[0])


def select_bt_plus_plus(
    train: pd.DataFrame,
    endpoint: str,
    seed: int,
    bt_model: str,
    dose_parameters: dict[str, object],
    config: dict[str, object],
) -> tuple[str, float, float]:
    """Compare fixed BT+ and DOSE-SMOOTH using outer-training rows only."""
    bt_actual: list[np.ndarray] = []
    bt_prediction: list[np.ndarray] = []
    dose_prediction: list[np.ndarray] = []
    features = ["log10_1p_dose", "cohort_toxcast", "structure_missing"]
    for inner_train_idx, inner_valid_idx in outer_folds(
        train, seed=seed, n_splits=int(config["inner_folds"])
    ):
        inner_train = train.iloc[inner_train_idx].reset_index(drop=True)
        inner_valid = train.iloc[inner_valid_idx].reset_index(drop=True)
        inner_train["endpoint_name"] = endpoint
        inner_valid["endpoint_name"] = endpoint
        fitted = fit_baseline(bt_model, inner_train, endpoint)
        bt_actual.append(inner_valid["target12"].to_numpy())
        bt_prediction.append(predict_baseline(fitted, inner_valid))
        dose_prediction.append(
            fit_fixed(
                inner_train,
                inner_valid,
                features,
                dose_parameters,
                config,
                seed,
            )
        )
    actual = np.concatenate(bt_actual)
    bt_mae = mean_absolute_error(actual, np.concatenate(bt_prediction))
    dose_mae = mean_absolute_error(actual, np.concatenate(dose_prediction))
    selected = "DOSE_SMOOTH" if dose_mae < bt_mae else "BT+"
    return selected, float(bt_mae), float(dose_mae)


def build_bt_plus_plus(
    frame: pd.DataFrame,
    config: dict[str, object],
    results_dir: Path,
    seeds: list[int],
) -> None:
    fixed = load_fixed_settings(results_dir)["B3"]
    checkpoint_dir = results_dir / "bt_plus_plus_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        for fold, (train_idx, test_idx) in enumerate(
            outer_folds(frame, seed, int(config["outer_folds"]))
        ):
            for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
                path = checkpoint_dir / f"seed{seed}_fold{fold}_{endpoint}.csv"
                if path.exists():
                    continue
                train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
                test = endpoint_frame(frame.iloc[test_idx], endpoint).reset_index(drop=True)
                bt_model = bt_plus_model_for_task(results_dir, seed, fold, endpoint)
                selected, bt_inner_mae, dose_inner_mae = select_bt_plus_plus(
                    train, endpoint, seed, bt_model, fixed[endpoint], config
                )
                if selected == "BT+":
                    source = pd.read_csv(
                        results_dir / "bt_plus_checkpoints" / f"seed{seed}_fold{fold}_{endpoint}.csv"
                    )
                    prediction = source["prediction"].to_numpy()
                else:
                    source = pd.read_csv(
                        results_dir / "audit" / "dose_smooth_checkpoints" / f"seed{seed}_fold{fold}_{endpoint}.csv"
                    )
                    prediction = source["prediction"].to_numpy()
                if not np.array_equal(source["sample_id"].to_numpy(), test["sample_id"].to_numpy()):
                    raise ValueError(f"BT++ source alignment failed for {seed}/{fold}/{endpoint}")
                output = source[KEYS + ["target12", "target7"]].copy()
                output["model"] = "BT++"
                output["prediction"] = prediction
                output["bt_plus_plus_model"] = selected
                output["bt_plus_candidate_model"] = bt_model
                output["inner_bt_plus_mae"] = bt_inner_mae
                output["inner_dose_smooth_mae"] = dose_inner_mae
                output.to_csv(path, index=False)
                print(f"RUN BT++ seed={seed} fold={fold} endpoint={endpoint} selected={selected}", flush=True)


def summarize_bt_plus_plus(results_dir: Path) -> None:
    files = sorted((results_dir / "bt_plus_plus_checkpoints").glob("*.csv"))
    if len(files) != 75:
        raise RuntimeError(f"BT++ requires 75 checkpoints; found {len(files)}")
    predictions = pd.concat([pd.read_csv(path) for path in files], ignore_index=True)
    m1 = pd.read_csv(results_dir / "m1_predictions.csv")
    rows: list[dict[str, object]] = []
    for endpoint, reference in predictions.groupby("endpoint", sort=True):
        candidate = m1.loc[m1["endpoint"].eq(endpoint)]
        merged = candidate.merge(
            reference[KEYS + ["prediction"]].rename(columns={"prediction": "btpp_prediction"}),
            on=KEYS,
            how="inner",
            validate="one_to_one",
        )
        mae = mean_absolute_error(merged["target12"], merged["prediction"])
        ref_mae = mean_absolute_error(merged["target12"], merged["btpp_prediction"])
        low, high = bootstrap_paired_mae(merged, "prediction", "btpp_prediction")
        rows.append(
            {
                "endpoint": endpoint,
                "model": "M1",
                "comparator": "BT++",
                "n_rows": len(merged),
                "n_chemicals": merged["casrn"].nunique(),
                "mae": mae,
                "bt_plus_plus_mae": ref_mae,
                "delta_mae_vs_bt_plus_plus": mae - ref_mae,
                "delta_mae_ci_low": low,
                "delta_mae_ci_high": high,
                "relative_gain_percent": 100 * (ref_mae - mae) / ref_mae,
            }
        )
    selections = predictions[
        ["endpoint", "seed", "outer_fold", "bt_plus_plus_model", "bt_plus_candidate_model", "inner_bt_plus_mae", "inner_dose_smooth_mae"]
    ].drop_duplicates()
    predictions.to_csv(results_dir / "bt_plus_plus_predictions.csv", index=False)
    selections.to_csv(results_dir / "bt_plus_plus_selections.csv", index=False)
    pd.DataFrame(rows).to_csv(results_dir / "bt_plus_plus.csv", index=False)


def fit_cvplus_fold(
    inner_train: pd.DataFrame,
    inner_valid: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    record: dict[str, object],
    config: dict[str, object],
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    parameters = dict(record["parameters"])
    trees = int(parameters.pop("n_estimators"))
    variant = str(record["variant"])
    bt_model = str(record["bt_model"])
    endpoint = str(record["endpoint"])
    if variant == "bt_residual":
        fitted_bt = fit_baseline(bt_model, inner_train, endpoint)
        train_bt = predict_baseline(fitted_bt, inner_train)
        valid_bt = predict_baseline(fitted_bt, inner_valid)
        test_bt = predict_baseline(fitted_bt, test)
    else:
        train_bt = np.zeros(len(inner_train))
        valid_bt = np.zeros(len(inner_valid))
        test_bt = np.zeros(len(test))
    target = m1_training_target(inner_train, variant, train_bt)
    model = make_xgb(parameters, config["xgboost"], seed=seed, trees=trees)
    model.fit(feature_matrix(inner_train, features), target, verbose=False)
    valid_raw = model.predict(feature_matrix(inner_valid, features))
    test_raw = model.predict(feature_matrix(test, features))
    return (
        compose_m1_prediction(valid_raw, variant, valid_bt),
        compose_m1_prediction(test_raw, variant, test_bt),
    )


def cvplus_bounds(
    residual_parts: list[np.ndarray],
    test_prediction_parts: list[np.ndarray],
    alpha: float = ALPHA,
) -> tuple[np.ndarray, np.ndarray]:
    if len(residual_parts) != len(test_prediction_parts) or not residual_parts:
        raise ValueError("CV+ requires aligned non-empty residual/prediction folds")
    lower_parts = [prediction[:, None] - residual[None, :] for residual, prediction in zip(residual_parts, test_prediction_parts, strict=True)]
    upper_parts = [prediction[:, None] + residual[None, :] for residual, prediction in zip(residual_parts, test_prediction_parts, strict=True)]
    lower_candidates = np.concatenate(lower_parts, axis=1)
    upper_candidates = np.concatenate(upper_parts, axis=1)
    lower = np.quantile(lower_candidates, alpha, axis=1, method="lower")
    upper = np.quantile(upper_candidates, 1 - alpha, axis=1, method="higher")
    return lower, upper


def run_cvplus(
    frame: pd.DataFrame,
    chemistry_columns: list[str],
    config: dict[str, object],
    results_dir: Path,
    seeds: list[int],
) -> None:
    features = list(dict.fromkeys(primary_feature_columns(frame) + ["cohort_toxcast"] + chemistry_columns))
    settings = load_m1_settings(results_dir)
    checkpoint_dir = results_dir / "m2_cvplus_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        for fold, (train_idx, test_idx) in enumerate(
            outer_folds(frame, seed, int(config["outer_folds"]))
        ):
            for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
                path = checkpoint_dir / f"seed{seed}_fold{fold}_{endpoint}.csv"
                if path.exists():
                    continue
                train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
                test = endpoint_frame(frame.iloc[test_idx], endpoint).reset_index(drop=True)
                train["endpoint_name"] = endpoint
                test["endpoint_name"] = endpoint
                record = settings[(seed, fold, endpoint)]
                residual_parts: list[np.ndarray] = []
                test_parts: list[np.ndarray] = []
                for inner_train_idx, inner_valid_idx in outer_folds(
                    train, seed=seed, n_splits=int(config["inner_folds"])
                ):
                    inner_train = train.iloc[inner_train_idx].reset_index(drop=True)
                    inner_valid = train.iloc[inner_valid_idx].reset_index(drop=True)
                    valid_prediction, test_prediction = fit_cvplus_fold(
                        inner_train, inner_valid, test, features, record, config, seed
                    )
                    residual_parts.append(np.abs(inner_valid["target12"].to_numpy() - valid_prediction))
                    test_parts.append(test_prediction)
                lower, upper = cvplus_bounds(residual_parts, test_parts)
                point = pd.read_csv(
                    results_dir / "m1_checkpoints" / f"seed{seed}_fold{fold}_{endpoint}.csv"
                )
                if not np.array_equal(point["sample_id"].to_numpy(), test["sample_id"].to_numpy()):
                    raise ValueError(f"M2 point-prediction alignment failed for {seed}/{fold}/{endpoint}")
                output = point[KEYS + ["target12", "target7", "prediction"]].copy()
                output["uncertainty_lower"] = lower
                output["uncertainty_upper"] = upper
                output["uncertainty"] = upper - lower
                output["covered"] = output["target12"].between(lower, upper, inclusive="both")
                output["nominal_coverage"] = 1 - ALPHA
                output["method"] = "nested_group_cvplus"
                output.to_csv(path, index=False)
                print(f"RUN M2 seed={seed} fold={fold} endpoint={endpoint}", flush=True)


def summarize_m2(results_dir: Path) -> pd.DataFrame:
    files = sorted((results_dir / "m2_cvplus_checkpoints").glob("*.csv"))
    if len(files) != 75:
        raise RuntimeError(f"M2 requires 75 checkpoints; found {len(files)}")
    predictions = pd.concat([pd.read_csv(path) for path in files], ignore_index=True)
    rows: list[dict[str, object]] = []
    for endpoint, source in predictions.groupby("endpoint", sort=True):
        ntp = source.loc[source["cohort"].eq("NTP"), "covered"].mean()
        toxcast = source.loc[source["cohort"].eq("ToxCast"), "covered"].mean()
        overall = source["covered"].mean()
        rows.append(
            {
                "endpoint": endpoint,
                "method": "nested_group_cvplus",
                "nominal_coverage": 0.90,
                "overall_coverage": overall,
                "ntp_coverage": ntp,
                "toxcast_coverage": toxcast,
                "median_interval_width": source["uncertainty"].median(),
                "n_rows": len(source),
                "pass_overall": 0.85 <= overall <= 0.95,
                "pass_ntp": ntp >= 0.80,
                "pass_toxcast": toxcast >= 0.80,
            }
        )
    summary = pd.DataFrame(rows)
    summary["gate_pass"] = summary[["pass_overall", "pass_ntp", "pass_toxcast"]].all(axis=1)
    predictions.to_csv(results_dir / "m2_predictions.csv", index=False)
    summary.to_csv(results_dir / "m2_calibration.csv", index=False)
    return summary


def bootstrap_abstention_delta(source: pd.DataFrame, draws: int = 1000) -> tuple[float, float]:
    grouped = source.assign(
        error=np.abs(source["target12"] - source["prediction"]),
        accepted_error=np.where(source["accepted"], np.abs(source["target12"] - source["prediction"]), 0.0),
        accepted_count=source["accepted"].astype(int),
    ).groupby("casrn", sort=True).agg(
        error_sum=("error", "sum"),
        count=("error", "size"),
        accepted_error_sum=("accepted_error", "sum"),
        accepted_count=("accepted_count", "sum"),
    )
    rng = np.random.default_rng(20260928)
    sampled = rng.integers(0, len(grouped), size=(draws, len(grouped)))
    full = grouped["error_sum"].to_numpy()[sampled].sum(axis=1) / grouped["count"].to_numpy()[sampled].sum(axis=1)
    accepted_count = grouped["accepted_count"].to_numpy()[sampled].sum(axis=1)
    accepted = grouped["accepted_error_sum"].to_numpy()[sampled].sum(axis=1) / accepted_count
    delta = accepted - full
    return float(np.quantile(delta, 0.025)), float(np.quantile(delta, 0.975))


def evaluate_m3(results_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    predictions = pd.read_csv(results_dir / "m2_predictions.csv")
    rows: list[dict[str, object]] = []
    labeled: list[pd.DataFrame] = []
    for endpoint, source in predictions.groupby("endpoint", sort=True):
        source = source.sort_values(["uncertainty", "casrn", "sample_id", "seed", "outer_fold"], kind="stable").reset_index(drop=True)
        full_mae = mean_absolute_error(source["target12"], source["prediction"])
        endpoint_rows: list[dict[str, object]] = []
        for coverage in COVERAGE_LEVELS:
            accepted_n = max(1, int(np.floor(coverage * len(source))))
            evaluated = source.copy()
            evaluated["accepted"] = False
            evaluated.loc[: accepted_n - 1, "accepted"] = True
            accepted = evaluated.loc[evaluated["accepted"]]
            accepted_mae = mean_absolute_error(accepted["target12"], accepted["prediction"])
            low, high = (0.0, 0.0) if coverage == 1.0 else bootstrap_abstention_delta(evaluated)
            endpoint_rows.append(
                {
                    "endpoint": endpoint,
                    "coverage_target": coverage,
                    "accepted_rows": accepted_n,
                    "total_rows": len(source),
                    "actual_coverage": accepted_n / len(source),
                    "full_mae": full_mae,
                    "accepted_mae": accepted_mae,
                    "delta_mae": accepted_mae - full_mae,
                    "delta_mae_ci_low": low,
                    "delta_mae_ci_high": high,
                    "relative_risk_reduction_percent": 100 * (full_mae - accepted_mae) / full_mae,
                }
            )
            if coverage == 0.7:
                evaluated["verdict"] = np.where(
                    evaluated["accepted"], "EARLY DECISION POSSIBLE", "CONTINUE TO DIV12"
                )
                evaluated["coverage_target"] = coverage
                labeled.append(evaluated)
        endpoint_frame_rows = pd.DataFrame(endpoint_rows).sort_values("coverage_target")
        aurc = float(np.trapezoid(endpoint_frame_rows["accepted_mae"], endpoint_frame_rows["coverage_target"]))
        for record in endpoint_rows:
            record["aurc_0_6_to_1_0"] = aurc
            rows.append(record)
    risk = pd.DataFrame(rows)
    decisions = pd.concat(labeled, ignore_index=True)
    risk.to_csv(results_dir / "m3_risk_coverage.csv", index=False)
    decisions.to_csv(results_dir / "m3_predictions.csv", index=False)
    return risk, decisions


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    parser.add_argument("--stage", choices=["btpp", "summarize_btpp", "cvplus", "summarize_m2", "m3"], required=True)
    parser.add_argument("--seeds", nargs="+", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    results_dir = Path(config["results_dir"])
    seeds = args.seeds if args.seeds is not None else list(config["seeds"])
    if args.stage in {"summarize_btpp", "summarize_m2", "m3"}:
        if args.stage == "summarize_btpp":
            summarize_bt_plus_plus(results_dir)
        elif args.stage == "summarize_m2":
            print(summarize_m2(results_dir).to_string(index=False))
        else:
            risk, _ = evaluate_m3(results_dir)
            print(risk.loc[risk["coverage_target"].eq(0.7)].to_string(index=False))
        return
    base = attach_identity(build_longitudinal_table(Path(config["data_root"])))
    frame, chemistry_columns = attach_chemistry(base, Path(config["chemical_mapping"]))
    if args.stage == "btpp":
        build_bt_plus_plus(frame, config, results_dir, seeds)
    else:
        run_cvplus(frame, chemistry_columns, config, results_dir, seeds)


if __name__ == "__main__":
    main()
