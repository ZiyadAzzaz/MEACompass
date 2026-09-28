import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


def test_report_headline_matches_saved_results() -> None:
    report = (ROOT / "docs" / "report_draft.md").read_text(encoding="utf-8")
    main = pd.read_csv(RESULTS / "gate_s_main.csv")
    m1 = main.loc[main["model"].eq("M1")]
    strict = pd.read_csv(RESULTS / "bt_plus_plus.csv")

    assert round(m1["relative_gain_vs_bt_plus_percent"].min(), 1) == 14.2
    assert round(m1["relative_gain_vs_bt_plus_percent"].max(), 1) == 39.0
    assert (m1["delta_mae_vs_bt_plus_ci_high"] < 0).all()
    assert round(strict["relative_gain_percent"].min(), 1) == 12.3
    assert round(strict["relative_gain_percent"].max(), 1) == 42.9
    assert (strict["delta_mae_ci_high"] < 0).all()
    assert "14.2–39.0%" in report
    assert "12.3–42.9%" in report


def test_report_preserves_gate_s_failure_and_l1_scope() -> None:
    report = (ROOT / "docs" / "report_draft.md").read_text(encoding="utf-8")
    gate_s = json.loads((RESULTS / "gate_s_decision.json").read_text())
    audit = json.loads((RESULTS / "audit" / "audit_decision.json").read_text())
    l1 = json.loads((RESULTS / "l1_decision.json").read_text())

    assert gate_s["decision"] == "STOP_SUSPECTED_LEAKAGE_OR_CONFOUNDING"
    assert audit["registered_gate_s_decision"] == "FAIL_STOP_UNCHANGED"
    assert audit["decision"] == "PASS_RESIDUAL_STRUCTURE_UNDER_NULL"
    assert l1["decision"] == "LOCK"
    assert "Gate S was STOP" in report
    assert "does not erase the registered stop" in report
    assert "not an autonomous assay-termination system" in report


def test_report_calibration_and_m3_numbers_match() -> None:
    report = (ROOT / "docs" / "report_draft.md").read_text(encoding="utf-8")
    m2 = pd.read_csv(RESULTS / "m2_calibration.csv")
    m3 = json.loads((RESULTS / "m3_decision.json").read_text())

    assert round(100 * m2["overall_coverage"].min(), 2) == 91.03
    assert round(100 * m2["overall_coverage"].max(), 2) == 92.40
    assert m3["passing_count"] == 3
    assert m3["endpoints_total"] == 5
    assert "91.03–92.40%" in report
    assert "passed on three of five endpoints" in report


def test_submission_narrative_names_all_endpoints_and_scope() -> None:
    files = ["report_draft.md", "defense_qa.md", "video_script.md", "slides_outline.md"]
    combined = "\n".join(
        (ROOT / "docs" / name).read_text(encoding="utf-8").lower() for name in files
    )
    for term in [
        "mean firing rate",
        "bursts",
        "active electrodes",
        "network spikes",
        "coordinated activity",
        "rat cortical",
        "not an organ-on-chip dataset",
    ]:
        assert term in combined
