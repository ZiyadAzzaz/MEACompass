"""Deterministic RDKit features keyed by canonical CAS RN."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator


DESCRIPTOR_FUNCTIONS = [
    ("MolWt", Descriptors.MolWt),
    ("ExactMolWt", Descriptors.ExactMolWt),
    ("MolLogP", Descriptors.MolLogP),
    ("MolMR", Descriptors.MolMR),
    ("TPSA", Descriptors.TPSA),
    ("NumHDonors", Descriptors.NumHDonors),
    ("NumHAcceptors", Descriptors.NumHAcceptors),
    ("NumRotatableBonds", Descriptors.NumRotatableBonds),
    ("RingCount", Descriptors.RingCount),
    ("NumAromaticRings", Descriptors.NumAromaticRings),
    ("NumAliphaticRings", Descriptors.NumAliphaticRings),
    ("NumSaturatedRings", Descriptors.NumSaturatedRings),
    ("HeavyAtomCount", Descriptors.HeavyAtomCount),
    ("FractionCSP3", Descriptors.FractionCSP3),
    ("NHOHCount", Descriptors.NHOHCount),
    ("NOCount", Descriptors.NOCount),
]


def chemistry_features(mapping_path: Path, radius: int = 2, fp_size: int = 2048) -> pd.DataFrame:
    mapping = pd.read_csv(mapping_path).drop_duplicates("casrn", keep="first")
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=radius, fpSize=fp_size)
    rows: list[dict[str, object]] = []
    for record in mapping.to_dict("records"):
        smiles = record.get("canonical_smiles")
        mol = Chem.MolFromSmiles(smiles) if isinstance(smiles, str) and smiles else None
        row: dict[str, object] = {
            "casrn": record["casrn"],
            "structure_missing": int(mol is None),
        }
        if mol is None:
            row.update({f"desc_{name}": np.nan for name, _ in DESCRIPTOR_FUNCTIONS})
            row.update({f"morgan_{index}": 0 for index in range(fp_size)})
        else:
            for name, function in DESCRIPTOR_FUNCTIONS:
                try:
                    value = float(function(mol))
                    row[f"desc_{name}"] = value if np.isfinite(value) else np.nan
                except Exception:
                    row[f"desc_{name}"] = np.nan
            fingerprint = generator.GetFingerprintAsNumPy(mol)
            row.update({f"morgan_{index}": int(value) for index, value in enumerate(fingerprint)})
        rows.append(row)
    return pd.DataFrame(rows)


def attach_chemistry(frame: pd.DataFrame, mapping_path: Path) -> tuple[pd.DataFrame, list[str]]:
    features = chemistry_features(mapping_path)
    merged = frame.merge(features, on="casrn", how="left", validate="many_to_one")
    chemistry_columns = [
        column
        for column in merged.columns
        if column.startswith("desc_") or column.startswith("morgan_")
    ] + ["structure_missing"]
    merged["structure_missing"] = merged["structure_missing"].fillna(1).astype("int8")
    fingerprint_columns = [column for column in chemistry_columns if column.startswith("morgan_")]
    merged[fingerprint_columns] = merged[fingerprint_columns].fillna(0).astype("uint8")
    return merged, chemistry_columns
