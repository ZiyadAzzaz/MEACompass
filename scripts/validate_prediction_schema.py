from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
from meacompass.result_schema import adapt_baseline_predictions, load_prediction_file

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--legacy-baseline", action="store_true")
parser.add_argument("--models", nargs="*", default=[])
args = parser.parse_args()
if args.legacy_baseline:
    frame = pd.read_csv(args.input)
    if args.models:
        frame = frame.loc[frame["model"].isin(args.models)]
    validated = adapt_baseline_predictions(frame)
else:
    validated = load_prediction_file(args.input)
print(f"schema=1.0.0 rows={len(validated)} models={sorted(validated['model'].unique())}")
