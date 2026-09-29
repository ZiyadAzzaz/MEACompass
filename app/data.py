from __future__ import annotations
from pathlib import Path
import pandas as pd
from meacompass.result_schema import load_prediction_file

DEMO_COLUMNS = {
    "sample_id", "casrn", "trt", "cohort", "dose", "endpoint",
    "observed_div5", "observed_div7", "observed_div9", "target12",
    "prediction", "uncertainty_lower", "uncertainty_upper",
    "bt_plus_plus_prediction", "day9_prediction", "day9_lower", "day9_upper",
    "verdict",
}

def load_demo_predictions(path: Path = Path("results/standardized_predictions.csv")) -> pd.DataFrame:
    return load_prediction_file(path)


def load_demo_table(path: Path = Path("results/demo_predictions.csv")) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required demo artifact is missing: {path}")
    frame = pd.read_csv(path)
    missing = DEMO_COLUMNS - set(frame.columns)
    if missing:
        raise ValueError(f"Demo artifact is missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Demo artifact is empty")
    return frame
