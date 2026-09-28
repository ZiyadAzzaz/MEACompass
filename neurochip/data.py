"""EPA NFA loading and chemical-identity canonicalization."""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


NETWORK_METRICS = [
    "meanfiringrate",
    "burst.per.min",
    "mean.isis",
    "per.spikes.in.burst",
    "mean.dur",
    "mean.IBIs",
    "nAE",
    "nABE",
    "ns.n",
    "ns.peak.m",
    "ns.durn.m",
    "ns.percent.of.spikes.in.ns",
    "ns.mean.insis",
    "ns.durn.sd",
    "ns.mean.spikes.in.ns",
    "r",
    "cv.time",
    "cv.network",
]

PRIMARY_ENDPOINTS = ["meanfiringrate", "burst.per.min", "nAE", "ns.n", "r"]


RAW_FILES = {
    "NTP": "New NTP/sourceData/ALL_NTP.csv",
    "ToxCast": "New TC/sourceData/AllCombined_ToxCast_20180923.csv",
}

CATALOG_FILES = {
    "NTP": (
        "New NTP/sourceData/NTP Experimental Summary of Data for Analysis_Complete.csv",
        "preferred name",
    ),
    "ToxCast": (
        "New TC/sourceData/ToxCast Experimental Summary of Data for Analysis.csv",
        "preferred_name",
    ),
}

# These aliases cannot be recovered reliably by punctuation normalization alone.
# Every value is verified against the official cohort catalog, or (for
# Valinomycin) the same official CAS in the NTP catalog.
MANUAL_TREATMENT_TO_CAS = {
    ("ToxCast", "Diphenhydramine"): "147-24-0",
    ("ToxCast", "Disulfiram - ToxCast G-8"): "97-77-8",
    ("ToxCast", "HPTE"): "2971-36-0",
    ("ToxCast", "IPBC"): "55406-53-6",
    ("ToxCast", "Methadone"): "1095-90-5",
    ("ToxCast", "Rotenone - ToxCast G-8"): "83-79-4",
    ("ToxCast", "TBHQ"): "1948-33-0",
    ("ToxCast", "Valinomycin - NTP"): "2001-95-8",
}

# Present in the combined raw file but absent from both official experimental
# summary catalogs and the paper's declared 146 test entries. They are retained
# in raw data and excluded from the pre-registered primary cohort.
EXCLUDED_RAW_TREATMENTS = {
    ("ToxCast", "1,1,2,2-Tetrahydroperfluoro-1-decanol - TP0001411"),
    ("ToxCast", "1H,1H,2H,2H-Perfluorooctyl iodide - TP0001413"),
    ("ToxCast", "Perfluoroundecanoic acid - TP0001411"),
}


def clean_cas(value: object) -> str:
    """Normalize quoting artifacts while preserving a source's identifier."""
    return str(value).strip().strip("'\"").rstrip("',")


