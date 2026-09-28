import pandas as pd

from neurochip.time_ablation import add_div9_missingness, window_features


def test_window_features_respect_decision_day() -> None:
    frame = pd.DataFrame(
        {
            "div5_r": [1.0],
            "div7_r": [2.0],
            "div9_r": [3.0],
            "div12_r": [4.0],
            "log10_1p_dose": [0.0],
            "cohort_toxcast": [0],
            "chem": [1.0],
        }
    )
    day5 = window_features(frame, ["chem"], 5)
    day9 = window_features(frame, ["chem"], 9)
    assert "div5_r" in day5 and "div7_r" not in day5 and "div9_r" not in day5
    assert "div9_r" in day9 and "div12_r" not in day9


def test_div9_missingness_is_row_local() -> None:
    frame = pd.DataFrame({"div9_metric": [1.0, None]})
    # Use the production metric name set without constructing a full raw table.
    from neurochip import time_ablation

    original = time_ablation.NETWORK_METRICS
    time_ablation.NETWORK_METRICS = ["metric"]
    try:
        output = add_div9_missingness(frame)
    finally:
        time_ablation.NETWORK_METRICS = original
    assert output["div9_metric_missing"].tolist() == [0, 1]
