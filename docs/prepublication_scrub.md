# Pre-publication repository scrub

Date: 2026-09-29  
Scope: current tracked tree, generated demo, report PDF, deck package/XML,
SRT/HTML, structured files, and every reachable Git commit. History was not
rewritten.

## Security and packaging evidence

| Check | Status | Evidence |
|---|---|---|
| Secrets and credentials | PASS | No AWS/GitHub/OpenAI-style token, bearer header, password assignment, private-key marker, or secret-key assignment in the current tree or reachable history |
| Sensitive filenames | PASS | No tracked or historical `.env`, private key, credential, or secret file |
| Local/machine paths | PASS | No tracked deliverable, PPTX XML, PDF text, HTML, or subtitle contains a workstation/user-home path; the scrub document describes this check without embedding one |
| Raw data | PASS | No tracked path under `data/` or `external/`; the 20.4 MiB refinement download remains ignored and is not redistributed |
| Models/checkpoints | PASS | No tracked `.pt`, `.pth`, `.ckpt`, `.joblib`, `.pkl`, or `.onnx`; local final-model artifacts remain ignored |
| Other-project content | PASS | No tracked file from the earlier imaging repository or its deliverables |
| Oversized/history blobs | PASS | Largest current tracked file is `results/demo_predictions.csv` at 5,811,523 bytes; no reachable historical blob exceeds 10 MiB |
| Temporary outputs | PASS | Duplicate authoring deck removed from the tracked tree; working deck is retained locally under an ignore rule; only the judge-facing deck is tracked |
| Personal correspondence | PASS | No private email text or personal email address detected in tracked deliverables or history |
| Structured/package validity | PASS | All checked JSON/YAML parses; PPTX ZIP CRC passes; report PDF opens as 18 pages; no tracked notebook |
| URL syntax | PASS | 22 unique HTTP(S) references found across text artifacts; all parse as absolute URLs |
| Public demo package | PASS | Self-contained 160,901-byte HTML; live anonymous HTTP 200 at `https://ziyadazzaz.github.io/MEACompass/demo/`; OBSERVED/PREDICTED/HYPOTHESIS and all three registered cases present; no external request |
| License boundary | PASS | Apache-2.0 covers project-authored material; data/dependency terms and the limited EPA file-level rationale are separated |
| Scientific boundaries | PASS | Failed Gate S, rat-MEA scope, 3/5 abstention limitation, F3b harmonization CUT, and non-autonomous-use wording remain visible |
| AI disclosure | PASS | Author confirmed Codex/coding-agent, ChatGPT, and Claude roles; scientific-number and human-review boundaries are stated consistently |
| Team identity | PASS | MEACompass; solo submission by Ziyad Azzaz with the verified AASTMT affiliation; no other members |
| Deck screenshot | BRANCH | Final-named 12-slide deck retains a visible real-capture requirement; no mock screenshot was inserted |
| GitHub identity and repository | PASS | `gh api user --jq .login` returned exactly `ZiyadAzzaz`; public `main` repository created at `https://github.com/ZiyadAzzaz/MEACompass` |

## External-validation handling

Six allowlisted EPA refinement files were fetched from the pinned commit only,
then hashed. They remain ignored. F3b was CUT before external outcome scoring
because `cv.time` and `cv.network` are absent and `r` fails the registered
compatibility threshold. Only aggregate harmonization/audit evidence is tracked.

## Publication decision

**PUBLICATION SCRUB: PASS — SAFE TO PUBLISH**

The complete rerun found no secret, raw-data, checkpoint, local-path,
other-project, malformed-package, or oversized-history defect. Team and AI-tool
fields are confirmed and filled. The runtime identity check returned exactly
`ZiyadAzzaz`, the scrubbed history was pushed publicly, and the static demo was
verified anonymously. The slide-10 real screenshot and final video remain
post-publication human/recording work and do not weaken repository security.
