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
repository-wide reuse grant. Under the registered four-part file-level provenance
rule, the six declared EPA analysis files are marked `allowed_for_analysis=YES` in
`results/f3b/source_manifest.csv`; this is not a blanket repository license claim.
The six allowlisted files were downloaded locally from the pinned commit, hashed,
and analyzed only for provenance and harmonization. They remain ignored and are
not redistributed. F3b was CUT before outcome scoring because required inputs
were absent or not comparable. The recorded license clarification request remains
unanswered.

## Dependencies

Python dependencies and versions are declared in `pyproject.toml`,
`requirements.txt`, and `environment.yml`. Each dependency retains its own
license. No EPA seal, logo, or project affiliation is claimed or implied.

## AI assistance

The confirmed AI-tool disclosure is in `docs/ai_tool_disclosure.md`. Codex/the
repository coding agent supported implementation and artifact preparation;
ChatGPT supported planning and review; Claude supported independent review and
source exploration. None was accepted as a source of scientific result values.
All values came from executed code and saved artifacts, automated claim tests
were used, and the author manually reviewed the public scientific claims and
submission materials.
