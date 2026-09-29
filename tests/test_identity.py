from __future__ import annotations

import re
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEGACY_STEM = "neuro" + "chip"
FORBIDDEN = re.compile(rf"{LEGACY_STEM}(?:-twin)?", re.IGNORECASE)
TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".html",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".srt",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_PARTS = {
    ".git",
    ".pytest_cache",
    ".venv",
    ".venv-system",
    "__pycache__",
    "checkpoints",
    "data",
    "repro_checks",
}


def _deliverables() -> list[Path]:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    paths: list[Path] = []
    for relative in listed:
        path = ROOT / relative
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        if any(part.startswith("pytest-cache-files-") for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.suffix.lower() == ".pptx":
            paths.append(path)
    return paths


def test_legacy_identity_absent_from_deliverables() -> None:
    violations: list[str] = []
    allowed_note = "- Identity: MEACompass (formerly " + "Neuro" + "Chip-Twin)."

    for path in _deliverables():
        relative = path.relative_to(ROOT).as_posix()
        if FORBIDDEN.search(relative):
            violations.append(f"legacy identity in path: {relative}")

        if path.suffix.lower() == ".pptx":
            with zipfile.ZipFile(path) as archive:
                for member in archive.namelist():
                    if not member.endswith(".xml"):
                        continue
                    text = archive.read(member).decode("utf-8", errors="ignore")
                    if FORBIDDEN.search(text):
                        violations.append(f"legacy identity in {relative}:{member}")
            continue

        text = path.read_text(encoding="utf-8", errors="ignore")
        for number, line in enumerate(text.splitlines(), start=1):
            if not FORBIDDEN.search(line):
                continue
            if relative == "docs/decisions.md" and line == allowed_note:
                continue
            violations.append(f"legacy identity in {relative}:{number}")

    assert not violations, "\n".join(violations)
