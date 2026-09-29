# Sources and licenses

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

## Chemical structures

Chemical identifiers and structures were resolved through the public PubChem PUG
REST service. Users must follow PubChem's current usage and attribution guidance.

## EPA refinement repository

The post-lock external-validation candidate is pinned at commit
`01adf3e1a0068c87fe221d60df36b9f96c4b4b1d` of
`USEPA/CompTox-DNT-NFA-Refinement`. The repository has no detected root license or
repository-wide reuse grant. Repository ownership alone is not used to classify
individual files as U.S. Government works. The file-level provenance gate is in
`results/f3b/source_manifest.csv`; all candidates are currently disallowed, no
raw refinement file is redistributed, and F3b remains CUT.

## Dependencies

Python dependencies and versions are declared in `pyproject.toml`,
`requirements.txt`, and `environment.yml`. Each dependency retains its own
license. No EPA seal, logo, or project affiliation is claimed or implied.
