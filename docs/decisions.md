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

## 2026-09-28 — Phase 3 protocol registered before M1 completion

- Timing: registered with 26/75 M1 prediction checkpoints complete and before
  any aggregate M1 result or Gate M1 evaluation existed.
- BT+ is now the only baseline for headline claims. Original BT comparisons stay
  visible as the pre-registered analysis and are never removed.
- Main-model selection is fixed as follows: M1 becomes the main model only if it
  beats B3 with a chemical-bootstrap confidence interval excluding zero on at
  least two endpoints. A tie or worse result selects the simpler B3; chemistry
  remains an ablation.
- Gate S remains mandatory before M2. Gate M2/M3 and Gate L1 stop/lock rules are
  fixed in `docs/phase3_protocol.md`.
- The percent-of-control transform for coordinated activity `r` will not be
  changed. Active electrodes and `r` remain visible limitations unless later
  registered evidence materially changes their status.

## 2026-09-28 — Gate M1: SELECT M1

- All 75 prediction and 75 tuning checkpoints completed before aggregate
  evaluation.
- M1 beat B3 with a beneficial chemical-bootstrap confidence interval on exactly
  two endpoints: active electrodes and coordinated activity `r`.
- M1 beat inner-selected BT+ on all five endpoints, but did not decisively beat
  B3 for bursting or firing and was tied/slightly worse for network spikes.
- Decision: select M1 under the Phase 3 rule, while retaining the pre-registered
  warning that percent-control `r` is unstable near zero control denominators.
- Full evidence: `docs/phase3_m1_results.md`.

## 2026-09-28 — Sanity Gate S: STOP, suspected leakage/confounding

- The chemical-group permutation negative control retained a beneficial
  bursts/min delta MAE versus BT+ of -0.525, with 95% CI [-0.969, -0.136].
- Its relative gain was small (1.60%), and the other four endpoints did not have
  a beneficial confidence interval, but the registered rule requires an
  immediate stop whenever the permutation CI excludes zero beneficially.
- The non-permuted M1 cleared the fair-gain condition on all five endpoints and
  showed low/mid-dose signal. These positive results do not override the negative
  control.
- Decision: do not run M2, M3, or Gate L1. Freeze scientific progression pending
  an integrity audit and user review. Do not claim a validated early-prediction
  result yet.
- Full evidence: `docs/sanity_gate_s_results.md`.
