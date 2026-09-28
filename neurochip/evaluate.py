"""Metrics and chemical-level bootstrap intervals."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error


def safe_spearman(actual: np.ndarray, predicted: np.ndarray) -> float:
    if len(actual) < 2 or np.unique(actual).size < 2 or np.unique(predicted).size < 2:
        return float("nan")
    # Spearman is Pearson correlation of average ranks. Computing the short
    # formula directly avoids a fragile Windows BLAS path in scipy/numpy.corrcoef.
    actual_rank = pd.Series(actual).rank(method="average").to_numpy(dtype=float)
    predicted_rank = pd.Series(predicted).rank(method="average").to_numpy(dtype=float)
    actual_centered = actual_rank - actual_rank.mean()
    predicted_centered = predicted_rank - predicted_rank.mean()
    denominator = float(
        np.sqrt(np.sum(actual_centered**2) * np.sum(predicted_centered**2))
    )
    if denominator == 0:
        return float("nan")
    return float(np.sum(actual_centered * predicted_centered) / denominator)


def prediction_metrics(frame: pd.DataFrame) -> dict[str, float]:
    actual = frame["target12"].to_numpy()
    predicted = frame["prediction"].to_numpy()
    actual_delta = frame["delta"].to_numpy()
    predicted_delta = predicted - frame["target7"].to_numpy()
    bt = frame["bt_prediction"].to_numpy()
    mae = mean_absolute_error(actual, predicted)
    bt_mae = mean_absolute_error(actual, bt)
    return {
        "mae_y12": float(mae),
        "rmse_y12": float(mean_squared_error(actual, predicted) ** 0.5),
        "spearman_y12": safe_spearman(actual, predicted),
        "mae_delta": float(mean_absolute_error(actual_delta, predicted_delta)),
        "spearman_delta": safe_spearman(actual_delta, predicted_delta),
        "delta_mae_vs_bt": float(mae - bt_mae),
        "relative_gain_percent": float(100.0 * (bt_mae - mae) / bt_mae) if bt_mae else float("nan"),
    }


def bootstrap_delta_mae(
    frame: pd.DataFrame, draws: int = 1000, seed: int = 20260928
) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    errors = frame.assign(
        model_absolute_error=np.abs(frame["target12"] - frame["prediction"]),
        bt_absolute_error=np.abs(frame["target12"] - frame["bt_prediction"]),
    )
    grouped = errors.groupby("casrn", sort=True).agg(
        model_sum=("model_absolute_error", "sum"),
        bt_sum=("bt_absolute_error", "sum"),
        count=("model_absolute_error", "size"),
    )
    # Sampling group indices is exactly the registered cluster bootstrap, but
    # aggregating sums/counts first avoids reconstructing thousands of DataFrames.
    sampled = rng.integers(0, len(grouped), size=(draws, len(grouped)))
    model_sums = grouped["model_sum"].to_numpy()[sampled].sum(axis=1)
    bt_sums = grouped["bt_sum"].to_numpy()[sampled].sum(axis=1)
    counts = grouped["count"].to_numpy()[sampled].sum(axis=1)
    estimates = model_sums / counts - bt_sums / counts
    return float(np.quantile(estimates, 0.025)), float(np.quantile(estimates, 0.975))
