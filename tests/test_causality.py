from pathlib import Path

import pytest

from meacompass.data import (
    build_longitudinal_table,
    primary_feature_columns,
    validate_time_causal_features,
)


DATA_ROOT = Path("data/raw/epa_nfa/extracted")


@pytest.mark.skipif(not DATA_ROOT.exists(), reason="official EPA data not downloaded")
def test_primary_feature_view_contains_only_div5_and_div7() -> None:
    frame = build_longitudinal_table(DATA_ROOT)
    features = primary_feature_columns(frame)
    assert features
    assert all("div9" not in column.lower() for column in features)
    assert all("div12" not in column.lower() for column in features)
    assert not any(column.startswith("control_") for column in features)


@pytest.mark.parametrize(
    "forbidden",
    ["div9_nAE", "div12_meanfiringrate", "control_div12_r", "official_ec50", "hit_call"],
)
def test_causality_validator_fails_closed(forbidden: str) -> None:
    with pytest.raises(ValueError, match="forbidden"):
        validate_time_causal_features(["div5_nAE", forbidden])
