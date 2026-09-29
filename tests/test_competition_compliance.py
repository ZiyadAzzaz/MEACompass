from __future__ import annotations

import re
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _deck_text() -> str:
    with zipfile.ZipFile(DOCS / "MEACompass_Competition_Deck.pptx") as archive:
        return " ".join(
            archive.read(name).decode("utf-8", errors="ignore")
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        )


def test_required_compliance_artifacts_exist() -> None:
    required = [
        DOCS / "kaggle_writeup.md",
        DOCS / "MEACompass_Technical_Report.pdf",
        DOCS / "competition_compliance.md",
        DOCS / "judging_alignment.md",
        DOCS / "final_competition_compliance.md",
        DOCS / "sources_and_licenses.md",
        DOCS / "ai_tool_disclosure.md",
    ]
    assert all(path.is_file() and path.stat().st_size > 0 for path in required)


def test_writeup_order_summary_length_and_only_allowed_placeholder() -> None:
    writeup = _read(DOCS / "kaggle_writeup.md")
    assert writeup.lstrip().startswith("**Submission Category: Model & Algorithm**")
    assert writeup.index("## Links") < writeup.index("## Team") < writeup.index("## Project summary")
    ordered = [
        "## Project summary",
        "## Method",
        "## Results and validation",
        "## Reliability and limitations",
        "## Practical value",
        "## Reproduction",
        "## Sources and licenses",
        "## AI-tool disclosure",
    ]
    assert [writeup.index(heading) for heading in ordered] == sorted(
        writeup.index(heading) for heading in ordered
    )
    summary = writeup.split("## Project summary", 1)[1].split("## Method", 1)[0]
    assert 200 <= len(summary.split()) <= 300
    placeholders = re.findall(
        r"[A-Z][A-Z0-9_]*(?:TO_BE_ADDED|CONFIRMATION_REQUIRED)[A-Z0-9_]*", writeup
    )
    assert placeholders == ["VIDEO_URL_TO_BE_ADDED_AFTER_UPLOAD"]


def test_locked_claims_remain_consistent_in_core_public_materials() -> None:
    core = {
        "README": _read(ROOT / "README.md"),
        "report": _read(DOCS / "report_draft.md"),
        "writeup": _read(DOCS / "kaggle_writeup.md"),
        "video": _read(DOCS / "video_script.md"),
        "deck": _deck_text(),
    }
    for name, text in core.items():
        flat = " ".join(text.split()).lower()
        if name == "deck":
            assert "14.2%" in flat and "39.0%" in flat
            assert "12.3" in flat and "42.9%" in flat
            assert "91.0" in flat and "92.4%" in flat
            assert "three endpoints" in flat and "not five" in flat
        else:
            assert re.search(r"14\.2\s*(?:–|-|to)\s*39\.0", flat), name
            assert re.search(r"12\.3\s*(?:–|-|to)\s*42\.9", flat), name
            assert re.search(r"91\.0\s*(?:–|-|to)\s*92\.4", flat), name
            assert "three of five" in flat or "3/5" in flat, name

    boundary_corpus = "\n".join(core.values()).lower()
    assert "cut before scoring" in boundary_corpus
    assert "rat cortical" in boundary_corpus
    assert "not an organ-on-chip" in boundary_corpus or "not organ-on-chip" in boundary_corpus
    assert "not an autonomous" in boundary_corpus


def test_final_gate_is_ready_except_video_and_registration_is_recorded() -> None:
    final = _read(DOCS / "final_competition_compliance.md")
    writeup = _read(DOCS / "kaggle_writeup.md")
    assert "FINAL STATUS: READY EXCEPT VIDEO" in final
    assert "PENDING HUMAN UPLOAD" in final
    assert "Required external registration completed." in writeup
    assert "cross-disciplinary bonus" not in writeup.lower()


def test_team_identity_is_consistent_in_public_identity_materials() -> None:
    files = [
        ROOT / "README.md",
        DOCS / "kaggle_writeup.md",
        DOCS / "report_draft.md",
        DOCS / "ai_tool_disclosure.md",
    ]
    for path in files:
        text = _read(path)
        assert "Ziyad Azzaz" in text, path
        assert "AASTMT" in text, path
    assert "Solo submission" in _read(DOCS / "kaggle_writeup.md")


def test_rights_inventory_covers_data_dependencies_media_and_ai() -> None:
    rights = _read(DOCS / "sources_and_licenses.md")
    for term in [
        "EPA NFA",
        "PubChem PUG REST",
        "CompTox-DNT-NFA-Refinement",
        "pyreadr",
        "demo_public_neutral.png",
        "No font file",
        "AI services",
    ]:
        assert term in rights
