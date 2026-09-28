# Decision log

## 2026-09-28 — Gates N0/N1: data feasibility

- Evidence: 136 unique CAS RNs, 4,344 per-well trajectories, DIV5/7/9/12,
  96.5% complete trajectories, 95.6% PubChem SMILES resolution.
- Decision: make NeuroChip the primary project, while keeping CellTwin-X as the
  measured fallback until Gate L1.
- Claim constraint: EPA NFA is a rat cortical neural MEA assay, not OoC data.
- Full evidence: `docs/neurochip_data_audit.md`.

## 2026-09-28 — Phase 2 protocol corrections

- Primary split: canonical-CAS-disjoint, with all aliases and biological
  replicates grouped together.
- Control definition: same-plate, same-DIV median across all dose-zero wells.
  Dose-zero rows are stored under compound labels; no literal DMSO group exists.
- Constant prediction metrics: undefined Spearman values remain missing and are
  never replaced by zero.
- Primary category remains Model & Algorithm unless the final implementation
  demonstrates a genuinely complete research workflow.

## 2026-09-28 — Pre-registration frozen

- Frozen commit: `8671fd84cc48d5b4fc45fe09ee20227cb3d46ac0`.
- No predictive result was computed before this commit.
- The exact primary endpoints, transformations, folds, baseline selection,
  metrics, confidence intervals, gates, and kill condition are fixed in
  `docs/preregistration.md`.

## 2026-09-28 — Raw labels outside the official cohort

- Three PFAS treatment labels occur in the combined ToxCast raw CSV but are absent
  from both official experimental summary catalogs and the paper's declared 146
  entries.
- Decision: retain their raw rows but exclude them from the pre-registered primary
  cohort. Do not invent study metadata for them. They may be described separately
  in an appendix.

## 2026-09-28 — Gate D2: PASS

- Evidence: 11 tests passed for canonical mapping, seeds 0/1/2 chemical-disjoint
  outer folds, complete fold coverage, and fail-closed causal feature selection.
- Primary cohort: 136 canonical CAS groups after the three pre-declared
  out-of-catalog treatments are excluded.
- Causal contract rejects DIV9, DIV12, control-DIV12, EC50, hit-call, and viability
  fields as inputs.
- Decision: proceed to matched-control normalization and B0–B4.
