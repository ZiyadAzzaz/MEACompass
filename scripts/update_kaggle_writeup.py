"""Regenerate the Kaggle endpoint table and public links from frozen artifacts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WRITEUP = ROOT / "docs" / "kaggle_writeup.md"
START = "<!-- GENERATED_MAIN_RESULTS_START -->"
END = "<!-- GENERATED_MAIN_RESULTS_END -->"
LABELS = {
    "burst.per.min": "Bursts/min",
    "meanfiringrate": "Mean firing rate",
    "nAE": "Active electrodes",
    "ns.n": "Network spikes",
    "r": "Coordinated activity (`r`)",
}


def generated_table(results_dir: Path) -> str:
    primary = pd.read_csv(results_dir / "gate_s_main.csv")
    primary = primary.loc[primary["model"].eq("M1")].set_index("endpoint")
    strict = pd.read_csv(results_dir / "bt_plus_plus.csv").set_index("endpoint")
    rows = [
        "| Endpoint | M1 MAE | BT+ MAE | Gain vs BT+ | ΔMAE vs BT+ [95% CI] | BT++ Gain | ΔMAE vs BT++ [95% CI] |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for endpoint, label in LABELS.items():
        left = primary.loc[endpoint]
        right = strict.loc[endpoint]
        rows.append(
            f"| {label} | {left.mae:.2f} | {left.bt_plus_mae:.2f} | "
            f"{left.relative_gain_vs_bt_plus_percent:.1f}% | "
            f"{left.delta_mae_vs_bt_plus:.2f} "
            f"[{left.delta_mae_vs_bt_plus_ci_low:.2f}, {left.delta_mae_vs_bt_plus_ci_high:.2f}] | "
            f"{right.relative_gain_percent:.1f}% | "
            f"{right.delta_mae_vs_bt_plus_plus:.2f} "
            f"[{right.delta_mae_ci_low:.2f}, {right.delta_mae_ci_high:.2f}] |"
        )
    return "\n".join(rows)


def update(path: Path = WRITEUP) -> None:
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise ValueError("Kaggle writeup is missing generated-table markers")
    before, remainder = text.split(START, 1)
    _, after = remainder.split(END, 1)
    replacement = f"{START}\n{generated_table(ROOT / 'results')}\n{END}"
    path.write_text(before + replacement + after, encoding="utf-8")


if __name__ == "__main__":
    update()
