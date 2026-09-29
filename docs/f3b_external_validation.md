# F3b post-lock external validation

## Gate report

**GATE: CUT AT HARMONIZATION — NO EXTERNAL OUTCOME SCORING**

F3b is post-lock secondary work. It cannot alter the locked primary results.
Under Amendment B, deterministic final models were built from all eligible 2019
development chemicals before external access. The three-seed models, final BT+ /
BT++ selections, grouped residual pool, abstention thresholds, feature order,
package versions, and every artifact hash are recorded in
`schemas/final_model_manifest.json`.

## Controlled source acquisition

Only six files listed as `allowed_for_analysis=YES` in
`results/f3b/source_manifest.csv` were fetched from USEPA repository commit
`01adf3e1a0068c87fe221d60df36b9f96c4b4b1d`. Their combined local size is
21,357,516 bytes (20.4 MiB). The manifest freezes each SHA-256. Raw files remain
ignored and are not redistributed.

This is a file-level provenance determination, not a blanket license claim. The
repository has no detected repository-wide license. The permission clarification
reported as requested by email and GitHub issue on 2026-09-29 remains unanswered.

## Independence audit stopped after harmonization CUT

The refinement objects cover 45 experiment dates. Twenty-eight dates are absent
from the 2019 development release, yielding 10,422 candidate rows and 111
treatment labels before CAS filtering. CAS-level external eligibility was not
continued because the earlier harmonization gate failed. No candidate row became
an evaluation row and no outcome was scored.

## Harmonization evidence

The audit matched 12,709 recordings across 96 plates using cohort, plate, well,
and DIV. Each release was independently transformed with the preregistered
same-plate, same-DIV zero-dose percent-control rule.

- Fifteen of 18 neural variables passed Spearman ≥ 0.95 and median-ratio
  0.9–1.1.
- `cv.time` and `cv.network` are absent from the refinement objects. The frozen
  M1 feature order requires their DIV5 and DIV7 values and missingness flags.
- `r` is present but fails the rank-correlation threshold: Spearman 0.817, with
  median ratio 1.000.
- No mapping was fitted using candidate test rows or outcomes.

Because every final endpoint model requires the full registered input vector,
all five endpoints are `NOT_COMPARABLE`. The preregistered rule therefore forbids
external scoring, including MAE, rank correlation, interval coverage, abstention,
or case selection.

Machine-readable evidence:

- `results/f3b/harmonization.csv`
- `results/f3b/independence_audit.json`
- `results/f3b/decision.json`
- `results/f3b/source_manifest.csv`

Reproduce the gate with `make f3b-audit PYTHON=<environment-python>` after placing
the verified allowlisted files under ignored `data/external/f3b/`.

## Narrow interpretation

F3b is **CUT**, not a positive or negative external-performance result. The
actual reason is missing/non-comparable required inputs, not model availability.
The completed post-lock NTP↔ToxCast held-out-cohort analysis remains the fallback:
it retained predictive value without model retuning, but it is not external
laboratory, device, human, or organ-on-chip validation.
