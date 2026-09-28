"""Result-only tables and figures; this module never trains or tunes a model."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def require_columns(frame: pd.DataFrame, columns: set[str], source: Path) -> None:
    missing = columns - set(frame.columns)
    if missing:
        raise ValueError(f"{source} is missing required columns: {sorted(missing)}")


def load_required(path: Path, columns: set[str]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required saved result file is missing: {path}")
    frame = pd.read_csv(path)
    require_columns(frame, columns, path)
    return frame


def write_main_table(source: Path, output: Path, models: list[str] | None = None) -> None:
    columns = {"model", "endpoint", "mae_y12_mean", "spearman_y12_mean", "spearman_delta_mean"}
    frame = load_required(source, columns)
    if models:
        frame = frame.loc[frame["model"].isin(models)]
    if frame.empty:
        raise ValueError("Main-results model filter produced no rows")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.sort_values(["endpoint", "model"]).to_csv(output, index=False)


def plot_risk_coverage(source: Path, output: Path) -> None:
    frame = load_required(source, {"endpoint", "model", "coverage", "mae"})
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for (endpoint, model), part in frame.groupby(["endpoint", "model"]):
        part = part.sort_values("coverage")
        ax.plot(part["coverage"], part["mae"], marker="o", label=f"{endpoint} · {model}")
    ax.set(xlabel="Accepted coverage", ylabel="Accepted-case MAE", title="Risk–coverage")
    ax.legend(fontsize=7)
    fig.tight_layout(); output.parent.mkdir(parents=True, exist_ok=True); fig.savefig(output, dpi=180); plt.close(fig)


def plot_time_ablation(source: Path, output: Path) -> None:
    frame = load_required(source, {"endpoint", "input_window", "decision_day", "mae", "coverage", "abstention_rate"})
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for endpoint, part in frame.groupby("endpoint"):
        part = part.sort_values("decision_day")
        axes[0].plot(part["decision_day"], part["mae"], marker="o", label=endpoint)
        axes[1].plot(part["decision_day"], part["abstention_rate"], marker="o", label=endpoint)
    axes[0].set(xlabel="Decision day", ylabel="MAE", title="Accuracy by decision day")
    axes[1].set(xlabel="Decision day", ylabel="Abstention rate", title="Abstention by decision day")
    axes[0].legend(fontsize=7); fig.tight_layout(); output.parent.mkdir(parents=True, exist_ok=True); fig.savefig(output, dpi=180); plt.close(fig)


def plot_dose_strata(source: Path, output: Path) -> None:
    frame = load_required(source, {"endpoint", "model", "dose_stratum", "relative_gain_percent"})
    pivot = frame.pivot_table(index="endpoint", columns="dose_stratum", values="relative_gain_percent", aggfunc="mean")
    ax = pivot.plot(kind="bar", figsize=(9, 4.8))
    ax.axhline(0, color="black", linewidth=0.8); ax.set(ylabel="Relative MAE gain vs BT+ (%)", title="Dose-stratified evaluation")
    ax.figure.tight_layout(); output.parent.mkdir(parents=True, exist_ok=True); ax.figure.savefig(output, dpi=180); plt.close(ax.figure)


def plot_calibration(source: Path, output: Path) -> None:
    frame = load_required(source, {"endpoint", "cohort", "nominal_coverage", "observed_coverage"})
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], linestyle="--", color="grey", label="Ideal")
    for (endpoint, cohort), part in frame.groupby(["endpoint", "cohort"]):
        part = part.sort_values("nominal_coverage")
        ax.plot(part["nominal_coverage"], part["observed_coverage"], marker="o", label=f"{endpoint} · {cohort}")
    ax.set(xlim=(0, 1), ylim=(0, 1), xlabel="Nominal coverage", ylabel="Observed coverage", title="Interval calibration")
    ax.legend(fontsize=7); fig.tight_layout(); output.parent.mkdir(parents=True, exist_ok=True); fig.savefig(output, dpi=180); plt.close(fig)
