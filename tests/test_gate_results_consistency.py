import json
from pathlib import Path

import pandas as pd


RESULTS = Path("results")


def test_m2_decision_matches_calibration_table() -> None:
    summary = pd.read_csv(RESULTS / "m2_calibration.csv")
    decision = json.loads((RESULTS / "m2_decision.json").read_text(encoding="utf-8"))
    assert len(summary) == 5
    assert summary["gate_pass"].all()
    assert decision["decision"] == "PASS"
    assert decision["endpoints_passing"] == int(summary["gate_pass"].sum())


def test_m3_decision_matches_risk_coverage_table() -> None:
    risk = pd.read_csv(RESULTS / "m3_risk_coverage.csv")
    at_70 = risk.loc[risk["coverage_target"].eq(0.7)].copy()
    passing = at_70.loc[
        at_70["relative_risk_reduction_percent"].ge(15)
        & at_70["delta_mae_ci_high"].lt(0),
        "endpoint",
    ].tolist()
    decision = json.loads((RESULTS / "m3_decision.json").read_text(encoding="utf-8"))
    assert sorted(passing) == sorted(decision["passing_endpoints"])
    assert decision["passing_count"] == len(passing) == 3


def test_lock_preserves_registered_gate_s_failure() -> None:
    registered = json.loads((RESULTS / "gate_s_decision.json").read_text(encoding="utf-8"))
    lock = json.loads((RESULTS / "l1_decision.json").read_text(encoding="utf-8"))
    assert registered["decision"] == "STOP_SUSPECTED_LEAKAGE_OR_CONFOUNDING"
    assert not registered["m2_authorized"]
    assert lock["basis"]["registered_gate_s"] == "FAIL_STOP_UNCHANGED"
    assert lock["decision"] == "LOCK"
