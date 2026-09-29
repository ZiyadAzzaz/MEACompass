from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from meacompass.figures import (
    load_required,
    write_main_table,
)
from meacompass.reproduce_lite import reproduce
from meacompass.result_schema import REQUIRED_COLUMNS, adapt_baseline_predictions, validate_prediction_frame


def test_b0_b3_legacy_predictions_match_frozen_schema() -> None:
    legacy = pd.DataFrame(
        {
            "sample_id": ["NTP|P1|A01", "NTP|P1|A01"],
            "endpoint": ["nAE", "nAE"],
            "model": ["B0", "B3"],
            "casrn": ["50-00-0", "50-00-0"],
            "cohort": ["NTP", "NTP"],
            "target12": [90.0, 90.0],
            "prediction": [100.0, 92.0],
            "outer_fold": [0, 0],
            "seed": [0, 0],
        }
    )
    adapted = adapt_baseline_predictions(legacy)
    assert tuple(adapted.columns) == REQUIRED_COLUMNS
    assert adapted["dose"].isna().all()
    assert set(adapted["model"]) == {"B0", "B3"}


def test_schema_rejects_duplicate_prediction_identity() -> None:
    row = {column: np.nan for column in REQUIRED_COLUMNS}
    row.update(sample_id="x", endpoint="nAE", model="B0", chemical_id="a", cohort="NTP", y_true=1.0, y_pred=1.0, fold=0, seed=0)
    with pytest.raises(ValueError, match="not unique"):
        validate_prediction_frame(pd.DataFrame([row, row]))


def test_result_only_figure_inputs_accept_frozen_contracts() -> None:
    output_root = Path("artifacts/test-result-infrastructure")
    output_root.mkdir(parents=True, exist_ok=True)
    main = pd.DataFrame({"model": ["B0", "B3"], "endpoint": ["nAE", "nAE"], "mae_y12_mean": [2.0, 1.0], "spearman_y12_mean": [0.1, 0.2], "spearman_delta_mean": [0.2, 0.3]})
    risk = pd.DataFrame({"endpoint": ["nAE"] * 2, "model": ["B3"] * 2, "coverage": [0.7, 1.0], "mae": [1.0, 2.0]})
    time = pd.DataFrame({"endpoint": ["nAE"] * 2, "input_window": ["DIV5", "DIV5+7"], "decision_day": [5, 7], "mae": [3.0, 2.0], "coverage": [0.9, 0.9], "abstention_rate": [0.4, 0.3]})
    dose = pd.DataFrame({"endpoint": ["nAE"] * 2, "model": ["B3"] * 2, "dose_stratum": ["low", "mid"], "relative_gain_percent": [1.0, 2.0]})
    calibration = pd.DataFrame({"endpoint": ["nAE"] * 2, "cohort": ["NTP"] * 2, "nominal_coverage": [0.8, 0.9], "observed_coverage": [0.79, 0.88]})
    inputs = {"main.csv": main, "risk.csv": risk, "time.csv": time, "dose.csv": dose, "calibration.csv": calibration}
    for name, frame in inputs.items(): frame.to_csv(output_root / name, index=False)
    write_main_table(output_root / "main.csv", output_root / "main_out.csv", ["B0", "B3"])
    load_required(output_root / "risk.csv", {"endpoint", "model", "coverage", "mae"})
    load_required(output_root / "time.csv", {"endpoint", "input_window", "decision_day", "mae", "coverage", "abstention_rate"})
    load_required(output_root / "dose.csv", {"endpoint", "model", "dose_stratum", "relative_gain_percent"})
    load_required(output_root / "calibration.csv", {"endpoint", "cohort", "nominal_coverage", "observed_coverage"})
    assert (output_root / "main_out.csv").stat().st_size > 0


def test_reproduce_lite_fails_explicitly_and_never_trains() -> None:
    with pytest.raises(FileNotFoundError, match="never retrains"):
        reproduce(Path("artifacts/intentionally-missing-results"), Path("artifacts/test-output"))
    source = Path("meacompass/reproduce_lite.py").read_text(encoding="utf-8")
    assert "train_baselines" not in source
    assert "train_m1" not in source
