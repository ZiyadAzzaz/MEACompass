from pathlib import Path

import pandas as pd

from scripts.build_static_demo import DISPLAY_ENDPOINTS, select_rows


ROOT = Path(__file__).resolve().parents[1]


def test_static_demo_selection_is_complete_and_deterministic() -> None:
    source = pd.read_csv(ROOT / "results" / "demo_predictions.csv")
    first = select_rows(source, per_cohort=3)
    second = select_rows(source, per_cohort=3)
    pd.testing.assert_frame_equal(first, second)
    assert set(first["endpoint"]) == set(DISPLAY_ENDPOINTS)
    assert first.groupby("sample_id")["endpoint"].nunique().eq(3).all()
    assert first.groupby("cohort")["sample_id"].nunique().eq(3).all()


def test_static_demo_is_self_contained_and_scope_safe() -> None:
    html = (ROOT / "docs" / "demo" / "index.html").read_text(encoding="utf-8")
    assert "MEACompass" in html
    assert "OBSERVED" in html
    assert "PREDICTED" in html
    assert "HYPOTHESIS" in html
    assert "not organ-on-chip experiments" in html
    assert "http://" not in html
    assert "https://" not in html
    assert "__DATA__" not in html
