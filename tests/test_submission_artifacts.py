from pathlib import Path

import pandas as pd

from app.data import load_demo_table
from neurochip.result_schema import load_prediction_file


RESULTS = Path("results")


def test_saved_submission_artifacts_are_schema_complete() -> None:
    predictions = load_prediction_file(RESULTS / "standardized_predictions.csv")
    demo = load_demo_table(RESULTS / "demo_predictions.csv")
    assert len(predictions) > 0
    assert predictions["model"].eq("M1_DIV7").all()
    assert {"meanfiringrate", "nAE", "r"}.issubset(set(demo["endpoint"]))
    assert demo["verdict"].isin(["EARLY DECISION POSSIBLE", "CONTINUE TO DIV12"]).all()


def test_time_and_practical_tables_cover_all_endpoints() -> None:
    time = pd.read_csv(RESULTS / "time_ablation.csv")
    practical = pd.read_csv(RESULTS / "practical_value.csv")
    assert len(time) == 15
    assert set(time["decision_day"]) == {5, 7, 9}
    assert time["coverage"].between(0.85, 0.95).all()
    assert len(practical) == 5
    assert practical["accepted_percent"].between(69.9, 70.1).all()
    assert practical["days_saved_per_accepted_case"].eq(5).all()
