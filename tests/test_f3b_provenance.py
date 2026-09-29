from pathlib import Path

import pandas as pd
import pytest

from scripts.fetch_f3b import PINNED_COMMIT, load_approved


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "results" / "f3b" / "source_manifest.csv"


def test_f3b_manifest_is_pinned_and_provenance_reviewed() -> None:
    frame = pd.read_csv(MANIFEST, dtype=str).fillna("")
    assert frame["pinned_commit"].eq(PINNED_COMMIT).all()
    assert frame["source_url"].str.contains(PINNED_COMMIT, regex=False).all()
    assert frame["allowed_for_analysis"].eq("YES").all()
    assert frame["provenance_basis"].str.len().gt(0).all()
    assert frame["reuse_basis"].str.len().gt(0).all()


def test_f3b_fetch_refuses_until_sha256_is_frozen() -> None:
    with pytest.raises(ValueError, match="Missing frozen SHA-256"):
        load_approved(MANIFEST, PINNED_COMMIT)


def test_f3b_fetch_refuses_commit_drift() -> None:
    with pytest.raises(ValueError, match="pinned commit"):
        load_approved(MANIFEST, "0" * 40)
