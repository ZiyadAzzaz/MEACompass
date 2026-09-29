from pathlib import Path

import pandas as pd
import pytest

from scripts.fetch_f3b import PINNED_COMMIT, load_approved


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "f3b" / "source_manifest.csv"


def test_f3b_manifest_is_pinned_and_fail_closed() -> None:
    frame = pd.read_csv(MANIFEST, dtype=str).fillna("")
    assert frame["pinned_commit"].eq(PINNED_COMMIT).all()
    assert frame["source_url"].str.contains(PINNED_COMMIT, regex=False).all()
    assert frame["allowed_for_analysis"].eq("NO").all()
    assert frame["provenance_basis"].str.len().gt(0).all()
    assert frame["reuse_basis"].str.len().gt(0).all()


def test_f3b_fetch_refuses_without_file_level_approval() -> None:
    with pytest.raises(PermissionError, match="No manifest row is approved"):
        load_approved(MANIFEST, PINNED_COMMIT)


def test_f3b_fetch_refuses_commit_drift() -> None:
    with pytest.raises(ValueError, match="pinned commit"):
        load_approved(MANIFEST, "0" * 40)
