from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def test_readme_uses_verified_public_links_and_has_no_stale_hosting_text() -> None:
    text = README.read_text(encoding="utf-8")
    lowered = text.lower()
    assert "https://github.com/ZiyadAzzaz/MEACompass" in text
    assert "https://ziyadazzaz.github.io/MEACompass/demo/" in text
    assert "hosting is pending" not in lowered
    assert "no public url is claimed" not in lowered
    assert "video_url_to_be_added" not in lowered


def test_readme_judge_images_are_relative_and_exist() -> None:
    text = README.read_text(encoding="utf-8")
    image_paths = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text)
    assert image_paths == [
        "docs/assets/demo_public_neutral.png",
        "docs/assets/main_results_locked.png",
        "artifacts/reproduce-lite/risk_coverage.png",
    ]
    assert all(not re.match(r"(?:[A-Za-z]:|file://|https?://|localhost)", path) for path in image_paths)
    assert all((ROOT / path).is_file() for path in image_paths)


def test_readme_keeps_registered_boundaries_visible() -> None:
    text = README.read_text(encoding="utf-8")
    required = [
        "3/5 endpoints",
        "registered permutation gate originally stopped",
        "CUT before scoring",
        "not an organ-on-chip dataset",
        "not an autonomous",
    ]
    assert all(term in text for term in required)
