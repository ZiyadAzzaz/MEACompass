from pathlib import Path
import re

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "docs" / "MEACompass_Technical_Report.pdf"


def test_report_pdf_exists_and_has_required_sections() -> None:
    assert PDF.is_file() and PDF.stat().st_size > 100_000
    reader = PdfReader(PDF)
    assert 12 <= len(reader.pages) <= 18
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    for phrase in (
        "Reliability-Aware Early Prediction",
        "Team information",
        "Main results",
        "Selective prediction / abstention",
        "AI-tool disclosure",
        "Registered status ledger",
    ):
        assert phrase in text


def test_report_pdf_contains_no_local_machine_paths() -> None:
    text = "\n".join(page.extract_text() or "" for page in PdfReader(PDF).pages)
    lowered = text.lower()
    assert "appdata" not in lowered
    assert "/users/" not in lowered
    assert "/home/" not in lowered


def test_report_source_has_required_sections_and_short_abstract() -> None:
    source = (ROOT / "docs" / "report_draft.md").read_text(encoding="utf-8")
    abstract = source.split("## Abstract", 1)[1].split("## 1.", 1)[0]
    assert len(re.findall(r"\b[\w–-]+\b", abstract)) <= 250
    required = (
        "Team information", "Problem and importance", "Related work",
        "Data and audit", "Preregistered protocol", "Deviations and integrity audit",
        "Methods", "Implementation", "Main results", "Calibration",
        "Selective prediction / abstention", "Time ablation", "Interpretability",
        "External validation", "Practical value", "Adoption path", "Limitations",
        "Ethics and compliance", "AI-tool disclosure", "Reproduction",
        "Sources and licenses", "Appendix A", "Appendix B",
    )
    for heading in required:
        assert heading in source
