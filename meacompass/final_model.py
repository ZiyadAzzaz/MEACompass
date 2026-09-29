"""Deterministic all-2019 final models for post-lock external evaluation."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from meacompass.baselines import endpoint_frame, fit_baseline, predict_baseline
from meacompass.build_bt_plus import BT_PLUS_CANDIDATES
from meacompass.chem import DESCRIPTOR_FUNCTIONS, attach_chemistry
from meacompass.data import PRIMARY_ENDPOINTS, RAW_FILES, build_longitudinal_table, primary_feature_columns, validate_time_causal_features
from meacompass.integrity_audit import load_fixed_settings
from meacompass.reliability import select_bt_plus_plus
from meacompass.train_baselines import feature_matrix, file_sha256, make_xgb, select_best_baseline
from meacompass.train_m1 import m1_training_target


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "baselines.yaml"
DEFAULT_TUNING = ROOT / "results" / "m1_tuning.json"
DEFAULT_SETTINGS = ROOT / "schemas" / "final_model_hyperparameters.json"
DEFAULT_MANIFEST = ROOT / "schemas" / "final_model_manifest.json"


def _mode(values: list[Any]) -> Any:
    """Return a deterministic mode; lexical JSON order breaks count ties."""
    counts = Counter(values)
    highest = max(counts.values())
    tied = [value for value, count in counts.items() if count == highest]
    return min(tied, key=lambda value: json.dumps(value, sort_keys=True))


def _nearest_allowed(value: float, allowed: list[float]) -> float:
    """Choose the closest registered value; choose the smaller value on a tie."""
    return min(sorted(allowed), key=lambda candidate: (abs(candidate - value), candidate))


def derive_final_hyperparameters(
    records: list[dict[str, Any]], config: dict[str, Any]
) -> dict[str, Any]:
    """Aggregate the 15 locked outer-fit configurations for every endpoint."""
    output: dict[str, Any] = {
        "rule_version": "amendment_b_median_mode_v1",
        "source_records": 75,
        "records_per_endpoint": 15,
        "numeric_rule": "median; registered-grid parameters snap to nearest allowed value, ties smaller",
        "integer_rule": "median then floor(x + 0.5); minimum one",
        "categorical_rule": "mode; ties resolved by lexical JSON order",
        "endpoints": {},
    }
    grid = config["xgboost"]
    grid_keys = ("max_depth", "learning_rate", "min_child_weight", "colsample_bytree")
    integer_keys = {"max_depth", "min_child_weight"}
    for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
        selected = [record for record in records if record["endpoint"] == endpoint]
        if len(selected) != 15:
            raise ValueError(f"Expected 15 tuning records for {endpoint}; found {len(selected)}")
        parameters: dict[str, Any] = {}
        for key in grid_keys:
            median = float(np.median([float(record["parameters"][key]) for record in selected]))
            value = _nearest_allowed(median, [float(item) for item in grid[key]])
            parameters[key] = int(value) if key in integer_keys else float(value)
        tree_median = float(
            np.median([int(record["parameters"]["n_estimators"]) for record in selected])
        )
        parameters["n_estimators"] = max(1, int(math.floor(tree_median + 0.5)))
        output["endpoints"][endpoint] = {
            "variant": str(_mode([str(record["variant"]) for record in selected])),
            "bt_model": str(_mode([str(record["bt_model"]) for record in selected])),
            "parameters": parameters,
            "source_seed_fold_pairs": sorted(
                [[int(record["seed"]), int(record["outer_fold"])] for record in selected]
            ),
        }
    return output


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_derived_settings(config_path: Path, tuning_path: Path, output_path: Path) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    records = json.loads(tuning_path.read_text(encoding="utf-8"))
    settings = derive_final_hyperparameters(records, config)
    settings["source_tuning_path"] = "results/m1_tuning.json"
    settings["source_tuning_sha256"] = file_sha256(tuning_path)
    settings["config_path"] = "configs/baselines.yaml"
    settings["config_sha256"] = file_sha256(config_path)
    _write_json(output_path, settings)
    return settings


def _conformal_quantile(values: np.ndarray, alpha: float = 0.10) -> float:
    clean = np.sort(np.asarray(values, dtype=float)[np.isfinite(values)])
    if not len(clean):
        raise ValueError("Calibration residual pool is empty")
    rank = min(len(clean), int(math.ceil((len(clean) + 1) * (1 - alpha))))
    return float(clean[rank - 1])


def _baseline_payload(fitted: Any) -> dict[str, Any]:
    return {"model": fitted.model, "endpoint": fitted.endpoint, "parameters": fitted.parameters}


def _artifact_record(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(root).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": file_sha256(path),
    }


def build_final_models(config_path: Path, settings_path: Path, overwrite: bool = False) -> dict[str, Any]:
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    results_dir = ROOT / "results"
    output_dir = results_dir / "final_model"
    if output_dir.exists() and any(output_dir.iterdir()) and not overwrite:
        raise FileExistsError(f"{output_dir} is non-empty; pass --overwrite to rebuild deterministically")
    output_dir.mkdir(parents=True, exist_ok=True)

    data_root = ROOT / str(config["data_root"])
    mapping_path = ROOT / str(config["chemical_mapping"])
    frame = build_longitudinal_table(data_root)
    frame["sample_id"] = frame["cohort"].astype(str) + "|" + frame["Plate.SN"].astype(str) + "|" + frame["well"].astype(str)
    frame["cohort_toxcast"] = frame["cohort"].eq("ToxCast").astype("int8")
    frame, chemistry_columns = attach_chemistry(frame, mapping_path)
    features = list(dict.fromkeys(primary_feature_columns(frame) + ["cohort_toxcast"] + chemistry_columns))
    validate_time_causal_features(features)

    feature_path = output_dir / "feature_order.json"
    descriptor_path = output_dir / "descriptor_config.json"
    chemicals_path = output_dir / "training_chemicals.json"
    _write_json(feature_path, features)
    _write_json(
        descriptor_path,
        {
            "rdkit_descriptors": [name for name, _ in DESCRIPTOR_FUNCTIONS],
            "morgan_radius": 2,
            "morgan_bits": 2048,
            "structure_source": "data/derived/chemical_mapping.csv",
            "structure_source_sha256": file_sha256(mapping_path),
        },
    )
    _write_json(chemicals_path, sorted(frame["casrn"].dropna().astype(str).unique().tolist()))

    fixed = load_fixed_settings(results_dir)
    model_records: list[dict[str, Any]] = []
    selection_records: list[dict[str, Any]] = []
    for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
        train = endpoint_frame(frame, endpoint).reset_index(drop=True)
        train["endpoint_name"] = endpoint
        endpoint_settings = settings["endpoints"][endpoint]
        parameters = dict(endpoint_settings["parameters"])
        trees = int(parameters.pop("n_estimators"))
        variant = str(endpoint_settings["variant"])
        residual_bt_model = str(endpoint_settings["bt_model"])
        fitted_residual_bt = fit_baseline(residual_bt_model, train, endpoint)
        train_bt = predict_baseline(fitted_residual_bt, train) if variant == "bt_residual" else np.zeros(len(train))
        target = m1_training_target(train, variant, train_bt)

        for seed in [0, 1, 2]:
            model = make_xgb(parameters, config["xgboost"], seed=seed, trees=trees)
            model.fit(feature_matrix(train, features), target, verbose=False)
            model_path = output_dir / f"m1_{endpoint}_seed{seed}.json"
            model.save_model(model_path)

            bt_plus_model = select_best_baseline(
                train, endpoint, seed, int(config["inner_folds"]), BT_PLUS_CANDIDATES
            )
            fitted_bt_plus = fit_baseline(bt_plus_model, train, endpoint)
            bt_plus_path = output_dir / f"bt_plus_{endpoint}_seed{seed}.json"
            _write_json(bt_plus_path, _baseline_payload(fitted_bt_plus))

            btpp_selected, bt_inner_mae, dose_inner_mae = select_bt_plus_plus(
                train,
                endpoint,
                seed,
                bt_plus_model,
                fixed["B3"][endpoint],
                config,
            )
            btpp_path = output_dir / f"bt_plus_plus_{endpoint}_seed{seed}.json"
            if btpp_selected == "BT+":
                _write_json(btpp_path, {"selected": "BT+", "baseline": _baseline_payload(fitted_bt_plus)})
            else:
                dose_parameters = dict(fixed["B3"][endpoint])
                dose_trees = int(dose_parameters.pop("n_estimators"))
                dose_model = make_xgb(dose_parameters, config["xgboost"], seed=seed, trees=dose_trees)
                dose_features = ["log10_1p_dose", "cohort_toxcast", "structure_missing"]
                dose_model.fit(feature_matrix(train, dose_features), train["target12"], verbose=False)
                dose_path = output_dir / f"dose_smooth_{endpoint}_seed{seed}.json"
                dose_model.save_model(dose_path)
                _write_json(
                    btpp_path,
                    {"selected": "DOSE_SMOOTH", "model_path": dose_path.relative_to(ROOT).as_posix(), "features": dose_features},
                )

            residual_path = output_dir / f"m1_residual_baseline_{endpoint}_seed{seed}.json"
            _write_json(residual_path, _baseline_payload(fitted_residual_bt))
            selection_records.append(
                {
                    "endpoint": endpoint,
                    "seed": seed,
                    "bt_plus_model": bt_plus_model,
                    "bt_plus_plus_model": btpp_selected,
                    "inner_bt_plus_mae": bt_inner_mae,
                    "inner_dose_smooth_mae": dose_inner_mae,
                }
            )
            model_records.append(
                {
                    "endpoint": endpoint,
                    "seed": seed,
                    "variant": variant,
                    "residual_bt_model": residual_bt_model,
                    "parameters": {**parameters, "n_estimators": trees},
                    "model_path": model_path.relative_to(ROOT).as_posix(),
                    "model_sha256": file_sha256(model_path),
                }
            )

    pd.DataFrame(selection_records).to_csv(output_dir / "comparator_selections.csv", index=False)
    _write_json(output_dir / "seed_metadata.json", model_records)

    locked = pd.read_csv(results_dir / "m1_predictions.csv")
    pool_rows: list[pd.DataFrame] = []
    calibration_summary: dict[str, Any] = {}
    for endpoint, source in locked.groupby("endpoint", sort=True):
        pooled = source.groupby(["sample_id", "casrn", "cohort"], as_index=False).agg(
            target12=("target12", "first"),
            prediction=("prediction", "mean"),
            seed_disagreement=("prediction", "std"),
        )
        pooled["endpoint"] = endpoint
        pooled["absolute_residual"] = (pooled["target12"] - pooled["prediction"]).abs()
        pooled["seed_disagreement"] = pooled["seed_disagreement"].fillna(0.0)
        pool_rows.append(pooled)
        calibration_summary[endpoint] = {
            "residual_quantile_90": _conformal_quantile(pooled["absolute_residual"].to_numpy()),
            "abstention_disagreement_threshold_70": float(
                np.quantile(pooled["seed_disagreement"], 0.70, method="higher")
            ),
            "rows": len(pooled),
            "chemicals": int(pooled["casrn"].nunique()),
        }
    pd.concat(pool_rows, ignore_index=True).to_csv(output_dir / "calibration_pool.csv", index=False)
    _write_json(output_dir / "calibration_rule.json", {
        "source": "2019 locked chemical-disjoint outer-fold predictions, seed-averaged per sample",
        "interval": "final three-seed mean prediction plus/minus endpoint finite-sample 90% absolute-residual quantile",
        "abstention": "accept when three-seed prediction standard deviation is at or below the frozen endpoint 70th-percentile threshold",
        "external_outcomes_used": False,
        "endpoints": calibration_summary,
    })

    artifacts = sorted(path for path in output_dir.iterdir() if path.is_file())
    versions = {}
    for package in ["numpy", "pandas", "scikit-learn", "xgboost", "rdkit", "PyYAML"]:
        versions[package] = importlib.metadata.version(package)
    manifest = {
        "manifest_version": 1,
        "purpose": "post-lock external validation only",
        "training_release": "EPA NFA 2019 development release",
        "training_rows": len(frame),
        "training_chemicals": int(frame["casrn"].nunique()),
        "seeds": [0, 1, 2],
        "prediction_ensemble": "arithmetic mean of three final all-2019 seed models",
        "settings_path": settings_path.relative_to(ROOT).as_posix(),
        "settings_sha256": file_sha256(settings_path),
        "feature_count": len(features),
        "raw_training_files": {
            cohort: {"path": relative, "sha256": file_sha256(data_root / relative)}
            for cohort, relative in RAW_FILES.items()
        },
        "package_versions": versions,
        "artifacts": [_artifact_record(path, ROOT) for path in artifacts],
    }
    _write_json(DEFAULT_MANIFEST, manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--tuning", type=Path, default=DEFAULT_TUNING)
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS)
    parser.add_argument("--derive-only", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = write_derived_settings(args.config, args.tuning, args.settings)
    if args.derive_only:
        print(json.dumps(settings, indent=2, sort_keys=True))
        return
    manifest = build_final_models(args.config, args.settings, overwrite=args.overwrite)
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
