"""Pre-registered trivial baselines and endpoint preparation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


ALPHA_GRID = np.asarray([-1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 3.0])
TRIVIAL_MODELS = ("B1", "B1b", "B2")


def endpoint_frame(frame: pd.DataFrame, endpoint: str) -> pd.DataFrame:
    required = [
        f"div5_{endpoint}",
        f"div7_{endpoint}",
        f"div12_{endpoint}",
        f"control_div7_{endpoint}",
        f"control_div12_{endpoint}",
    ]
    eligible = frame[required].notna().all(axis=1)
    eligible &= frame[f"control_div7_{endpoint}"].gt(0)
    eligible &= frame[f"control_div12_{endpoint}"].gt(0)
    output = frame.loc[eligible].copy()
    output["target12"] = (
        100.0 * output[f"div12_{endpoint}"] / output[f"control_div12_{endpoint}"]
    )
    output["target7"] = 100.0 * output[f"div7_{endpoint}"] / output[f"control_div7_{endpoint}"]
    output["delta"] = output["target12"] - output["target7"]
    return output.replace([np.inf, -np.inf], np.nan).dropna(subset=["target12", "target7", "delta"])


@dataclass(frozen=True)
class BaselineFit:
    model: str
    endpoint: str
    parameters: dict[str, object]


def fit_baseline(model: str, train: pd.DataFrame, endpoint: str) -> BaselineFit:
    if model == "B0":
        values = train["log10_1p_dose"].to_numpy()
        edges = np.unique(np.quantile(values, np.linspace(0, 1, 6)))
        bins = np.digitize(values, edges[1:-1], right=True)
        means = {
            int(index): float(train.loc[bins == index, "target12"].mean())
            for index in np.unique(bins)
        }
        parameters = {"edges": edges.tolist(), "means": means, "fallback": float(train["target12"].mean())}
    elif model == "B1":
        parameters = {}
    elif model == "B1b":
        controls = train.loc[
            train["dose"].eq(0) & train[f"div7_{endpoint}"].gt(0),
            [f"div7_{endpoint}", f"div12_{endpoint}"],
        ]
        ratios = controls[f"div12_{endpoint}"] / controls[f"div7_{endpoint}"]
        finite = ratios[np.isfinite(ratios)]
        parameters = {"growth_ratio": float(finite.median()) if len(finite) else 1.0}
    elif model == "B2":
        predictions = np.stack(
            [
                train[f"div7_{endpoint}"].to_numpy()
                + alpha
                * (train[f"div7_{endpoint}"].to_numpy() - train[f"div5_{endpoint}"].to_numpy())
                for alpha in ALPHA_GRID
            ],
            axis=1,
        )
        target_units = 100.0 * predictions / train[f"control_div12_{endpoint}"].to_numpy()[:, None]
        losses = np.nanmean(np.abs(target_units - train["target12"].to_numpy()[:, None]), axis=0)
        parameters = {"alpha": float(ALPHA_GRID[int(np.nanargmin(losses))])}
    else:
        raise ValueError(f"Unknown baseline: {model}")
    return BaselineFit(model=model, endpoint=endpoint, parameters=parameters)


def predict_baseline(fitted: BaselineFit, frame: pd.DataFrame) -> np.ndarray:
    endpoint = fitted.endpoint
    if fitted.model == "B0":
        edges = np.asarray(fitted.parameters["edges"])
        bins = np.digitize(frame["log10_1p_dose"].to_numpy(), edges[1:-1], right=True)
        means = fitted.parameters["means"]
        fallback = float(fitted.parameters["fallback"])
        return np.asarray([means.get(int(index), fallback) for index in bins])
    if fitted.model == "B1":
        return frame["target7"].to_numpy()
    if fitted.model == "B1b":
        return frame["target7"].to_numpy() * float(fitted.parameters["growth_ratio"])
    if fitted.model == "B2":
        alpha = float(fitted.parameters["alpha"])
        raw_prediction = frame[f"div7_{endpoint}"].to_numpy() + alpha * (
            frame[f"div7_{endpoint}"].to_numpy() - frame[f"div5_{endpoint}"].to_numpy()
        )
        return 100.0 * raw_prediction / frame[f"control_div12_{endpoint}"].to_numpy()
    raise ValueError(f"Unknown baseline: {fitted.model}")

