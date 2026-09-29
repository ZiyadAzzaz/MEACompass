from __future__ import annotations

import argparse
import csv
import hashlib
import re
import urllib.request
from pathlib import Path


PINNED_COMMIT = "01adf3e1a0068c87fe221d60df36b9f96c4b4b1d"
REQUIRED_COLUMNS = {
    "file_name", "repository_path", "source_url", "pinned_commit",
    "claimed_author_or_agency", "provenance_basis", "reuse_basis",
    "permission_status", "allowed_for_analysis", "notes",
}
SHA_PATTERN = re.compile(r"(?:^|;\s*)sha256:([0-9a-f]{64})(?:;|$)", re.I)


def load_approved(manifest: Path, commit: str) -> list[dict[str, str]]:
    if commit != PINNED_COMMIT:
        raise ValueError(f"Commit must equal pinned commit {PINNED_COMMIT}")
    with manifest.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if set(reader.fieldnames or []) != REQUIRED_COLUMNS:
            raise ValueError("F3b manifest columns differ from the registered schema")
        rows = list(reader)
    approved: list[dict[str, str]] = []
    for row in rows:
        if row["pinned_commit"] != commit or f"/{commit}/" not in row["source_url"]:
            raise ValueError(f"Unpinned source declaration: {row['repository_path']}")
        if row["allowed_for_analysis"].strip().upper() != "YES":
            continue
        if not row["provenance_basis"].strip() or not row["reuse_basis"].strip():
            raise ValueError(f"Missing provenance approval: {row['repository_path']}")
        match = SHA_PATTERN.search(row["notes"])
        if match is None:
            raise ValueError(f"Missing frozen SHA-256: {row['repository_path']}")
        row["expected_sha256"] = match.group(1).lower()
        approved.append(row)
    if not approved:
        raise PermissionError("No manifest row is approved for analysis; refusing download")
    return approved


def fetch(manifest: Path, output: Path, commit: str) -> None:
    approved = load_approved(manifest, commit)
    output.mkdir(parents=True, exist_ok=True)
    declared = {row["file_name"] for row in approved}
    undeclared = {path.name for path in output.iterdir() if path.is_file()} - declared
    if undeclared:
        raise ValueError(f"Undeclared external files present: {sorted(undeclared)}")
    for row in approved:
        destination = output / row["file_name"]
        request = urllib.request.Request(
            row["source_url"], headers={"User-Agent": "MEACompass-F3b/1.0"}
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = response.read()
        observed = hashlib.sha256(payload).hexdigest()
        if observed != row["expected_sha256"]:
            raise ValueError(f"SHA-256 mismatch for {row['repository_path']}")
        destination.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed pinned F3b fetch")
    parser.add_argument("--manifest", type=Path, default=Path("results/f3b/source_manifest.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/external/f3b"))
    parser.add_argument("--commit", default=PINNED_COMMIT)
    args = parser.parse_args()
    fetch(args.manifest, args.output, args.commit)


if __name__ == "__main__":
    main()
