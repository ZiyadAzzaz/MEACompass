# Decision log

## 2026-09-29 — Project identity lock

- Identity: MEACompass (formerly NeuroChip-Twin).
- Full title: **MEACompass: Reliability-Aware Early Prediction of Neural Network
  Development from Microelectrode-Array Assays**.
- Subtitle: **Toward Functional Digital Twins for Neural Organ-on-Chip Screening**.
- Scope: rename repository, package/module imports, CLI commands, app, report,
  README, deck, video assets, schemas, and documentation without modifying
  locked scientific values or result contents beyond identity strings.

## 2026-09-29 — Gate F2: PASS

- Result-only reproduction was verified from a fresh local clone at commit
  `093d08e` with a distinct Python 3.11 environment.
- The committed 8.34 MiB result bundle passed all seven SHA-256 checks; 56 tests
  passed; five tables/figures regenerated without retraining; and the Streamlit
  demo returned HTTP 200.
- `git status --porcelain` remained empty after setup and reproduction.
- A Windows path-with-spaces defect found during the clean-clone test was fixed
  by quoting Python invocations and selecting `cmd.exe` only on Windows.
- Evidence and timings: `docs/reproducibility.md`.

## 2026-09-29 — Gate F3b: SKIPPED AT LICENSE GATE

- Official source audited: `USEPA/CompTox-DNT-NFA-Refinement`, pinned at
  `01adf3e1a0068c87fe221d60df36b9f96c4b4b1d`.
- The repository is publicly visible but contains no root license file, its
  README grants no reuse license, and GitHub reports no detected license.
- Decision: do not clone, download, harmonize, or score the external release.
  Public visibility is not treated as permission.
- No F3b result or external-validation claim is permitted. Resume only after an
  explicit license or written permission is available, and commit the full
  preregistration before scoring.
- Full record: `docs/f3b_external_validation.md`.

## 2026-09-29 — F3b controlled provenance protocol registered

- This registration does not reopen or modify the locked primary analysis.
  External evaluation is post-lock secondary work only.
- The user reports that permission clarification was requested by email and a
  GitHub issue on 2026-09-29. No response or verification link is stored here;
  this is not recorded as permission granted.
- For files verified as EPA-authored U.S. Government works, document the
  17 U.S.C. §105 public-domain rationale. Repository ownership alone is not
  sufficient to classify every included file as public domain. Each downloaded
  file must have documented provenance and a reuse basis before harmonization or
  scoring.
- Public GitHub access does not equal reuse permission. Unclear files are skipped.
- The pre-acquisition manifest is `results/f3b/source_manifest.csv`. Only rows
  marked `allowed_for_analysis=YES` may enter the pinned, checksum-verified fetch.
- Required order after provenance approval: controlled fetch → committed
  external preregistration → chemical-overlap exclusion → endpoint
  harmonization → frozen M1 evaluation → STRONG/MIXED/FAIL interpretation.
- No retraining, external tuning, or silent recalibration is allowed. Zero-shot
  calibration and any locally recalibrated secondary analysis must remain separate.
- Current decision remains **CUT** because every required data-bearing candidate
  has unclear file-level provenance/reuse status.

## 2026-09-29 — Gate F5: BRANCH / PUBLICATION READY

- Built a self-contained static fallback from precomputed outer-test predictions
  at `docs/demo/index.html`; the generator is `scripts/build_static_demo.py`.
- The deterministic cohort-balanced subset contains 100 held-out wells and does
  not select cases using outcomes, errors, uncertainty, or verdicts.
- Local delivery returned HTTP 200 in 0.16 seconds with no external requests;
  automated tests cover schema completeness and required scope labels.
- A public URL is not yet claimed: the repository has no remote, GitHub
  authentication is invalid, and making a repository public is a human-only
  action under the approved protocol.
- Full record and completion instructions: `docs/f5_demo.md`.

## 2026-09-29 — Pre-publication scrub: DO NOT PUSH

- Current tree, public HTML, PowerPoint XML, and reachable git history were
  scanned for local paths, machine identifiers, secrets, personal email, raw or
  external data, CellTwin-X material, checkpoints, temporary outputs, sensitive
  filenames, and oversized blobs; no violation was detected.
- License, source record, reproduction instructions, and `docs/.nojekyll` are
  present.
- Publication remains blocked because the actual AI assistants/services and
  their roles require user confirmation. The template is not a final disclosure.
- No history rewrite is required. Do not push until the disclosure is confirmed,
  tests are rerun, and `docs/prepublication_scrub.md` is updated to SAFE TO PUSH.

## 2026-09-28 — Gates N0/N1: data feasibility

