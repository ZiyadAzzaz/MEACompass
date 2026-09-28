"""Frozen-model XGBoost contribution audit and descriptive held-out cases."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
import yaml

from neurochip.baselines import endpoint_frame, fit_baseline, predict_baseline
from neurochip.chem import attach_chemistry
from neurochip.data import PRIMARY_ENDPOINTS, build_longitudinal_table, primary_feature_columns
from neurochip.sanity_gate import attach_identity
from neurochip.splits import outer_folds
from neurochip.train_baselines import feature_matrix, make_xgb
from neurochip.train_m1 import m1_training_target


CASE_ENDPOINTS = ("meanfiringrate", "nAE", "r")


def feature_family(feature: str) -> str:
    if feature.startswith("div5_"):
        return "DIV5 neural"
    if feature.startswith("div7_"):
        return "DIV7 neural"
    if feature.startswith("morgan_"):
        return "Morgan chemistry"
    if feature.startswith("desc_"):
        return "RDKit descriptor"
    if feature == "log10_1p_dose":
        return "dose"
    if feature == "cohort_toxcast":
        return "cohort"
    return "structure availability"


def select_cases(results_dir: Path) -> pd.DataFrame:
    demo = pd.read_csv(results_dir / "demo_predictions.csv")
    source = demo.loc[
        demo["endpoint"].isin(CASE_ENDPOINTS) & demo["dose"].gt(0)
    ].copy()
    endpoint_scale = source.groupby("endpoint").apply(
        lambda part: np.mean(np.abs(part["target12"] - part["prediction"])),
        include_groups=False,
    )
    source["scaled_absolute_error"] = (
        np.abs(source["target12"] - source["prediction"])
        / source["endpoint"].map(endpoint_scale)
    )
    scores = source.groupby(
        ["sample_id", "casrn", "trt", "cohort", "dose"], as_index=False
    ).agg(
        endpoints=("endpoint", "nunique"),
        mean_scaled_absolute_error=("scaled_absolute_error", "mean"),
        all_endpoints_accepted=("accepted", "all"),
    )
    scores = scores.loc[scores["endpoints"].eq(len(CASE_ENDPOINTS))]

    def distinct_extremes(frame: pd.DataFrame, ascending: bool, count: int) -> list[pd.Series]:
        rows: list[pd.Series] = []
        used: set[str] = set()
        for _, row in frame.sort_values("mean_scaled_absolute_error", ascending=ascending).iterrows():
            if row["casrn"] in used:
                continue
            rows.append(row)
            used.add(str(row["casrn"]))
            if len(rows) == count:
                break
        return rows

    chosen = distinct_extremes(scores, True, 3) + distinct_extremes(scores, False, 2)
    output = pd.DataFrame(chosen).reset_index(drop=True)
    output["case_type"] = ["correct"] * 3 + ["failure"] * 2
    output["selection_note"] = (
        "post-lock descriptive extreme by mean endpoint-scaled absolute error; not performance estimation"
    )
    return output


def run_interpretability(
    frame: pd.DataFrame,
    chemistry_columns: list[str],
    config: dict[str, object],
    results_dir: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    features = list(
        dict.fromkeys(primary_feature_columns(frame) + ["cohort_toxcast"] + chemistry_columns)
    )
    tuning = {
        (int(record["outer_fold"]), str(record["endpoint"])): record
        for record in [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((results_dir / "m1_tuning_checkpoints").glob("seed0_*.json"))
        ]
    }
    if len(tuning) != 25:
        raise RuntimeError(f"Interpretability requires 25 seed-0 tuning records; found {len(tuning)}")
    cases = select_cases(results_dir)
    case_ids = set(cases["sample_id"])
    importance_sum = {endpoint: np.zeros(len(features), dtype=float) for endpoint in PRIMARY_ENDPOINTS}
    importance_count = {endpoint: 0 for endpoint in PRIMARY_ENDPOINTS}
    variants: dict[str, set[str]] = {endpoint: set() for endpoint in PRIMARY_ENDPOINTS}
    contribution_rows: list[dict[str, object]] = []

    for fold, (train_idx, test_idx) in enumerate(outer_folds(frame, seed=0, n_splits=int(config["outer_folds"]))):
        for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
            train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
            test = endpoint_frame(frame.iloc[test_idx], endpoint).reset_index(drop=True)
            record = tuning[(fold, endpoint)]
            parameters = dict(record["parameters"])
            trees = int(parameters.pop("n_estimators"))
            variant = str(record["variant"])
            bt_model = str(record["bt_model"])
            variants[endpoint].add(variant)
            if variant == "bt_residual":
                fitted_bt = fit_baseline(bt_model, train, endpoint)
                train_bt = predict_baseline(fitted_bt, train)
                test_bt = predict_baseline(fitted_bt, test)
            else:
                train_bt = np.zeros(len(train))
                test_bt = np.zeros(len(test))
            model = make_xgb(parameters, config["xgboost"], seed=0, trees=trees)
            model.fit(
                feature_matrix(train, features),
                m1_training_target(train, variant, train_bt),
                verbose=False,
            )
            matrix = feature_matrix(test, features)
            contributions = model.get_booster().predict(
                xgb.DMatrix(matrix), pred_contribs=True
            )
            importance_sum[endpoint] += np.abs(contributions[:, :-1]).sum(axis=0)
            importance_count[endpoint] += len(test)
            selected_indices = [index for index, value in enumerate(test["sample_id"]) if value in case_ids]
            for index in selected_indices:
                order = np.argsort(np.abs(contributions[index, :-1]))[::-1][:8]
                for rank, feature_index in enumerate(order, start=1):
                    contribution_rows.append(
                        {
                            "sample_id": test.iloc[index]["sample_id"],
                            "casrn": test.iloc[index]["casrn"],
                            "endpoint": endpoint,
                            "outer_fold": fold,
                            "variant": variant,
                            "bt_anchor_prediction": test_bt[index] if variant == "bt_residual" else 0.0,
                            "model_base_value": contributions[index, -1],
                            "feature": features[feature_index],
                            "family": feature_family(features[feature_index]),
                            "feature_value": test.iloc[index][features[feature_index]],
                            "contribution": contributions[index, feature_index],
                            "absolute_rank": rank,
                        }
                    )
            print(f"RUN interpretability fold={fold} endpoint={endpoint}", flush=True)

    importance_rows: list[dict[str, object]] = []
    for endpoint in PRIMARY_ENDPOINTS:
        values = importance_sum[endpoint] / importance_count[endpoint]
        order = np.argsort(values)[::-1]
        for rank, index in enumerate(order, start=1):
            importance_rows.append(
                {
                    "endpoint": endpoint,
                    "feature": features[index],
                    "family": feature_family(features[index]),
                    "mean_absolute_contribution": values[index],
                    "rank": rank,
                    "seed": 0,
                    "outer_folds": 5,
                    "variants_present": "+".join(sorted(variants[endpoint])),
                }
            )
    importance = pd.DataFrame(importance_rows)
    contributions = pd.DataFrame(contribution_rows)
    importance.to_csv(results_dir / "feature_importance.csv", index=False)
    cases.to_csv(results_dir / "case_studies.csv", index=False)
    contributions.to_csv(results_dir / "case_contributions.csv", index=False)
    return importance, cases, contributions


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    base = attach_identity(build_longitudinal_table(Path(config["data_root"])))
    frame, chemistry_columns = attach_chemistry(base, Path(config["chemical_mapping"]))
    importance, cases, _ = run_interpretability(
        frame, chemistry_columns, config, Path(config["results_dir"])
    )
    print(cases.to_string(index=False))
    print(importance.loc[importance["rank"].le(5)].to_string(index=False))


if __name__ == "__main__":
    main()
