import numpy as np
import pandas as pd

from neurochip.baselines import endpoint_frame, fit_baseline, predict_baseline
from neurochip.evaluate import prediction_metrics


def synthetic_frame() -> pd.DataFrame:
    rows = 12
    return pd.DataFrame(
        {
            "dose": np.tile([0.0, 0.1, 1.0], 4),
            "log10_1p_dose": np.log10(1 + np.tile([0.0, 0.1, 1.0], 4)),
            "div5_nAE": np.arange(rows, dtype=float) + 1,
            "div7_nAE": np.arange(rows, dtype=float) + 2,
            "div12_nAE": np.arange(rows, dtype=float) + 4,
            "control_div7_nAE": np.full(rows, 10.0),
            "control_div12_nAE": np.full(rows, 20.0),
        }
    )


def test_endpoint_target_and_delta_are_matched_control_ratios() -> None:
    frame = endpoint_frame(synthetic_frame(), "nAE")
    assert np.allclose(frame["target12"], 100 * frame["div12_nAE"] / 20)
    assert np.allclose(frame["delta"], frame["target12"] - 100 * frame["div7_nAE"] / 10)


def test_all_trivial_baselines_produce_finite_predictions() -> None:
    frame = endpoint_frame(synthetic_frame(), "nAE")
    for model in ["B0", "B1", "B1b", "B2"]:
        prediction = predict_baseline(fit_baseline(model, frame, "nAE"), frame)
        assert prediction.shape == (len(frame),)
        assert np.isfinite(prediction).all()


def test_locf_has_undefined_delta_spearman() -> None:
    frame = endpoint_frame(synthetic_frame(), "nAE")
    frame["prediction"] = frame["target7"]
    frame["bt_prediction"] = frame["target7"]
    metrics = prediction_metrics(frame)
    assert np.isnan(metrics["spearman_delta"])

