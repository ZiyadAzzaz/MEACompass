from pathlib import Path

import pandas as pd
import pytest

from neurochip.data import (
    EXCLUDED_RAW_TREATMENTS,
    attach_canonical_cas,
    build_treatment_crosswalk,
    load_raw,
)
from neurochip.splits import outer_folds


DATA_ROOT = Path("data/raw/epa_nfa/extracted")


@pytest.mark.skipif(not DATA_ROOT.exists(), reason="official EPA data not downloaded")
def test_official_crosswalk_is_complete_and_has_136_chemicals() -> None:
    crosswalk = build_treatment_crosswalk(DATA_ROOT)
    excluded = crosswalk.loc[crosswalk["casrn"].eq("")]
    assert len(excluded) == len(EXCLUDED_RAW_TREATMENTS) == 3

    raw = attach_canonical_cas(load_raw(DATA_ROOT), DATA_ROOT)
    assert raw["casrn"].nunique() == 136
    assert not raw["casrn"].isna().any()


@pytest.mark.skipif(not DATA_ROOT.exists(), reason="official EPA data not downloaded")
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_outer_folds_have_no_cas_leakage(seed: int) -> None:
    raw = attach_canonical_cas(load_raw(DATA_ROOT), DATA_ROOT)
    trajectories = raw[["cohort", "Plate.SN", "well", "casrn"]].drop_duplicates()
    seen_test_groups: set[str] = set()
    for train_index, test_index in outer_folds(trajectories, seed=seed):
        train_cas = set(trajectories.iloc[train_index]["casrn"])
        test_cas = set(trajectories.iloc[test_index]["casrn"])
        assert train_cas.isdisjoint(test_cas)
        seen_test_groups.update(test_cas)
    assert seen_test_groups == set(trajectories["casrn"])


def test_split_helper_rejects_empty_cas() -> None:
    frame = pd.DataFrame({"casrn": ["1-11-1", ""], "cohort": ["NTP", "ToxCast"]})
    with pytest.raises(ValueError, match="non-empty"):
        list(outer_folds(frame, seed=0, n_splits=2))

