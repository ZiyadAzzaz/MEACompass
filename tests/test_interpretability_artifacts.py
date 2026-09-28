from pathlib import Path

import pandas as pd


def test_interpretability_artifacts_are_complete() -> None:
    root = Path("results")
    importance = pd.read_csv(root / "feature_importance.csv")
    cases = pd.read_csv(root / "case_studies.csv")
    contributions = pd.read_csv(root / "case_contributions.csv")
    assert importance["endpoint"].nunique() == 5
    assert importance.groupby("endpoint")["rank"].min().eq(1).all()
    assert importance.groupby("endpoint").size().eq(2139).all()
    assert cases["case_type"].value_counts().to_dict() == {"correct": 3, "failure": 2}
    assert set(cases["sample_id"]).issubset(set(contributions["sample_id"]))
    assert contributions["absolute_rank"].between(1, 8).all()
