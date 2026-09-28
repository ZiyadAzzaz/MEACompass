"""Audit the downloaded EPA neural network formation assay CSV files.

This script performs no modelling and writes no derived data. It exists so the
project-selection gate can be reproduced from the official archive.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


METRICS = [
    "meanfiringrate",
    "burst.per.min",
    "mean.isis",
    "per.spikes.in.burst",
    "mean.dur",
    "mean.IBIs",
    "nAE",
    "nABE",
    "ns.n",
    "ns.peak.m",
    "ns.durn.m",
    "ns.percent.of.spikes.in.ns",
    "ns.mean.insis",
    "ns.durn.sd",
    "ns.mean.spikes.in.ns",
    "r",
    "cv.time",
    "cv.network",
]


COHORTS = {
    "NTP": {
        "raw": "New NTP/sourceData/ALL_NTP.csv",
        "chemicals": "New NTP/sourceData/NTP Experimental Summary of Data for Analysis_Complete.csv",
        "ec50": "New NTP/Summary Files/ec50_allOntogeny.csv",
    },
    "ToxCast": {
        "raw": "New TC/sourceData/AllCombined_ToxCast_20180923.csv",
        "chemicals": "New TC/sourceData/ToxCast Experimental Summary of Data for Analysis.csv",
        "ec50": "New TC/Summary Files/ec50_allOntogeny.csv",
    },
}


def clean_cas(value: object) -> str:
    return str(value).strip().strip("'\"").rstrip("',")


def audit(root: Path) -> dict[str, object]:
    frames: list[pd.DataFrame] = []
    chemical_rows: list[pd.DataFrame] = []
    ec50_rows: list[pd.DataFrame] = []

    for cohort, files in COHORTS.items():
        raw = pd.read_csv(root / files["raw"], na_values=["NA", "NaN"])
        raw.insert(0, "cohort", cohort)
        frames.append(raw)

        chemicals = pd.read_csv(root / files["chemicals"])
        chemicals.insert(0, "cohort", cohort)
        cas_col = "casrn"
        name_col = "preferred name" if cohort == "NTP" else "preferred_name"
        chemicals = chemicals[["cohort", cas_col, name_col]].rename(
            columns={cas_col: "casrn", name_col: "preferred_name"}
        )
        chemicals["casrn"] = chemicals["casrn"].map(clean_cas)
        chemical_rows.append(chemicals)

        ec50 = pd.read_csv(root / files["ec50"], na_values=["n/a", "NA"])
        ec50.insert(0, "cohort", cohort)
        ec50_rows.append(ec50)

    raw = pd.concat(frames, ignore_index=True)
    chemicals = pd.concat(chemical_rows, ignore_index=True)
    ec50 = pd.concat(ec50_rows, ignore_index=True)
    trajectory_cols = ["cohort", "Plate.SN", "well"]
    timepoint_cols = trajectory_cols + ["DIV"]

    by_trajectory = raw.groupby(trajectory_cols, dropna=False)
    div_counts = by_trajectory["DIV"].nunique()
    stable_exposure = by_trajectory[["trt", "dose", "units"]].nunique(dropna=False)
    duplicate_timepoints = int(raw.duplicated(timepoint_cols, keep=False).sum())

    cohort_summary: dict[str, object] = {}
    for cohort, frame in raw.groupby("cohort"):
        groups = frame.groupby(["Plate.SN", "well"], dropna=False)
        complete = groups["DIV"].nunique().eq(4)
        cohort_summary[cohort] = {
            "records": int(len(frame)),
            "plates": int(frame["Plate.SN"].nunique()),
            "plate_well_trajectories": int(groups.ngroups),
            "complete_four_div_trajectories": int(complete.sum()),
            "div_record_counts": {
                str(int(k)): int(v) for k, v in frame["DIV"].value_counts().sort_index().items()
            },
            "raw_treatment_names": int(frame["trt"].nunique()),
        }

    missing = {
        metric: {
            "count": int(raw[metric].isna().sum()),
            "percent": round(float(raw[metric].isna().mean() * 100), 2),
        }
        for metric in METRICS
    }
    concentration_counts = raw.groupby(["cohort", "trt"])["dose"].nunique()

    return {
        "records": int(len(raw)),
        "plates": int(raw[["cohort", "Plate.SN"]].drop_duplicates().shape[0]),
        "plate_well_trajectories": int(by_trajectory.ngroups),
        "complete_four_div_trajectories": int(div_counts.eq(4).sum()),
        "complete_four_div_percent": round(float(div_counts.eq(4).mean() * 100), 2),
        "duplicate_timepoint_rows": duplicate_timepoints,
        "trajectories_with_exposure_changes": int(stable_exposure.gt(1).any(axis=1).sum()),
        "divs": sorted(int(value) for value in raw["DIV"].unique()),
        "network_parameters": METRICS,
        "official_test_entries": int(len(chemicals)),
        "unique_casrn": int(chemicals["casrn"].nunique()),
        "missing_casrn_entries": int(chemicals["casrn"].isin(["", "nan"]).sum()),
        "raw_treatment_names_combined": int(raw["trt"].nunique()),
        "distinct_dose_values": sorted(float(value) for value in raw["dose"].unique()),
        "concentrations_per_treatment": {
            "minimum": int(concentration_counts.min()),
            "median": float(concentration_counts.median()),
            "maximum": int(concentration_counts.max()),
        },
        "ec50_rows": int(len(ec50)),
        "ec50_numeric_rows": int(pd.to_numeric(ec50["ec"], errors="coerce").notna().sum()),
        "missingness": missing,
        "cohorts": cohort_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("data/raw/epa_nfa/extracted"),
        help="Directory containing the extracted official EPA archive",
    )
    args = parser.parse_args()
    print(json.dumps(audit(args.root), indent=2))


if __name__ == "__main__":
    main()
