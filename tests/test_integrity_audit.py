from pathlib import Path

import numpy as np
import pandas as pd

from meacompass.data import validate_time_causal_features
from meacompass.integrity_audit import block_permute, full_shuffle, lineage_table
from meacompass.splits import assert_group_disjoint, outer_folds


def test_audit_lineage_rejects_every_forbidden_future_family() -> None:
    forbidden = ["div9_nAE", "div12_r", "control_div12_nAE", "ec50", "hit_call", "late_viability"]
    for feature in forbidden:
        try:
            validate_time_causal_features([feature])
        except ValueError:
            continue
        raise AssertionError(f"Forbidden audit feature was accepted: {feature}")


def test_block_permutation_has_no_self_maps_or_index_rejoin() -> None:
    rows = []
    for chemical, offset in zip("abcde", range(0, 50, 10), strict=True):
        for index in range(3):
            rows.append({"casrn": chemical, "dose": index, "Plate.SN": "p", "well": f"{chemical}{index}", "target12": offset + index})
    original = pd.DataFrame(rows)
    permuted, mapping = block_permute(original, "burst.per.min", 0, 20260928)
    assert all(recipient != donor for recipient, donor in mapping.items())
    assert np.mean(original["target12"].to_numpy() == permuted["target12"].to_numpy()) == 0


def test_full_shuffle_is_reproducible_and_breaks_alignment() -> None:
    frame = pd.DataFrame({"target12": np.arange(100, dtype=float)})
    first = full_shuffle(frame, 7)
    second = full_shuffle(frame, 7)
    assert np.array_equal(first["target12"], second["target12"])
    assert not np.array_equal(first["target12"], frame["target12"])


def test_canonical_groups_and_trajectories_are_outer_disjoint() -> None:
    frame = pd.DataFrame(
        {
            "casrn": np.repeat([f"c{i}" for i in range(10)], 2),
            "cohort": np.tile(["NTP", "ToxCast"], 10),
            "sample_id": [f"s{i}" for i in range(20)],
        }
    )
    seen = []
    for train_idx, test_idx in outer_folds(frame, seed=0, n_splits=5):
        assert_group_disjoint(frame, train_idx, test_idx)
        assert set(frame.iloc[train_idx]["sample_id"]).isdisjoint(frame.iloc[test_idx]["sample_id"])
        seen.extend(frame.iloc[test_idx]["sample_id"])
    assert sorted(seen) == sorted(frame["sample_id"])