- Evidence: 136 unique CAS RNs, 4,344 per-well trajectories, DIV5/7/9/12,
  96.5% complete trajectories, 95.6% PubChem SMILES resolution.
- Decision: make MEACompass the primary project, while keeping CellTwin-X as the
  measured fallback until Gate L1.
- Claim constraint: EPA NFA is a rat cortical neural MEA assay, not OoC data.
- Full evidence: `docs/meacompass_data_audit.md`.

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

## 2026-09-29 — F3b provenance amendment and frozen-model definition

- Replaced the earlier per-file-authorship requirement with the user-approved
  four-part provenance rule. The six declared candidate files are in the
  official USEPA repository, are described by the repository/readme as inputs or
  outputs for the NFA-refinement manuscript, trace to commit `ac86b693` authored
  with an `epa.gov` address, and have no third-party dataset license stated in
  their repository path or provenance record. They are therefore marked
  `allowed_for_analysis=YES`; this is not a blanket repository license claim.
- Permission clarification requested by email and GitHub issue on 2026-09-29
  remains recorded; no response has been supplied.
- Frozen external prediction is now defined as the mean of 15 historical M1
  outer-fold models per endpoint (five folds × seeds 0/1/2). Model file hashes
  must be registered before acquisition or scoring. No refit or reconstruction
  is permitted.
- The repository contains the 75 tuning records and locked out-of-fold
  predictions but no serialized M1 model artifacts. F3b therefore remains
  **CUT at the model-availability gate**. Eligible external files were not
  acquired, harmonized, or scored.
- Inputs and endpoints are both covered by the overlap harmonization gate in
  `docs/f3b_preregistration.md`. Any mapping must use overlapping recordings
  only; new test conditions remain untouched.
- Per the amendment fallback, frozen-hyperparameter ToxCast→NTP and NTP→ToxCast
  evaluation is the next post-lock secondary scientific analysis, time-boxed to
  one day.

## 2026-09-29 — F3 directional cross-cohort protocol frozen

- Registered the two directional analyses, chemical-overlap exclusion, frozen
  M1 parameter aggregation, three-seed ensemble, source-only BT+/BT++ selection,
  metrics, bootstrap unit, and PASS/MIXED/FAIL rule before execution.
- This is post-lock secondary robustness analysis inside the 2019 EPA assay
  release. It cannot change the locked result and is not external laboratory,
  device, human, or organ-on-chip validation.
- Full specification: `docs/f3_cross_cohort_preregistration.md`.

## 2026-09-29 — F3 directional cross-cohort result: PASS

- Frozen-hyperparameter M1 beat source-selected BT++ on all five endpoints in
  both directions, with all paired chemical-bootstrap confidence intervals below
  zero. Registered PASS required at least three wins in each direction.
- Eleven shared chemicals were excluded from each target direction. Eligible
  target sets contained 39 NTP chemicals and 86 ToxCast chemicals before
  endpoint-specific completeness filtering.
- This supports the narrow statement: “Retained predictive value under a
  held-out NTP↔ToxCast cohort shift without model retuning.” It is not external
  laboratory/device transfer, and it does not alter the locked primary headline.
- Full evidence: `docs/f3_cross_cohort_results.md` and aggregate files under
  `results/f3_cross_cohort/`.

## 2026-09-29 — F6 technical report generated

- Built `docs/MEACompass_Technical_Report.pdf` from the reviewed Markdown source
  using pinned, free ReportLab and pypdf dependencies.
- The report is 18 pages including two appendix sections, contains all 24 required
  topics, four evidence figures, the locked five-endpoint results, the preserved
  Gate S stop, F3b CUT, and secondary F3 PASS with bounded wording.
- PDF structure, page count, text extraction, required sections, figure embedding,
  and absence of local machine paths are automated tests. The full repository
  suite passed after generation.
- Gate F6 is **BRANCH — publication content complete, user fields pending**.
  Team information and AI-tool names/roles remain `USER CONFIRMATION REQUIRED`;
  neither was guessed.

## 2026-09-29 — Gate F7 deck and video package: BRANCH

- Rebuilt the competition narrative as a 12-slide editorial deck with the
  required problem, concept, scientific boundary, chemical-disjoint evaluation,
  locked results, integrity audit, calibration, selective prediction, time
  causality, interface, adoption, and reproduction sequence.
- Interpretability is merged into the locked-results and time-causality slides:
  DIV7 contributes 56.9–77.3%, chemistry contributes 11.2–31.8%, and the
  tributyltin chloride failure remains explicit.
