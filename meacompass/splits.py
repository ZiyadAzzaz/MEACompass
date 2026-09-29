"""Chemical-disjoint split utilities with fail-closed leakage checks."""

from __future__ import annotations

from collections.abc import Iterator

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold


def assert_group_disjoint(
    frame: pd.DataFrame, train_index: np.ndarray, test_index: np.ndarray, group_column: str = "casrn"
) -> None:
    train_groups = set(frame.iloc[train_index][group_column])
    test_groups = set(frame.iloc[test_index][group_column])
    overlap = train_groups & test_groups
    if overlap:
        raise AssertionError(f"Chemical leakage across split: {sorted(overlap)}")


def outer_folds(
    frame: pd.DataFrame, seed: int, n_splits: int = 5
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    required = {"casrn", "cohort"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Split frame is missing required columns: {sorted(missing)}")
    if frame["casrn"].isna().any() or frame["casrn"].eq("").any():
        raise ValueError("Canonical CAS groups must be non-empty")
    splitter = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    placeholder = np.zeros(len(frame), dtype=np.int8)
    for train_index, test_index in splitter.split(
        placeholder, y=frame["cohort"], groups=frame["casrn"]
    ):
        assert_group_disjoint(frame, train_index, test_index)
        yield train_index, test_index
