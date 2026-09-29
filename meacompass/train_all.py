"""Documented end-to-end rebuild of the locked pipeline.

This command is intentionally guarded because it regenerates ignored checkpoints
and result files. It does not run during result-only reproduction.
"""

from __future__ import annotations

import argparse
import subprocess
import sys


COMMANDS = [
    [sys.executable, "scripts/build_treatment_crosswalk.py"],
    [sys.executable, "scripts/resolve_pubchem_smiles.py"],
    [sys.executable, "-m", "meacompass.train_baselines"],
    [sys.executable, "-m", "meacompass.build_bt_plus"],
    [sys.executable, "-m", "meacompass.train_m1"],
    [sys.executable, "-m", "meacompass.evaluate_m1_gate"],
    [sys.executable, "-m", "meacompass.sanity_gate", "--stage", "permutation"],
    [sys.executable, "-m", "meacompass.sanity_gate", "--stage", "div5"],
    [sys.executable, "-m", "meacompass.sanity_gate", "--stage", "evaluate"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "mechanism"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "dose_smooth"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "full_shuffle"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "summarize_basic", "--diagnostic", "dose_smooth"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "summarize_basic", "--diagnostic", "full_shuffle"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "block_permutation"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "summarize_block"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "decomposition"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "summarize_decomposition"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "baseline_asymmetry"],
    [sys.executable, "-m", "meacompass.integrity_audit", "--stage", "real_vs_null"],
    [sys.executable, "-m", "meacompass.reliability", "--stage", "btpp"],
    [sys.executable, "-m", "meacompass.reliability", "--stage", "summarize_btpp"],
    [sys.executable, "-m", "meacompass.reliability", "--stage", "cvplus"],
    [sys.executable, "-m", "meacompass.reliability", "--stage", "summarize_m2"],
    [sys.executable, "-m", "meacompass.reliability", "--stage", "m3"],
    [sys.executable, "-m", "meacompass.time_ablation", "--stage", "run", "--window", "DIV5"],
    [sys.executable, "-m", "meacompass.time_ablation", "--stage", "run", "--window", "DIV5+7+9"],
    [sys.executable, "-m", "meacompass.time_ablation", "--stage", "summarize"],
    [sys.executable, "-m", "meacompass.time_ablation", "--stage", "practical"],
    [sys.executable, "-m", "meacompass.potency"],
    [sys.executable, "-m", "meacompass.interpretability"],
    [sys.executable, "-m", "meacompass.submission_artifacts"],
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm-locked-rebuild", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    for command in COMMANDS:
        print(" ".join(command))
    if args.dry_run:
        return
    if not args.confirm_locked_rebuild:
        raise SystemExit(
            "Refusing to regenerate locked results without --confirm-locked-rebuild "
            "(make train-all CONFIRM_LOCKED_REBUILD=1)."
        )
    for command in COMMANDS:
        subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
