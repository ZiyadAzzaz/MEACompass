"""Verify the compact result bundle committed for offline reproduction."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


MAX_COMMITTED_ARTIFACT_BYTES = 50 * 1024 * 1024


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest(manifest_path: Path, root: Path = Path(".")) -> dict[str, int]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    missing: list[str] = []
    invalid: list[str] = []
    total = 0
    for item in manifest["files"]:
        path = root / item["path"]
        if not path.is_file():
            missing.append(item["path"])
            continue
        size = path.stat().st_size
        total += size
        if size != item["bytes"] or sha256(path) != item["sha256"]:
            invalid.append(item["path"])
        if size > MAX_COMMITTED_ARTIFACT_BYTES:
            invalid.append(f"{item['path']} exceeds 50 MiB")
    if missing or invalid:
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if invalid:
            details.append("checksum/size invalid: " + ", ".join(invalid))
        raise RuntimeError("Result bundle verification failed; " + "; ".join(details))
    return {"files": len(manifest["files"]), "bytes": total}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("results/results_manifest.json"))
    args = parser.parse_args()
    summary = verify_manifest(args.manifest)
    print(
        f"Verified {summary['files']} committed result artifacts "
        f"({summary['bytes'] / 1024 / 1024:.2f} MiB); no download required."
    )


if __name__ == "__main__":
    main()
