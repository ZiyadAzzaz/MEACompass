# MEACompass data feasibility audit

Audit date: 2026-09-28  
Decision gate: N0/N1 project selection  
Status: **FULL PASS**, with claim narrowing required

## Decision

The public EPA Network Formation Assay data support a real per-well early-to-late
prediction task. MEACompass should replace CellTwin-X as the primary competition
project, while CellTwin-X remains the measured fallback. The submission must call
the source a rat cortical neural MEA assay, not an organ-on-chip dataset.

Approved working title:

> **MEACompass: Reliability-Aware Early Prediction of Neural Network
> Development from Microelectrode-Array Assays**

Subtitle:

> **Toward Functional Digital Twins for Neural Organ-on-Chip Screening**

The words “digital twin” must not become a headline result unless trajectory
forecasting beats last-observation and growth-curve baselines on held-out
chemicals.

## Sources and license

- Official catalog and DOI: <https://doi.org/10.23719/1503191>
- Data.gov record: <https://catalog.data.gov/dataset/data-for-evaluation-of-chemical-effects-on-network-formation-in-cortical-neurons-grown-on->
- Associated paper: <https://doi.org/10.1093/toxsci/kfz052>
- EPA ScienceHub license: <https://pasteur.epa.gov/license/sciencehub-license.html>
- Chemical structures: PubChem PUG REST, resolved by CAS RN.

The catalog marks access as public and links the EPA ScienceHub license. That
license states that, unless otherwise specified, data produced by the U.S. EPA
are public domain under 17 U.S.C. § 105. It provides no warranty and requires
careful attention to dataset limitations. The EPA name, seal, or logo must not be
used to imply endorsement.

## Files inspected

Official download files:

| File | Bytes | SHA-256 |
|---|---:|---|
| `NTP_TC_Analysis.zip` | 159,560,650 | `FD92C1339BB764EE9B96C935BF31867C12640505E5C3F065AD5956A7EEA08CFB` |
| `Excel_scatter_plot_potency_vs_viability_Nov_26_2018.xlsx` | 71,755 | `04D7759E3BBB7D3F1334BB5C78175E53C9FF57D25D5A5F99E2E97BF0F056F0CC` |
| `Excel_selectivity_Oct_26_2018_alt.xlsx` | 49,394 | `F3504F94FEAC531C62762494CAC11000C7E42542C7419AC50F5474720889E7F9` |
| `MEA_and_ToxCast_and_AEDs_for_TC_NTP_25Oct2018.xlsx` | 40,352 | `9E4D76320CB6926C331F3EBD5CBC01E19C8CD56B1644CDB72BED2D54BE335D17` |

The archive README says the two `DEPRECATED` folders must not be used. The audit
therefore uses only `New NTP` and `New TC` source data and summary files.

## Exact dataset structure

| Measure | Observed value |
|---|---:|
| Official test entries | 146 |
| Unique chemicals by CAS RN | 136 |
| Total longitudinal records | 17,224 |
| Plates/batches | 99 |
| Unique plate-well trajectories | 4,344 |
| Complete DIV5/7/9/12 trajectories | 4,192 (96.50%) |
| Duplicate cohort/plate/well/DIV rows | 0 |
| Trajectories whose treatment/dose/unit changes | 0 |
| Cohort-treatment-dose groups | 1,274 |
| Replicate wells per exposure group | median 3; range 3–6 |
| Distinct numeric dose values across the dataset | 31, including zero |
| Concentrations per cohort-treatment label | median 8; range 8–14 |
| EC50 summary rows | 2,774 |
| EC50 rows with a numeric estimate | 1,190 |

Breakdown:

| Cohort | Records | Plates | Plate-well trajectories | Complete four-DIV trajectories | Raw treatment labels |
|---|---:|---:|---:|---:|---:|
| NTP | 5,712 | 33 | 1,440 | 1,392 | 50 |
| ToxCast | 11,512 | 66 | 2,904 | 2,800 | 102 |

The combined raw tables have 147 literal treatment strings because naming differs
between cohorts and some chemicals are deliberate biological replicates. The
official chemical tables contain 146 test entries and 136 unique cleaned CAS RNs.
All later splits must group aliases and biological replicates by canonical CAS RN,
not by raw treatment string.

## Temporal structure

| Timepoint | Available | Granularity | Records |
|---|---|---|---:|
| DIV5 | yes | per well | 4,296 |
| DIV7 | yes | per well | 4,296 |
| DIV9 | yes | per well | 4,336 |
| DIV12 | yes | per well | 4,296 |

The stable key is `(cohort, Plate.SN, well)`. `file.name` identifies the source H5
recording at each DIV. Measurements are not only chemical-concentration averages.

## Available electrophysiology parameters

The raw files expose 18 columns used as functional endpoints/features:

1. `meanfiringrate`
2. `burst.per.min`
3. `mean.isis`
4. `per.spikes.in.burst`
5. `mean.dur`
6. `mean.IBIs`
7. `nAE`
8. `nABE`
9. `ns.n`
10. `ns.peak.m`
11. `ns.durn.m`
12. `ns.percent.of.spikes.in.ns`
13. `ns.mean.insis`
14. `ns.durn.sd`
15. `ns.mean.spikes.in.ns`
16. `r`
17. `cv.time`
18. `cv.network`

The EPA catalog describes 17 network parameters plus two viability measures. The
source tables also expose `cv.time` and `cv.network`; endpoint selection must be
reconciled with the paper rather than assuming that all 18 are independent primary
outcomes.

