"""Evaluate pre-registered Gate M1 from completed held-out predictions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error

from meacompass.evaluate import bootstrap_paired_mae
from meacompass.train_baselines import summarize
from meacompass.train_baselines import file_sha256


JOIN_KEYS = ["sample_id", "casrn", "cohort", "endpoint", "seed", "outer_fold"]


def merge_m1_and_b3(
    m1: pd.DataFrame, baselines: pd.DataFrame, bt_plus: pd.DataFrame
) -> pd.DataFrame:
    b3 = baselines.loc[baselines["model"].eq("B3")].copy()
    if m1.duplicated(JOIN_KEYS).any() or b3.duplicated(JOIN_KEYS).any():
        raise ValueError("M1/B3 prediction keys must be unique")
    merged = m1.merge(
        b3[JOIN_KEYS + ["prediction"]].rename(columns={"prediction": "b3_prediction"}),
        on=JOIN_KEYS,
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != len(m1) or len(merged) != len(b3):
        raise ValueError(
            f"M1 and B3 held-out rows do not match: M1={len(m1)}, B3={len(b3)}, "
            f"joined={len(merged)}"
        )
    if bt_plus.duplicated(JOIN_KEYS).any():
        raise ValueError("BT+ prediction keys must be unique")
    merged = merged.merge(
        bt_plus[JOIN_KEYS + ["prediction"]].rename(
            columns={"prediction": "bt_plus_prediction"}
        ),
        on=JOIN_KEYS,
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != len(m1):
        raise ValueError(
            f"M1 and BT+ held-out rows do not match: M1={len(m1)}, joined={len(merged)}"
        )
    return merged


def gate_table(merged: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for endpoint, source in merged.groupby("endpoint"):
        averaged = (
            source.groupby(["sample_id", "casrn", "cohort"], as_index=False)
            .agg(
                target12=("target12", "first"),
                m1_prediction=("prediction", "mean"),
                b3_prediction=("b3_prediction", "mean"),
                bt_prediction=("bt_prediction", "mean"),
                bt_plus_prediction=("bt_plus_prediction", "mean"),
            )
        )
        actual = averaged["target12"]
        m1_mae = mean_absolute_error(actual, averaged["m1_prediction"])
        b3_mae = mean_absolute_error(actual, averaged["b3_prediction"])
        bt_mae = mean_absolute_error(actual, averaged["bt_prediction"])
        bt_plus_mae = mean_absolute_error(actual, averaged["bt_plus_prediction"])
        b3_low, b3_high = bootstrap_paired_mae(
            averaged, "m1_prediction", "b3_prediction"
        )
        bt_low, bt_high = bootstrap_paired_mae(
            averaged, "m1_prediction", "bt_prediction"
        )
        bt_plus_low, bt_plus_high = bootstrap_paired_mae(
            averaged, "m1_prediction", "bt_plus_prediction"
        )
        beats_b3 = bool(b3_high < 0)
        beats_bt = bool(bt_high < 0)
        rows.append(
            {
                "endpoint": endpoint,
                "n_samples": len(averaged),
                "n_chemicals": averaged["casrn"].nunique(),
                "m1_mae": m1_mae,
                "b3_mae": b3_mae,
                "bt_mae": bt_mae,
                "bt_plus_mae": bt_plus_mae,
                "delta_mae_vs_b3": m1_mae - b3_mae,
                "delta_mae_vs_b3_ci_low": b3_low,
                "delta_mae_vs_b3_ci_high": b3_high,
                "delta_mae_vs_bt": m1_mae - bt_mae,
                "delta_mae_vs_bt_ci_low": bt_low,
                "delta_mae_vs_bt_ci_high": bt_high,
                "delta_mae_vs_bt_plus": m1_mae - bt_plus_mae,
                "delta_mae_vs_bt_plus_ci_low": bt_plus_low,
                "delta_mae_vs_bt_plus_ci_high": bt_plus_high,
                "beats_b3": beats_b3,
                "beats_bt": beats_bt,
                "gate_endpoint_pass": beats_b3 or beats_bt,
            }
        )
    return pd.DataFrame(rows).sort_values("endpoint")


def gate_m1_decision(table: pd.DataFrame) -> tuple[str, int]:
    """Apply the Phase 3 main-model rule registered before M1 completion."""
    endpoints_beating_b3 = int(table["beats_b3"].sum())
    decision = "SELECT_M1" if endpoints_beating_b3 >= 2 else "SELECT_B3"
    return decision, endpoints_beating_b3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checkpoint_files = sorted((args.results_dir / "m1_checkpoints").glob("*.csv"))
    tuning_files = sorted((args.results_dir / "m1_tuning_checkpoints").glob("*.json"))
    if len(checkpoint_files) != 75 or len(tuning_files) != 75:
        raise RuntimeError(
            "Gate M1 requires exactly 75 prediction and 75 tuning checkpoints; "
            f"found {len(checkpoint_files)} and {len(tuning_files)}"
        )
    m1 = pd.concat([pd.read_csv(path) for path in checkpoint_files], ignore_index=True)
    baselines = pd.read_csv(args.results_dir / "baseline_predictions.csv")
    bt_plus = pd.read_csv(args.results_dir / "bt_plus_predictions.csv")
    merged = merge_m1_and_b3(m1, baselines, bt_plus)
    summary = summarize(m1)
    summary.to_csv(args.results_dir / "m1.csv", index=False)
    m1.to_csv(args.results_dir / "m1_predictions.csv", index=False)
    table = gate_table(merged)
    table.to_csv(args.results_dir / "m1_gate.csv", index=False)
    tuning = pd.DataFrame(
        [json.loads(path.read_text(encoding="utf-8")) for path in tuning_files]
    ).sort_values(["seed", "outer_fold", "endpoint"])
    tuning.to_json(args.results_dir / "m1_tuning.json", orient="records", indent=2)
    manifest = {
        "preregistration_commit": "8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0",
        "m1_implementation_commit": "2085c30",
        "evaluation_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True
        ).strip(),
        "config": "configs/baselines.yaml",
        "config_sha256": file_sha256(Path("configs/baselines.yaml")),
        "seeds": sorted(int(value) for value in m1["seed"].unique()),
        "features": int(tuning["feature_count"].iloc[0]),
        "prediction_checkpoints": len(checkpoint_files),
        "tuning_records": len(tuning_files),
        "rows": len(m1),
    }
    (args.results_dir / "m1_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    decision, passes = gate_m1_decision(table)
    print(table.to_string(index=False))
    print(f"GATE M1: {decision} (M1 beats B3 on {passes}/5 endpoints)")


if __name__ == "__main__":
    main()
