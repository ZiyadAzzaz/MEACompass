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

## 2026-09-28 — Gates B1/B2: PASS / STRONG

- B0–B4 completed for all five registered endpoints, five chemical-disjoint
  outer folds, and seeds 0/1/2 (357,984 held-out prediction rows).
- B3 met the full strong criterion on bursting, firing, and network spikes:
  relative MAE gains were 41.65%, 15.78%, and 31.05%; the paired
  chemical-bootstrap confidence intervals excluded zero in the beneficial
  direction; delta Spearman values were 0.761, 0.583, and 0.610.
- Active electrodes improved by 9.22%, but its confidence interval crossed zero.
  Coordinated activity `r` did not improve in MAE and is a declared negative
  result.
- Decision: Gate B2 is **STRONG (3/5 endpoints)**. No feature-pack retry is
  permitted or needed. Proceed to the pre-registered M1 chemistry-fusion test.
- B4 structure-only modeling showed significant gains for bursting and network
  spikes, but was weaker than B3 overall. This is evidence that chemistry may be
  useful, not evidence that M1 will pass.
- Full table: `docs/phase2_baseline_results.md`.

## 2026-09-28 — Registered deviation: Sanity Gate S

- Timing: registered after B0–B4 results and after M1 was launched, but before
  M1 results, Gate M1 evaluation, or any uncertainty analysis.
- Rationale: B0 unexpectedly outperformed the original inner-selected BT on
  some endpoints. A stronger comparison and negative control are required before
  interpreting uncertainty or abstention.
- Original pre-registered BT and every original metric remain unchanged and will
  still be reported. This deviation adds BT+ (inner-selected from B0/B1/B1b/B2),
  chemical-group target permutation, dose-stratified evaluation, descriptive
  per-cohort evaluation, and a DIV5-only B3 time ablation.
- M2 is prohibited until Gate S is evaluated. A beneficial permutation result
  with a confidence interval excluding zero, or disappearance of gain across
  endpoints, triggers an immediate stop and report.
- Gate L1 may lock early only after M1 evaluation, Gate S PASS, and Gate M3 PASS
  or WEAK. CellTwin-X remains frozen only after that lock.
- Full deviation protocol: `docs/phase2_addendum.md`.
