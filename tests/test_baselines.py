import numpy as np
import pandas as pd

from meacompass.baselines import endpoint_frame, fit_baseline, predict_baseline
from meacompass.evaluate import bootstrap_paired_mae, prediction_metrics
from meacompass.evaluate_m1_gate import gate_m1_decision
from meacompass.train_m1 import compose_m1_prediction, m1_training_target


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


def test_m1_residual_target_and_prediction_round_trip() -> None:
    frame = endpoint_frame(synthetic_frame(), "nAE")
    bt_prediction = frame["target7"].to_numpy()
    residual = m1_training_target(frame, "bt_residual", bt_prediction)
    reconstructed = compose_m1_prediction(residual, "bt_residual", bt_prediction)
    assert np.allclose(reconstructed, frame["target12"])


def test_m1_direct_target_and_prediction_are_unchanged() -> None:
    frame = endpoint_frame(synthetic_frame(), "nAE")
    placeholder_bt = np.zeros(len(frame))
    target = m1_training_target(frame, "direct", placeholder_bt)
    assert np.allclose(
        compose_m1_prediction(target, "direct", placeholder_bt), frame["target12"]
    )


def test_paired_bootstrap_detects_uniformly_better_candidate() -> None:
    frame = pd.DataFrame(
        {
            "casrn": np.repeat(["a", "b", "c"], 3),
            "target12": np.arange(9, dtype=float),
            "candidate": np.arange(9, dtype=float),
            "reference": np.arange(9, dtype=float) + 2,
        }
    )
    low, high = bootstrap_paired_mae(frame, "candidate", "reference", draws=100)
    assert low < 0
    assert high < 0


def test_phase3_gate_m1_requires_two_endpoints_beating_b3() -> None:
    assert gate_m1_decision(pd.DataFrame({"beats_b3": [True, True, False]})) == (
        "SELECT_M1",
        2,
    )
    assert gate_m1_decision(pd.DataFrame({"beats_b3": [True, False, False]})) == (
        "SELECT_B3",
        1,
    )
