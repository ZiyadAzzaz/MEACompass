"""Fail-closed F3b overlap and harmonization audit.

This module never loads model outcomes or scores the external set. It evaluates
the preregistered data-comparability gate and stops before scoring if a required
input is unavailable.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr

from meacompass.data import NETWORK_METRICS, PRIMARY_ENDPOINTS, load_raw


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data" / "raw" / "epa_nfa" / "extracted"
EXTERNAL_ROOT = ROOT / "data" / "external" / "f3b"
OUTPUT_ROOT = ROOT / "results" / "f3b"
RDATA_FILES = {
    5: "div5.data.with.spids.Rdata",
    7: "div7.data.with.spids.Rdata",
    12: "div12.data.with.spids.RData",
}
SOURCE_TO_COHORT = {
    "NTP91_parameters_by_DIV.csv": "NTP",
    "ToxCast2016_parameters_by_DIV.csv": "ToxCast",
}


def load_refinement(root: Path = EXTERNAL_ROOT) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for expected_div, name in RDATA_FILES.items():
        objects = pyreadr.read_r(root / name)
        if len(objects) != 1:
            raise ValueError(f"Expected one R object in {name}; found {list(objects)}")
        frame = next(iter(objects.values())).copy()
        if not frame["DIV"].eq(expected_div).all():
            raise ValueError(f"{name} contains rows outside DIV{expected_div}")
        parts.append(frame)
    return pd.concat(parts, ignore_index=True)


def _percent_control(frame: pd.DataFrame, metric: str) -> pd.Series:
    controls = (
        frame.loc[frame["dose"].eq(0)]
        .groupby(["cohort", "plate", "DIV"], dropna=False)[metric]
        .median()
        .rename("control")
    )
    indexed = frame.join(controls, on=["cohort", "plate", "DIV"])
    values = 100.0 * indexed[metric] / indexed["control"]
    return values.where(indexed["control"].ne(0)).replace([np.inf, -np.inf], np.nan)


def _metric_record(overlap: pd.DataFrame, metric: str) -> dict[str, object]:
    old_name = f"{metric}_old"
    new_name = f"{metric}_new"
    roles = []
    if metric in NETWORK_METRICS:
        roles.append("input")
    if metric in PRIMARY_ENDPOINTS:
        roles.append("endpoint")
    if old_name not in overlap or new_name not in overlap:
        return {
            "metric": metric,
            "role": "+".join(roles),
            "available_old": old_name in overlap,
            "available_refinement": new_name in overlap,
            "overlap_pairs": 0,
            "spearman": np.nan,
            "median_new_old_ratio": np.nan,
            "old_missing_rate": np.nan,
            "refinement_missing_rate": 1.0,
            "status": "NOT_COMPARABLE",
            "note": "required input absent from refinement release",
        }

    pair = overlap[[old_name, new_name]].dropna()
    old_missing = float(overlap[old_name].isna().mean())
    new_missing = float(overlap[new_name].isna().mean())
    if len(pair) >= 2:
        old_rank = pair[old_name].rank(method="average").to_numpy(dtype=float)
        new_rank = pair[new_name].rank(method="average").to_numpy(dtype=float)
        old_centered = old_rank - old_rank.mean()
        new_centered = new_rank - new_rank.mean()
        denominator = float(
            np.sqrt(np.sum(old_centered * old_centered) * np.sum(new_centered * new_centered))
        )
        rho = float(np.sum(old_centered * new_centered) / denominator) if denominator else np.nan
    else:
        rho = np.nan
    ratios = pair.loc[pair[old_name].ne(0), new_name] / pair.loc[pair[old_name].ne(0), old_name]
    ratio = float(ratios.median()) if len(ratios) else np.nan
    compatible = bool(
        np.isfinite(rho)
        and rho >= 0.95
        and np.isfinite(ratio)
        and 0.9 <= ratio <= 1.1
    )
    return {
        "metric": metric,
        "role": "+".join(roles),
        "available_old": True,
        "available_refinement": True,
        "overlap_pairs": int(len(pair)),
        "spearman": rho,
        "median_new_old_ratio": ratio,
        "old_missing_rate": old_missing,
        "refinement_missing_rate": new_missing,
        "status": "COMPATIBLE_WITH_FROZEN_TRANSFORM" if compatible else "NOT_COMPARABLE",
        "note": "same-plate/same-well/same-DIV overlap; percent-control transformed",
    }


def build_audit(
    data_root: Path = DATA_ROOT,
    external_root: Path = EXTERNAL_ROOT,
) -> tuple[pd.DataFrame, dict[str, object], dict[str, object]]:
    old = load_raw(data_root).rename(columns={"Plate.SN": "plate"})
    refinement = load_refinement(external_root).rename(columns={"apid.short": "plate"})
    refinement["cohort"] = refinement["srcf"].map(SOURCE_TO_COHORT)

    old_dates = {int(value) for value in old["date"].dropna().unique()}
    refinement_dates = {int(value) for value in refinement["date"].dropna().unique()}
    candidate = refinement.loc[~refinement["date"].astype(int).isin(old_dates)].copy()

    old_overlap = old.rename(columns={metric: f"{metric}_old" for metric in NETWORK_METRICS})
    ref_overlap = refinement.loc[refinement["cohort"].notna()].rename(
        columns={metric: f"{metric}_new" for metric in NETWORK_METRICS if metric in refinement}
    )
    keys = ["cohort", "plate", "well", "DIV"]
    overlap = old_overlap.merge(
        ref_overlap,
        on=keys,
        how="inner",
        validate="one_to_one",
        suffixes=("_oldmeta", "_newmeta"),
    )

    # Apply the registered same-plate/same-DIV zero-dose transform independently
    # to each release before compatibility statistics are calculated.
    for metric in NETWORK_METRICS:
        old_name, new_name = f"{metric}_old", f"{metric}_new"
        if old_name in overlap:
            temp = overlap[keys + ["dose_oldmeta", old_name]].rename(
                columns={"dose_oldmeta": "dose", old_name: metric}
            )
            overlap[old_name] = _percent_control(temp, metric).to_numpy()
        if new_name in overlap:
            temp = overlap[keys + ["dose_newmeta", new_name]].rename(
                columns={"dose_newmeta": "dose", new_name: metric}
            )
            overlap[new_name] = _percent_control(temp, metric).to_numpy()

    harmonization = pd.DataFrame(
        [_metric_record(overlap, metric) for metric in NETWORK_METRICS]
    )
    missing_required = harmonization.loc[
        harmonization["status"].eq("NOT_COMPARABLE"), "metric"
    ].tolist()
    absent_required = harmonization.loc[
        ~harmonization["available_refinement"], "metric"
    ].tolist()
    threshold_failures = harmonization.loc[
        harmonization["available_refinement"]
        & harmonization["status"].eq("NOT_COMPARABLE"),
        "metric",
    ].tolist()

    independence = {
        "training_date_count": len(old_dates),
        "training_dates": sorted(old_dates),
        "refinement_date_count": len(refinement_dates),
        "refinement_dates": sorted(refinement_dates),
        "date_absent_candidate_count": len(refinement_dates - old_dates),
        "date_absent_candidates": sorted(refinement_dates - old_dates),
        "candidate_rows_before_chemical_filter": int(len(candidate)),
        "candidate_treatment_labels_before_cas_filter": int(candidate["treatment"].nunique()),
        "overlap_recordings": int(len(overlap)),
        "overlap_plates": int(overlap["plate"].nunique()),
        "cas_independence_status": "NOT_EVALUATED_AFTER_HARMONIZATION_CUT",
        "note": "CAS-level eligibility and scoring stop fail-closed because required M1 inputs are not comparable.",
    }
    decision = {
        "gate": "F3b",
        "classification": "CUT",
        "scoring_performed": False,
        "comparable_endpoints": [],
        "not_comparable_endpoints": PRIMARY_ENDPOINTS,
        "missing_or_not_comparable_required_inputs": missing_required,
        "absent_required_inputs": absent_required,
        "compatibility_threshold_failures": threshold_failures,
        "reason": (
            "Every final M1 endpoint requires all registered neural inputs. "
            "The refinement release omits cv.time and cv.network, including DIV5/DIV7 values "
            "and their missingness indicators; r also fails the registered rank-correlation threshold. "
            "The preregistered harmonization gate therefore forbids scoring."
        ),
        "fallback": "Use the completed post-lock held-out NTP-to-ToxCast and ToxCast-to-NTP analysis.",
    }
    return harmonization, independence, decision


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DATA_ROOT)
    parser.add_argument("--external-root", type=Path, default=EXTERNAL_ROOT)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()
    harmonization, independence, decision = build_audit(args.data_root, args.external_root)
    args.output_root.mkdir(parents=True, exist_ok=True)
    harmonization.to_csv(args.output_root / "harmonization.csv", index=False)
    for name, payload in (("independence_audit.json", independence), ("decision.json", decision)):
        (args.output_root / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps(decision, indent=2))


if __name__ == "__main__":
    main()
