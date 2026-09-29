"""Build saved, result-only submission and demo artifacts after Gate L1."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yaml

from meacompass.data import build_longitudinal_table
from meacompass.result_schema import REQUIRED_COLUMNS, validate_prediction_frame
from meacompass.sanity_gate import KEYS, attach_identity


def build_publication_tables(results_dir: Path) -> None:
    main = pd.concat(
        [pd.read_csv(results_dir / "baselines.csv"), pd.read_csv(results_dir / "m1.csv")],
        ignore_index=True,
    )
    main.to_csv(results_dir / "main_results.csv", index=False)

    risk = pd.read_csv(results_dir / "m3_risk_coverage.csv").rename(
        columns={"coverage_target": "coverage", "accepted_mae": "mae"}
    )
    risk["model"] = "M1"
    risk.to_csv(results_dir / "risk_coverage.csv", index=False)

    calibration = pd.read_csv(results_dir / "m2_calibration.csv")
    parts = []
    for cohort, column in (
        ("Overall", "overall_coverage"),
        ("NTP", "ntp_coverage"),
        ("ToxCast", "toxcast_coverage"),
    ):
        part = calibration[["endpoint", "nominal_coverage", column]].copy()
        part["cohort"] = cohort
        part = part.rename(columns={column: "observed_coverage"})
        parts.append(part)
    pd.concat(parts, ignore_index=True).to_csv(results_dir / "calibration.csv", index=False)


def build_prediction_and_demo_tables(
    frame: pd.DataFrame, results_dir: Path
) -> None:
    identity = frame[
        ["sample_id", "casrn", "trt", "cohort", "dose"]
        + [f"div{day}_{endpoint}" for day in (5, 7, 9) for endpoint in ("meanfiringrate", "burst.per.min", "nAE", "ns.n", "r")]
    ].drop_duplicates("sample_id")
    if identity["sample_id"].duplicated().any():
        raise ValueError("Demo metadata must be unique by sample_id")

    m2 = pd.read_csv(results_dir / "m2_predictions.csv")
    seed0 = m2.loc[m2["seed"].eq(0)].merge(
        identity[["sample_id", "dose"]], on="sample_id", how="left", validate="many_to_one"
    )
    standardized = seed0.rename(
        columns={
            "casrn": "chemical_id",
            "target12": "y_true",
            "prediction": "y_pred",
            "outer_fold": "fold",
        }
    ).copy()
    standardized["model"] = "M1_DIV7"
    standardized = standardized[list(REQUIRED_COLUMNS)]
    validate_prediction_frame(standardized).to_csv(
        results_dir / "standardized_predictions.csv", index=False
    )

    m3 = pd.read_csv(results_dir / "m3_predictions.csv")
    verdict = m3.loc[m3["seed"].eq(0), KEYS + ["verdict", "accepted"]]
    btpp = pd.read_csv(results_dir / "bt_plus_plus_predictions.csv")
    btpp = btpp.loc[btpp["seed"].eq(0), KEYS + ["prediction", "bt_plus_plus_model"]].rename(
        columns={"prediction": "bt_plus_plus_prediction"}
    )
    time = pd.read_csv(results_dir / "time_ablation_predictions.csv")
    day9 = time.loc[
        time["seed"].eq(0) & time["input_window"].eq("DIV5+7+9"),
        KEYS + ["prediction", "uncertainty_lower", "uncertainty_upper", "uncertainty"],
    ].rename(
        columns={
            "prediction": "day9_prediction",
            "uncertainty_lower": "day9_lower",
            "uncertainty_upper": "day9_upper",
            "uncertainty": "day9_width",
        }
    )
    demo = m2.loc[m2["seed"].eq(0)].merge(verdict, on=KEYS, how="left", validate="one_to_one")
    demo = demo.merge(btpp, on=KEYS, how="left", validate="one_to_one")
    demo = demo.merge(day9, on=KEYS, how="left", validate="one_to_one")
    demo = demo.merge(identity, on=["sample_id", "casrn", "cohort"], how="left", validate="many_to_one")
    demo["observed_div5"] = demo.apply(lambda row: row[f"div5_{row['endpoint']}"], axis=1)
    demo["observed_div7"] = demo.apply(lambda row: row[f"div7_{row['endpoint']}"], axis=1)
    demo["observed_div9"] = demo.apply(lambda row: row[f"div9_{row['endpoint']}"], axis=1)
    keep = [
        "sample_id", "casrn", "trt", "cohort", "dose", "endpoint", "outer_fold",
        "observed_div5", "observed_div7", "observed_div9", "target12", "prediction",
        "uncertainty_lower", "uncertainty_upper", "uncertainty", "bt_plus_plus_prediction",
        "bt_plus_plus_model", "day9_prediction", "day9_lower", "day9_upper", "day9_width",
        "verdict", "accepted",
    ]
    demo[keep].to_csv(results_dir / "demo_predictions.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/baselines.yaml"))
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    results_dir = Path(config["results_dir"])
    build_publication_tables(results_dir)
    frame = attach_identity(build_longitudinal_table(Path(config["data_root"])))
    build_prediction_and_demo_tables(frame, results_dir)


if __name__ == "__main__":
    main()
