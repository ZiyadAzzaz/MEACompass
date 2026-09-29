# Competition compliance matrix

Audit date: **2026-09-29**  
Submission category: **Model & Algorithm**

Controlling public sources reviewed:

- [Kaggle: AI4S Open Innovation — AI for Life Science](https://www.kaggle.com/competitions/ai-4-s-open-innovation-artificial-intelligence-for-life-scien)
- [Pazhou Algorithm Competition](https://www.aicompetition-pz.com/)
- [Pazhou participation guidelines](https://www.aicompetition-pz.com/guidelines)
- [Pazhou registration](https://www.aicompetition-pz.com/register)
- [Pazhou challenge registration guidance](https://www.aicompetition-pz.com/topic_registration)
- [Required registration form linked by the Kaggle challenge](https://docs.google.com/forms/d/e/1FAIpQLSdRAat5jIunRaFNh_NntsVeJUnekEJDrbuokLZ32LFgCwPtiA/viewform?usp=publish-editor)

The official Kaggle `Description`, `Rules`, `Submission Requirements`,
`Evaluation`, `Data`, and `Timeline` pages were retrieved through Kaggle's public
read-only competition page service. The Pazhou guidelines were directly checked
for truthful registration, dual-platform consistency where applicable,
originality, intellectual-property responsibility, and data-use constraints.

| Requirement | Official source | Level | MEACompass artifact | Status | Action needed |
|---|---|---|---|---|---|
| Category at the beginning | Kaggle challenge | Mandatory | `docs/kaggle_writeup.md` | **PASS** | None; Model & Algorithm is declared first |
| Kaggle Writeup | Kaggle challenge | Mandatory | `docs/kaggle_writeup.md` | **PASS, waiting video URL** | Replace the sole video placeholder after upload |
| Public demo video, maximum five minutes, no access barrier | Kaggle challenge | Mandatory | 4:45 local draft; script/shot list/SRT/QA committed | **PENDING HUMAN UPLOAD** | Record voice, retime SRTs, final QA, public upload |
| Public code repository | Kaggle challenge | Mandatory | [public GitHub repository](https://github.com/ZiyadAzzaz/MEACompass) | **PASS** | Keep public through judging |
| Technical report | Kaggle challenge | Mandatory | `docs/MEACompass_Technical_Report.pdf` | **PASS** | None; 18 pages |
| Public interactive demo | Kaggle challenge | Optional | [GitHub Pages demo](https://ziyadazzaz.github.io/MEACompass/demo/) | **PASS** | Keep public through judging |
| External registration and truthful team data | Pazhou registration/guidelines | Mandatory | Writeup compliance note; consistent team identity | **PASS** | Do not publish private registration records |
| Team size 1–5; one team per participant in this challenge | Kaggle rules/submission requirements | Mandatory | Solo team: Ziyad Azzaz | **PASS** | Keep Kaggle/Pazhou identity consistent |
| Original work and third-party rights | Pazhou guidelines | Mandatory | `LICENSE`, sources/licenses, provenance manifests | **PASS** | Preserve source/rights inventory |
| Disclose material external models/software/AI tools | Kaggle rules | Mandatory when material | Report, writeup, README, AI disclosure | **PASS** | Keep confirmed roles and human-verification boundary |
| Organizing Committee's stated joint ownership/use terms for submitted materials | Kaggle rules | Mandatory acknowledgement through participation | Submission package | **ACKNOWLEDGED** | Submit only materials the team has the right to submit; third-party terms remain separate |
| No unlicensed raw-data redistribution | Pazhou guidelines | Mandatory | `.gitignore`, EPA and F3b manifests | **PASS** | Keep raw EPA/refinement files ignored |
| Reproducible without paid service/private data | Kaggle challenge | Mandatory | Makefile, environments, committed result manifest | **PASS** | Result-only path needs no paid service or raw data |
| Video demonstrates workflow, outputs, and value | Kaggle challenge | Mandatory | video script and shot list | **READY FOR RECORDING** | Human recording and upload |
| Video/media rights documented | Kaggle challenge; Pazhou IP rule | Mandatory | video QA and sources/licenses | **PASS FOR CURRENT ASSETS** | Do not add media without rights |
| Factual AI-tool disclosure | Technical-report guidance | Recommended | report, writeup, README, AI disclosure | **PASS** | Keep; AI prose is not evidence |
| Report near 15–20 pages | Technical-report guidance | Recommended | 18-page report | **PASS** | None |
| Competition deck | Presentation package | Recommended | 12-slide deck | **PASS** | None |
| Cross-disciplinary bonus | Kaggle submission requirements | Optional | Not claimed; solo AI student team | **NOT CLAIMED** | Do not imply biology/clinical team membership |

## Category rationale

MEACompass is **Model & Algorithm** because its central contribution is the
forecasting and reliability pipeline: chemical-disjoint evaluation, early DIV12
prediction, training-only interval calibration, selective prediction, and
integrity controls. The demo communicates those outputs; it does not turn the
contribution into an end-to-end laboratory system.

## Submission boundary

The dataset is a rat cortical neural MEA assay. The work is not human validation,
not organ-on-chip validation, not external laboratory/device transfer, and not an
autonomous assay-termination system. F3b was CUT before external outcome scoring,
and the original Gate S stop remains visible.

## Originality and third-party-material audit

The tracked package contains project-authored code, prose, tables, demo UI,
figures, deck, report, and subtitles; the canonical Apache-2.0 license text; and
derived result tables. No stock image, third-party logo, external figure, music,
video clip, bundled font, copied notebook, vendored library, or external code
snippet was identified. Third-party scientific data and software are referenced
and installed under their own terms rather than represented as team-authored.

The authentic demo screenshot contains only the project-authored public UI and
stored model outputs. The deck contains that single image plus project-authored
text/shapes. The report uses only repository figures and tables. Raw EPA and
refinement files are excluded from Git.

## Technical-report audit

`docs/MEACompass_Technical_Report.pdf` is **18 pages**. It contains the confirmed
title/team, problem, data and licensing, methods, implementation, experiments,
results, reliability, limitations, practical impact, reproduction, sources, and
AI-tool disclosure. PDF text contains no publication placeholder, confirmation
request, workstation path, private email, or unsupported F3b external-performance
claim. Metadata identifies Ziyad Azzaz as author and ReportLab as producer.
