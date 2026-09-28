"""Pre-registered M1 early-measurement plus chemistry evaluation."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error

from neurochip.baselines import endpoint_frame, fit_baseline, predict_baseline
from neurochip.chem import attach_chemistry
from neurochip.data import (
    PRIMARY_ENDPOINTS,
    build_longitudinal_table,
    primary_feature_columns,
    validate_time_causal_features,
)
from neurochip.splits import outer_folds
from neurochip.train_baselines import (
    feature_matrix,
    file_sha256,
    make_xgb,
    prediction_records,
    select_best_trivial,
    summarize,
    xgb_grid,
)


VARIANTS = ("direct", "bt_residual")


def m1_training_target(
    frame: pd.DataFrame, variant: str, bt_prediction: np.ndarray
) -> np.ndarray:
    """Return the target used by a registered M1 variant."""
    if variant == "direct":
        return frame["target12"].to_numpy()
    if variant == "bt_residual":
        return frame["target12"].to_numpy() - bt_prediction
    raise ValueError(f"Unknown M1 variant: {variant}")


def compose_m1_prediction(
    model_prediction: np.ndarray, variant: str, bt_prediction: np.ndarray
) -> np.ndarray:
    """Convert direct or residual model output into a DIV12 prediction."""
    if variant == "direct":
        return model_prediction
    if variant == "bt_residual":
        return bt_prediction + model_prediction
    raise ValueError(f"Unknown M1 variant: {variant}")


def tune_m1(
    train: pd.DataFrame,
    features: list[str],
    endpoint: str,
    bt_model: str,
    seed: int,
    inner_folds: int,
    config: dict[str, object],
) -> tuple[str, dict[str, object], int, float]:
    """Jointly select direct/residual variant and XGBoost settings by inner CV."""
    split_data: list[dict[str, object]] = []
    for inner_train_idx, inner_valid_idx in outer_folds(
        train, seed=seed, n_splits=inner_folds
    ):
        inner_train = train.iloc[inner_train_idx]
        inner_valid = train.iloc[inner_valid_idx]
        fitted_bt = fit_baseline(bt_model, inner_train, endpoint)
        split_data.append(
            {
                "train_x": feature_matrix(inner_train, features),
                "valid_x": feature_matrix(inner_valid, features),
                "train_actual": inner_train["target12"].to_numpy(),
                "valid_actual": inner_valid["target12"].to_numpy(),
                "train_bt": predict_baseline(fitted_bt, inner_train),
                "valid_bt": predict_baseline(fitted_bt, inner_valid),
            }
        )

    def score_candidate(
        candidate: tuple[str, dict[str, object]],
    ) -> tuple[float, str, dict[str, object], int]:
        variant, parameters = candidate
        actual_parts: list[np.ndarray] = []
        prediction_parts: list[np.ndarray] = []
        fold_trees: list[int] = []
        for split in split_data:
            train_actual = np.asarray(split["train_actual"])
            valid_actual = np.asarray(split["valid_actual"])
            train_bt = np.asarray(split["train_bt"])
            valid_bt = np.asarray(split["valid_bt"])
            train_target = (
                train_actual if variant == "direct" else train_actual - train_bt
            )
            valid_target = (
                valid_actual if variant == "direct" else valid_actual - valid_bt
            )
            model = make_xgb(
                parameters,
                {**config, "n_jobs": 1},
                seed=seed,
                trees=int(config["n_estimators"]),
            )
            model.set_params(early_stopping_rounds=int(config["early_stopping_rounds"]))
            model.fit(
                split["train_x"],
                train_target,
                eval_set=[(split["valid_x"], valid_target)],
                verbose=False,
            )
            raw_prediction = model.predict(split["valid_x"])
            final_prediction = (
                raw_prediction if variant == "direct" else valid_bt + raw_prediction
            )
            actual_parts.append(valid_actual)
            prediction_parts.append(final_prediction)
            iteration = getattr(model, "best_iteration", int(config["n_estimators"]) - 1)
            fold_trees.append(int(iteration) + 1)
        score = mean_absolute_error(
            np.concatenate(actual_parts), np.concatenate(prediction_parts)
        )
        return float(score), variant, parameters, max(1, int(np.median(fold_trees)))

    candidates = [
        (variant, parameters) for variant in VARIANTS for parameters in xgb_grid(config)
    ]
    workers = min(int(config.get("parallel_configs", 4)), len(candidates))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        scores = list(executor.map(score_candidate, candidates))
    best_mae, best_variant, best_parameters, best_trees = min(
        scores, key=lambda item: (item[0], item[1], json.dumps(item[2], sort_keys=True))
    )
    return best_variant, best_parameters, best_trees, best_mae


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    parser.add_argument("--seeds", nargs="+", type=int)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    data_root = Path(config["data_root"])
    mapping_path = Path(config["chemical_mapping"])
    results_dir = Path(config["results_dir"])
    checkpoint_dir = results_dir / "m1_checkpoints"
    tuning_checkpoint_dir = results_dir / "m1_tuning_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    tuning_checkpoint_dir.mkdir(parents=True, exist_ok=True)

    frame = build_longitudinal_table(data_root)
    frame["sample_id"] = (
        frame["cohort"].astype(str)
        + "|"
        + frame["Plate.SN"].astype(str)
        + "|"
        + frame["well"].astype(str)
    )
    frame["cohort_toxcast"] = frame["cohort"].eq("ToxCast").astype("int8")
    frame, chemistry_columns = attach_chemistry(frame, mapping_path)
    features = list(
        dict.fromkeys(
            primary_feature_columns(frame) + ["cohort_toxcast"] + chemistry_columns
        )
    )
    validate_time_causal_features(features)

    seeds = args.seeds if args.seeds is not None else list(config["seeds"])
    endpoints = list(config.get("primary_endpoints", PRIMARY_ENDPOINTS))
    for seed in seeds:
        folds = list(outer_folds(frame, seed=seed, n_splits=int(config["outer_folds"])))
        for outer_fold, (train_idx, test_idx) in enumerate(folds):
            for endpoint in endpoints:
                checkpoint = checkpoint_dir / f"seed{seed}_fold{outer_fold}_{endpoint}.csv"
                tuning_checkpoint = (
                    tuning_checkpoint_dir / f"seed{seed}_fold{outer_fold}_{endpoint}.json"
                )
                if checkpoint.exists() and tuning_checkpoint.exists() and not args.overwrite:
                    print(
                        f"SKIP seed={seed} fold={outer_fold} endpoint={endpoint}",
                        flush=True,
                    )
                    continue
                train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
                test = endpoint_frame(frame.iloc[test_idx], endpoint).reset_index(drop=True)
                bt_model = select_best_trivial(
                    train, endpoint, seed, int(config["inner_folds"])
                )
                print(
                    f"RUN seed={seed} fold={outer_fold} endpoint={endpoint} "
                    f"bt={bt_model} train={len(train)} test={len(test)}",
                    flush=True,
                )
                started = time.perf_counter()
                variant, parameters, trees, inner_mae = tune_m1(
                    train,
                    features,
                    endpoint,
                    bt_model,
                    seed,
                    int(config["inner_folds"]),
                    config["xgboost"],
                )
                fitted_bt = fit_baseline(bt_model, train, endpoint)
                train_bt = predict_baseline(fitted_bt, train)
                test_bt = predict_baseline(fitted_bt, test)
                train_target = m1_training_target(train, variant, train_bt)
                model = make_xgb(
                    parameters, config["xgboost"], seed=seed, trees=trees
                )
                model.fit(feature_matrix(train, features), train_target, verbose=False)
                raw_prediction = model.predict(feature_matrix(test, features))
                prediction = compose_m1_prediction(raw_prediction, variant, test_bt)
                output = prediction_records(
                    test,
                    prediction,
                    test_bt,
                    "M1",
                    endpoint,
                    seed,
                    outer_fold,
                    bt_model,
                )
                output["variant"] = variant
                output.to_csv(checkpoint, index=False)
                tuning_record = {
                    "endpoint": endpoint,
                    "model": "M1",
                    "variant": variant,
                    "seed": seed,
                    "outer_fold": outer_fold,
                    "bt_model": bt_model,
                    "parameters": {**parameters, "n_estimators": trees},
                    "inner_mae": inner_mae,
                    "runtime_seconds": time.perf_counter() - started,
                    "feature_count": len(features),
                }
                tuning_checkpoint.write_text(
                    json.dumps(tuning_record, indent=2), encoding="utf-8"
                )

    predictions = pd.concat(
        [pd.read_csv(path) for path in sorted(checkpoint_dir.glob("*.csv"))],
        ignore_index=True,
    )
    predictions = predictions.loc[predictions["seed"].isin(seeds)]
    predictions.to_csv(results_dir / "m1_predictions.csv", index=False)
    summarize(predictions).to_csv(results_dir / "m1.csv", index=False)
    tuning_records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(tuning_checkpoint_dir.glob("*.json"))
    ]
    pd.DataFrame(tuning_records).to_json(
        results_dir / "m1_tuning.json", orient="records", indent=2
    )
    manifest = {
        "preregistration_commit": "8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0",
        "code_commit": __import__("subprocess")
        .check_output(["git", "rev-parse", "HEAD"], text=True)
        .strip(),
        "config": str(args.config),
        "config_sha256": file_sha256(args.config),
        "seeds": seeds,
        "features": len(features),
        "rows": len(predictions),
    }
    (results_dir / "m1_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(summarize(predictions).to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
