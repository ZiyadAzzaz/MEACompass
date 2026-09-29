# F3b frozen external validation: controlled provenance gate

## Gate record

**Status: CUT AT FROZEN-MODEL AVAILABILITY GATE**

The amended F3b protocol provides a four-part, file-level provenance rule. The
source audit was performed first. Six explicitly declared candidate files meet
that rule, but the exact serialized historical M1 models required by the frozen
evaluation definition are not present. No external data, predictions,
harmonization statistics, or endpoint scores were viewed or computed.

| Field | Frozen record |
|---|---|
| Repository | `https://github.com/USEPA/CompTox-DNT-NFA-Refinement` |
| Owner | U.S. Environmental Protection Agency (`USEPA`) |
| Default branch | `main` |
| Pinned commit | `01adf3e1a0068c87fe221d60df36b9f96c4b4b1d` |
| Commit date | 2026-04-24 02:41:37 UTC |
| Repository visibility | Public |
| GitHub license metadata | `null` / none detected |
| Root `LICENSE` or `COPYING` file | Not present |
| README license grant | Not present |

The repository describes source files and analysis outputs for the NFA refinement
manuscript, but its README does not state a reuse license. Public GitHub access is
not treated as permission to reuse or redistribute the included data. Government
authorship or public-domain status is not assumed because the provenance and
authorship of every included file are not established by the repository metadata.

## Decision

Per the registered F3b rule, model availability is also a prerequisite. Therefore:

- no repository clone or external data download was performed;
- no external files were copied into this project;
- no overlap or harmonization gate was computed;
- the frozen M1 model was not scored on the refinement release;
- no external-validation claim is permitted.

## Controlled reconsideration registered 2026-09-29

The user reports that permission clarification was requested by email and by a
GitHub issue on 2026-09-29. No message contents, issue URL, recipient confirmation,
or response were supplied to this repository, so this is recorded as a
user-reported request rather than verified permission. Private correspondence is
not copied into publication artifacts.

Controlling rule:

> For files verified as EPA-authored U.S. Government works, document the
> 17 U.S.C. §105 public-domain rationale. Repository ownership alone is not
> sufficient to classify every included file as public domain. Each downloaded
> file must have a documented provenance and reuse basis before harmonization or
> scoring.

This is not a blanket license claim. Public GitHub access is not treated as reuse
permission. A file with unclear provenance is skipped.

### Registered execution sequence

1. **Pre-acquisition manifest.** Every candidate appears in
   `results/f3b/source_manifest.csv`. Only `allowed_for_analysis=YES` may be
   fetched or analyzed.
2. **Controlled fetch.** `scripts/fetch_f3b.py` accepts the pinned commit only,
   downloads only declared files, requires a frozen SHA-256, refuses undeclared
   local files, and writes under ignored `data/external/f3b/`.
3. **Pre-registration.** Before outcomes, harmonization, or performance are
   viewed, freeze endpoint/time mappings, transforms, controls, chemical
   canonicalization, overlap exclusion, missingness, inclusion rules, metrics,
   chemical bootstrap, calibration, abstention, and gate criteria in
   `docs/f3b_preregistration.md`; commit it separately.
4. **Chemical independence.** Exclude every CAS RN present in original model
   development and report total, overlap-excluded, and remaining counts.
5. **Harmonization.** Classify each endpoint as `EXACT MATCH`,
   `COMPATIBLE WITH DECLARED TRANSFORM`, or `NOT COMPARABLE`; score only the first
   two categories.
6. **Frozen evaluation.** No retraining or tuning. Report MAE, RMSE, Spearman,
   gain versus external BT+/BT++, chemical-bootstrap 95% intervals, and zero-shot
   coverage if applicable. Any local recalibration is a separate secondary result.
7. **Interpretation.** Classify as STRONG, MIXED, FAIL, or CUT. Even a successful
   result is post-lock secondary evidence and does not imply human, organ-on-chip,
   laboratory/device, or deployment transfer.

### Amended file-level result

The official repository description associates the repository with the Vahanan
et al. NFA-refinement manuscript. `ReadMe_MV_27June2025.txt` identifies
`source_files` as inputs needed for the manuscript RMD and identifies the
`tcplfit2_results` inputs/results. GitHub's per-path commit history traces all six
candidate files to commit `ac86b693`, authored with an `epa.gov` address. No
third-party dataset or separate license is stated for those candidate paths.
Under the user-approved four-part rule they are marked
`allowed_for_analysis=YES`. This conclusion is limited to the manifest files and
is not a blanket license statement for the repository.

The controlled fetch still refuses to run because SHA-256 values have not been
frozen, and acquisition is unnecessary while the model gate fails. The repository
contains 75 tuning records and locked out-of-fold predictions, but no serialized
M1 model artifacts. The amendment defines an external prediction as the mean of
15 locked outer-fold models per endpoint and expressly forbids refitting. F3b is
therefore CUT without scoring. The full registered specification is in
`docs/f3b_preregistration.md`.

F3b may resume only if the exact historical serialized models are supplied and
their hashes verified. It remains future work rather than a positive or negative
external-transfer result. The registered fallback is the post-lock, directional
ToxCast-to-NTP and NTP-to-ToxCast analysis using frozen hyperparameters.
