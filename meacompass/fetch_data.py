"""Download and verify the public EPA NFA source files without paid services."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path
from zipfile import ZipFile


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verified(path: Path, item: dict[str, object]) -> bool:
    return (
        path.is_file()
        and path.stat().st_size == int(item["bytes"])
        and sha256(path) == str(item["sha256"])
    )


def download(item: dict[str, object], destination: Path) -> Path:
    target = destination / str(item["name"])
    if target.exists():
        if not verified(target, item):
            raise RuntimeError(
                f"Refusing to overwrite an existing file with a failed checksum: {target}"
            )
        print(f"Verified existing {target}")
        return target

    destination.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(target.suffix + ".part")
    request = urllib.request.Request(
        str(item["url"]), headers={"User-Agent": "MEACompass reproducibility/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as out:
            shutil.copyfileobj(response, out, length=1024 * 1024)
        if not verified(partial, item):
            raise RuntimeError(f"Downloaded file failed SHA-256 or size verification: {target.name}")
        partial.replace(target)
    finally:
        if partial.exists():
            partial.unlink()
    print(f"Downloaded and verified {target}")
    return target


def _safe_members(archive: ZipFile, destination: Path) -> None:
    root = destination.resolve()
    for member in archive.infolist():
        resolved = (destination / member.filename).resolve()
        if root != resolved and root not in resolved.parents:
            raise RuntimeError(f"Unsafe archive path: {member.filename}")


def extract_archive(archive_path: Path, destination: Path) -> None:
    required = [
        destination / "New NTP" / "sourceData" / "ALL_NTP.csv",
        destination / "New TC" / "sourceData" / "AllCombined_ToxCast_20180923.csv",
    ]
    if all(path.is_file() for path in required):
        print(f"Retained existing extracted data at {destination}")
        return
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError(
            f"Refusing to merge into a non-empty incomplete extraction: {destination}"
        )
    destination.mkdir(parents=True, exist_ok=True)
    with ZipFile(archive_path) as archive:
        _safe_members(archive, destination)
        archive.extractall(destination)
    if not all(path.is_file() for path in required):
        raise RuntimeError(
            "Archive extracted, but expected New NTP/New TC source tables were not found."
        )


def fetch(manifest_path: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    destination = Path(manifest["destination"])
    downloaded: list[tuple[dict[str, object], Path]] = []
    for item in manifest["files"]:
        downloaded.append((item, download(item, destination)))
    for item, path in downloaded:
        if item.get("extract"):
            extract_archive(path, destination / "extracted")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("schemas/epa_downloads_v1.json"))
    args = parser.parse_args()
    fetch(args.manifest)


if __name__ == "__main__":
    main()
