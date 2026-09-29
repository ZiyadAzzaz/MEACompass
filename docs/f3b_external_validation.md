# F3b frozen external validation: controlled provenance gate

## Gate record

**Status: CUT BEFORE DATA ACQUISITION OR SCORING**

The approved F3b protocol requires a clearly public and reusable license before
the external repository is obtained. The source audit was performed first and no
external predictions, harmonization statistics, or endpoint scores were viewed or
computed.

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

Per the registered F3b rule, license clarity is a prerequisite. Therefore:

- no repository clone or bulk download was performed;
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

### Current file-level result

Pinned tree metadata identifies candidate data-bearing files, but no candidate
currently has verified individual authorship plus a reuse grant or documented
§105 basis. All are therefore marked `allowed_for_analysis=NO`. No raw external
file was downloaded, no external outcome was viewed, and no preregistration or
scoring phase was activated.

F3b may resume only after explicit file-level permission or provenance evidence
covers every required input. The full preregistration must then be committed
before harmonization or scoring. Until then, external validation remains future
work rather than a positive or negative scientific result.
