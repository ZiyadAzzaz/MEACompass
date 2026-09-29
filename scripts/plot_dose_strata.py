from __future__ import annotations
import argparse
from pathlib import Path
from meacompass.figures import plot_dose_strata

parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args(); plot_dose_strata(args.input, args.output)
