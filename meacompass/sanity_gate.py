"""Registered Sanity Gate S analyses and negative controls."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error

from meacompass.baselines import endpoint_frame, fit_baseline, predict_baseline
from meacompass.data import PRIMARY_ENDPOINTS, build_longitudinal_table, primary_feature_columns
from meacompass.evaluate import bootstrap_paired_mae
from meacompass.splits import outer_folds
from meacompass.train_baselines import (
    feature_matrix,
    make_xgb,
    prediction_records,
    select_best_baseline,
    summarize,
    tune_xgb,
)


KEYS = ["sample_id", "casrn", "cohort", "endpoint", "seed", "outer_fold"]
BT_PLUS_CANDIDATES = ("B0", "B1", "B1b", "B2")
PERMUTATION_SEED = 20260928


def attach_identity(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.copy()
    output["sample_id"] = (
        output["cohort"].astype(str)
        + "|"
        + output["Plate.SN"].astype(str)
        + "|"
        + output["well"].astype(str)
    )
    output["cohort_toxcast"] = output["cohort"].eq("ToxCast").astype("int8")
    return output


def load_complete_predictions(results_dir: Path) -> pd.DataFrame:
    baseline = pd.read_csv(results_dir / "baseline_predictions.csv")
    m1_files = sorted((results_dir / "m1_checkpoints").glob("*.csv"))
    bt_files = sorted((results_dir / "bt_plus_checkpoints").glob("*.csv"))
    if len(m1_files) != 75 or len(bt_files) != 75:
        raise RuntimeError("Gate S requires 75 M1 and 75 BT+ checkpoints")
    m1 = pd.concat([pd.read_csv(path) for path in m1_files], ignore_index=True)
    bt_plus = pd.concat([pd.read_csv(path) for path in bt_files], ignore_index=True)
    selected = baseline.loc[baseline["model"].isin(["B3"])].copy()
    selected = pd.concat([selected, m1], ignore_index=True)
    reference = bt_plus[KEYS + ["prediction"]].rename(
        columns={"prediction": "bt_plus_prediction"}
    )
    merged = selected.merge(reference, on=KEYS, how="inner", validate="many_to_one")
    if len(merged) != len(selected):
        raise ValueError("B3/M1 and BT+ held-out rows do not align")
    return merged


def paired_summary(
    frame: pd.DataFrame,
    strata: list[str] | None = None,
) -> pd.DataFrame:
    group_columns = ["model", "endpoint"] + (strata or [])
    rows: list[dict[str, object]] = []
    for keys, source in frame.groupby(group_columns, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        labels = dict(zip(group_columns, keys, strict=True))
        source = source.copy()
        candidate_mae = mean_absolute_error(source["target12"], source["prediction"])
        original_bt_mae = mean_absolute_error(source["target12"], source["bt_prediction"])
        bt_plus_mae = mean_absolute_error(source["target12"], source["bt_plus_prediction"])
        original_low, original_high = bootstrap_paired_mae(
            source, "prediction", "bt_prediction"
        )
        plus_low, plus_high = bootstrap_paired_mae(
            source, "prediction", "bt_plus_prediction"
        )
        rows.append(
            {
                **labels,
                "n_rows": len(source),
                "n_chemicals": source["casrn"].nunique(),
                "mae": candidate_mae,
                "original_bt_mae": original_bt_mae,
                "bt_plus_mae": bt_plus_mae,
                "delta_mae_vs_original_bt": candidate_mae - original_bt_mae,
                "delta_mae_vs_original_bt_ci_low": original_low,
                "delta_mae_vs_original_bt_ci_high": original_high,
                "relative_gain_vs_original_bt_percent": 100 * (original_bt_mae - candidate_mae) / original_bt_mae,
                "delta_mae_vs_bt_plus": candidate_mae - bt_plus_mae,
                "delta_mae_vs_bt_plus_ci_low": plus_low,
                "delta_mae_vs_bt_plus_ci_high": plus_high,
                "relative_gain_vs_bt_plus_percent": 100 * (bt_plus_mae - candidate_mae) / bt_plus_mae,
            }
        )
    return pd.DataFrame(rows).sort_values(group_columns)


def dose_strata(frame: pd.DataFrame, config: dict[str, object]) -> pd.DataFrame:
    output: list[pd.DataFrame] = []
    for seed in config["seeds"]:
        folds = list(outer_folds(frame, int(seed), int(config["outer_folds"])))
        for fold, (train_idx, _) in enumerate(folds):
            train_all = frame.iloc[train_idx]
            for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
                train = endpoint_frame(train_all, endpoint)
                positive = train.loc[train["dose"].gt(0), "dose"]
                if positive.empty:
                    raise ValueError(f"No positive training doses for {endpoint}, seed {seed}, fold {fold}")
                low_cut, high_cut = positive.quantile([1 / 3, 2 / 3]).to_numpy()
                rows = pd.DataFrame(
                    {
                        "sample_id": frame["sample_id"],
                        "endpoint": endpoint,
                        "seed": int(seed),
                        "outer_fold": fold,
                        "dose": frame["dose"],
                    }
                )
                rows["dose_stratum"] = np.select(
                    [
                        rows["dose"].eq(0),
                        rows["dose"].gt(0) & rows["dose"].le(low_cut),
                        rows["dose"].gt(low_cut) & rows["dose"].le(high_cut),
                    ],
                    ["zero", "low", "mid"],
                    default="high",
                )
                rows["low_cut"] = float(low_cut)
                rows["high_cut"] = float(high_cut)
                output.append(rows)
    return pd.concat(output, ignore_index=True)


def permute_targets_by_chemical(
    train: pd.DataFrame, endpoint: str, fold: int
) -> tuple[pd.DataFrame, dict[str, str]]:
    output = train.copy()
    groups = np.asarray(sorted(output["casrn"].unique()))
    digest = int(hashlib.sha256(endpoint.encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng(PERMUTATION_SEED + fold * 1009 + digest)
    donors = rng.permutation(groups)
    while np.any(donors == groups):
        donors = rng.permutation(groups)
    mapping = dict(zip(groups, donors, strict=True))
    original = output.copy()
    for recipient, donor in mapping.items():
        recipient_index = (
            output.loc[output["casrn"].eq(recipient)]
            .sort_values(["dose", "Plate.SN", "well"])
            .index
        )
        donor_values = (
            original.loc[original["casrn"].eq(donor)]
            .sort_values(["dose", "Plate.SN", "well"])["target12"]
            .to_numpy()
        )
        source_quantiles = np.linspace(0, 1, len(donor_values))
        target_quantiles = np.linspace(0, 1, len(recipient_index))
        output.loc[recipient_index, "target12"] = np.interp(
            target_quantiles, source_quantiles, donor_values
        )
    return output, mapping


def train_control_task(
    train: pd.DataFrame,
    test: pd.DataFrame,
    endpoint: str,
    seed: int,
    fold: int,
    features: list[str],
    config: dict[str, object],
    model_name: str,
    permute: bool,
) -> tuple[pd.DataFrame, dict[str, object]]:
    bt_plus_model = select_best_baseline(
        train, endpoint, seed, int(config["inner_folds"]), BT_PLUS_CANDIDATES
    )
    bt_plus_fit = fit_baseline(bt_plus_model, train, endpoint)
    bt_plus_prediction = predict_baseline(bt_plus_fit, test)
    original_bt_model = select_best_baseline(
        train, endpoint, seed, int(config["inner_folds"])
    )
    original_bt_fit = fit_baseline(original_bt_model, train, endpoint)
    original_bt_prediction = predict_baseline(original_bt_fit, test)
    fit_train = train
    chemical_mapping: dict[str, str] = {}
    if permute:
        fit_train, chemical_mapping = permute_targets_by_chemical(train, endpoint, fold)
    parameters, trees, inner_mae = tune_xgb(
        fit_train,
        features,
        seed=seed,
        inner_folds=int(config["inner_folds"]),
        config=config["xgboost"],
    )
    model = make_xgb(parameters, config["xgboost"], seed=seed, trees=trees)
    model.fit(feature_matrix(fit_train, features), fit_train["target12"], verbose=False)
    prediction = model.predict(feature_matrix(test, features))
    records = prediction_records(
        test,
        prediction,
        original_bt_prediction,
        model_name,
        endpoint,
        seed,
        fold,
        original_bt_model,
    )
    records["bt_plus_prediction"] = bt_plus_prediction
    tuning = {
        "endpoint": endpoint,
        "model": model_name,
        "seed": seed,
        "outer_fold": fold,
        "features": len(features),
        "parameters": {**parameters, "n_estimators": trees},
        "inner_mae": inner_mae,
        "original_bt_model": original_bt_model,
        "bt_plus_model": bt_plus_model,
        "permutation_seed": PERMUTATION_SEED if permute else None,
        "chemical_mapping": chemical_mapping,
    }
    return records, tuning


def run_control(
    frame: pd.DataFrame,
    config: dict[str, object],
    results_dir: Path,
    control: str,
    requested_seeds: list[int] | None = None,
) -> None:
    if control == "permutation":
        seeds = [0]
        features = primary_feature_columns(frame) + ["cohort_toxcast"]
        model_name = "B3_PERMUTED"
        permute = True
    elif control == "div5":
        seeds = requested_seeds if requested_seeds is not None else list(config["seeds"])
        unknown = set(seeds) - set(config["seeds"])
        if unknown:
            raise ValueError(f"Unregistered DIV5 seeds: {sorted(unknown)}")
        features = [
            column
            for column in primary_feature_columns(frame)
            if column.startswith("div5_") or column == "log10_1p_dose"
        ] + ["cohort_toxcast"]
        model_name = "B3_DIV5"
        permute = False
    else:
        raise ValueError(control)
    checkpoint_dir = results_dir / f"gate_s_{control}_checkpoints"
    tuning_dir = results_dir / f"gate_s_{control}_tuning"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    tuning_dir.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        for fold, (train_idx, test_idx) in enumerate(
            outer_folds(frame, seed, int(config["outer_folds"]))
        ):
            for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
                checkpoint = checkpoint_dir / f"seed{seed}_fold{fold}_{endpoint}.csv"
                tuning_path = tuning_dir / f"seed{seed}_fold{fold}_{endpoint}.json"
                if checkpoint.exists() and tuning_path.exists():
                    continue
                train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
                test = endpoint_frame(frame.iloc[test_idx], endpoint).reset_index(drop=True)
                print(f"RUN {control} seed={seed} fold={fold} endpoint={endpoint}", flush=True)
                records, tuning = train_control_task(
                    train, test, endpoint, seed, fold, features, config, model_name, permute
                )
                records.to_csv(checkpoint, index=False)
                tuning_path.write_text(json.dumps(tuning, indent=2), encoding="utf-8")


def evaluate(results_dir: Path, frame: pd.DataFrame, config: dict[str, object]) -> None:
    complete = load_complete_predictions(results_dir)
    paired_summary(complete).to_csv(results_dir / "gate_s_main.csv", index=False)
    strata = dose_strata(frame, config)
    stratified = complete.merge(
        strata,
        on=["sample_id", "endpoint", "seed", "outer_fold"],
        how="left",
        validate="many_to_one",
    )
    if stratified["dose_stratum"].isna().any():
        raise ValueError("Dose stratum assignment is incomplete")
    paired_summary(stratified, ["dose_stratum"]).to_csv(
        results_dir / "dose_strata.csv", index=False
    )
    paired_summary(complete, ["cohort"]).to_csv(
        results_dir / "cohort_results.csv", index=False
    )
    for control in ("permutation", "div5"):
        files = sorted((results_dir / f"gate_s_{control}_checkpoints").glob("*.csv"))
        expected = 25 if control == "permutation" else 75
        if len(files) != expected:
            raise RuntimeError(f"{control} requires {expected} checkpoints; found {len(files)}")
        predictions = pd.concat([pd.read_csv(path) for path in files], ignore_index=True)
        paired_summary(predictions).to_csv(results_dir / f"gate_s_{control}.csv", index=False)
        if control == "div5":
            summarize(predictions).to_csv(results_dir / "gate_s_div5_metrics.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    parser.add_argument("--stage", choices=["permutation", "div5", "evaluate"], required=True)
    parser.add_argument("--seeds", nargs="+", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    frame = attach_identity(build_longitudinal_table(Path(config["data_root"])))
    results_dir = Path(config["results_dir"])
    if args.stage in {"permutation", "div5"}:
        run_control(frame, config, results_dir, args.stage, args.seeds)
    else:
        evaluate(results_dir, frame, config)


if __name__ == "__main__":
    main()
