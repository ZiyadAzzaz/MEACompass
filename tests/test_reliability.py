import numpy as np

from meacompass.reliability import cvplus_bounds


def test_cvplus_bounds_use_only_supplied_oof_residuals() -> None:
    residuals = [np.array([1.0, 2.0]), np.array([3.0, 4.0])]
    predictions = [np.array([10.0, 20.0]), np.array([12.0, 22.0])]
    lower, upper = cvplus_bounds(residuals, predictions, alpha=0.25)
    assert np.array_equal(lower, np.array([8.0, 18.0]))
    assert np.array_equal(upper, np.array([16.0, 26.0]))


def test_cvplus_bounds_are_ordered() -> None:
    residuals = [np.array([0.5, 1.5, 2.5])]
    predictions = [np.array([0.0, 100.0])]
    lower, upper = cvplus_bounds(residuals, predictions)
    assert np.all(lower <= upper)
    assert np.allclose(upper - lower, np.array([5.0, 5.0]))
