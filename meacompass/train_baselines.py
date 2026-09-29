"""Nested chemical-disjoint evaluation for pre-registered baselines B0--B4."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import itertools
import json
import subprocess
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from scipy import sparse
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

from meacompass.baselines import TRIVIAL_MODELS, endpoint_frame, fit_baseline, predict_baseline
from meacompass.chem import attach_chemistry
from meacompass.data import PRIMARY_ENDPOINTS, build_longitudinal_table, primary_feature_columns
from meacompass.evaluate import bootstrap_delta_mae, prediction_metrics
from meacompass.splits import outer_folds


ALL_MODELS = ("B0", "B1", "B1b", "B2", "B3", "B4")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def select_best_baseline(
    train: pd.DataFrame,
    endpoint: str,
    seed: int,
    inner_folds: int,
    candidates: tuple[str, ...] = TRIVIAL_MODELS,
) -> str:
    predictions = {model: [] for model in candidates}
    actual: list[np.ndarray] = []
    for inner_train_idx, inner_valid_idx in outer_folds(train, seed=seed, n_splits=inner_folds):
        inner_train = train.iloc[inner_train_idx]
        inner_valid = train.iloc[inner_valid_idx]
        actual.append(inner_valid["target12"].to_numpy())
        for model in candidates:
            fitted = fit_baseline(model, inner_train, endpoint)
            predictions[model].append(predict_baseline(fitted, inner_valid))
    joined_actual = np.concatenate(actual)
    scores = {
        model: mean_absolute_error(joined_actual, np.concatenate(parts))
        for model, parts in predictions.items()
    }
    return min(scores, key=lambda model: (scores[model], model))


def select_best_trivial(train: pd.DataFrame, endpoint: str, seed: int, inner_folds: int) -> str:
    return select_best_baseline(train, endpoint, seed, inner_folds, TRIVIAL_MODELS)


def xgb_grid(config: dict[str, object]) -> list[dict[str, object]]:
    keys = ["max_depth", "learning_rate", "min_child_weight", "colsample_bytree"]
    return [
        dict(zip(keys, values, strict=True))
        for values in itertools.product(*(config[key] for key in keys))
    ]


def make_xgb(parameters: dict[str, object], config: dict[str, object], seed: int, trees: int) -> XGBRegressor:
    return XGBRegressor(
        **parameters,
        n_estimators=trees,
        subsample=float(config["subsample"]),
        objective="reg:squarederror",
        tree_method="hist",
        random_state=seed,
        n_jobs=int(config["n_jobs"]),
        verbosity=0,
    )


def feature_matrix(frame: pd.DataFrame, features: list[str]):
    values = frame[features].to_numpy(dtype=np.float32, copy=True)
    # Morgan fingerprints are overwhelmingly zero. CSR preserves NaNs as stored
    # missing values while preventing XGBoost from binning millions of zeros.
    if len(features) > 500:
        return sparse.csr_matrix(values)
    return values


def tune_xgb(
    train: pd.DataFrame,
    features: list[str],
    seed: int,
    inner_folds: int,
    config: dict[str, object],
) -> tuple[dict[str, object], int, float]:
    split_data = []
    for inner_train_idx, inner_valid_idx in outer_folds(train, seed=seed, n_splits=inner_folds):
        inner_train = train.iloc[inner_train_idx]
        inner_valid = train.iloc[inner_valid_idx]
        split_data.append(
            (
                feature_matrix(inner_train, features),
                inner_train["target12"].to_numpy(),
                feature_matrix(inner_valid, features),
                inner_valid["target12"].to_numpy(),
            )
        )
    def score_parameters(parameters: dict[str, object]) -> tuple[float, dict[str, object], int]:
        fold_actual: list[np.ndarray] = []
        fold_prediction: list[np.ndarray] = []
        fold_trees: list[int] = []
        for train_x, train_y, valid_x, valid_y in split_data:
            model = XGBRegressor(
                **parameters,
                n_estimators=int(config["n_estimators"]),
                subsample=float(config["subsample"]),
                objective="reg:squarederror",
                tree_method="hist",
                random_state=seed,
                n_jobs=1,
                early_stopping_rounds=int(config["early_stopping_rounds"]),
                verbosity=0,
            )
            model.fit(
                train_x,
                train_y,
                eval_set=[(valid_x, valid_y)],
                verbose=False,
            )
            fold_actual.append(valid_y)
            fold_prediction.append(model.predict(valid_x))
            iteration = getattr(model, "best_iteration", int(config["n_estimators"]) - 1)
            fold_trees.append(int(iteration) + 1)
        mae = mean_absolute_error(np.concatenate(fold_actual), np.concatenate(fold_prediction))
        return float(mae), parameters, max(1, int(np.median(fold_trees)))

    grid = xgb_grid(config)
    workers = min(int(config.get("parallel_configs", 4)), len(grid))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        scores = list(executor.map(score_parameters, grid))
    best_mae, best_parameters, best_trees = min(scores, key=lambda item: item[0])
    return best_parameters, best_trees, best_mae


def prediction_records(
    test: pd.DataFrame,
    prediction: np.ndarray,
    bt_prediction: np.ndarray,
    model: str,
    endpoint: str,
    seed: int,
    outer_fold: int,
    bt_model: str,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "sample_id": test["sample_id"].to_numpy(),
            "casrn": test["casrn"].to_numpy(),
            "cohort": test["cohort"].to_numpy(),
            "endpoint": endpoint,
            "model": model,
            "seed": seed,
            "outer_fold": outer_fold,
            "bt_model": bt_model,
            "target12": test["target12"].to_numpy(),
            "target7": test["target7"].to_numpy(),
            "delta": test["delta"].to_numpy(),
            "prediction": prediction,
            "bt_prediction": bt_prediction,
        }
    )


def run_task(
    train: pd.DataFrame,
    test: pd.DataFrame,
    endpoint: str,
    seed: int,
    outer_fold: int,
    models: list[str],
    inner_folds: int,
    xgb_config: dict[str, object],
    early_features: list[str],
    chemistry_features: list[str],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    bt_model = select_best_trivial(train, endpoint, seed, inner_folds)
    bt_fit = fit_baseline(bt_model, train, endpoint)
    bt_prediction = predict_baseline(bt_fit, test)
    outputs: list[pd.DataFrame] = []
    tuning: list[dict[str, object]] = []
    for model_name in models:
        started = time.perf_counter()
        if model_name in {"B0", "B1", "B1b", "B2"}:
            fitted = fit_baseline(model_name, train, endpoint)
            prediction = predict_baseline(fitted, test)
            parameters = fitted.parameters
            inner_mae = float("nan")
        elif model_name in {"B3", "B4"}:
            features = early_features if model_name == "B3" else chemistry_features
            parameters, trees, inner_mae = tune_xgb(
                train, features, seed=seed, inner_folds=inner_folds, config=xgb_config
            )
            fitted_xgb = make_xgb(parameters, xgb_config, seed=seed, trees=trees)
            fitted_xgb.fit(feature_matrix(train, features), train["target12"], verbose=False)
            prediction = fitted_xgb.predict(feature_matrix(test, features))
            parameters = {**parameters, "n_estimators": trees}
        else:
            raise ValueError(f"Unsupported model: {model_name}")
        outputs.append(
            prediction_records(
                test,
                prediction,
                bt_prediction,
                model_name,
                endpoint,
                seed,
                outer_fold,
                bt_model,
            )
        )
        tuning.append(
            {
                "endpoint": endpoint,
                "model": model_name,
                "seed": seed,
                "outer_fold": outer_fold,
                "bt_model": bt_model,
                "parameters": json.dumps(parameters, sort_keys=True),
                "inner_mae": inner_mae,
                "runtime_seconds": time.perf_counter() - started,
            }
        )
    return pd.concat(outputs, ignore_index=True), tuning


def summarize(predictions: pd.DataFrame) -> pd.DataFrame:
    seed_rows: list[dict[str, object]] = []
    for (model, endpoint, seed), frame in predictions.groupby(["model", "endpoint", "seed"]):
        seed_rows.append(
            {"model": model, "endpoint": endpoint, "seed": seed, **prediction_metrics(frame)}
        )
    seed_metrics = pd.DataFrame(seed_rows)
    summary_rows: list[dict[str, object]] = []
    for (model, endpoint), metrics in seed_metrics.groupby(["model", "endpoint"]):
        source = predictions.loc[
            predictions["model"].eq(model) & predictions["endpoint"].eq(endpoint)
        ]
        averaged = (
            source.groupby(["sample_id", "casrn", "cohort"], as_index=False)
            .agg(
                target12=("target12", "first"),
                target7=("target7", "first"),
                delta=("delta", "first"),
                prediction=("prediction", "mean"),
                bt_prediction=("bt_prediction", "mean"),
            )
        )
        ci_low, ci_high = bootstrap_delta_mae(averaged)
        row: dict[str, object] = {
            "model": model,
            "endpoint": endpoint,
            "n_samples": len(averaged),
            "n_chemicals": averaged["casrn"].nunique(),
            "delta_mae_ci_low": ci_low,
            "delta_mae_ci_high": ci_high,
        }
        for metric in [
            "mae_y12",
            "rmse_y12",
            "spearman_y12",
            "mae_delta",
            "spearman_delta",
            "delta_mae_vs_bt",
            "relative_gain_percent",
        ]:
            row[f"{metric}_mean"] = float(metrics[metric].mean())
            row[f"{metric}_std"] = float(metrics[metric].std(ddof=1))
        summary_rows.append(row)
    return pd.DataFrame(summary_rows).sort_values(["endpoint", "model"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    parser.add_argument("--models", nargs="+", choices=ALL_MODELS, default=list(ALL_MODELS))
    parser.add_argument("--seeds", nargs="+", type=int)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    data_root = Path(config["data_root"])
    mapping_path = Path(config["chemical_mapping"])
    results_dir = Path(config["results_dir"])
    checkpoint_dir = results_dir / "baseline_checkpoints"
    tuning_checkpoint_dir = results_dir / "baseline_tuning_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    tuning_checkpoint_dir.mkdir(parents=True, exist_ok=True)

    frame = build_longitudinal_table(data_root)
    frame["sample_id"] = (
        frame["cohort"].astype(str) + "|" + frame["Plate.SN"].astype(str) + "|" + frame["well"].astype(str)
    )
    frame["cohort_toxcast"] = frame["cohort"].eq("ToxCast").astype("int8")
    early_features = primary_feature_columns(frame) + ["cohort_toxcast"]
    chemistry_columns: list[str] = []
    if "B4" in args.models:
        frame, chemistry_columns = attach_chemistry(frame, mapping_path)
    chemistry_features = chemistry_columns + ["log10_1p_dose", "cohort_toxcast"]

    seeds = args.seeds if args.seeds is not None else list(config["seeds"])
    endpoints = list(config.get("primary_endpoints", PRIMARY_ENDPOINTS))
    tuning_rows: list[dict[str, object]] = []
    for seed in seeds:
        folds = list(outer_folds(frame, seed=seed, n_splits=int(config["outer_folds"])))
        for outer_fold, (train_idx, test_idx) in enumerate(folds):
            outer_train_all = frame.iloc[train_idx]
            outer_test_all = frame.iloc[test_idx]
            for endpoint in endpoints:
                checkpoint = checkpoint_dir / f"seed{seed}_fold{outer_fold}_{endpoint}.csv"
                tuning_checkpoint = (
                    tuning_checkpoint_dir / f"seed{seed}_fold{outer_fold}_{endpoint}.csv"
                )
                existing = pd.read_csv(checkpoint) if checkpoint.exists() and not args.overwrite else pd.DataFrame()
                completed = set(existing["model"]) if not existing.empty else set()
                pending = [model for model in args.models if model not in completed]
                if not pending:
                    print(f"SKIP seed={seed} fold={outer_fold} endpoint={endpoint}", flush=True)
                    continue
                train = endpoint_frame(outer_train_all, endpoint).reset_index(drop=True)
                test = endpoint_frame(outer_test_all, endpoint).reset_index(drop=True)
                print(
                    f"RUN seed={seed} fold={outer_fold} endpoint={endpoint} models={','.join(pending)} "
                    f"train={len(train)} test={len(test)}",
                    flush=True,
                )
                output, task_tuning = run_task(
                    train,
                    test,
                    endpoint,
                    seed,
                    outer_fold,
                    pending,
                    int(config["inner_folds"]),
                    config["xgboost"],
                    early_features,
                    chemistry_features,
                )
                combined = pd.concat([existing, output], ignore_index=True)
                combined.to_csv(checkpoint, index=False)
                existing_tuning = (
                    pd.read_csv(tuning_checkpoint)
                    if tuning_checkpoint.exists() and not args.overwrite
                    else pd.DataFrame()
                )
                combined_tuning = pd.concat(
                    [existing_tuning, pd.DataFrame(task_tuning)], ignore_index=True
                )
                combined_tuning.to_csv(tuning_checkpoint, index=False)
                tuning_rows.extend(task_tuning)

    checkpoint_files = sorted(checkpoint_dir.glob("*.csv"))
    predictions = pd.concat([pd.read_csv(path) for path in checkpoint_files], ignore_index=True)
    predictions = predictions.loc[
        predictions["seed"].isin(seeds) & predictions["model"].isin(args.models)
    ]
    predictions.to_csv(results_dir / "baseline_predictions.csv", index=False)
    summary = summarize(predictions)
    summary.to_csv(results_dir / "baselines.csv", index=False)
    tuning_checkpoint_files = sorted(tuning_checkpoint_dir.glob("*.csv"))
    if tuning_checkpoint_files:
        tuning = pd.concat(
            [pd.read_csv(path) for path in tuning_checkpoint_files], ignore_index=True
        )
        tuning = tuning.loc[tuning["seed"].isin(seeds) & tuning["model"].isin(args.models)]
        tuning.to_csv(results_dir / "baseline_tuning.csv", index=False)

    manifest = {
        "preregistration_commit": "8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "config": str(args.config),
        "config_sha256": file_sha256(args.config),
        "models": args.models,
        "seeds": seeds,
        "rows": len(predictions),
    }
    (results_dir / "baseline_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(summary.to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
