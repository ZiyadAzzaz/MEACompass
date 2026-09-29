"""Post-lock directional NTP/ToxCast cohort-shift evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error, mean_squared_error

from meacompass.baselines import endpoint_frame, fit_baseline, predict_baseline
from meacompass.chem import attach_chemistry
from meacompass.data import (
    PRIMARY_ENDPOINTS,
    build_longitudinal_table,
    primary_feature_columns,
    validate_time_causal_features,
)
from meacompass.evaluate import bootstrap_paired_mae, safe_spearman
from meacompass.integrity_audit import fit_fixed, load_fixed_settings
from meacompass.reliability import select_bt_plus_plus
from meacompass.train_baselines import select_best_baseline


DIRECTIONS = (("ToxCast", "NTP"), ("NTP", "ToxCast"))
COMPARATOR_SEED = 0
ENSEMBLE_SEEDS = (0, 1, 2)


def split_direction(
    frame: pd.DataFrame, source: str, target: str
) -> tuple[pd.DataFrame, pd.DataFrame, set[str]]:
    """Return source and chemically novel target rows for one direction."""
    source_frame = frame.loc[frame["cohort"].eq(source)].copy()
    target_frame = frame.loc[frame["cohort"].eq(target)].copy()
    overlap = set(source_frame["casrn"]) & set(target_frame["casrn"])
    target_frame = target_frame.loc[~target_frame["casrn"].isin(overlap)].copy()
    if set(source_frame["casrn"]) & set(target_frame["casrn"]):
        raise AssertionError("Cross-cohort target still contains source chemicals")
    return source_frame, target_frame, overlap


def prepare_frame(config: dict[str, object]) -> tuple[pd.DataFrame, list[str]]:
    frame = build_longitudinal_table(Path(config["data_root"]))
    frame["sample_id"] = (
        frame["cohort"].astype(str)
        + "|"
        + frame["Plate.SN"].astype(str)
        + "|"
        + frame["well"].astype(str)
    )
    frame["cohort_toxcast"] = frame["cohort"].eq("ToxCast").astype("int8")
    frame, chemistry = attach_chemistry(frame, Path(config["chemical_mapping"]))
    features = list(
        dict.fromkeys(primary_feature_columns(frame) + ["cohort_toxcast"] + chemistry)
    )
    validate_time_causal_features(features)
    return frame, features


def comparator_predictions(
    train: pd.DataFrame,
    test: pd.DataFrame,
    endpoint: str,
    config: dict[str, object],
    dose_parameters: dict[str, object],
) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    bt_model = select_best_baseline(
        train,
        endpoint,
        COMPARATOR_SEED,
        int(config["inner_folds"]),
        candidates=("B0", "B1", "B1b", "B2"),
    )
    fitted_bt = fit_baseline(bt_model, train, endpoint)
    bt_prediction = predict_baseline(fitted_bt, test)
    selected, bt_inner_mae, dose_inner_mae = select_bt_plus_plus(
        train,
        endpoint,
        COMPARATOR_SEED,
        bt_model,
        dose_parameters,
        config,
    )
    if selected == "BT+":
        btpp_prediction = bt_prediction.copy()
    else:
        dose_features = ["log10_1p_dose", "cohort_toxcast", "structure_missing"]
        btpp_prediction = fit_fixed(
            train,
            test,
            dose_features,
            dose_parameters,
            config,
            COMPARATOR_SEED,
        )
    selection = {
        "bt_plus_model": bt_model,
        "bt_plus_plus_model": selected,
        "inner_bt_plus_mae": bt_inner_mae,
        "inner_dose_smooth_mae": dose_inner_mae,
        "selection_seed": COMPARATOR_SEED,
    }
    return bt_prediction, btpp_prediction, selection


def summarize_endpoint(frame: pd.DataFrame) -> dict[str, object]:
    actual = frame["target12"].to_numpy()
    prediction = frame["prediction"].to_numpy()
    bt = frame["bt_plus_prediction"].to_numpy()
    btpp = frame["bt_plus_plus_prediction"].to_numpy()
    mae = mean_absolute_error(actual, prediction)
    bt_mae = mean_absolute_error(actual, bt)
    btpp_mae = mean_absolute_error(actual, btpp)
    bt_low, bt_high = bootstrap_paired_mae(
        frame, "prediction", "bt_plus_prediction"
    )
    btpp_low, btpp_high = bootstrap_paired_mae(
        frame, "prediction", "bt_plus_plus_prediction"
    )
    return {
        "n_test_rows": len(frame),
        "n_test_chemicals": frame["casrn"].nunique(),
        "mae": float(mae),
        "rmse": float(mean_squared_error(actual, prediction) ** 0.5),
        "spearman": safe_spearman(actual, prediction),
        "bt_plus_mae": float(bt_mae),
        "delta_mae_vs_bt_plus": float(mae - bt_mae),
        "delta_mae_vs_bt_plus_ci_low": bt_low,
        "delta_mae_vs_bt_plus_ci_high": bt_high,
        "relative_gain_vs_bt_plus_percent": float(100 * (bt_mae - mae) / bt_mae),
        "bt_plus_plus_mae": float(btpp_mae),
        "delta_mae_vs_bt_plus_plus": float(mae - btpp_mae),
        "delta_mae_vs_bt_plus_plus_ci_low": btpp_low,
        "delta_mae_vs_bt_plus_plus_ci_high": btpp_high,
        "relative_gain_vs_bt_plus_plus_percent": float(
            100 * (btpp_mae - mae) / btpp_mae
        ),
        "win_vs_bt_plus_plus": bool(btpp_high < 0),
    }


def run(config_path: Path) -> None:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    results_dir = Path(config["results_dir"])
    output_dir = results_dir / "f3_cross_cohort"
    output_dir.mkdir(parents=True, exist_ok=True)
    frame, features = prepare_frame(config)
    settings = load_fixed_settings(results_dir)
    endpoints = list(config.get("primary_endpoints", PRIMARY_ENDPOINTS))
    prediction_parts: list[pd.DataFrame] = []
    selections: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    audit_rows: list[dict[str, object]] = []

    for source, target in DIRECTIONS:
        source_all, target_all, overlap = split_direction(frame, source, target)
        audit_rows.append(
            {
                "direction": f"{source}->{target}",
                "source_rows": len(source_all),
                "source_chemicals": source_all["casrn"].nunique(),
                "target_rows_before_exclusion": len(frame.loc[frame["cohort"].eq(target)]),
                "target_chemicals_before_exclusion": frame.loc[
                    frame["cohort"].eq(target), "casrn"
                ].nunique(),
                "overlap_chemicals_excluded": len(overlap),
                "target_rows_after_exclusion": len(target_all),
                "target_chemicals_after_exclusion": target_all["casrn"].nunique(),
            }
        )
        for endpoint in endpoints:
            train = endpoint_frame(source_all, endpoint).reset_index(drop=True)
            test = endpoint_frame(target_all, endpoint).reset_index(drop=True)
            train["endpoint_name"] = endpoint
            test["endpoint_name"] = endpoint
            if train.empty or test.empty:
                raise RuntimeError(f"No eligible rows for {source}->{target} {endpoint}")
            bt, btpp, selection = comparator_predictions(
                train, test, endpoint, config, settings["B3"][endpoint]
            )
            seed_predictions = []
            for seed in ENSEMBLE_SEEDS:
                setting = settings["M1"][endpoint]
                seed_predictions.append(
                    fit_fixed(
                        train,
                        test,
                        features,
                        setting,
                        config,
                        seed,
                        target_variant=str(setting["variant"]),
                        bt_model=str(setting["bt_model"]),
                    )
                )
            prediction = np.mean(np.stack(seed_predictions), axis=0)
            output = pd.DataFrame(
                {
                    "sample_id": test["sample_id"].to_numpy(),
                    "chemical_id": test["casrn"].to_numpy(),
                    "casrn": test["casrn"].to_numpy(),
                    "cohort": test["cohort"].to_numpy(),
                    "dose": test["dose"].to_numpy(),
                    "endpoint": endpoint,
                    "model": "M1-frozen-hyperparameters",
                    "direction": f"{source}->{target}",
                    "y_true": test["target12"].to_numpy(),
                    "target12": test["target12"].to_numpy(),
                    "y_pred": prediction,
                    "prediction": prediction,
                    "bt_plus_prediction": bt,
                    "bt_plus_plus_prediction": btpp,
                    "uncertainty": np.nan,
                    "fold": "held-out-cohort",
                    "seed": "ensemble-0-1-2",
                }
            )
            prediction_parts.append(output)
            selection_row = {
                "direction": f"{source}->{target}",
                "endpoint": endpoint,
                "n_train_rows": len(train),
                "n_train_chemicals": train["casrn"].nunique(),
                **selection,
                "m1_setting": json.dumps(settings["M1"][endpoint], sort_keys=True),
            }
            selections.append(selection_row)
            summaries.append(
                {
                    "direction": f"{source}->{target}",
                    "source_cohort": source,
                    "target_cohort": target,
                    "endpoint": endpoint,
                    "model": "M1-frozen-hyperparameters",
                    "n_train_rows": len(train),
                    "n_train_chemicals": train["casrn"].nunique(),
                    **summarize_endpoint(output),
                }
            )
            print(f"RUN F3 {source}->{target} endpoint={endpoint}", flush=True)

    summary = pd.DataFrame(summaries)
    wins = summary.groupby("direction")["win_vs_bt_plus_plus"].sum().astype(int)
    if bool((wins >= 3).all()):
        status = "PASS"
    elif bool(summary["win_vs_bt_plus_plus"].any()):
        status = "MIXED"
    else:
        status = "FAIL"
    pd.concat(prediction_parts, ignore_index=True).to_csv(
        output_dir / "predictions.csv", index=False
    )
    pd.DataFrame(selections).to_csv(output_dir / "selections.csv", index=False)
    pd.DataFrame(audit_rows).to_csv(output_dir / "cohort_audit.csv", index=False)
    summary.to_csv(output_dir / "summary.csv", index=False)
    decision = {
        "gate": "F3",
        "status": status,
        "post_lock_secondary": True,
        "wins_vs_bt_plus_plus": {key: int(value) for key, value in wins.items()},
        "external_laboratory_transfer": False,
        "model_retuning": False,
    }
    (output_dir / "decision.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    args = parser.parse_args()
    run(args.config)


if __name__ == "__main__":
    main()
