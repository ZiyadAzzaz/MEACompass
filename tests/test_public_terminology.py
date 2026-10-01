from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BANNED_CHINESE_TERM = "类器官" + "芯片"
PUBLIC_SUFFIXES = {".html", ".md", ".srt", ".txt"}


def public_files() -> list[Path]:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return [
        ROOT / relative
        for relative in listed
        if (ROOT / relative).is_file()
        and ((ROOT / relative).suffix.lower() in PUBLIC_SUFFIXES or (ROOT / relative).suffix.lower() == ".pptx")
    ]


def test_prohibited_chinese_term_absent_from_public_materials() -> None:
    violations: list[str] = []
    for path in public_files():
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix.lower() == ".pptx":
            with zipfile.ZipFile(path) as archive:
                for member in archive.namelist():
                    if member.endswith(".xml") and BANNED_CHINESE_TERM in archive.read(member).decode("utf-8", errors="ignore"):
                        violations.append(f"{relative}:{member}")
        elif BANNED_CHINESE_TERM in path.read_text(encoding="utf-8", errors="ignore"):
            violations.append(relative)
    assert not violations, "Prohibited Chinese term found in: " + ", ".join(violations)


def test_subtitle_headline_and_preferred_terms_are_present() -> None:
    english = (ROOT / "docs" / "video_script_en.srt").read_text(encoding="utf-8")
    chinese = (ROOT / "docs" / "video_script_zh.srt").read_text(encoding="utf-8")
    normalized_english = " ".join(english.split())
    assert "14.2–39.0% versus BT+" in normalized_english
    assert "Confidence intervals across chemicals excluded zero" in normalized_english
    assert "最强基线 BT+" in chinese
    assert "平均绝对误差（MAE）" in chinese
    assert "14.2–39.0%" in chinese
    assert "选择性预测" in chinese
    assert "限定审计" in chinese