- The deck reports all five preregistered endpoints, the three passing abstention
  endpoints, and the two limitations. The F3 cohort-shift evidence uses the
  approved narrow wording and explicitly denies external laboratory/device
  transfer.
- Automated presentation-layout QA reports 0 errors and 0 warnings. The
  comeback score is 43/45.
- Gate F7 is **BRANCH — content and layout complete; real demo capture pending**.
  Slide 10 contains a visible capture requirement because the mandated in-app
  browser connection was unavailable. No synthetic, drawn, or selectively
  curated screenshot was substituted.
- The video package now includes a 4:45 shot list, an early demo segment, a
  six-group spoken-number budget, and provisional English and Chinese SRT files.
  The Chinese first mention uses “最强基线 BT+” and “平均绝对误差（MAE）”. Final
  timings require the recorded narration and human translation review.

## 2026-09-29 — Gate F8 Kaggle writeup: BRANCH

- Created `docs/kaggle_writeup.md` in the required order: links, a 231-word
  project summary, technical evidence with figures, use-on-your-own-data recipe,
  sources/licenses, and AI-tool disclosure.
- The summary carries the three locked headline groups: 14.2–39.0% MAE gain
  versus BT+, 91.0–92.4% empirical interval coverage, and three of five
  abstention endpoints passing. All five endpoint names and both abstention
  limitations remain explicit.
- Added automated checks for the summary word count, locked numbers, scientific
  boundary, decision-support wording, and deck text. The full suite passes 69/69.
- Corrected the refinement-source license note to match the registered provenance
  amendment: six files are eligible for analysis, but none was downloaded or
  redistributed because F3b was cut at frozen-model availability.
- Gate F8 is **BRANCH — writeup content complete; human publication fields
  pending**. The video URL is the allowed placeholder. The intended GitHub and
  Pages URLs do not resolve until the user performs the human-only publication
  action, and the AI-tool disclosure cannot be finalized until the user confirms
  the actual tools and roles. No tool identity was guessed.

## 2026-09-29 — Gate F4 fallback: schema and recipe shipped

- Applied the approved time-box fallback instead of shipping a partially tested
  adaptation CLI. Added `schemas/mea_input_v1.yaml` and
  `docs/adoption_recipe.md`.
- The schema requires chemical, dose, plate, well, DIV, and all five reference
  endpoint columns; SMILES, cohort, and replicate are optional. It fails closed
  on duplicate keys, missing time points, missing plate/DIV controls, mixed dose
  units, invalid control denominators, or time-causality violations.
- The recipe covers endpoint harmonization, same-plate zero-dose normalization,
  chemical-disjoint nested evaluation, training-only selection/calibration,
  chemical bootstrap, drift checks, and frozen prospective validation.
- Wording is deliberately bounded: this is a local evaluation/adaptation toolkit,
  not evidence that the frozen EPA model deploys directly on a new chip. New
  platforms require local validation and recalibration.
- Gate F4 is **CUT TO APPROVED FALLBACK — schema + recipe complete; no CLI**.
  Automated schema/boundary tests pass; the full suite is 71/71.

## 2026-09-29 — Amendment B F3b final-refit protocol registered

- Amendment B supersedes only the earlier prohibition on reconstructing a final
  model. The primary locked analysis and every headline result remain immutable.
- Before any new refinement byte is fetched or opened, registered a deterministic
  final M1 rule from the 75 preserved tuning records: median aggregation for
  numeric settings, deterministic valid rounding, categorical mode with lexical
  tie-breaking, all eligible 2019 chemicals, seeds 0/1/2, and a three-seed mean.
- Frozen endpoint settings are stored in
  `schemas/final_model_hyperparameters.json`; the feature and descriptor contract
  remains DIV5/DIV7-only and unchanged from locked M1.
- Final BT+ and BT++ selection, the grouped 2019 out-of-fold residual pool,
  finite-sample nominal-90% interval rule, and 70%-policy seed-disagreement
  threshold are fixed using 2019 data only. External outcomes cannot select,
  calibrate, or fit any component.
- Registered the pinned source allowlist, file-level EPA provenance rule,
  controlled first-fetch hash initialization, chemical/plate/date/batch overlap
  exclusion, 18-input/five-endpoint harmonization contract, bootstrap seed and
  draws, and STRONG/MIXED/FAIL/CUT rules.
- Verified author identity is Ziyad Azzaz, College of Artificial Intelligence,
  AASTMT, Alamein Campus, Egypt. Team name and AI-tool identities remain
  `USER CONFIRMATION REQUIRED`; neither is inferred.
- No refinement file was fetched, opened, harmonized, or scored while preparing
  this registration.
