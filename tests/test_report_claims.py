from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
ENDPOINTS = {"burst.per.min", "meanfiringrate", "nAE", "ns.n", "r"}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat_text(path: Path) -> str:
    return " ".join(_text(path).split())


def _deck_text() -> str:
    published = DOCS / "MEACompass_Competition_Deck.pptx"
    working = DOCS / "MEACompass_Competition_Deck_WORKING.pptx"
    decks = [published] if published.exists() else ([working] if working.exists() else [])
    assert len(decks) == 1
    with ZipFile(decks[0]) as archive:
        slide_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )
        return " ".join(archive.read(name).decode("utf-8") for name in slide_names)


def test_all_five_headline_claims_are_supported() -> None:
    main = pd.read_csv(RESULTS / "gate_s_main.csv")
    m1 = main.loc[main["model"].eq("M1")]
    strict = pd.read_csv(RESULTS / "bt_plus_plus.csv")

    assert set(m1["endpoint"]) == ENDPOINTS
    assert (m1["delta_mae_vs_bt_plus_ci_high"] < 0).all()
    assert set(strict["endpoint"]) == ENDPOINTS
    assert (strict["delta_mae_ci_high"] < 0).all()

    corpus = "\n".join(
        [
            _text(ROOT / "README.md"),
            _text(DOCS / "report_draft.md"),
            _text(DOCS / "video_script.md"),
            _text(DOCS / "kaggle_writeup.md"),
            _deck_text(),
        ]
    )
    assert "all five" in corpus.lower()


def test_kaggle_summary_and_boundary_are_submission_ready() -> None:
    writeup = _text(DOCS / "kaggle_writeup.md")
    summary = writeup.split("## Project summary", 1)[1].split("## Method", 1)[0]
    words = summary.split()

    assert 200 <= len(words) <= 300
    assert "14.2–39.0%" in summary
    assert "91.0–92.4%" in summary
    assert "three of five" in summary
    assert "not organ-on-chip or human data" in summary
    assert "autonomous assay termination" in summary
    assert "VIDEO_URL_TO_BE_ADDED_AFTER_UPLOAD" in writeup


def test_kaggle_category_is_declared_at_the_beginning() -> None:
    writeup = _text(DOCS / "kaggle_writeup.md")
    first_nonempty = next(line for line in writeup.splitlines() if line.strip())
    assert first_nonempty == "**Submission Category: Model & Algorithm**"
    assert writeup.index("Submission Category") < writeup.index("## Links")
    assert writeup.index("## Links") < writeup.index("## Team")


def test_kaggle_endpoint_table_matches_frozen_results() -> None:
    from scripts.update_kaggle_writeup import generated_table

    writeup = _text(DOCS / "kaggle_writeup.md")
    expected = generated_table(RESULTS)
    assert expected in writeup
    assert expected.count("\n|") == 6


def test_deck_uses_locked_title_and_subtitle() -> None:
    deck = _deck_text()
    assert "Reliability-Aware Early Prediction of Neural Network Development" in deck
    assert "from Microelectrode-Array Assays" in deck
    assert "Toward Functional Digital Twins for Neural Organ-on-Chip Screening" in deck


def test_dose_claims_distinguish_point_estimates_and_intervals() -> None:
    dose = pd.read_csv(RESULTS / "dose_strata.csv")
    m1 = dose.loc[dose["model"].eq("M1")].copy()
    exposed = m1.loc[m1["dose_stratum"].isin(["low", "mid"])]
    significant = exposed.loc[exposed["delta_mae_vs_bt_plus_ci_high"] < 0]

    assert (exposed["delta_mae_vs_bt_plus"] < 0).all()
    assert set(significant.loc[significant["dose_stratum"].eq("low"), "endpoint"]) == {
        "burst.per.min",
        "nAE",
        "r",
    }
    assert set(significant.loc[significant["dose_stratum"].eq("mid"), "endpoint"]) == {
        "burst.per.min",
        "nAE",
        "ns.n",
        "r",
    }

    report = _flat_text(DOCS / "report_draft.md")
    assert "present at low and mid doses for all five endpoints" not in report
    assert "Firing-rate intervals crossed zero at both low and mid dose" in report
    assert "network-spike interval crossed zero at low dose" in report


def test_zero_dose_underperformance_is_disclosed_without_expected_wording() -> None:
    dose = pd.read_csv(RESULTS / "dose_strata.csv")
    zero = dose.loc[(dose["model"].eq("M1")) & (dose["dose_stratum"].eq("zero"))]
    worse = set(zero.loc[zero["delta_mae_vs_bt_plus"] > 0, "endpoint"])
    harmful = set(zero.loc[zero["delta_mae_vs_bt_plus_ci_low"] > 0, "endpoint"])

    assert worse == {"burst.per.min", "meanfiringrate", "ns.n"}
    assert harmful == {"burst.per.min", "ns.n"}

    corpus = "\n".join(
        [_text(ROOT / "README.md"), _text(DOCS / "report_draft.md"), _text(DOCS / "defense_qa.md")]
    )
    assert "zero dose, M1 was worse than BT+" in corpus
    assert "Interpretation:" in corpus
    assert "zero-dose underperformance is expected" not in corpus.lower()
    assert "expected because" not in corpus.lower()


def test_cohort_claims_name_the_inconclusive_toxcast_endpoint() -> None:
    cohort = pd.read_csv(RESULTS / "cohort_results.csv")
    m1 = cohort.loc[cohort["model"].eq("M1")]
    assert (m1["delta_mae_vs_bt_plus"] < 0).all()

    inconclusive = m1.loc[m1["delta_mae_vs_bt_plus_ci_high"] >= 0]
    assert len(inconclusive) == 1
    assert inconclusive.iloc[0]["cohort"] == "ToxCast"
    assert inconclusive.iloc[0]["endpoint"] == "meanfiringrate"

    report = _flat_text(DOCS / "report_draft.md")
    assert "improved on BT+ for both NTP and ToxCast for all five endpoints" not in report
    assert "ToxCast firing-rate interval crossed zero" in report
    assert "not held-out cohort transfer" in report
    assert "transfers across screening programs" not in report


def test_three_of_five_abstention_claim_is_exact() -> None:
    decision = json.loads((RESULTS / "m3_decision.json").read_text(encoding="utf-8"))
    assert decision["passing_count"] == 3
    assert decision["endpoints_total"] == 5
    assert set(decision["passing_endpoints"]) == {"meanfiringrate", "nAE", "r"}

    corpus = "\n".join(
        [_text(ROOT / "README.md"), _text(DOCS / "report_draft.md"), _text(DOCS / "video_script.md")]
    ).lower()
    assert "three of five" in corpus or "3/5" in corpus


def test_time_saving_wording_is_conditional() -> None:
    corpus = "\n".join(
        [_text(ROOT / "README.md"), _text(DOCS / "report_draft.md"), _text(DOCS / "video_script.md")]
    ).lower()
    assert "accepted cases" in corpus or "accepted forecast" in corpus
    assert "every assay can be concluded five days early" not in corpus
    assert "all assays five days early" not in corpus
