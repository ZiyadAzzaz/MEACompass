"""Build inner-selected BT+ held-out predictions for Sanity Gate S."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from neurochip.baselines import endpoint_frame, fit_baseline, predict_baseline
from neurochip.data import PRIMARY_ENDPOINTS, build_longitudinal_table
from neurochip.splits import outer_folds
from neurochip.train_baselines import prediction_records, select_best_baseline, summarize


BT_PLUS_CANDIDATES = ("B0", "B1", "B1b", "B2")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    results_dir = Path(config["results_dir"])
    checkpoint_dir = results_dir / "bt_plus_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    frame = build_longitudinal_table(Path(config["data_root"]))
    frame["sample_id"] = (
        frame["cohort"].astype(str)
        + "|"
        + frame["Plate.SN"].astype(str)
        + "|"
        + frame["well"].astype(str)
    )
    endpoints = list(config.get("primary_endpoints", PRIMARY_ENDPOINTS))
    seeds = list(config["seeds"])
    for seed in seeds:
        for outer_fold, (train_idx, test_idx) in enumerate(
            outer_folds(frame, seed=seed, n_splits=int(config["outer_folds"]))
        ):
            for endpoint in endpoints:
                checkpoint = checkpoint_dir / f"seed{seed}_fold{outer_fold}_{endpoint}.csv"
                if checkpoint.exists():
                    continue
                train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
                test = endpoint_frame(frame.iloc[test_idx], endpoint).reset_index(drop=True)
                selected = select_best_baseline(
                    train,
                    endpoint,
                    seed,
                    int(config["inner_folds"]),
                    BT_PLUS_CANDIDATES,
                )
                fitted = fit_baseline(selected, train, endpoint)
                prediction = predict_baseline(fitted, test)
                output = prediction_records(
                    test,
                    prediction,
                    prediction,
                    "BT+",
                    endpoint,
                    seed,
                    outer_fold,
                    selected,
                )
                output = output.rename(columns={"bt_model": "bt_plus_model"})
                output.to_csv(checkpoint, index=False)

    files = sorted(checkpoint_dir.glob("*.csv"))
    if len(files) != 75:
        raise RuntimeError(f"BT+ requires 75 checkpoints; found {len(files)}")
    predictions = pd.concat([pd.read_csv(path) for path in files], ignore_index=True)
    predictions.to_csv(results_dir / "bt_plus_predictions.csv", index=False)
    summarize(predictions.rename(columns={"bt_plus_model": "bt_model"})).to_csv(
        results_dir / "bt_plus.csv", index=False
    )
    selections = (
        predictions[["endpoint", "seed", "outer_fold", "bt_plus_model"]]
        .drop_duplicates()
        .sort_values(["endpoint", "seed", "outer_fold"])
    )
    selections.to_csv(results_dir / "bt_plus_selections.csv", index=False)
    manifest = {
        "candidates": list(BT_PLUS_CANDIDATES),
        "selection": "inner_validation_mae_only",
        "outer_test_role": "evaluation_only",
        "checkpoints": len(files),
    }
    (results_dir / "bt_plus_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
