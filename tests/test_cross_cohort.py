import numpy as np
import pandas as pd

from meacompass.cross_cohort import split_direction, summarize_endpoint


def test_split_direction_excludes_chemical_overlap() -> None:
    frame = pd.DataFrame(
        {
            "cohort": ["NTP", "NTP", "ToxCast", "ToxCast"],
            "casrn": ["a", "shared", "b", "shared"],
        }
    )
    source, target, overlap = split_direction(frame, "NTP", "ToxCast")
    assert set(source["casrn"]) == {"a", "shared"}
    assert set(target["casrn"]) == {"b"}
    assert overlap == {"shared"}


def test_summary_uses_chemical_bootstrap_and_marks_clear_win() -> None:
    frame = pd.DataFrame(
        {
            "casrn": np.repeat(["a", "b", "c", "d"], 2),
            "target12": np.arange(8, dtype=float),
            "prediction": np.arange(8, dtype=float),
            "bt_plus_prediction": np.arange(8, dtype=float) + 2,
            "bt_plus_plus_prediction": np.arange(8, dtype=float) + 1,
        }
    )
    result = summarize_endpoint(frame)
    assert result["mae"] == 0
    assert result["delta_mae_vs_bt_plus_plus"] == -1
    assert result["win_vs_bt_plus_plus"] is True
