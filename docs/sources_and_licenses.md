# Sources and licenses

Compliance audit date: **2026-09-29**.

## Project code and authored materials

MEACompass code and project-authored documentation are released under the
Apache License 2.0 in the repository `LICENSE` file. This does not relicense
third-party data, source material, or software dependencies.

## Primary EPA NFA data

The original locked analysis uses the public EPA NFA files identified in
`schemas/epa_downloads_v1.json`. Their source URLs, sizes, and SHA-256 hashes are
frozen there. The source catalog and EPA ScienceHub terms are documented in
`docs/meacompass_data_audit.md`. Raw EPA files are downloaded locally and excluded
from Git; the repository publishes code and derived evaluation artifacts.

| Source | Role | License/terms | Redistributed? | Attribution needed? | Permission needed? |
|---|---|---|---|---|---|
| [EPA NFA dataset, DOI 10.23719/1503191](https://doi.org/10.23719/1503191) | Primary rat cortical neural MEA measurements | EPA ScienceHub terms; public U.S.-government-work basis unless otherwise specified | No raw files | EPA dataset, DOI, and catalog | No separate permission identified for this documented public analysis; terms still apply |
| [Data.gov catalog](https://catalog.data.gov/dataset/data-for-evaluation-of-chemical-effects-on-network-formation-in-cortical-neurons-grown-on-) | Official provenance | Data.gov/EPA catalog terms | No | Yes | No |
| [EPA ScienceHub license](https://pasteur.epa.gov/license/sciencehub-license.html) | Controlling terms and no-endorsement boundary | Page-specific EPA terms | No | Cite/link terms | No |

## Chemical structures

Chemical identifiers and structures were resolved through the public PubChem PUG
REST service. Users must follow PubChem's current usage and attribution guidance.

| Source | Role | License/terms | Redistributed? | Attribution needed? | Permission needed? |
|---|---|---|---|---|---|
| [PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest) | Resolve chemical identifiers for local RDKit descriptors | NCBI/PubChem usage policies and service limits | No lookup cache or bulk record | Cite PubChem | No separate permission for ordinary public API use; current policies apply |

## EPA refinement repository

The post-lock external-validation candidate is pinned at commit
`01adf3e1a0068c87fe221d60df36b9f96c4b4b1d` of
`USEPA/CompTox-DNT-NFA-Refinement`. The repository has no detected root license or
repository-wide reuse grant. Under the registered four-part file-level provenance
rule, the six declared EPA analysis files are marked `allowed_for_analysis=YES` in
`results/f3b/source_manifest.csv`; this is not a blanket repository license claim.
The six allowlisted files were downloaded locally from the pinned commit, hashed,
and analyzed only for provenance and harmonization. They remain ignored and are
not redistributed. F3b was CUT before outcome scoring because required inputs
were absent or not comparable. The recorded license clarification request remains
unanswered.

| Source | Role | License/terms | Redistributed? | Attribution needed? | Permission needed? |
|---|---|---|---|---|---|
| [`USEPA/CompTox-DNT-NFA-Refinement`](https://github.com/USEPA/CompTox-DNT-NFA-Refinement/tree/01adf3e1a0068c87fe221d60df36b9f96c4b4b1d) | Post-lock provenance/harmonization audit only | No root repository-wide license detected; file-level EPA provenance rationale is recorded | **No** | Repository, commit, EPA manuscript team | Clarification requested; therefore no raw redistribution or external outcome claim |

## Dependencies

Python dependencies and versions are declared in `pyproject.toml`,
`requirements.txt`, and `environment.yml`. Each dependency retains its own
license. No EPA seal, logo, or project affiliation is claimed or implied.

Dependencies are installed from their normal public package channels; source and
binary distributions are not vendored here.

| Dependency | Role | License in installed package metadata | Redistributed? |
|---|---|---|---|
| NumPy | arrays/numerics | BSD-3-Clause plus bundled permissive notices | No |
| pandas | tables | BSD-3-Clause | No |
| SciPy | statistics | BSD-3-Clause | No |
| scikit-learn | metrics/splits/preprocessing | BSD-3-Clause | No |
| XGBoost | boosted-tree models | Apache-2.0 | No |
| RDKit | chemical descriptors | BSD-3-Clause | No |
| PyYAML | configuration | MIT | No |
| pytest | tests | MIT | No |
| Matplotlib | figures | Matplotlib license (PSF-compatible) | No |
| Pillow | image inspection/export | MIT-CMU | No |
| seaborn | figure styling | BSD-3-Clause | No |
| Streamlit | optional local demo | Apache-2.0 | No |
| ReportLab | report generation | BSD-style ReportLab license | No |
| pypdf | report QA | BSD-3-Clause | No |
| pyreadr | optional F3b reader | AGPL-3.0-or-later | No; optional local analysis only |

Upstream notices must be retained if a dependency is redistributed. The optional
`pyreadr` dependency remains separate and unvendored; its AGPL terms apply to any
redistribution or covered combined work.

## Visual, presentation, and video assets

| Artifact | Source/role | Terms | Redistributed? | Rights note |
|---|---|---|---|---|
| `artifacts/reproduce-lite/*.png` | Generated by MEACompass scripts from committed result tables | Project-authored, Apache-2.0 | Yes | No external image |
| `docs/assets/main_results_locked.png` | Render of the project-authored locked-results slide | Project-authored, Apache-2.0 | Yes | No external image |
| `docs/assets/demo_public_neutral.png` | Authentic crop from the author's public MEACompass demo capture | Project-authored UI/model outputs | Yes | Provenance hash in `docs/deck_qa.md`; no redrawn value |
| Competition deck/report | Project-authored text, shapes, tables, and figures | Project-authored; upstream terms stay separate | Yes | No logo, stock image, or paid asset |
| Competition video | Project slides and authentic public-demo footage | Project-authored | Draft not committed | No music; any later addition requires documented rights |

The demo uses generic system font families and the deck uses system presentation
fonts. No font file is committed or embedded for redistribution. No stock icons,
third-party logos, music, external photographs, or third-party footage are used.

## AI assistance

The confirmed AI-tool disclosure is in `docs/ai_tool_disclosure.md`. Codex/the
repository coding agent supported implementation and artifact preparation;
ChatGPT supported planning and review; Claude supported independent review and
source exploration. None was accepted as a source of scientific result values.
All values came from executed code and saved artifacts, automated claim tests
were used, and the author manually reviewed the public scientific claims and
submission materials.

AI services are authoring/review tools, not scientific evidence sources and not
runtime dependencies of the public reproduction path. No generated statement is
treated as independent validation of scientific evidence.