def normalize_chemical_name(value: object) -> str:
    """Create a conservative comparison key, not a chemical identifier."""
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    text = text.lower().replace("beta", "b").replace("alpha", "a")
    replacements = {
        "acetylsalicylic acid": "aspirin",
        "d glucitol": "sorbitol",
        "6 hydroxydopamine hydrochloride": "oxidopamine hydrochloride",
        "tetraethylthiuram disulfide": "disulfiram",
        "carbamic acid butyl 3 iodo 2 propynyl ester": "ipbc",
        "17b estradiol": "estradiol",
        "17 beta estradiol": "estradiol",
    }
    text = re.sub(r"\btoxcast\b|\bntp\b|\btp\d+\b|\bg\s*\d+\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()
    return replacements.get(text, text)


def load_raw(root: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for cohort, relative_path in RAW_FILES.items():
        frame = pd.read_csv(root / relative_path, na_values=["NA", "NaN"])
        frame.insert(0, "cohort", cohort)
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


def load_catalog(root: Path) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for cohort, (relative_path, name_column) in CATALOG_FILES.items():
        frame = pd.read_csv(root / relative_path)
        selected = frame[["casrn", name_column]].copy()
        selected.columns = ["casrn", "preferred_name"]
        selected.insert(0, "cohort", cohort)
        selected["casrn"] = selected["casrn"].map(clean_cas)
        selected["preferred_name"] = selected["preferred_name"].astype(str).str.strip()
        selected["normalized_name"] = selected["preferred_name"].map(normalize_chemical_name)
        frames.append(selected)
    return pd.concat(frames, ignore_index=True)


def propose_treatment_crosswalk(root: Path) -> pd.DataFrame:
    """Return the best and second-best metadata-name matches for every raw label."""
    raw = load_raw(root)
    catalog = load_catalog(root)
    rows: list[dict[str, object]] = []
    for cohort, cohort_raw in raw.groupby("cohort", sort=True):
        candidates = catalog.loc[catalog["cohort"].eq(cohort)]
        for treatment in sorted(cohort_raw["trt"].unique()):
            normalized = normalize_chemical_name(treatment)
            scored = []
            for candidate in candidates.itertuples(index=False):
                score = SequenceMatcher(None, normalized, candidate.normalized_name).ratio()
                scored.append((score, candidate.casrn, candidate.preferred_name))
            scored.sort(reverse=True)
            best, second = scored[0], scored[1]
            rows.append(
                {
                    "cohort": cohort,
                    "treatment": treatment,
                    "normalized_treatment": normalized,
                    "casrn": best[1],
                    "preferred_name": best[2],
                    "score": best[0],
                    "second_casrn": second[1],
                    "second_name": second[2],
                    "second_score": second[0],
                    "margin": best[0] - second[0],
                }
            )
    return pd.DataFrame(rows)


def build_treatment_crosswalk(root: Path) -> pd.DataFrame:
    """Create a strict mapping from every in-scope raw label to canonical CAS.

    Exact normalized matches and explicitly reviewed aliases are allowed. Fuzzy
    proposals are never accepted automatically.
    """
    raw = load_raw(root)
    catalog = load_catalog(root)
    normalized_lookup: dict[tuple[str, str], list[str]] = {}
    for row in catalog.itertuples(index=False):
        normalized_lookup.setdefault((row.cohort, row.normalized_name), []).append(row.casrn)

    official_cas = set(catalog["casrn"])
    rows: list[dict[str, str]] = []
    unresolved: list[tuple[str, str]] = []
    for cohort, treatment in (
        raw[["cohort", "trt"]].drop_duplicates().sort_values(["cohort", "trt"]).itertuples(index=False)
    ):
        key = (cohort, treatment)
        if key in EXCLUDED_RAW_TREATMENTS:
            rows.append(
                {
                    "cohort": cohort,
                    "treatment": treatment,
                    "casrn": "",
                    "mapping_source": "excluded_not_in_official_catalog",
                }
            )
            continue
        if key in MANUAL_TREATMENT_TO_CAS:
            casrn = MANUAL_TREATMENT_TO_CAS[key]
            if casrn not in official_cas:
                raise ValueError(f"Reviewed alias points outside official catalog: {key} -> {casrn}")
            rows.append(
                {
                    "cohort": cohort,
                    "treatment": treatment,
                    "casrn": casrn,
                    "mapping_source": "reviewed_alias",
                }
            )
            continue
        candidates = set(
            normalized_lookup.get((cohort, normalize_chemical_name(treatment)), [])
        )
        if len(candidates) != 1:
            unresolved.append(key)
            continue
        rows.append(
            {
                "cohort": cohort,
                "treatment": treatment,
                "casrn": candidates.pop(),
                "mapping_source": "exact_normalized_name",
            }
        )
    if unresolved:
        raise ValueError(f"Unresolved or ambiguous raw treatment labels: {unresolved}")
    return pd.DataFrame(rows)


def attach_canonical_cas(raw: pd.DataFrame, root: Path) -> pd.DataFrame:
    """Attach canonical CAS and remove only pre-declared out-of-cohort labels."""
    crosswalk = build_treatment_crosswalk(root)
    merged = raw.merge(
        crosswalk,
        left_on=["cohort", "trt"],
        right_on=["cohort", "treatment"],
        how="left",
        validate="many_to_one",
    )
    if merged["mapping_source"].isna().any():
        missing = merged.loc[merged["mapping_source"].isna(), ["cohort", "trt"]].drop_duplicates()
        raise ValueError(f"Rows lack a reviewed chemical mapping:\n{missing}")
    return merged.loc[merged["casrn"].ne("")].drop(columns="treatment").reset_index(drop=True)


def build_longitudinal_table(root: Path) -> pd.DataFrame:
    """Return one trajectory per plate-well with time-causal features and targets."""
    raw = attach_canonical_cas(load_raw(root), root)
    identity = ["cohort", "Plate.SN", "well", "casrn", "trt", "dose", "units"]
    wide = raw.pivot(index=identity, columns="DIV", values=NETWORK_METRICS)
    wide.columns = [f"div{int(div)}_{metric}" for metric, div in wide.columns]
    wide = wide.reset_index()

    controls = (
        raw.loc[raw["dose"].eq(0)]
        .groupby(["cohort", "Plate.SN", "DIV"])[NETWORK_METRICS]
        .median()
        .unstack("DIV")
    )
    controls.columns = [f"control_div{int(div)}_{metric}" for metric, div in controls.columns]
    controls = controls.reset_index()
    wide = wide.merge(controls, on=["cohort", "Plate.SN"], how="left", validate="many_to_one")
    wide["log10_1p_dose"] = wide["dose"].clip(lower=0).map(lambda value: __import__("math").log10(1 + value))

    for div in (5, 7):
        for metric in NETWORK_METRICS:
            column = f"div{div}_{metric}"
            wide[f"{column}_missing"] = wide[column].isna().astype("int8")
    return wide


def primary_feature_columns(frame: pd.DataFrame) -> list[str]:
    """Select the registered primary inputs and reject accidental future data."""
    columns = [
        column
        for column in frame.columns
        if column.startswith("div5_") or column.startswith("div7_")
    ]
    columns.append("log10_1p_dose")
    validate_time_causal_features(columns)
    return columns


def validate_time_causal_features(columns: list[str]) -> None:
    forbidden = [
        column
        for column in columns
        if re.search(r"(^|_)div(?:9|12)(?:_|$)", column.lower())
        or "ec50" in column.lower()
        or "hit" in column.lower()
        or "viability" in column.lower()
    ]
    if forbidden:
        raise ValueError(f"Future or outcome-derived input features are forbidden: {forbidden}")
