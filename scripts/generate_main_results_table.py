from __future__ import annotations
import argparse
from pathlib import Path
from meacompass.figures import write_main_table

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--models", nargs="*")
args = parser.parse_args()
write_main_table(args.input, args.output, args.models)
