"""Bounded post-registration integrity audit for Sanity Gate S."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error

from neurochip.baselines import endpoint_frame, fit_baseline, predict_baseline
from neurochip.chem import attach_chemistry
from neurochip.data import NETWORK_METRICS, PRIMARY_ENDPOINTS, build_longitudinal_table, primary_feature_columns, validate_time_causal_features
from neurochip.evaluate import bootstrap_paired_mae
from neurochip.sanity_gate import KEYS, attach_identity, load_complete_predictions, paired_summary
from neurochip.splits import assert_group_disjoint, outer_folds
from neurochip.train_baselines import feature_matrix, make_xgb
from neurochip.train_m1 import compose_m1_prediction, m1_training_target


AUDIT_SEED = 20260928
DIAGNOSTIC_MODELS = ("DOSE_SMOOTH", "FULL_SHUFFLE")


def safe_pearson(left: pd.Series, right: pd.Series) -> float:
    """Pearson correlation without the fragile Windows BLAS corrcoef path."""
    x = left.to_numpy(dtype=float)
    y = right.to_numpy(dtype=float)
    x = x - x.mean()
    y = y - y.mean()
    denominator = float(np.sqrt(np.sum(x**2) * np.sum(y**2)))
    return float(np.sum(x * y) / denominator) if denominator else float("nan")


def fixed_parameters(records: list[dict[str, object]], endpoint: str) -> dict[str, object]:
    selected = [record for record in records if record["endpoint"] == endpoint]
    if not selected:
        raise ValueError(f"No preserved tuning records for {endpoint}")
    parameters = [record["parameters"] for record in selected]
    keys = ("max_depth", "learning_rate", "min_child_weight", "colsample_bytree", "n_estimators")
    return {
        key: int(np.median([item[key] for item in parameters]))
        if key in {"max_depth", "min_child_weight", "n_estimators"}
        else float(np.median([item[key] for item in parameters]))
        for key in keys
    }


def load_fixed_settings(results_dir: Path) -> dict[str, dict[str, dict[str, object]]]:
    b3_records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((results_dir / "gate_s_permutation_tuning").glob("*.json"))
    ]
    m1_records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((results_dir / "m1_tuning_checkpoints").glob("*.json"))
    ]
    if len(b3_records) != 25 or len(m1_records) != 75:
        raise RuntimeError("Fixed diagnostics require 25 S2 and 75 M1 tuning records")
    settings: dict[str, dict[str, dict[str, object]]] = {"B3": {}, "M1": {}}
    for endpoint in PRIMARY_ENDPOINTS:
        settings["B3"][endpoint] = fixed_parameters(b3_records, endpoint)
        endpoint_m1 = [record for record in m1_records if record["endpoint"] == endpoint]
        variants = pd.Series([record["variant"] for record in endpoint_m1]).value_counts()
        bt_models = pd.Series([record["bt_model"] for record in endpoint_m1]).value_counts()
        settings["M1"][endpoint] = {
            **fixed_parameters(m1_records, endpoint),
            "variant": str(variants.index[0]),
            "bt_model": str(bt_models.index[0]),
        }
    return settings


def lineage_table(frame: pd.DataFrame, chemistry_columns: list[str]) -> pd.DataFrame:
    early = primary_feature_columns(frame) + ["cohort_toxcast"]
    m1 = list(dict.fromkeys(early + chemistry_columns))
    rows: list[dict[str, object]] = []
    for model, features in (("B3", early), ("M1", m1)):
        for feature in features:
            if feature.startswith(("div5_", "div7_")):
                missing_flag = feature.endswith("_missing")
                raw_name = feature.removesuffix("_missing")
                source_div = int(raw_name[3])
                source = "EPA New NTP/New TC per-well network CSV"
                computed = f"isna({raw_name})" if missing_flag else "raw per-well measurement"
            elif feature == "log10_1p_dose":
                source_div = "design"
                source = "EPA New NTP/New TC exposure columns"
                computed = "log10(1 + max(dose_uM, 0))"
            elif feature == "cohort_toxcast":
                source_div = "design"
                source = "EPA cohort/source table"
                computed = "fixed indicator: ToxCast=1, NTP=0"
            elif feature.startswith("desc_"):
                source_div = "structure"
                source = "reviewed CAS-to-PubChem canonical SMILES mapping"
                computed = f"RDKit {feature.removeprefix('desc_')}"
            elif feature.startswith("morgan_"):
                source_div = "structure"
                source = "reviewed CAS-to-PubChem canonical SMILES mapping"
                computed = "RDKit Morgan radius=2, 2048-bit fingerprint"
            elif feature == "structure_missing":
                source_div = "structure"
                source = "reviewed CAS-to-PubChem canonical SMILES mapping"
                computed = "canonical SMILES unresolved indicator"
            else:
                raise ValueError(f"Unclassified feature: {feature}")
            rows.append(
                {
                    "feature": feature,
                    "model": model,
                    "source_file_table": source,
                    "source_div": source_div,
                    "computed_from": computed,
                    "fit_rows": "none; raw/deterministic transform",
                    "target_derived": False,
                    "test_derived": False,
                    "future_info_possible": False,
                }
            )
    return pd.DataFrame(rows)


def block_permute(
    train: pd.DataFrame, endpoint: str, fold: int, permutation_seed: int
) -> tuple[pd.DataFrame, dict[str, str]]:
    output = train.copy()
    groups = np.asarray(sorted(output["casrn"].unique()))
    digest = int(hashlib.sha256(endpoint.encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng(permutation_seed + fold * 1009 + digest)
    donors = rng.permutation(groups)
    while np.any(donors == groups):
        donors = rng.permutation(groups)
    mapping = dict(zip(groups, donors, strict=True))
    original = output.copy()
    for recipient, donor in mapping.items():
        recipient_index = output.loc[output["casrn"].eq(recipient)].sort_values(
            ["dose", "Plate.SN", "well"]
        ).index
        donor_values = original.loc[original["casrn"].eq(donor)].sort_values(
            ["dose", "Plate.SN", "well"]
        )["target12"].to_numpy()
        output.loc[recipient_index, "target12"] = np.interp(
            np.linspace(0, 1, len(recipient_index)),
            np.linspace(0, 1, len(donor_values)),
            donor_values,
        )
    return output, mapping


def write_mechanism_outputs(
    frame: pd.DataFrame,
    chemistry_columns: list[str],
    config: dict[str, object],
    results_dir: Path,
) -> None:
    audit_dir = results_dir / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    lineage = lineage_table(frame, chemistry_columns)
    validate_time_causal_features(lineage["feature"].tolist())
    lineage.to_csv(audit_dir / "feature_lineage.csv", index=False)
    stored_paths = sorted((results_dir / "gate_s_permutation_tuning").glob("*.json"))
    stored = {
        (int(record["outer_fold"]), str(record["endpoint"])): record
        for record in [json.loads(path.read_text(encoding="utf-8")) for path in stored_paths]
    }
    rows: list[dict[str, object]] = []
    folds = list(outer_folds(frame, seed=0, n_splits=int(config["outer_folds"])))
    for fold, (train_idx, test_idx) in enumerate(folds):
        assert_group_disjoint(frame, train_idx, test_idx)
        for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
            train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
            permuted, mapping = block_permute(train, endpoint, fold, AUDIT_SEED)
            stored_mapping = stored[(fold, endpoint)]["chemical_mapping"]
            if mapping != stored_mapping:
                raise AssertionError(f"Registered mapping reconstruction differs: {fold} {endpoint}")
            correlation = safe_pearson(train["target12"], permuted["target12"])
            mapping_hash = hashlib.sha256(
                json.dumps(mapping, sort_keys=True).encode("utf-8")
            ).hexdigest()
            self_maps = sum(recipient == donor for recipient, donor in mapping.items())
            for recipient, donor in sorted(mapping.items()):
                rows.append(
                    {
                        "outer_fold": fold,
                        "endpoint": endpoint,
                        "recipient_chemical": recipient,
                        "donor_chemical": donor,
                        "self_mapped": recipient == donor,
                        "groups": len(mapping),
                        "groups_changed": len(mapping) - self_maps,
                        "fraction_groups_changed": (len(mapping) - self_maps) / len(mapping),
                        "target_correlation": correlation,
                        "mapping_sha256": mapping_hash,
                        "outer_test_targets_touched": False,
                    }
                )
    pd.DataFrame(rows).to_csv(audit_dir / "permutation_mapping.csv", index=False)


def full_shuffle(train: pd.DataFrame, seed: int) -> pd.DataFrame:
    output = train.copy()
    rng = np.random.default_rng(seed)
    output["target12"] = rng.permutation(train["target12"].to_numpy())
    return output


def bt_plus_for_task(results_dir: Path, seed: int, fold: int, endpoint: str) -> pd.DataFrame:
    path = results_dir / "bt_plus_checkpoints" / f"seed{seed}_fold{fold}_{endpoint}.csv"
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path)[KEYS + ["prediction"]].rename(
        columns={"prediction": "bt_plus_prediction"}
    )


def fit_fixed(
    train: pd.DataFrame,
    test: pd.DataFrame,
    features: list[str],
    parameters: dict[str, object],
    config: dict[str, object],
    seed: int,
    target_variant: str = "direct",
    bt_model: str = "B2",
) -> np.ndarray:
    model_parameters = {
        key: parameters[key]
        for key in ("max_depth", "learning_rate", "min_child_weight", "colsample_bytree")
    }
    trees = int(parameters["n_estimators"])
    if target_variant == "bt_residual":
        fitted_bt = fit_baseline(bt_model, train, str(train["endpoint_name"].iloc[0]))
        train_bt = predict_baseline(fitted_bt, train)
        test_bt = predict_baseline(fitted_bt, test)
    else:
        train_bt = np.zeros(len(train))
        test_bt = np.zeros(len(test))
    target = m1_training_target(train, target_variant, train_bt)
    model = make_xgb(model_parameters, config["xgboost"], seed=seed, trees=trees)
    model.fit(feature_matrix(train, features), target, verbose=False)
    raw = model.predict(feature_matrix(test, features))
    return compose_m1_prediction(raw, target_variant, test_bt)


def diagnostic_record(
    test: pd.DataFrame,
    prediction: np.ndarray,
    reference: pd.DataFrame,
    model: str,
    endpoint: str,
    seed: int,
    fold: int,
) -> pd.DataFrame:
    output = pd.DataFrame(
        {
            "sample_id": test["sample_id"].to_numpy(),
            "casrn": test["casrn"].to_numpy(),
            "cohort": test["cohort"].to_numpy(),
            "endpoint": endpoint,
            "model": model,
            "seed": seed,
            "outer_fold": fold,
            "target12": test["target12"].to_numpy(),
            "target7": test["target7"].to_numpy(),
            "prediction": prediction,
        }
    )
    merged = output.merge(
        reference[KEYS + ["bt_plus_prediction"]],
        on=KEYS,
        how="inner",
        validate="one_to_one",
    )
    if len(merged) != len(output):
        raise ValueError("Diagnostic and BT+ rows do not align")
    return merged


def run_basic_diagnostic(
    frame: pd.DataFrame,
    config: dict[str, object],
    results_dir: Path,
    stage: str,
    seeds: list[int],
    settings: dict[str, dict[str, dict[str, object]]],
) -> None:
    early_features = primary_feature_columns(frame) + ["cohort_toxcast"]
    if stage == "dose_smooth":
        features = ["log10_1p_dose", "cohort_toxcast", "structure_missing"]
        model_name = "DOSE_SMOOTH"
    elif stage == "full_shuffle":
        features = early_features
        model_name = "FULL_SHUFFLE"
    else:
        raise ValueError(stage)
    checkpoint_dir = results_dir / "audit" / f"{stage}_checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        folds = list(outer_folds(frame, seed, int(config["outer_folds"])))
        for fold, (train_idx, test_idx) in enumerate(folds):
            for endpoint in config.get("primary_endpoints", PRIMARY_ENDPOINTS):
                path = checkpoint_dir / f"seed{seed}_fold{fold}_{endpoint}.csv"
                if path.exists():
                    continue
                train = endpoint_frame(frame.iloc[train_idx], endpoint).reset_index(drop=True)
                test = endpoint_frame(frame.iloc[test_idx], endpoint).reset_index(drop=True)
                train["endpoint_name"] = endpoint
                test["endpoint_name"] = endpoint
                if stage == "full_shuffle":
                    digest = int(hashlib.sha256(endpoint.encode()).hexdigest()[:8], 16)
                    train = full_shuffle(train, AUDIT_SEED + seed * 10007 + fold * 101 + digest)
                prediction = fit_fixed(
                    train, test, features, settings["B3"][endpoint], config, seed
                )
                reference = bt_plus_for_task(results_dir, seed, fold, endpoint)
                diagnostic_record(
                    test, prediction, reference, model_name, endpoint, seed, fold
                ).to_csv(path, index=False)
                print(f"RUN {stage} seed={seed} fold={fold} endpoint={endpoint}", flush=True)


def summarize_basic(results_dir: Path, stage: str, expected: int = 75) -> None:
    files = sorted((results_dir / "audit" / f"{stage}_checkpoints").glob("*.csv"))
    if len(files) != expected:
        raise RuntimeError(f"{stage} requires {expected} checkpoints; found {len(files)}")
    predictions = pd.concat([pd.read_csv(path) for path in files], ignore_index=True)
    paired_summary(predictions).to_csv(results_dir / "audit" / f"{stage}.csv", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    parser.add_argument("--stage", choices=["mechanism", "dose_smooth", "full_shuffle", "summarize_basic"], required=True)
    parser.add_argument("--diagnostic", choices=["dose_smooth", "full_shuffle"])
    parser.add_argument("--seeds", nargs="+", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    base = attach_identity(build_longitudinal_table(Path(config["data_root"])))
    frame, chemistry_columns = attach_chemistry(base, Path(config["chemical_mapping"]))
    results_dir = Path(config["results_dir"])
    settings = load_fixed_settings(results_dir)
    if args.stage == "mechanism":
        write_mechanism_outputs(frame, chemistry_columns, config, results_dir)
    elif args.stage in {"dose_smooth", "full_shuffle"}:
        seeds = args.seeds if args.seeds is not None else list(config["seeds"])
        run_basic_diagnostic(frame, config, results_dir, args.stage, seeds, settings)
    else:
        if args.diagnostic is None:
            raise ValueError("--diagnostic is required for summarize_basic")
        summarize_basic(results_dir, args.diagnostic)


if __name__ == "__main__":
    main()
