"""Regenerate publication artifacts exclusively from saved result files."""

from __future__ import annotations
import argparse
from pathlib import Path
from neurochip.figures import plot_calibration, plot_dose_strata, plot_risk_coverage, plot_time_ablation, write_main_table
from neurochip.result_schema import load_prediction_file

REQUIRED = {
    "main_results": "main_results.csv",
    "predictions": "standardized_predictions.csv",
    "risk_coverage": "risk_coverage.csv",
    "time_ablation": "time_ablation.csv",
    "dose_strata": "dose_strata.csv",
    "calibration": "calibration.csv",
}

def reproduce(results_dir: Path, output_dir: Path) -> None:
    paths = {key: results_dir / name for key, name in REQUIRED.items()}
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("reproduce-lite requires saved results and never retrains. Missing:\n- " + "\n- ".join(missing))
    load_prediction_file(paths["predictions"])
    write_main_table(paths["main_results"], output_dir / "main_results.csv")
    plot_risk_coverage(paths["risk_coverage"], output_dir / "risk_coverage.png")
    plot_time_ablation(paths["time_ablation"], output_dir / "time_ablation.png")
    plot_dose_strata(paths["dose_strata"], output_dir / "dose_strata.png")
    plot_calibration(paths["calibration"], output_dir / "calibration.png")

def main() -> None:
    parser = argparse.ArgumentParser(); parser.add_argument("--results-dir", type=Path, default=Path("results")); parser.add_argument("--output-dir", type=Path, default=Path("artifacts/reproduce-lite"))
    args = parser.parse_args(); reproduce(args.results_dir, args.output_dir)

if __name__ == "__main__": main()
