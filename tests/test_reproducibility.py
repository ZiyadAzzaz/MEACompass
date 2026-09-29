from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from neurochip.fetch_results import MAX_COMMITTED_ARTIFACT_BYTES, verify_manifest
from neurochip.train_all import COMMANDS


ROOT = Path(__file__).resolve().parents[1]


def test_committed_result_bundle_is_small_and_verified() -> None:
    manifest_path = ROOT / "results" / "results_manifest.json"
    summary = verify_manifest(manifest_path, ROOT)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert summary == {"files": 7, "bytes": 8_749_852}
    assert summary["bytes"] < MAX_COMMITTED_ARTIFACT_BYTES
    assert max(item["bytes"] for item in manifest["files"]) < MAX_COMMITTED_ARTIFACT_BYTES


def test_result_bundle_fails_closed_when_a_file_is_missing() -> None:
    manifest = {
        "files": [
            {
                "path": "results/missing.csv",
                "bytes": 1,
                "sha256": "0" * 64,
            }
        ]
    }
    scratch = ROOT / ".test_runs_repro"
    scratch.mkdir(exist_ok=True)
    path = scratch / "missing-manifest.json"
    try:
        path.write_text(json.dumps(manifest), encoding="utf-8")
        with pytest.raises(RuntimeError, match="missing"):
            verify_manifest(path, scratch)
    finally:
        if path.exists():
            path.unlink()
        scratch.rmdir()


def test_epa_manifest_uses_public_https_and_audit_hashes() -> None:
    manifest = json.loads((ROOT / "schemas" / "epa_downloads_v1.json").read_text())
    assert manifest["doi"] == "10.23719/1503191"
    assert len(manifest["files"]) == 4
    assert all(item["url"].startswith("https://pasteur.epa.gov/") for item in manifest["files"])
    assert all(len(item["sha256"]) == 64 for item in manifest["files"])
    archive = next(item for item in manifest["files"] if item["extract"])
    assert archive["name"] == "NTP_TC_Analysis.zip"
    assert archive["sha256"] == "fd92c1339bb764ee9b96c935bf31867c12640505e5c3f065ad5956a7eea08cfb"


def test_train_all_is_guarded_and_complete() -> None:
    modules = " ".join(" ".join(command) for command in COMMANDS)
    for required in [
        "neurochip.train_baselines",
        "neurochip.train_m1",
        "neurochip.integrity_audit",
        "neurochip.reliability",
        "neurochip.time_ablation",
        "neurochip.submission_artifacts",
    ]:
        assert required in modules
    result = subprocess.run(
        [sys.executable, "-m", "neurochip.train_all", "--dry-run"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "neurochip.train_m1" in result.stdout


def test_makefile_exposes_required_reproduction_targets() -> None:
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in ["setup:", "fetch-results:", "data:", "train-all:", "test:", "reproduce-lite:", "demo:"]:
        assert target in makefile
