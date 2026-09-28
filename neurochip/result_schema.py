"""Frozen prediction-schema validation and legacy baseline adaptation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SCHEMA_VERSION = "1.0.0"
REQUIRED_COLUMNS = (
    "sample_id",
    "endpoint",
    "model",
    "chemical_id",
    "cohort",
    "dose",
    "y_true",
    "y_pred",
    "uncertainty",
    "uncertainty_lower",
    "uncertainty_upper",
    "fold",
    "seed",
)
IDENTITY_COLUMNS = ("sample_id", "endpoint", "model", "fold", "seed")


def validate_prediction_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Prediction schema v{SCHEMA_VERSION} missing columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("Prediction file is empty")
    for column in ("sample_id", "endpoint", "model", "chemical_id", "cohort"):
        if frame[column].isna().any() or frame[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Required identifier column contains missing values: {column}")
    for column in ("y_true", "y_pred"):
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values).all():
            raise ValueError(f"Required numeric column is not finite: {column}")
    for column in ("fold", "seed"):
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or not np.equal(values, np.floor(values)).all():
            raise ValueError(f"Required integer column is invalid: {column}")
    if frame.duplicated(list(IDENTITY_COLUMNS)).any():
        raise ValueError("Prediction identity columns are not unique")
    bounds = frame[["uncertainty_lower", "uncertainty_upper"]]
    both = bounds.notna().all(axis=1)
    if (bounds.loc[both, "uncertainty_lower"] > bounds.loc[both, "uncertainty_upper"]).any():
        raise ValueError("Uncertainty lower bound exceeds upper bound")
    return frame


def adapt_baseline_predictions(frame: pd.DataFrame) -> pd.DataFrame:
    """Adapt saved B0/B3-style predictions without inventing unavailable values."""
    mapping = {
        "casrn": "chemical_id",
        "target12": "y_true",
        "prediction": "y_pred",
        "outer_fold": "fold",
    }
    required_legacy = {"sample_id", "endpoint", "model", "casrn", "cohort", "target12", "prediction", "outer_fold", "seed"}
    missing = required_legacy - set(frame.columns)
    if missing:
        raise ValueError(f"Legacy baseline predictions missing columns: {sorted(missing)}")
    output = frame.rename(columns=mapping).copy()
    for column in ("dose", "uncertainty", "uncertainty_lower", "uncertainty_upper"):
        if column not in output:
            output[column] = np.nan
    return validate_prediction_frame(output.loc[:, list(REQUIRED_COLUMNS)])


def load_prediction_file(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(f"Required standardized prediction file is missing: {path}")
    return validate_prediction_frame(pd.read_csv(path))
