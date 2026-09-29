# Pre-publication repository scrub

Date: 2026-09-29  
Scope: current tracked tree, generated public demo, current PowerPoint XML, and
reachable git history where practical. Git history was not rewritten.

## Summary

| Check | Status | Evidence |
|---|---|---|
| LOCAL PATHS | PASS | No tracked `C:\\`, `E:\\`, `/Users/`, user-home, AppData, username, or machine-path match; no PowerPoint XML match |
| SECRETS | PASS | No token, credential, bearer header, password assignment, private-key marker, `.env`, credential, or secret-key filename match in the tree or reachable history |
| RAW DATA | PASS | No tracked file under `data/` or `external/`; no external refinement file downloaded; only the provenance manifest is committed |
| CELLTWIN-X | PASS | No tracked path contains `celltwin`; the separate project was not copied, modified, or deleted |
| CHECKPOINTS | PASS | No tracked `.pt`, `.pth`, `.ckpt`, `.joblib`, or `.pkl` file |
| TEMPORARY OUTPUTS | PASS | No tracked pytest cache, Python cache, temporary, preview, or layout workspace |
| PERSONAL EMAIL | PASS | No tracked personal email address detected |
| LICENSE | PASS | Root Apache-2.0 license present; third-party/data terms separated in `docs/sources_and_licenses.md` |
| AI DISCLOSURE | **FAIL — USER CONFIRMATION REQUIRED** | Required template exists, but actual assistant/service names and roles have not been confirmed |
| GITHUB PAGES | PASS | Self-contained `docs/demo/index.html` and `docs/.nojekyll` present; no external requests |
| GIT HISTORY | PASS | No path/secret filename or content match; no reachable blob exceeds 10 MiB |

## Size and publication controls

- Largest tracked file: `results/demo_predictions.csv`, 5,791,634 bytes.
- No tracked file exceeds the repository's 50 MiB artifact limit.
- Raw EPA downloads, external refinement files, checkpoints, environments, and
  generated artifacts remain ignored.
- Current external-validation candidates are all marked
  `allowed_for_analysis=NO`; the fetcher refuses to download them.
- The repository contains no git remote and no public URL is claimed.

## Publication status

**PUBLICATION STATUS: DO NOT PUSH**

The only content blocker found by this scrub is the unconfirmed AI-tool
disclosure. Making the repository public is also a human-only action under the
approved protocol. Exact first-push commands are intentionally withheld until:

1. the user confirms every AI assistant/service used and its role;
2. `docs/ai_tool_disclosure.md` is finalized and reviewed;
3. the scrub and tests are rerun with `AI DISCLOSURE: PASS`.

No secret or sensitive-history remediation is currently required.
