import numpy as np

from neurochip.potency import estimate_div12_ec50


def test_potency_recovers_simple_decreasing_curve() -> None:
    dose = np.array([0, 0.1, 0.3, 1, 3, 10], dtype=float)
    response = 100 / (1 + dose / 2)
    estimate, method = estimate_div12_ec50(dose, response)
    assert method == "hill_fixed_0_100_grid"
    assert abs(estimate - 2) < 0.2


def test_potency_refuses_non_crossing_curve() -> None:
    estimate, method = estimate_div12_ec50(
        np.array([0, 1, 3, 10], dtype=float), np.array([100, 95, 90, 85], dtype=float)
    )
    assert np.isnan(estimate)
    assert method == "no_high_dose_50pct_crossing"