Eight network columns are complete. Burst-conditional quantities contain genuine
missing values when insufficient events occur:

- `mean.isis`, `mean.dur`, `mean.IBIs`: 28.07% missing;
- `ns.peak.m`, `ns.durn.m`, `ns.mean.spikes.in.ns`: 37.02% missing;
- `ns.mean.insis`, `ns.durn.sd`: 38.28% missing.

Missingness is biologically informative and must receive explicit indicators; it
must not be hidden by complete-case filtering.

## Outcomes, controls, and identifiers

- Per-well DIV12 values are present for regression.
- Per-parameter concentration-response EC50 tables are present.
- Network parameter potency and selectivity score tables are present.
- AB and LDH viability tables contain three replicate columns per concentration.
- Dose-zero measurements are present, but they are labelled under each tested
  compound rather than a single literal `DMSO` treatment. Normalization must
  follow the study design and use the matched zero-dose/plate context.
- A ready-made binary `hit` column was not found in the raw CSVs. Any activity
  label must come from a verified EPA summary rule or a pre-registered threshold;
  it must not be reverse-engineered from the test fold.
- Raw identifiers include date, plate serial number, well, treatment name, dose,
  units, DIV, and source filename.
- Experimental summary CSVs contain preferred chemical name and CAS RN for every
  one of the 146 official test entries. The associated paper table also reports
  DTXSID, but DTXSID is not a raw-table column.

## Chemical structure mapping

The audit queried PubChem by each of the 136 unique CAS-style identifiers and
cached the results in `data/derived/chemical_mapping.csv`.

- Resolved to SMILES: **130/136 (95.59%)**
- Unresolved: **6/136 (4.41%)**
- Mapping-file SHA-256:
  `57E2B4CDFD85085913A51FDE6561C238B6B0298126330E0FA5D10AAE6653EBBB`

Unresolved identifiers: `12108-13-3`, `1330-78-5`, `68937-41-7`, `8000-34-8`,
`860302-33-6`, and `NOCAS_47330`. Several are mixtures or nonstandard substances,
so unresolved structure is not evidence of a failed lookup pipeline. Chemistry
features will include a missing-structure indicator, and early-readout-only models
remain the primary comparison.

## Leakage and evaluation implications

The task is feasible, but a random well split would be invalid. Required controls:

- group the primary split by canonical CAS RN;
- keep all aliases, concentrations, wells, and biological replicates of a chemical
  in the same fold;
- fit normalization, imputation, calibration, and conformal residuals inside the
  training fold only;
- use chemical-disjoint evaluation as primary;
- use plate-disjoint evaluation as a secondary robustness analysis;
- use scaffold-disjoint evaluation only as a secondary stress test because 136
  unique chemicals can produce small, unstable scaffold groups.

## Competition comparison

| Dimension | CellTwin-X | MEACompass |
|---|---|---|
| Sponsor alignment | Moderate: phenotype transfer is relevant but generic | High: neural functional data and forecasting match the sponsor’s stated direction |
| Direct neural relevance | None | High |
| Organ-on-chip relevance | Indirect; JUMP is not OoC | Indirect but closer; neural MEA is not automatically OoC |
| Data certainty | High: one downloaded JUMP plate and measured Gate 1 | High after this audit: clean longitudinal keys and public source |
| Licensing clarity | Public JUMP source documented in CellTwin repo | Explicit EPA public-domain terms and public access |
| Scientific novelty | Moderate; brightfield-to-phenotype transfer is competitive | Moderate-to-high only if chemical-held-out early prediction and reliability succeed |
| Practical value | Reduces staining burden in principle | Clear early-assay triage and “continue to DIV12” decision |
| Validation strength today | Measured one-plate CV; no external OoC result | No model result yet, but 136 chemical groups and 99 plates permit stronger tests |
| Risk of data failure | Low | Low after N0/N1; model-signal risk remains |
| Time to complete | Lower because Gate 1 exists | Moderate; compact tabular pipeline is CPU-friendly |
| Compute requirement | Moderate GPU for images | Low; CPU-first tree models are appropriate |
| Demo clarity | Moderate | High: DIV5/7 → DIV12, interval, and continue/stop verdict |
| Reproducibility | Good foundation | Feasible with small public tables and deterministic splits |
| Reliability story | Strong concept; partially measured | Natural decision workflow; not yet measured |
| Podium upside | Medium | Higher, conditional on honest held-out results |

## Gate result

**DATA DOWNLOAD:** PASS  
**EARLY→LATE TASK:** FEASIBLE  
**DATA THRESHOLDS:** FULL PASS  
**PROJECT DECISION:** SWITCH PRIMARY DEVELOPMENT TO MEACOMPASS  

Main risk: strong within-well temporal autocorrelation may make DIV12 prediction
look easy without demonstrating generalization to unseen chemicals. The primary
headline must therefore compare against DIV7 last-observation carried forward on
chemical-disjoint folds, not against a weak global-mean baseline.

Kill condition: after pre-registered feature engineering, if early-to-late
Spearman is below 0.20, classification AUROC is below 0.60, and abstention does not
lower accepted-case error, stop MEACompass and return to CellTwin-X.

## Reproduction

From the repository root, after placing the extracted official archive at the
documented path:

```powershell
python scripts/audit_epa_nfa.py
python scripts/resolve_pubchem_smiles.py
```

No model was trained before this gate decision.
