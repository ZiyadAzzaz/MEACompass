from __future__ import annotations
import argparse
from pathlib import Path
from neurochip.figures import plot_calibration

parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args(); plot_calibration(args.input, args.output)
