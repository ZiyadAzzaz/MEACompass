from __future__ import annotations
from pathlib import Path
import pandas as pd
from neurochip.result_schema import load_prediction_file

def load_demo_predictions(path: Path = Path("results/standardized_predictions.csv")) -> pd.DataFrame:
    return load_prediction_file(path)
