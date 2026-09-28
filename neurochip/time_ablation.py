"""Post-lock DIV5 / DIV5+7 / DIV5+7+9 reliability ablation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error

from neurochip.baselines import endpoint_frame
from neurochip.chem import attach_chemistry
from neurochip.data import NETWORK_METRICS, PRIMARY_ENDPOINTS, build_longitudinal_table
from neurochip.integrity_audit import fit_fixed
from neurochip.reliability import ALPHA, cvplus_bounds, fit_cvplus_fold, load_m1_settings
from neurochip.sanity_gate import KEYS, attach_identity
from neurochip.splits import outer_folds


WINDOWS = {
    "DIV5": 5,
    "DIV5+7": 7,
    "DIV5+7+9": 9,
}


def add_div9_missingness(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    for metric in NETWORK_METRICS:
        column = f"div9_{metric}"
        if column not in output:
            raise ValueError(f"DIV9 ablation requires {column}")
        output[f"{column}_missing"] = output[column].isna().astype("int8")
    return output


def window_features(
    frame: pd.DataFrame, chemistry_columns: list[str], decision_day: int
) -> list[str]:
    allowed = tuple(f"div{day}_" for day in (5, 7, 9) if day <= decision_day)
    neural = [column for column in frame.columns if column.startswith(allowed)]
    forbidden = [column for column in neural if column.startswith("div12_")]
    if forbidden:
        raise ValueError(f"Future features entered time ablation: {forbidden}")
    return list(
        dict.fromkeys(neural + ["log10_1p_dose", "cohort_toxcast"] + chemistry_columns)
    )


def run_window(
    frame: pd.DataFrame,
    chemistry_columns: list[str],
    config: dict[str, object],
    results_dir: Path,
    window: str,
    seeds: list[int],
) -> None:
    decision_day = WINDOWS[window]
    if decision_day == 7:
        raise ValueError("DIV5+7 uses the frozen M2 predictions and is not retrained")
    features = window_features(frame, chemistry_columns, decision_day)
    settings = load_m1_settings(results_dir)
    checkpoint_dir = results_dir / "time_ablation_checkpoints" / window.replace("+", "_")
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
                point_prediction = fit_fixed(
                    train,
                    test,
                    features,
                    dict(record["parameters"]),
                    config,
                    seed,
                    str(record["variant"]),
                    str(record["bt_model"]),
                )
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
                    residual_parts.append(
                        np.abs(inner_valid["target12"].to_numpy() - valid_prediction)
                    )
                    test_parts.append(test_prediction)
                lower, upper = cvplus_bounds(residual_parts, test_parts, ALPHA)
                output = pd.DataFrame(
                    {
                        "sample_id": test["sample_id"].to_numpy(),
                        "casrn": test["casrn"].to_numpy(),
                        "cohort": test["cohort"].to_numpy(),
                        "endpoint": endpoint,
                        "model": "M1",
                        "seed": seed,
                        "outer_fold": fold,
                        "target12": test["target12"].to_numpy(),
                        "target7": test["target7"].to_numpy(),
                        "prediction": point_prediction,
                        "uncertainty_lower": lower,
                        "uncertainty_upper": upper,
                        "uncertainty": upper - lower,
                        "covered": test["target12"].between(lower, upper, inclusive="both").to_numpy(),
                        "input_window": window,
                        "decision_day": decision_day,
                    }
                )
                output.to_csv(path, index=False)
                print(f"RUN time window={window} seed={seed} fold={fold} endpoint={endpoint}", flush=True)


def summarize_time_ablation(results_dir: Path) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for window, decision_day in WINDOWS.items():
        if window == "DIV5+7":
            frame = pd.read_csv(results_dir / "m2_predictions.csv")
            frame["input_window"] = window
            frame["decision_day"] = decision_day
        else:
            directory = results_dir / "time_ablation_checkpoints" / window.replace("+", "_")
            files = sorted(directory.glob("*.csv"))
            if len(files) != 75:
                raise RuntimeError(f"{window} requires 75 checkpoints; found {len(files)}")
            frame = pd.concat([pd.read_csv(path) for path in files], ignore_index=True)
        parts.append(frame)
    predictions = pd.concat(parts, ignore_index=True)
    bt_plus = pd.read_csv(results_dir / "bt_plus_predictions.csv")
    bt_reference = bt_plus[KEYS + ["prediction"]].rename(
        columns={"prediction": "bt_plus_prediction"}
    )
    predictions = predictions.merge(
        bt_reference, on=KEYS, how="left", validate="many_to_one"
    )
    if predictions["bt_plus_prediction"].isna().any():
        raise ValueError("Time ablation does not align with BT+")
    thresholds = (
        predictions.loc[predictions["input_window"].eq("DIV5+7")]
        .groupby("endpoint")["uncertainty"]
        .quantile(0.70)
        .to_dict()
    )
    predictions["width_threshold"] = predictions["endpoint"].map(thresholds)
    predictions["accepted"] = predictions["uncertainty"].le(predictions["width_threshold"])
    rows: list[dict[str, object]] = []
    for (endpoint, window, day), source in predictions.groupby(
        ["endpoint", "input_window", "decision_day"], sort=True
    ):
        mae = mean_absolute_error(source["target12"], source["prediction"])
        bt_mae = mean_absolute_error(source["target12"], source["bt_plus_prediction"])
        accepted = source.loc[source["accepted"]]
        rows.append(
            {
                "endpoint": endpoint,
                "input_window": window,
                "decision_day": day,
                "mae": mae,
                "bt_plus_mae": bt_mae,
                "relative_gain_vs_bt_plus_percent": 100 * (bt_mae - mae) / bt_mae,
                "interval_coverage": source["covered"].mean(),
                "coverage": source["covered"].mean(),
                "median_interval_width": source["uncertainty"].median(),
                "width_threshold_from_div7": source["width_threshold"].iloc[0],
                "accepted_fraction": source["accepted"].mean(),
                "abstention_rate": 1 - source["accepted"].mean(),
                "accepted_mae": mean_absolute_error(accepted["target12"], accepted["prediction"])
                if len(accepted)
                else float("nan"),
                "n_rows": len(source),
            }
        )
    summary = pd.DataFrame(rows).sort_values(["endpoint", "decision_day"])
    predictions.to_csv(results_dir / "time_ablation_predictions.csv", index=False)
    summary.to_csv(results_dir / "time_ablation.csv", index=False)
    return summary


def write_practical_value(results_dir: Path) -> pd.DataFrame:
    time = pd.read_csv(results_dir / "time_ablation.csv")
    day7 = time.loc[time["decision_day"].eq(7)].copy()
    day7["accepted_percent"] = 100 * day7["accepted_fraction"]
    day7["days_saved_per_accepted_case"] = 5
    day7["assay_duration_saved_per_accepted_case_percent"] = 100 * 5 / 12
    day7["expected_days_saved_per_prediction"] = 5 * day7["accepted_fraction"]
    day7["operational_status"] = "research decision support; prospective validation required"
    selected = day7[
        [
            "endpoint",
            "accepted_percent",
            "accepted_mae",
            "mae",
            "abstention_rate",
            "days_saved_per_accepted_case",
            "assay_duration_saved_per_accepted_case_percent",
            "expected_days_saved_per_prediction",
            "operational_status",
        ]
    ]
    selected.to_csv(results_dir / "practical_value.csv", index=False)
    return selected


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    parser.add_argument("--stage", choices=["run", "summarize", "practical"], required=True)
    parser.add_argument("--window", choices=["DIV5", "DIV5+7+9"])
    parser.add_argument("--seeds", nargs="+", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    results_dir = Path(config["results_dir"])
    if args.stage == "summarize":
        print(summarize_time_ablation(results_dir).to_string(index=False))
        return
    if args.stage == "practical":
        print(write_practical_value(results_dir).to_string(index=False))
        return
    if args.window is None:
        raise ValueError("--window is required for run")
    base = attach_identity(build_longitudinal_table(Path(config["data_root"])))
    base = add_div9_missingness(base)
    frame, chemistry_columns = attach_chemistry(base, Path(config["chemical_mapping"]))
    seeds = args.seeds if args.seeds is not None else list(config["seeds"])
    run_window(frame, chemistry_columns, config, results_dir, args.window, seeds)


if __name__ == "__main__":
    main()
