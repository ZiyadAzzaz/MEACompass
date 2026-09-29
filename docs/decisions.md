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

## 2026-09-28 — Authorized post-registration Gate S integrity audit

- The registered Gate S result remains **FAIL / STOP** and will not be rewritten.
- Scope is limited to mechanism/data-flow review, fixed-hyperparameter diagnostic
  models, baseline asymmetry, null distributions, and residual-signal
  decomposition. Original data, targets, transforms, endpoints, splits,
  predictions, results, and checkpoints are immutable.
- All diagnostic outputs must be new files under `results/audit/`. M2/M3 remain
  prohibited unless every audit PASS condition is met.
- Diagnostic models use the frozen outer splits, seeds 0/1/2 unless explicitly
  specified, no re-tuning, and median inner-selected hyperparameters.
- Required controls are DOSE-SMOOTH, full well-level target shuffle, and 20
  documented chemical-block permutations for B3 and M1. If the timebox is tight,
  10 permutations are allowed only as an explicit deviation.
- Audit outcomes are fixed as PASS — residual structure under null; LEAK FOUND;
  or UNEXPLAINED. A full-shuffle beneficial CI, leaking feature/data path, or
  target/index realignment triggers LEAK FOUND. Failure of any PASS condition
  without an identified leak triggers UNEXPLAINED and stops before M2/M3.
- If and only if the audit passes, the historical Gate S failure remains visible,
  BT++ is added post hoc as inner-selected best of BT+ and DOSE-SMOOTH, and M2 may
  resume with both BT+ and BT++ reported.
- Deadline/timebox supplied by the user: 2026-09-29 14:00 Africa/Cairo.

## 2026-09-28 — Post-registration integrity audit: PASS

- Audit classification: **PASS — RESIDUAL STRUCTURE UNDER NULL**. The historical
  registered Gate S remains **FAIL / STOP** and its files are unchanged.
- No feature/data leak or target realignment was found. The full well-level target
  shuffle had no beneficial confidence interval on any endpoint.
- The registered burst null was compatible with DOSE-SMOOTH and did not
  significantly beat it. Decomposition showed that rank-interpolated chemical
  blocks retain generic early-neural trajectory structure.
- Real M1 beat DOSE-SMOOTH with a beneficial chemical-bootstrap interval on all
  five endpoints, exceeded all 20 repeated M1 block-null runs on all five, and had
  zero exceedances per endpoint (reported as empirical p < 0.05).
- Per the authorized audit rule, scientific progression may resume after adding
  post-hoc BT++ (inner-selected best of BT+ and DOSE-SMOOTH). All future reports
  must preserve both original BT+ and post-hoc BT++ results.
- Full evidence: `docs/integrity_audit.md` and `results/audit/`.

## 2026-09-28 — Gates M2/M3 and early L1 lock

- Added post-hoc BT++ exactly as authorized: the better of BT+ and fixed
  DOSE-SMOOTH is selected using chemical-disjoint inner-validation rows only.
  Outer-test labels remain evaluation-only. Both BT+ and BT++ stay reported.
- Gate M2 **PASS**: nested group-aware CV+ achieved 91.03-92.40% overall coverage
  for nominal 90% intervals across all five endpoints, with every NTP/ToxCast
  coverage above 90%. The allowed CQR switch was not used.
- Gate M3 **PASS, mixed by endpoint**: at 70% accepted coverage, firing rate,
  active electrodes, and `r` exceeded 15% risk reduction with chemical-bootstrap
  intervals below zero. Bursts improved by 4.61%; network spikes improved by
  5.26% with its interval crossing zero. All five remain visible.
- Gate L1: **LOCK**. Freeze M1 and the reliability protocol. `r` retains its
  percent-control normalization caveat despite passing the abstention criterion.
- Full evidence: `docs/phase3_m2_m3_results.md`.

## 2026-09-28 — Post-lock time and practical-value analysis

- P1 completed with frozen settings at DIV5, DIV5+7, and DIV5+7+9. DIV9 is a
  post-lock ablation only and does not alter the registered primary model.
- DIV7 is the earliest window with material gain across all five endpoints. DIV9
  improves four endpoints; `r` does not improve from DIV7 to DIV9.
- A fixed DIV7 reliability threshold abstains on nearly every DIV5 prediction,
  30% at DIV7 by construction, and 2.7-7.1% at DIV9 for four endpoints; `r`
  remains at 29.3% abstention.
- P2 reports approximately 70% accepted held-out prediction instances. An accepted
  DIV7 result is five assay days earlier than DIV12 (41.7% of the stated 12-day
  duration). No monetary or autonomous-deployment claim is made.
- Full evidence: `docs/time_practical_results.md`.

## 2026-09-28 — Potency Gate P1: appendix due target mismatch

- The bundled official EC50 tables measure ontogeny-AUC potency, not DIV12-only
  potency. Their `NA` values mean no supported in-range estimate under the EPA R
  workflow and were not imputed or converted to zero.
- Exploratory predicted-DIV12 versus official-AUC rankings are strong across all
  five endpoints (Spearman 0.773-0.868; 54-61 comparable chemical/cohort pairs).
- Gate P1 is **not eligible for a headline pass** because the response targets do
  not match. Preserve the result in the appendix; do not claim that official
  potency was predicted five days earlier.
- Full evidence: `docs/potency_appendix.md`.

## 2026-09-28 — Frozen M1 interpretability

- Seed-0 outer models were refit with preserved task settings solely to compute
  held-out XGBoost tree contributions; no tuning or result selection changed.
- DIV7 neural features contribute 56.9-77.3% of total absolute attribution across
  endpoints. Chemistry is complementary (11.2-31.8% combined Morgan/RDKit), while
  cohort and explicit dose are small globally.
- Three correct and two failure cases were selected post-lock by a disclosed
  endpoint-scaled error rule. They are descriptive, not performance estimates or
  automatically chosen showcase defaults.
- Full evidence: `docs/interpretability.md`.

## 2026-09-29 — Gate F1 claim correction

- The locked model, endpoints, splits, comparators, predictions, and headline
  numbers remain unchanged.
- Dose language now separates beneficial point estimates from confidence
  intervals excluding zero. Firing-rate low/mid and network-spike low-dose
  intervals are explicitly inconclusive.
- Cohort language now states that ToxCast firing rate is inconclusive and that
  the existing slices are not held-out cohort or external device transfer.
- Zero-dose underperformance for bursts, firing rate, and network spikes is
  disclosed. Control normalization is labeled interpretation rather than an
  established explanation; the intended early-triage use is exposed wells.
- The locked title is restored in the report and README. Deck-title alignment is
  reserved for the required F7 deck rebuild.
