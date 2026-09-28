"""Resolve the EPA NFA CAS identifiers through the free PubChem PUG REST API."""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


SOURCES = (
    ("NTP", "New NTP/sourceData/NTP Experimental Summary of Data for Analysis_Complete.csv", "preferred name"),
    ("ToxCast", "New TC/sourceData/ToxCast Experimental Summary of Data for Analysis.csv", "preferred_name"),
)


def clean_cas(value: object) -> str:
    return str(value).strip().strip("'\"").rstrip("',")


def load_chemicals(root: Path) -> list[dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    for cohort, relative_path, name_column in SOURCES:
        frame = pd.read_csv(root / relative_path)
        for row in frame.to_dict("records"):
            casrn = clean_cas(row["casrn"])
            if casrn not in records:
                records[casrn] = {
                    "casrn": casrn,
                    "preferred_name": str(row[name_column]).strip(),
                    "cohorts": cohort,
                }
            elif cohort not in records[casrn]["cohorts"].split(";"):
                records[casrn]["cohorts"] += f";{cohort}"
    return sorted(records.values(), key=lambda item: item["casrn"])


def resolve(casrn: str, attempts: int = 3) -> dict[str, object]:
    encoded = urllib.parse.quote(casrn, safe="")
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
        f"{encoded}/property/CanonicalSMILES,IsomericSMILES,InChIKey/JSON"
    )
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "NeuroChip-Twin/0.1"})
            with urllib.request.urlopen(request, timeout=30) as response:
                record = json.load(response)["PropertyTable"]["Properties"][0]
            return {
                "pubchem_cid": record.get("CID", ""),
                "canonical_smiles": record.get("ConnectivitySMILES", record.get("SMILES", "")),
                "isomeric_smiles": record.get("SMILES", ""),
                "inchikey": record.get("InChIKey", ""),
                "resolution_status": "resolved",
            }
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as error:
            if attempt + 1 == attempts:
                return {
                    "pubchem_cid": "",
                    "canonical_smiles": "",
                    "isomeric_smiles": "",
                    "inchikey": "",
                    "resolution_status": f"unresolved:{type(error).__name__}",
                }
            time.sleep(1.0 * (attempt + 1))
    raise AssertionError("unreachable")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("data/raw/epa_nfa/extracted"))
    parser.add_argument("--output", type=Path, default=Path("data/derived/chemical_mapping.csv"))
    parser.add_argument("--delay", type=float, default=0.22, help="Seconds between PubChem requests")
    args = parser.parse_args()

    chemicals = load_chemicals(args.root)
    existing: dict[str, dict[str, str]] = {}
    if args.output.exists():
        with args.output.open(newline="", encoding="utf-8") as handle:
            existing = {row["casrn"]: row for row in csv.DictReader(handle)}

    rows: list[dict[str, object]] = []
    for index, chemical in enumerate(chemicals, start=1):
        cached = existing.get(chemical["casrn"])
        if cached and cached.get("resolution_status") == "resolved":
            result: dict[str, object] = cached
        else:
            result = {**chemical, **resolve(chemical["casrn"])}
            time.sleep(args.delay)
        rows.append({**chemical, **result})
        print(f"[{index:03d}/{len(chemicals)}] {chemical['casrn']}: {rows[-1]['resolution_status']}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "casrn",
        "preferred_name",
        "cohorts",
        "pubchem_cid",
        "canonical_smiles",
        "isomeric_smiles",
        "inchikey",
        "resolution_status",
    ]
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    resolved = sum(bool(row["canonical_smiles"]) for row in rows)
    print(f"Resolved {resolved}/{len(rows)} ({resolved / len(rows):.1%})")


if __name__ == "__main__":
    main()
