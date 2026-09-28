import numpy as np
import pandas as pd

from neurochip.sanity_gate import paired_summary, permute_targets_by_chemical


def test_group_permutation_moves_whole_chemical_blocks() -> None:
    rows = []
    for chemical, offset, size in [("a", 0, 3), ("b", 10, 4), ("c", 20, 5), ("d", 30, 3)]:
        for index in range(size):
            rows.append(
                {
                    "casrn": chemical,
                    "dose": float(index),
                    "Plate.SN": "P",
                    "well": f"{chemical}{index}",
                    "target12": float(offset + index),
                }
            )
    frame = pd.DataFrame(rows)
    permuted, mapping = permute_targets_by_chemical(frame, "nAE", 0)
    assert all(recipient != donor for recipient, donor in mapping.items())
    assert set(mapping) == {"a", "b", "c", "d"}
    assert not np.allclose(permuted["target12"], frame["target12"])


def test_paired_summary_reports_beneficial_gain() -> None:
    frame = pd.DataFrame(
        {
            "model": ["M1"] * 6,
            "endpoint": ["nAE"] * 6,
            "casrn": np.repeat(["a", "b", "c"], 2),
            "target12": np.arange(6, dtype=float),
            "prediction": np.arange(6, dtype=float),
            "bt_prediction": np.arange(6, dtype=float) + 2,
            "bt_plus_prediction": np.arange(6, dtype=float) + 1,
        }
    )
    result = paired_summary(frame)
    assert result.loc[0, "delta_mae_vs_bt_plus"] < 0
    assert result.loc[0, "relative_gain_vs_bt_plus_percent"] > 0
