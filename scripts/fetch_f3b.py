from __future__ import annotations

import argparse
import csv
import hashlib
import re
import urllib.request
from pathlib import Path


PINNED_COMMIT = "01adf3e1a0068c87fe221d60df36b9f96c4b4b1d"
REQUIRED_COLUMNS = {
    "file_name", "repository_path", "pinned_commit", "source_url",
    "author/provenance", "reuse_basis", "permission_status",
    "allowed_for_analysis", "SHA256", "notes",
}
SHA_PATTERN = re.compile(r"^[0-9a-f]{64}$", re.I)


def load_approved(
    manifest: Path, commit: str, *, require_hashes: bool = True
) -> list[dict[str, str]]:
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
        if not row["author/provenance"].strip() or not row["reuse_basis"].strip():
            raise ValueError(f"Missing provenance approval: {row['repository_path']}")
        declared_sha = row["SHA256"].strip().lower()
        if require_hashes and not SHA_PATTERN.fullmatch(declared_sha):
            raise ValueError(f"Missing frozen SHA-256: {row['repository_path']}")
        row["expected_sha256"] = declared_sha
        approved.append(row)
    if not approved:
        raise PermissionError("No manifest row is approved for analysis; refusing download")
    return approved


def _download(row: dict[str, str]) -> bytes:
    request = urllib.request.Request(
        row["source_url"], headers={"User-Agent": "MEACompass-F3b/1.0"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def initialize_hashes(manifest: Path, output: Path, commit: str) -> None:
    """Perform the first authorized fetch and freeze observed hashes atomically."""
    approved = load_approved(manifest, commit, require_hashes=False)
    if any(SHA_PATTERN.fullmatch(row["SHA256"].strip()) for row in approved):
        raise ValueError("Manifest already contains frozen SHA-256 values; use normal fetch")
    output.mkdir(parents=True, exist_ok=True)
    if any((output / row["file_name"]).exists() for row in approved):
        raise FileExistsError("First-fetch initialization refuses existing destination files")
    payloads = {row["file_name"]: _download(row) for row in approved}
    hashes = {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()}
    for name, payload in payloads.items():
        (output / name).write_bytes(payload)

    with manifest.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    for row in rows:
        if row["file_name"] in hashes:
            row["SHA256"] = hashes[row["file_name"]]
            row["notes"] = row["notes"].replace("sha256:PENDING", "sha256:frozen_after_first_authorized_fetch")
    with manifest.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fetch(manifest: Path, output: Path, commit: str) -> None:
    approved = load_approved(manifest, commit, require_hashes=True)
    output.mkdir(parents=True, exist_ok=True)
    declared = {row["file_name"] for row in approved}
    undeclared = {path.name for path in output.iterdir() if path.is_file()} - declared
    if undeclared:
        raise ValueError(f"Undeclared external files present: {sorted(undeclared)}")
    for row in approved:
        destination = output / row["file_name"]
        if destination.exists():
            observed = hashlib.sha256(destination.read_bytes()).hexdigest()
            if observed != row["expected_sha256"]:
                raise ValueError(f"Existing file SHA-256 mismatch for {row['repository_path']}")
            continue
        payload = _download(row)
        observed = hashlib.sha256(payload).hexdigest()
        if observed != row["expected_sha256"]:
            raise ValueError(f"SHA-256 mismatch for {row['repository_path']}")
        destination.write_bytes(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description="Fail-closed pinned F3b fetch")
    parser.add_argument("--manifest", type=Path, default=Path("results/f3b/source_manifest.csv"))
    parser.add_argument("--output", type=Path, default=Path("data/external/f3b"))
    parser.add_argument("--commit", default=PINNED_COMMIT)
    parser.add_argument("--initialize-hashes", action="store_true")
    args = parser.parse_args()
    if args.initialize_hashes:
        initialize_hashes(args.manifest, args.output, args.commit)
    else:
        fetch(args.manifest, args.output, args.commit)


if __name__ == "__main__":
    main()
