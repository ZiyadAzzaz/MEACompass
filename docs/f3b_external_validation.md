# F3b frozen external validation: source and license gate

## Gate record

**Status: SKIPPED BEFORE DATA ACQUISITION OR SCORING**

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

F3b may resume only after the repository owner supplies an explicit license or
written permission covering the required source data and derived evaluation.
When that happens, the complete preregistration must be committed before any
harmonization or scoring begins. Until then, frozen external validation remains
future work rather than a positive or negative scientific result.
